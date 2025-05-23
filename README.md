# English Accent Analyzer 🗣️🔍

This project is a web application that analyzes the English accent of a speaker from a video. Users can either upload a video file directly or provide a YouTube video URL. The application extracts the audio from the video, sends it to Google's Gemini API for accent analysis, and then displays the results, including the classified accent type, a confidence score, and an explanation.

## ✨ Features

*   **Video Upload**: Supports direct video file uploads.
*   **YouTube Video Support**: Allows users to analyze videos directly from YouTube URLs.
*   **Automatic Audio Extraction**: Extracts audio from the provided video (MP4 format).
*   **Accent Analysis with Gemini API**: Leverages Google's Gemini API for sophisticated accent classification and analysis.
*   **Detailed Results**: Provides:
    *   Accent Classification (e.g., American, British, Indian)
    *   Confidence Score (0-100%) of the accent assessment.
    *   Detailed Explanation of the accent characteristics.
*   **User-Friendly Web Interface**: Simple and intuitive interface built with Flask and HTML/CSS/JavaScript.
*   **Temporary File Management**: Cleans up temporary video and audio files.

## ⚙️ How It Works

1.  **User Input**: The user visits the web application and either:
    *   Uploads a video file (e.g., `.mp4`).
    *   Pastes a YouTube video URL.
2.  **Video Processing**:
    *   **Uploaded Video**: The video is saved to a temporary directory.
    *   **YouTube Video**: The video is downloaded from the provided URL using `pytubefix` and saved to a temporary directory.
3.  **Audio Extraction**: `ffmpeg` is used to extract the audio track (as an `.mp3` file) from the video.
4.  **Gemini API Interaction**:
    *   The extracted audio file is uploaded to the Gemini API.
    *   A specifically crafted prompt instructs the Gemini model to analyze the speaker's English accent, focusing on pronunciation, rhythm, intonation, and distinctive features.
    *   The API is configured to use function calling to return structured data: accent classification, confidence score, and an explanation.
5.  **Results Display**: The analysis results received from the Gemini API are displayed on a results page in the web application.
6.  **Cleanup**: Temporary video and audio files are deleted from the server.

## 🛠️ Technologies Used

*   **Backend**:
    *   Python
    *   Flask (Web framework)
    *   Google Generative AI SDK (`google-generativeai`) for Gemini API
    *   `pytubefix` (for downloading YouTube videos)
    *   `ffmpeg` (for audio extraction - requires separate installation)
*   **Frontend**:
    *   HTML
    *   CSS
    *   JavaScript
*   **Environment Management**:
    *   `python-dotenv` (for managing environment variables)
*   **Key Python Libraries**: (See `requirements.txt` for a full list)
    *   `Flask`
    *   `google-generativeai`
    *   `pytubefix`
    *   `Werkzeug` (for file handling)
    *   `requests`

## 🚀 Setup and Installation

1.  **Clone the Repository (if applicable)**:
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    ```
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install ffmpeg**:
    `ffmpeg` is required for audio extraction and is not installed via pip. You need to install it separately and ensure it's in your system's PATH.
    *   **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add the `bin` directory to your PATH.
    *   **macOS**: `brew install ffmpeg`
    *   **Linux**: `sudo apt update && sudo apt install ffmpeg`

5.  **Set Up Environment Variables**:
    Create a `.env` file in the root directory of the project and add your Google Gemini API key:
    ```env
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    SECRET_KEY="a_strong_random_secret_key_for_flask_sessions"
    # Optional: Set max upload file size in MB (default is 200MB)
    # MAX_FILE_SIZE=200
    ```
    Replace `"YOUR_GEMINI_API_KEY"` with your actual API key. You can generate a `SECRET_KEY` using `python -c 'import os; print(os.urandom(24).hex())'`.

6.  **Run the Application**:
    ```bash
    flask run
    ```
    Or, for development mode:
    ```bash
    python app.py
    ```
    The application will typically be available at `http://127.0.0.1:5000/`.

## 📖 Usage

1.  Open your web browser and navigate to the application's URL (e.g., `http://127.0.0.1:5000/`).
2.  You will see two options:
    *   **Upload a Video File**: Click "Choose File", select your video, and click "Analyze Video File".
    *   **Enter YouTube URL**: Paste the YouTube video URL into the input field and click "Analyze YouTube Video".
3.  Wait for the analysis to complete. This may take some time depending on the video length and API response time.
4.  The results page will display the accent classification, confidence score, and a detailed explanation.

## 🎬 Demo Video

A demonstration of the application in action can be found here:

[![Watch the Demo Video](https://img.youtube.com/vi/MttW2lFnhKw/0.jpg)](WhatsApp%20Video%202025-05-21%20at%2021.05.52_3c6865ef.mp4)

*(If the image link doesn't work, please ensure the video file `WhatsApp Video 2025-05-21 at 21.05.52_3c6865ef.mp4` is in the root directory or update the path accordingly. For a web-hosted README, you might need to upload the video to a service like YouTube and link it).*

Alternatively, you can link to the video directly:
[Link to Demo Video](WhatsApp%20Video%202025-05-21%20at%2021.05.52_3c6865ef.mp4)


## 🔗 YouTube Videos Analyzed in Demo

The following YouTube videos were used for demonstration and analysis in the project or its development:

1.  [https://www.youtube.com/watch?v=MttW2lFnhKw](https://www.youtube.com/watch?v=MttW2lFnhKw)
2.  [https://www.youtube.com/watch?v=AmC9SmCBUj4](https://www.youtube.com/watch?v=AmC9SmCBUj4)
3.  [https://www.youtube.com/watch?v=NsyI9LIXbFM](https://www.youtube.com/watch?v=NsyI9LIXbFM)

## 📄 Code Overview (`app.py`)

The main application logic is contained in `app.py`. Here's a breakdown of its key components:

*   **Initialization**:
    *   Imports necessary libraries (Flask, Pytube, Gemini API, os, etc.).
    *   Sets up logging.
    *   Loads environment variables (API key, secret key).
    *   Configures the Flask app (upload folder, output folder, max file size).
    *   Initializes the Gemini API with the API key.
    *   Includes a `cleanup_temp_videos()` function to clear the `temp_videos` directory on startup.

*   **Helper Functions**:
    *   `download_youtube_video(youtube_url)`: Downloads a video from a given YouTube URL using `pytubefix`. Handles various exceptions like `RegexMatchError`, `VideoUnavailable`, and general `PytubeError`.
    *   `extract_audio(video_path)`: Uses `ffmpeg` (via `subprocess`) to extract the audio from a video file and saves it as an MP3.
    *   `analyze_accent_with_gemini(audio_path)`:
        *   Uploads the extracted audio file to the Gemini API.
        *   Waits for the file to be processed by the API.
        *   Defines a function declaration (`provide_accent_analysis`) for structured output from the Gemini model. This tells the model what information to return (accent classification, confidence score, explanation).
        *   Constructs a detailed prompt for the Gemini model, instructing it on how to analyze the accent and what criteria to use.
        *   Calls the Gemini API (`gemini-pro-vision` model is used, but for audio-only, a text-based model with audio input capability like `gemini-2.0-flash` as seen in the code is more appropriate) with the prompt and the uploaded audio file.
        *   Parses the structured response from the API.
    *   `download_direct_video(url)`: A placeholder or utility function, potentially for direct video downloads (not fully implemented or used in the primary accent analysis flow in the provided snippet).

*   **Flask Routes**:
    *   `@app.route('/')`:
        *   `index()`: Renders the main page (`index.html`) where users can upload videos or submit YouTube URLs.
    *   `@app.route('/analyze', methods=['POST'])`:
        *   `analyze()`: This is the core endpoint for handling analysis requests.
            *   Determines if the input is a file upload or a YouTube URL.
            *   If a file upload: secures the filename, saves the file, and checks its size.
            *   If a YouTube URL: calls `download_youtube_video()`.
            *   If video processing (upload/download) is successful, it proceeds to:
                1.  Extract audio using `extract_audio()`.
                2.  Analyze the accent using `analyze_accent_with_gemini()`.
                3.  Stores the results (title, analysis data) in the Flask `session`.
                4.  Redirects to the `results` page.
            *   Handles various errors and flashes messages to the user.
    *   `@app.route('/results')`:
        *   `results()`: Retrieves the analysis results from the session and renders the `results.html` page to display them. If no results are found in the session, it redirects back to the home page.
    *   `@app.before_request`:
        *   `cleanup_old_temp_files()`: This function is intended to run before each request to clean up old files in the temporary directory, though the implementation details for "old" files (e.g., based on timestamp) are not shown in the initial snippet (the startup cleanup handles current files).

*   **Error Handling**: The application includes error handling for file uploads (size, type), YouTube video downloads, audio extraction, and API interactions, providing feedback to the user via flashed messages.

## ⚠️ Important Warning

**This code is provided for demonstration and educational purposes related to a specific project or assessment.**

*   **DO NOT REUSE OR COPY THIS CODE** for other assignments, projects, or any commercial/non-commercial purposes without explicit permission.
*   The code may contain specific solutions tailored to the requirements of this particular task.
*   Attempting to submit this code, in whole or in part, as your own work for another purpose may constitute plagiarism or academic dishonesty.

Please respect the intellectual effort involved in creating this solution.

---

This `README.md` should provide a good starting point. You can further customize it with more specific details, screenshots of the UI if you wish, or refine any sections as needed. 