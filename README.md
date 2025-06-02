# AI Productivity Assistant Browser Plugin

This project is a browser plugin designed to boost productivity by integrating Large Language Model (LLM) capabilities directly into your browser. It offers features like text translation, document format analysis/conversion (currently text extraction and analysis), and intelligent search.

## Features

*   **Text Translation:** Translate selected text or manually entered text to various languages.
*   **Document Analysis:** Upload text-based documents (.txt, .md, .py, .js, .html, .css, .csv, .json, .xml) for analysis and summarization by an LLM.
*   **Intelligent Search:** Perform intelligent searches using an LLM for context-aware results.
*   **User-Friendly Interface:** Simple popup interface for easy access to all features.

## Project Structure

```
.
├── backend/                # Python Flask backend
│   ├── app/                # Main application logic
│   │   ├── __init__.py
│   │   ├── main.py         # Flask API endpoints
│   │   └── llm_service.py  # LLM interaction logic (OpenAI)
│   ├── tests/              # Backend unit tests
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_llm_service.py
│   └── requirements.txt    # Python dependencies
├── plugin/                 # Browser plugin files (for Chrome, Firefox, etc.)
│   ├── images/             # Icons for the plugin
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── icon128.png
│   ├── manifest.json       # Plugin manifest file
│   ├── popup.html          # HTML for the plugin popup
│   ├── popup.js            # JavaScript for popup logic
│   └── style.css           # CSS for popup styling
├── TESTING_MANUAL.md       # Manual testing plan
└── README.md               # This file
```

## Setup and Usage

### 1. Backend Setup

The backend is a Python Flask server that handles LLM interactions.

*   **Prerequisites:**
    *   Python 3.7+
    *   An OpenAI API Key (obtain from [https://platform.openai.com/signup/](https://platform.openai.com/signup/))

*   **Steps:**
    1.  **Clone the repository:**
        ```bash
        git clone <repository_url>
        cd <repository_name>
        ```
    2.  **Navigate to the backend directory:**
        ```bash
        cd backend
        ```
    3.  **Create and activate a virtual environment:**
        ```bash
        python -m venv venv
        # On macOS/Linux:
        source venv/bin/activate
        # On Windows:
        # venv\Scripts\activate
        ```
    4.  **Install dependencies:**
        ```bash
        pip install -r requirements.txt
        ```
    5.  **Set your OpenAI API Key:**
        Replace `'your_openai_api_key_here'` with your actual key.
        ```bash
        # On macOS/Linux:
        export OPENAI_API_KEY='your_openai_api_key_here'
        # On Windows (PowerShell):
        # $env:OPENAI_API_KEY='your_openai_api_key_here'
        # On Windows (Command Prompt):
        # set OPENAI_API_KEY=your_openai_api_key_here
        ```
        **Important:** Do not commit your API key. Ensure it's kept secret.
    6.  **Run the Flask server:**
        ```bash
        python -m app.main
        ```
        The backend server will start, typically on `http://localhost:5000`.

### 2. Frontend Plugin Setup (Loading the Extension)

This plugin is loaded as an unpacked extension in your browser.

*   **For Google Chrome (or Chromium-based browsers):**
    1.  Open Chrome and navigate to `chrome://extensions`.
    2.  Enable **Developer mode** (usually a toggle in the top right).
    3.  Click the **Load unpacked** button.
    4.  In the file dialog, navigate to the root directory of this project and select the `plugin/` sub-directory.
    5.  The "AI Productivity Assistant" plugin should now appear in your list of extensions and its icon in the browser toolbar.

*   **For Mozilla Firefox:**
    1.  Open Firefox and navigate to `about:debugging#/runtime/this-firefox`.
    2.  Click the **Load Temporary Add-on...** button.
    3.  In the file dialog, navigate to the `plugin/` directory and select the `manifest.json` file.
    4.  The plugin will be loaded temporarily and its icon should appear. (Note: Temporary add-ons in Firefox are removed when you close the browser unless you use `web-ext` for development).

### 3. Using the Plugin

Once the backend is running and the plugin is loaded:

1.  Click the "AI Productivity Assistant" icon in your browser's toolbar.
2.  The plugin popup will appear, allowing you to use the translation, document analysis, and search features.

## Running Backend Tests

The backend includes unit tests for the API endpoints and the LLM service.

1.  Ensure your virtual environment is activated and dependencies are installed (see Backend Setup).
2.  Navigate to the `backend/` directory if you are not already there.
3.  Run the tests:
    ```bash
    python -m unittest discover tests
    ```
    (If you are in the root directory, you can run `python -m unittest discover backend/tests`)

## Future Development Ideas

*   Full document conversion (e.g., PDF/DOCX to text).
*   User-configurable knowledge base for intelligent search.
*   More advanced LLM models and prompt engineering.
*   OAuth for user-specific data or settings.
*   Packaging for easier distribution (e.g., as a `.zip` file for Chrome Web Store).

## Contributing

Contributions are welcome! Please feel free to fork the repository, make changes, and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

---

*This README provides a comprehensive guide to setting up and using the AI Productivity Assistant.*
