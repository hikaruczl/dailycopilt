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
