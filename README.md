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
        (This installs Flask, python-dotenv, and the SDKs for OpenAI, Google Gemini, and Alibaba Qwen).

    5.  **Set your API Keys and Choose Provider:**
        The backend requires API keys for the LLM services you intend to use. These are configured in the `backend/.env` file.

        *   Navigate to the `backend/` directory if you are not already there (you should be if following these steps sequentially).
        *   Copy `backend/.env.example` to `backend/.env` if you haven't already:
            ```bash
            cp .env.example .env
            ```
        *   Open `backend/.env` in a text editor.

        *   **Choose your LLM Provider:**
            Set the `LLM_PROVIDER` variable to one of `"openai"`, `"google"`, or `"qwen"`.
            Example: `LLM_PROVIDER="google"` (The default in `.env.example` is "openai").

        *   **Configure API Key(s):**
            You only need to provide the API key for the `LLM_PROVIDER` you have selected. However, you can fill in all keys if you plan to switch between them.

            *   **For OpenAI:**
                Set `OPENAI_API_KEY` with your key from [OpenAI Platform](https://platform.openai.com/signup/).
                Default model used: `gpt-3.5-turbo`.
                ```
                OPENAI_API_KEY="sk-YourActualOpenAIKeyHere..."
                ```

            *   **For Google Gemini:**
                Set `GOOGLE_API_KEY` with your key from [Google AI Studio](https://aistudio.google.com/app/apikey) or Google Cloud Console.
                Default model used: `gemini-1.5-flash-latest`.
                ```
                GOOGLE_API_KEY="YourActualGoogleApiKeyHere..."
                ```

            *   **For Alibaba Qwen (Tongyi via Dashscope):**
                Set `QWEN_API_KEY` with your API Key from the [Dashscope Console](https://help.aliyun.com/document_detail/2512185.html). The service will use this key to configure the Dashscope SDK.
                Default model used: `qwen-turbo`.
                ```
                QWEN_API_KEY="sk-YourActualDashscopeApiKeyHere..."
                ```
                (Note: The Dashscope SDK also typically recognizes the `DASHSCOPE_API_KEY` environment variable if set globally, but the application primarily uses the key provided via `QWEN_API_KEY` to configure the SDK at runtime.)

        **Important:** Ensure the `.env` file (which contains your secret keys) is never committed to version control. The project's `.gitignore` file is already configured to ignore `.env` files.
    6.  **Run the Flask server:**
        ```bash
        python -m app.main
        ```
        The backend server will start, typically on `http://localhost:5000`.

        **Cross-Origin Resource Sharing (CORS):**
        The backend is configured using `Flask-CORS` to allow cross-origin requests from any origin to the `/api/*` routes. This is necessary for the browser plugin (and other web applications) to interact with the API when served from a different domain or port (e.g., the plugin's `chrome-extension://` origin).

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

### Configuring the Backend URL (Optional)

By default, the plugin attempts to connect to a backend server running at `http://localhost:5000`. If your backend server is running on a different URL or port, you can configure the plugin to use your custom address:

1.  Navigate to the `plugin/` directory within the project.
2.  Copy the example configuration file `config.json.example` to a new file named `config.json`:
    ```bash
    # If you are in the plugin/ directory
    cp config.json.example config.json
    ```
3.  Open `plugin/config.json` in a text editor.
4.  Modify the `backend_url` value to your backend server's address. For example:
    ```json
    {
      "backend_url": "https://your-custom-backend.example.com"
    }
    ```
5.  Save the `plugin/config.json` file.

If `plugin/config.json` is not found, is malformed, or the `backend_url` is invalid, the plugin will default to using `http://localhost:5000`.

**Note:** After creating or modifying `plugin/config.json`, you may need to reload the extension in your browser for the changes to take effect. You can usually do this from the browser's extensions page (e.g., by clicking the "reload" icon for the extension in Chrome Developer Mode).

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
