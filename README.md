# 🇬🇧🎙️ English Accent Analyzer 🗣️🔍🌏

Welcome to the **English Accent Analyzer**! This web application leverages the power of Google's Gemini AI to analyze the English accent of a speaker from a video. Users can conveniently provide a video by either uploading a file directly 📤 or by pasting a YouTube/direct video URL 🔗. The application then processes the video, extracts the audio 🔊, sends it for AI-powered accent analysis, and presents a comprehensive report 📊 including the classified accent type, a confidence score, and a detailed explanation of the vocal characteristics.

## ✨ Core Features

*   📥 **Flexible Video Input**:
    *   Supports direct video file uploads (e.g., `.mp4`, `.mov`).
    *   Accepts YouTube video URLs.
    *   Handles direct video URLs from other sources.
*   🔊 **Automatic Audio Extraction**: Seamlessly extracts the audio track from the input video using `ffmpeg`.
*   🧠 **AI-Powered Accent Analysis**: Utilizes Google's Gemini API for sophisticated English accent classification.
*   📊 **Detailed & Structured Results**: Provides clear and insightful feedback:
    *   🗣️ **Accent Classification**: Identifies the type of English accent (e.g., American, British, Australian, Indian).
    *   💯 **Confidence Score**: Rates the AI's confidence in its assessment (0-100%).
    *   📝 **In-depth Explanation**: Offers a textual description of the accent's key characteristics and the reasoning behind the classification.
*   🌐 **User-Friendly Web Interface**: A clean, intuitive, and responsive interface built with Flask and modern web technologies.
*   ⏱️ **Temporary File Management**:
    *   Automatically clears the temporary video upload directory (`temp_videos`) upon application startup.
    *   Periodically cleans up old analysis result files (older than 1 hour) from the `outputs/temp` directory.
*   🛡️ **Error Handling**: Gracefully handles potential issues during video download, audio extraction, and API communication, providing informative feedback to the user.

## ⚙️ Application Workflow: A Step-by-Step Guide

The application follows a clear and logical process:

1.  **🎬 User Provides Video**:
    *   The user navigates to the application's homepage (`/`).
    *   They input a video URL (YouTube or direct link) into the form or (previously, this feature might be adapted/removed based on current `app.py` which focuses on URL) upload a video file.
2.  **⬇️ Video Acquisition & Preparation**:
    *   The application receives the URL via a `POST` request to the `/analyze` endpoint.
    *   **YouTube Videos**: If a YouTube URL is detected, `download_youtube_video()` uses the `pytubefix` library to download the video into the `temp_videos` folder. It selects the best available MP4 stream.
    *   **Direct Video URLs**: For other URLs, `download_direct_video()` attempts to download the video using the `requests` library and saves it with a unique name in `temp_videos`.
    *   A unique `session_id` is generated using `uuid.uuid4()` to track the user's request.
3.  **🔊 Audio Extraction**:
    *   The `extract_audio()` function is called with the path to the downloaded video.
    *   `ffmpeg` (executed as a subprocess) is employed to strip the audio from the video and save it as an `.mp3` file in the same `temp_videos` directory.
4.  **🤖 Accent Analysis via Gemini API**:
    *   The `analyze_accent_with_gemini()` function takes the path to the extracted `.mp3` audio file.
    *   **File Upload**: The audio file is uploaded to Google's Generative AI file service using `genai.upload_file()`.
    *   **Processing Wait**: The application polls the status of the uploaded file using `genai.get_file()` until its state becomes `ACTIVE` (state code 2), indicating it's ready for processing.
    *   **Function Declaration**: A `FunctionDeclaration` named `provide_accent_analysis` is defined. This tells the Gemini model the exact structure (parameters: `accent_classification`, `confidence_score`, `explanation`) in which to return its analysis. This ensures predictable and parsable output.
    *   **Prompt Engineering**: A detailed prompt is sent to the Gemini model (`gemini-2.0-flash`). This prompt guides the AI to:
        *   Identify the English accent type.
        *   Provide a confidence score (0-100%) regarding native/fluent English speech.
        *   Explain its reasoning, focusing on pronunciation, rhythm, intonation, and grammatical patterns.
    *   **API Call**: The `model.generate_content()` method is invoked with the prompt, the uploaded audio file, and the `tools` (containing the function declaration).
    *   **Response Parsing**: The structured data from the model's `function_call` (within the response) is extracted. The confidence score is validated to be within 0-100.
5.  **💾 Storing Results**:
    *   If the analysis is successful, the results (accent data, video title, original URL) are packaged into a dictionary.
    *   This dictionary is then serialized using `pickle` and saved to a file named `{session_id}.pkl` within the `outputs/temp` directory.
6.  **📈 Displaying Results**:
    *   The user is redirected to the `/results` page.
    *   The `results()` function retrieves the `session_id`.
    *   It loads the pickled data from the corresponding `.pkl` file.
    *   The data is then passed to the `results.html` template for rendering, displaying the accent analysis to the user.
7.  **🧹 Automated Cleanup**:
    *   `cleanup_temp_videos()`: Runs on application startup to clear any leftover files in the `temp_videos` (video upload) directory.
    *   `cleanup_old_temp_files()`: Runs `@app.before_request`. This function checks the `outputs/temp` directory (where pickled results are stored) and deletes any `.pkl` files older than 1 hour (3600 seconds). This helps manage storage space.

## 🛠️ Technologies & Libraries Powering the Analyzer

*   **🐍 Backend Framework**:
    *   Flask (Python web framework)
*   **☁️ AI & Cloud Services**:
    *   Google Generative AI SDK (`google-generativeai`) for the Gemini API.
*   **🎬 Video & Audio Processing**:
    *   `pytubefix`: For robust downloading of YouTube videos.
    *   `requests`: For downloading videos from direct URLs.
    *   `ffmpeg`: The industry-standard tool for audio extraction (requires separate installation).
    *   `subprocess`: To interact with `ffmpeg`.
*   **📄 Data Handling & Utilities**:
    *   `os`, `time`, `json`, `uuid`, `pickle` (Python standard libraries)
    *   `werkzeug.utils.secure_filename`: For sanitizing filenames.
    *   `python-dotenv`: For managing environment variables (like API keys).
*   **🎨 Frontend**:
    *   HTML5
    *   CSS3
    *   JavaScript (for any client-side interactions, though primarily server-rendered via Flask templates)
*   **🪵 Logging**:
    *   Python's `logging` module for application event tracking and debugging.

*(Refer to `requirements.txt` for a complete list of Python dependencies and their versions.)*

## 🚀 Getting Started: Setup and Installation

1.  **💾 Clone the Repository** (if you haven't already):
    ```bash
    git clone https://github.com/nikeshmalik3/AI--Accent-Analyzer.git
    cd AI--Accent-Analyzer
    ```

2.  **🌳 Create and Activate a Python Virtual Environment**:
    ```bash
    python -m venv venv
    ```
    *   Windows: `venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`

3.  **📦 Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **🔊 Install `ffmpeg`**:
    This application relies on `ffmpeg` for audio extraction. It's a powerful multimedia framework that needs to be installed separately.
    *   **Windows**: Download binaries from [ffmpeg.org](https://ffmpeg.org/download.html). Extract them and add the `bin` directory to your system's PATH environment variable.
    *   **macOS** (using Homebrew): `brew install ffmpeg`
    *   **Linux** (Debian/Ubuntu): `sudo apt update && sudo apt install ffmpeg`
    Verify installation by typing `ffmpeg -version` in your terminal.

5.  **🔑 Set Up Environment Variables**:
    Create a `.env` file in the project's root directory. This file will store sensitive information and configurations.
    ```env
    GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
    SECRET_KEY="YOUR_FLASK_SECRET_KEY"
    # Optional: Adjust maximum file size for uploads (default is 200MB)
    # MAX_FILE_SIZE=200
    ```
    *   Replace `YOUR_GOOGLE_GEMINI_API_KEY` with your actual key from Google AI Studio.
    *   Generate a strong `SECRET_KEY` for Flask sessions (e.g., run `python -c "import os; print(os.urandom(24).hex())"` in your terminal).

6.  **▶️ Run the Application**:
    ```bash
    flask run
    ```
    Or, for development mode with debugging (as per `app.py`):
    ```bash
    python app.py
    ```
    The application will typically be accessible at `http://127.0.0.1:5001/` (note the port 5001 from your `app.py`).

## 📖 How to Use the Analyzer

1.  Open your favorite web browser 🌐.
2.  Navigate to the application's URL (e.g., `http://127.0.0.1:5001/`).
3.  On the homepage, you'll find an input field:
    *   **Enter Video URL**: Paste a YouTube video URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`) or a direct link to a video file (e.g., `https://example.com/myvideo.mp4`).
4.  Click the "Analyze Video" (or similar) button.
5.  ⏳ Please be patient! The analysis involves video download, audio extraction, and AI processing, which can take some time depending on video length and server load.
6.  Once complete, you'll be redirected to the results page, showcasing:
    *   The **video title**.
    *   The **classified accent**.
    *   The AI's **confidence score**.
    *   A **detailed explanation** of the accent features.

## 🎬 Demo Video (from Repository via Git LFS)

Check out the application in action with our demo video, hosted directly in this repository using Git LFS:

**➡️ [Watch Demo Video (MP4)](WhatsApp%20Video%202025-05-21%20at%2021.05.52_3c6865ef.mp4)**

*To view: Click the link above. GitHub will allow you to view or download the video. For the best viewing experience, downloading the MP4 file might be preferable.*

*(Note: This video is stored using Git LFS. Ensure you have Git LFS installed if you are cloning and working with this repository locally and need to interact with the actual video file.)*


## 🔗 YouTube Videos Previously Referenced for Demo/Analysis

The following YouTube videos were mentioned in earlier development or demonstration contexts:

1.  [https://www.youtube.com/watch?v=MttW2lFnhKw](https://www.youtube.com/watch?v=MttW2lFnhKw)
2.  [https://www.youtube.com/watch?v=AmC9SmCBUj4](https://www.youtube.com/watch?v=AmC9SmCBUj4)
3.  [https://www.youtube.com/watch?v=NsyI9LIXbFM](https://www.youtube.com/watch?v=NsyI9LIXbFM)

## 📄 Code Deep Dive (`app.py`)

The heart of the application, `app.py`, orchestrates the entire process. Here's a summary of its main sections:

*   **🔵 Initial Setup & Configuration**:
    *   Imports: `Flask`, `google.generativeai`, `pytubefix`, `requests`, `os`, `time`, `uuid`, `pickle`, etc.
    *   Logging: Basic logging is configured to INFO level.
    *   Environment: `load_dotenv()` loads API keys and other secrets.
    *   Flask App: `app = Flask(__name__)` initializes the web server.
    *   Configuration: Sets `SECRET_KEY`, `UPLOAD_FOLDER` (`temp_videos`), `OUTPUT_FOLDER` (`outputs`), and `MAX_CONTENT_LENGTH`.
    *   Directory Creation: Ensures `temp_videos` and `outputs` directories exist.
    *   Gemini API: `genai.configure()` sets up the API key.
    *   Startup Cleanup: `cleanup_temp_videos()` is called to empty the upload directory.

*   **🛠️ Core Helper Functions**:
    *   `download_youtube_video(youtube_url)`:
        *   Uses `pytubefix.YouTube` to fetch and download MP4 streams.
        *   Includes User-Agent headers to mitigate 403 errors.
        *   Returns a dictionary with `success`, `file_path`, and `title`.
        *   Handles `RegexMatchError`, `VideoUnavailable`, `PytubeError`, and `requests.exceptions.HTTPError`.
    *   `download_direct_video(url)`:
        *   Downloads content from any direct video URL using `requests.get(url, stream=True)`.
        *   Saves with a unique UUID-based filename.
        *   Returns `success`, `file_path`, and a title derived from the URL.
    *   `extract_audio(video_path)`:
        *   Constructs an `ffmpeg` command (`ffmpeg -y -i <video_path> -q:a 0 -map a <audio_path.mp3>`).
        *   Runs it using `subprocess.run(cmd, check=True)`.
        *   Returns the path to the `.mp3` file.
    *   `analyze_accent_with_gemini(audio_path)`:
        *   Uploads audio: `genai.upload_file(path=audio_path)`.
        *   Polls file status: `genai.get_file()` in a loop until `doc.state == 2` (ACTIVE).
        *   Defines `accent_analysis_function` (a `genai.types.FunctionDeclaration`) to structure the AI's output (accent, confidence, explanation).
        *   Crafts a detailed `prompt` for the "gemini-2.0-flash" model.
        *   Generates content: `model.generate_content([prompt, uploaded_file], tools=...)`.
        *   Extracts structured arguments from `response.candidates[0].content.parts[0].function_call.args`.
        *   Validates and sanitizes `confidence_score`.
        *   Returns a dictionary with `success` and `accent_data`.

*   **🌐 Flask Routes (Endpoints)**:
    *   `@app.route('/') def index()`:
        *   Renders `templates/index.html`.
    *   `@app.route('/analyze', methods=['POST']) def analyze()`:
        *   Handles the form submission from `index.html`.
        *   Retrieves `video_url`.
        *   Generates `session_id = str(uuid.uuid4())` and stores it in `session['session_id']`.
        *   Calls `download_youtube_video` or `download_direct_video` based on URL.
        *   Calls `extract_audio`.
        *   Calls `analyze_accent_with_gemini`.
        *   If all successful:
            *   Creates `outputs/temp` directory if needed.
            *   Pickles a dictionary containing `accent_data`, `video_title`, and `video_url` into `outputs/temp/{session_id}.pkl`.
            *   Redirects to `url_for('results')`.
        *   Flashes error messages on failure and redirects to `index`.
    *   `@app.route('/results') def results()`:
        *   Retrieves `session_id` from the Flask `session`.
        *   Constructs the path to the `.pkl` file in `outputs/temp`.
        *   Loads the pickled data.
        *   Renders `templates/results.html`, passing the loaded data to the template.
        *   Handles cases where `session_id` or the data file is missing.
    *   `@app.before_request def cleanup_old_temp_files()`:
        *   Iterates through files in `outputs/temp`.
        *   Deletes any file older than 1 hour (`os.path.getmtime(file_path) < current_time - 3600`).

*   **🚦 Main Execution Block**:
    *   `if __name__ == '__main__': app.run(debug=True, port=5001)`: Starts the Flask development server on port 5001 with debugging enabled.

## ⚠️ Important Warning & Code Usage Policy

**This codebase is provided strictly for demonstration and educational purposes related to a specific project or academic assessment.**

*   🛑 **DO NOT REUSE, COPY, OR REDISTRIBUTE THIS CODE** for any other assignments, personal projects, commercial ventures, or non-commercial activities without obtaining explicit prior permission.
*   💡 The solutions herein are tailored to the unique requirements of this specific task and may not be suitable for other applications.
*   🎓 Submitting this code, either in its entirety or in part, as your own original work for any other purpose is a violation of academic integrity and may be considered plagiarism.

Your respect for the intellectual effort invested in this project is greatly appreciated. Please use it responsibly and ethically.

---

This updated `README.md` aims to be more visually appealing, comprehensive, and directly reflective of your `app.py`. Feel free to suggest further refinements! 