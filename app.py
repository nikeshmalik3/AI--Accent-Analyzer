import os
import time
import json
import uuid
import pickle
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import logging
from pytubefix import YouTube
from pytube.exceptions import RegexMatchError, VideoUnavailable, PytubeError
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Clean up temp videos directory on startup
def cleanup_temp_videos():
    """Delete all files in the temp_videos directory on script startup"""
    try:
        temp_dir = 'temp_videos'
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    logger.info(f"Deleted temporary file: {file_path}")
        logger.info("Temporary video directory cleaned up")
    except Exception as e:
        logger.error(f"Error cleaning up temporary videos: {str(e)}")

# Run cleanup on startup
cleanup_temp_videos()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY', '#')) # i have already delete the api key 😊

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'development_key')
app.config['UPLOAD_FOLDER'] = 'temp_videos'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 200)) * 1024 * 1024  # Default 200MB

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def download_youtube_video(youtube_url):
    try:
        # Add user-agent to help avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Set up YouTube with additional parameters
        yt = YouTube(
            youtube_url,
            use_oauth=False,
            allow_oauth_cache=True
        )
        
        # Get video information
        logger.info(f"Attempting to download video: {yt.title}")
        
        # Try to get the highest resolution progressive stream
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not video:
            # If no progressive stream is available, try adaptive streams
            logger.info("No progressive stream found, trying adaptive streams")
            video = yt.streams.filter(file_extension='mp4').first()
            
        if not video:
            raise Exception("No suitable video format found")
        
        # Create a filename based on the video title
        filename = secure_filename(yt.title) + '.mp4'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Try to download the video
        logger.info(f"Downloading video to {file_path}")
        video.download(app.config['UPLOAD_FOLDER'], filename=filename)
        
        # Verify file exists and has content
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise Exception("Download failed: File empty or not created")
            
        logger.info(f"Successfully downloaded video: {yt.title}")
        
        return {
            'success': True,
            'file_path': file_path,
            'title': yt.title
        }
    except RegexMatchError:
        return {
            'success': False,
            'error': "Failed to parse video ID. Please check the YouTube URL and try again."
        }
    except VideoUnavailable:
        return {
            'success': False,
            'error': "This video is unavailable. It might be private, age-restricted, or deleted."
        }
    except PytubeError as e:
        logger.error(f"Pytube error: {str(e)}")
        return {
            'success': False,
            'error': f"YouTube download error: {str(e)}. This might be due to YouTube's restrictions or recent changes to their website."
        }
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {str(e)}")
        if "403" in str(e):
            return {
                'success': False,
                'error': "Access forbidden by YouTube. This might be due to regional restrictions, age verification requirements, or YouTube's anti-bot measures."
            }
        return {
            'success': False,
            'error': f"HTTP Error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error during download: {str(e)}")
        return {
            'success': False,
            'error': f"Error downloading video: {str(e)}"
        }

def extract_audio(video_path):
    """
    Extract audio from the video file
    
    Args:
        video_path: Path to the input video file
        
    Returns:
        Path to the extracted audio file
    """
    try:
        audio_path = os.path.splitext(video_path)[0] + '.mp3'
        
        # Use ffmpeg to extract audio
        cmd = [
            'ffmpeg', '-y', '-i', video_path, 
            '-q:a', '0', '-map', 'a', audio_path
        ]
        
        subprocess.run(cmd, check=True)
        logger.info(f"Audio extracted to {audio_path}")
        
        return audio_path
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        raise

def analyze_accent_with_gemini(audio_path):
    try:
        logger.info(f"Analyzing audio file: {audio_path}")
        
        # Upload the audio file to Gemini
        uploaded_file = genai.upload_file(path=audio_path)
        logger.info(f"Audio file uploaded to Gemini API")
        
        # Wait for file to be processed
        while True:
            try:
                doc = genai.get_file(name=uploaded_file.name)
                logger.info(f"File state: {doc.state}")
                if doc.state == 2:  # ACTIVE state
                    break
            except Exception as e:
                logger.error(f"Error checking file state: {str(e)}")
            time.sleep(5)
        
        # Set up function calling for accent analysis
        accent_analysis_function = genai.types.FunctionDeclaration(
            name="provide_accent_analysis",
            description="Provide analysis of speaker's English accent",
            parameters={
                "type": "object",
                "properties": {
                    "accent_classification": {
                        "type": "string",
                        "description": "Classification of the accent (e.g., British, American, Australian, etc.)"
                    },
                    "confidence_score": {
                        "type": "integer",
                        "description": "Confidence score of English accent (0-100%)"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Brief explanation of accent characteristics and why it was classified this way"
                    }
                },
                "required": ["accent_classification", "confidence_score", "explanation"]
            }
        )
        
        tools = [genai.types.Tool(
            function_declarations=[accent_analysis_function]
        )]
        
        # Create prompt for accent analysis
        prompt = """
        Analyze this audio to evaluate the speaker's English accent. 
        
        I need you to:
        1. Determine the English accent type (e.g., American, British, Australian, Indian, etc.)
        2. Rate how confident you are that this is a native or fluent English speaker on a scale of 0-100%
           - Use the FULL range from 0-100 based on actual evidence in the audio
           - Low scores (0-40%) for speakers with strong non-native accents and many pronunciation errors
           - Medium scores (40-70%) for non-native speakers with moderate accents but good fluency
           - High scores (70-90%) for near-native speakers with slight accents
           - Very high scores (90-100%) only for speakers who sound completely native
        3. Provide a brief explanation of your analysis
        
        Focus specifically on:
        - Pronunciation of vowels and consonants
        - Rhythm and intonation patterns
        - Any distinctive features of the accent
        - Common speech patterns that identify the accent origin
        - Grammatical errors that might indicate non-native speaking
        
        Be critical and objective in your assessment. Vary your confidence score based on the actual evidence in the audio.
        
        Return your findings using the provide_accent_analysis function.
        """
        
        # Generate content with Gemini using function calling
        logger.info("Generating accent analysis with Gemini")
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content([prompt, uploaded_file], tools=tools)
        
        # Log the raw response for debugging
        logger.info(f"Raw Gemini response: {response}")
        
        # Extract the function call results - FIXED approach
        function_call = response.candidates[0].content.parts[0].function_call
        
        # Get individual function call args directly and validate
        try:
            confidence_score = int(function_call.args["confidence_score"])
            # Ensure score is within valid range
            confidence_score = max(0, min(100, confidence_score))
        except (ValueError, TypeError):
            # Default to 50% if we can't parse the score
            confidence_score = 50
            logger.warning("Could not parse confidence score, using default value of 50%")
        
        result_data = {
            "accent_classification": function_call.args["accent_classification"],
            "confidence_score": confidence_score,
            "explanation": function_call.args["explanation"]
        }
        
        return {
            "success": True,
            "accent_data": result_data
        }
            
    except Exception as e:
        logger.error(f"Error in accent analysis: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def download_direct_video(url):
    try:
        # Generate a unique filename
        extension = url.split('.')[-1] if '.' in url.split('/')[-1] else 'mp4'
        filename = f"direct_video_{str(uuid.uuid4())[:8]}.{extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise Exception("Download failed: File empty or not created")
        
        # Simple title based on the URL
        title = url.split('/')[-1]
        
        return {
            'success': True,
            'file_path': file_path,
            'title': title
        }
    except Exception as e:
        logger.error(f"Error downloading direct video: {str(e)}")
        return {
            'success': False,
            'error': f"Error downloading video: {str(e)}"
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        
        if not video_url:
            flash('Please provide a video URL', 'error')
            return redirect(url_for('index'))
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        try:
            # Determine the type of URL and download the video
            if 'youtube.com' in video_url or 'youtu.be' in video_url:
                download_result = download_youtube_video(video_url)
            else:
                # Assume it's a direct video URL
                download_result = download_direct_video(video_url)
            
            if not download_result['success']:
                flash(f'Error downloading video: {download_result["error"]}', 'error')
                return redirect(url_for('index'))
            
            video_path = download_result['file_path']
            
            # Extract audio from the video
            audio_path = extract_audio(video_path)
            
            # Analyze the accent with Gemini
            analysis_result = analyze_accent_with_gemini(audio_path)
            
            if analysis_result['success']:
                # Store results in file system
                temp_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'temp')
                os.makedirs(temp_dir, exist_ok=True)
                
                data_path = os.path.join(temp_dir, f"{session_id}.pkl")
                with open(data_path, 'wb') as f:
                    pickle.dump({
                        'accent_data': analysis_result['accent_data'],
                        'video_title': download_result['title'],
                        'video_url': video_url
                    }, f)
                
                return redirect(url_for('results'))
            else:
                flash(f'Error analyzing accent: {analysis_result.get("error", "Unknown error")}', 'error')
                return redirect(url_for('index'))
        
        except Exception as e:
            logger.error(f"Error in analyze route: {str(e)}")
            flash(f'An unexpected error occurred: {str(e)}', 'error')
            return redirect(url_for('index'))

@app.route('/results')
def results():
    session_id = session.get('session_id')
    if not session_id:
        flash('No analysis results available', 'error')
        return redirect(url_for('index'))
    
    # Load data from file
    temp_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'temp')
    data_path = os.path.join(temp_dir, f"{session_id}.pkl")
    
    if not os.path.exists(data_path):
        flash('Results no longer available', 'error')
        return redirect(url_for('index'))
    
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
    
    return render_template('results.html', accent_data=data['accent_data'], 
                           video_title=data['video_title'],
                           video_url=data['video_url'])

# Add cleanup function to delete temporary files
@app.before_request
def cleanup_old_temp_files():
    """Delete temporary files older than 1 hour"""
    try:
        temp_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'temp')
        if os.path.exists(temp_dir):
            current_time = time.time()
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    # If file is older than 1 hour, delete it
                    if current_time - os.path.getmtime(file_path) > 3600:
                        os.unlink(file_path)
                        logger.info(f"Deleted old temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
