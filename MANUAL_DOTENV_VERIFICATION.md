# Manual Verification Steps for `.env` API Key Loading

These steps are for manually verifying that the OpenAI API key is being correctly loaded from the `backend/.env` file by the `python-dotenv` library in the Flask application.

1.  **Ensure No Direct Environment Variable:**
    *   Make sure the `OPENAI_API_KEY` environment variable is **not** set directly in your current shell session. This is to ensure the key is loaded *only* from the `.env` file.
    *   On Linux/macOS, you can run: `unset OPENAI_API_KEY`
    *   On Windows (Command Prompt): `set OPENAI_API_KEY=`
    *   On Windows (PowerShell): `Remove-Item Env:OPENAI_API_KEY` or `$env:OPENAI_API_KEY = ''`
    *   Verify by trying to print it, e.g., `echo $OPENAI_API_KEY` (Linux/macOS) or `echo %OPENAI_API_KEY%` (Windows CMD), which should show nothing or an empty line.

2.  **Prepare `backend/.env` File:**
    *   Navigate to the `backend/` directory of the project.
    *   If you haven't already, copy `.env.example` to `.env`. If `.env` already exists, ensure it's configured as below.
        ```bash
        cp .env.example .env
        ```
    *   Edit the `backend/.env` file (e.g., using `nano .env` or a text editor).
    *   Insert your **valid** OpenAI API key. The content should be exactly like:
        ```
        OPENAI_API_KEY="sk-YourActualValidOpenAIKeyHerexxxx"
        ```
        (Replace `sk-YourActualValidOpenAIKeyHerexxxx` with your real key). Ensure there are no extra spaces or quotes.

3.  **Install Dependencies:**
    *   From the `backend/` directory, ensure all dependencies, including `python-dotenv`, are installed:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Run the Backend Server:**
    *   From the `backend/` directory, run the Flask application:
        ```bash
        python -m app.main
        ```
    *   **Observe Server Startup:**
        *   Carefully examine the terminal output when the server starts.
        *   You should **not** see the warning: `Warning: OPENAI_API_KEY not found in environment or .env file. LLM calls will fail.`
        *   The server should start normally, indicating it's running (e.g., `* Running on http://localhost:5000/`).

5.  **Test an API Endpoint (e.g., using `curl`):**
    *   Open a **new** terminal window (to ensure it doesn't have any lingering `OPENAI_API_KEY` if you set one temporarily and then unset it).
    *   Make a POST request to the `/api/translate` endpoint. You can use `curl` for this:
        ```bash
        curl -X POST -H "Content-Type: application/json" \
             -d '{"text":"Hello", "target_language":"French"}' \
             http://localhost:5000/api/translate
        ```
    *   **Expected Result:**
        *   You should receive a JSON response similar to this (the exact translation may vary):
            ```json
            {
              "original_text": "Hello",
              "target_language": "French",
              "translated_text": "Bonjour"
            }
            ```
        *   Receiving a successful translation confirms that the API key was loaded from the `.env` file and used by the OpenAI client to make a successful LLM call.
    *   **If it fails:**
        *   Check the backend server logs (the terminal where `python -m app.main` is running) for any error messages, especially those related to API authentication or key issues.
        *   Double-check the `backend/.env` file:
            *   Is it named exactly `.env`?
            *   Is it in the correct `backend/` directory?
            *   Does the key start with `sk-` and is it correctly copied?
            *   Are there any accidental extra characters, spaces, or quotes around the key?

6.  **Clean Up (Optional but Recommended):**
    *   After verification, you can remove your actual API key from the `backend/.env` file if you don't intend to use it for further development immediately, or if you are on a shared machine.
    *   If you had an `OPENAI_API_KEY` set globally in your shell environment before this test and unset it, you might want to set it back if you use it for other projects.

These steps will help confirm that the `python-dotenv` setup is working as expected for loading the OpenAI API key.
