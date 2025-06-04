# Manual Testing Plan for AI Productivity Assistant Plugin

This document outlines the steps to manually test the functionality of the AI Productivity Assistant browser plugin.

**Prerequisites:**

1.  **Backend Server Running:**
    *   Navigate to the `backend/` directory.
    *   Ensure Python dependencies are installed: `pip install -r requirements.txt`.
    *   Set the `OPENAI_API_KEY` environment variable: `export OPENAI_API_KEY='your_openai_api_key'`.
    *   Run the backend server: `python -m app.main`. (It should be running on `http://localhost:5000`).
2.  **Plugin Loaded in Browser:**
    *   Open your browser (e.g., Chrome, Firefox).
    *   Go to the extensions page (e.g., `chrome://extensions` or `about:debugging#/runtime/this-firefox`).
    *   Enable "Developer mode".
    *   Click "Load unpacked" (or equivalent) and select the `plugin/` directory from this project.
    *   The plugin icon should appear in your browser's toolbar.
3.  **CORS Verification (During Functional Tests):**
    *   With the backend now including CORS headers (via `Flask-CORS`), ensure that when you run the functional test cases below (Translation, Document Analysis, Search), there are **no** CORS-related errors in the browser's developer console for the plugin popup.
    *   This is especially important if your backend server is configured via `plugin/config.json` to run on a different domain/port than the plugin's default `http://localhost:5000`.
    *   If CORS is correctly configured on the backend and the plugin is making requests to the allowed `/api/*` routes, these operations should work smoothly without browser complaints about `Access-Control-Allow-Origin`. Pay attention to the console when first testing each feature.

**Test Cases:**

Click the plugin icon to open the popup for each test.

**1. Translation Feature**

*   **Test Case 1.1: Successful Translation**
    *   **Input Text:** `Hello, how are you?`
    *   **Target Language:** `Spanish`
    *   **Action:** Click "Translate".
    *   **Expected Result:** The result area should display the Spanish translation (e.g., `Hola, ¿cómo estás?` or similar, depending on LLM). The area should be styled as a success.
*   **Test Case 1.2: Empty Text Input**
    *   **Input Text:** (leave empty)
    *   **Target Language:** `French`
    *   **Action:** Click "Translate".
    *   **Expected Result:** Result area shows an error message like "Error: Text to translate cannot be empty." Styled as an error.
*   **Test Case 1.3: Empty Target Language**
    *   **Input Text:** `Good morning`
    *   **Target Language:** (leave empty)
    *   **Action:** Click "Translate".
    *   **Expected Result:** Result area shows an error message like "Error: Target language cannot be empty." Styled as an error.
*   **Test Case 1.4: Long Text Translation**
    *   **Input Text:** (Paste a paragraph of text, around 100-150 words)
    *   **Target Language:** `German`
    *   **Action:** Click "Translate".
    *   **Expected Result:** The result area displays the German translation. The area should be scrollable if the text is long.

**2. Document Analysis Feature**

*   **Test Case 2.1: Successful Analysis (Supported File - .txt)**
    *   **Action:**
        1. Create a simple `.txt` file (e.g., `testdoc.txt`) with a few sentences of text.
        2. Click "Choose File", select `testdoc.txt`.
        3. Click "Upload and Analyze".
    *   **Expected Result:** The result area displays a message like "Document processed for analysis." and an "Analysis Preview:" with a summary/analysis from the LLM. Filename and content type should be displayed.
*   **Test Case 2.2: Successful Analysis (Supported File - .md)**
    *   **Action:**
        1. Create a simple `.md` file (e.g., `testdoc.md`) with some markdown text.
        2. Click "Choose File", select `testdoc.md`.
        3. Click "Upload and Analyze".
    *   **Expected Result:** Similar to 2.1, showing analysis from the LLM.
*   **Test Case 2.3: Unsupported File Type (.pdf)**
    *   **Action:**
        1. Have a `.pdf` file ready.
        2. Click "Choose File", select the `.pdf` file.
        3. Click "Upload and Analyze".
    *   **Expected Result:** The result area displays a message indicating that PDF files cannot be automatically extracted from and that full processing is not yet implemented. The "Analysis Preview:" should reflect this message.
*   **Test Case 2.4: No File Selected**
    *   **Action:** Click "Upload and Analyze" without selecting a file.
    *   **Expected Result:** Result area shows an error like "Error: No file selected." Styled as an error.
*   **Test Case 2.5: Large Text File (within limits)**
    *   **Action:**
        1. Create a `.txt` file that is ~1MB in size.
        2. Click "Choose File", select the large text file.
        3. Click "Upload and Analyze".
    *   **Expected Result:** The document is processed, and an analysis is provided. (Verify backend doesn't crash, and if truncation message appears from backend, it's handled).

**3. Intelligent Search Feature**

*   **Test Case 3.1: Successful Search**
    *   **Search Query:** `What are the benefits of unit testing?`
    *   **Action:** Click "Search".
    *   **Expected Result:** The result area displays search results or an answer from the LLM related to unit testing benefits. Styled as success.
*   **Test Case 3.2: Empty Search Query**
    *   **Search Query:** (leave empty)
    *   **Action:** Click "Search".
    *   **Expected Result:** Result area shows an error message like "Error: Search query cannot be empty." Styled as an error.
*   **Test Case 3.3: Broad Search Query**
    *   **Search Query:** `Artificial Intelligence`
    *   **Action:** Click "Search".
    *   **Expected Result:** The result area displays relevant information about Artificial Intelligence. Check for scrollability if the response is long.

**4. General UI/UX**

*   **Test Case 4.1: Responsiveness**
    *   **Action:** Open and close the plugin popup multiple times. Interact with different features.
    *   **Expected Result:** The UI remains responsive. No crashes or significant lag.
*   **Test Case 4.2: Clarity of Messages**
    *   **Action:** Trigger various success and error states for each feature.
    *   **Expected Result:** All messages (loading, success, error) are clear, user-friendly, and displayed in the correct style.
*   **Test Case 4.3: Scrollability of Long Results**
    *   **Action:** Perform actions that are expected to return long text (long translation, detailed search query, analysis of a moderately sized text file).
    *   **Expected Result:** The result areas for each feature become scrollable if the content exceeds the `max-height` (150px), and the entire content is accessible.

**Reporting Issues:**

If any test case fails, note down the test case number, steps taken, actual result, and expected result. Include any console errors from the browser's developer tools (inspect the plugin popup) or the backend server terminal.

## 5. Backend URL Configuration Testing

These tests verify that the plugin correctly loads and uses the backend URL from `plugin/config.json`, and gracefully falls back to the default URL if the configuration is missing or invalid.

**Prerequisites for this section:**
*   Ensure you can start/stop your backend server and know its URL.
*   Be comfortable creating/editing/deleting `plugin/config.json`.
*   Know how to reload the plugin in your browser's developer mode.
*   Have the browser's developer console open for the plugin popup to observe log messages.

**Test Case 5.1: Using `config.json` with a (temporarily) invalid custom URL**
*   **Setup:**
    1.  Ensure your backend server IS running (e.g., on the default `http://localhost:5000`).
    2.  In `plugin/` directory, create `config.json` (copy from `config.json.example` if needed).
    3.  Edit `plugin/config.json` to set `backend_url` to a URL where no server is running, e.g., `http://localhost:9999`.
    4.  Reload the plugin in your browser.
*   **Action:**
    1.  Open the plugin popup.
    2.  Attempt to use a feature (e.g., Translate "Test" to "Spanish").
*   **Expected Result:**
    *   The plugin UI should show an error message indicating a failure to connect to the server (e.g., "Error: Could not connect to the server." or a network error).
    *   The browser's developer console for the plugin popup should show an error related to fetching from `http://localhost:9999/api/translate`.
    *   The console should also show a log "Backend URL loaded from config.json: http://localhost:9999".

**Test Case 5.2: Fallback to default URL when `config.json` is missing**
*   **Setup:**
    1.  Ensure your backend server IS running on `http://localhost:5000`.
    2.  In `plugin/` directory, ensure `config.json` does **not** exist (delete it if it does).
    3.  Reload the plugin in your browser.
*   **Action:**
    1.  Open the plugin popup.
    2.  Attempt to use a feature (e.g., Translate "Hello" to "French").
*   **Expected Result:**
    *   The translation should succeed, and the French translation for "Hello" should be displayed.
    *   The browser's developer console should show a log message similar to "config.json not found. Using default backend URL: http://localhost:5000".

**Test Case 5.3: Fallback to default URL when `config.json` is malformed**
*   **Setup:**
    1.  Ensure your backend server IS running on `http://localhost:5000`.
    2.  In `plugin/` directory, create `config.json` with invalid JSON content (e.g., `{"backend_url": "http://localhost:5000", }` - note the trailing comma).
    3.  Reload the plugin in your browser.
*   **Action:**
    1.  Open the plugin popup.
    2.  Attempt to use a feature (e.g., Translate "Good day" to "German").
*   **Expected Result:**
    *   The translation should succeed.
    *   The browser's developer console should show a warning similar to "Error loading or parsing config.json. Using default backend URL: http://localhost:5000" and include details of the parsing error.

**Test Case 5.4: Fallback to default URL when `backend_url` key is missing in `config.json`**
*   **Setup:**
    1.  Ensure your backend server IS running on `http://localhost:5000`.
    2.  In `plugin/` directory, create `config.json` with valid JSON but missing the `backend_url` key (e.g., `{"some_other_setting": "value"}`).
    3.  Reload the plugin in your browser.
*   **Action:**
    1.  Open the plugin popup.
    2.  Attempt to use a feature (e.g., Translate "Morning" to "Italian").
*   **Expected Result:**
    *   The translation should succeed.
    *   The browser's developer console should show a warning similar to "config.json found, but backend_url is missing or invalid. Using default: http://localhost:5000".

**Test Case 5.5: Using `config.json` with the actual default URL**
*   **Setup:**
    1.  Ensure your backend server IS running on `http://localhost:5000`.
    2.  In `plugin/` directory, create `config.json` with the content: `{"backend_url": "http://localhost:5000"}`.
    3.  Reload the plugin in your browser.
*   **Action:**
    1.  Open the plugin popup.
    2.  Attempt to use a feature (e.g., Translate "Evening" to "Japanese").
*   **Expected Result:**
    *   The translation should succeed.
    *   The browser's developer console should show a log "Backend URL loaded from config.json: http://localhost:5000".
