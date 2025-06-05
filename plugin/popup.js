let backendBaseUrl = 'http://localhost:5000'; // Default value

async function loadBackendConfig() {
    try {
        // In extensions, paths are relative to the extension's root if not starting with /
        // For popup.html, './config.json' might work, but chrome.runtime.getURL is more robust.
        const response = await fetch(chrome.runtime.getURL('config.json'));
        if (response.ok) {
            const config = await response.json();
            if (config && config.backend_url) {
                // Basic validation: ensure it's a http/https URL.
                if (config.backend_url.startsWith('http://') || config.backend_url.startsWith('https://')) {
                    backendBaseUrl = config.backend_url.replace(/\/+$/, ""); // Remove trailing slashes
                    console.log('Backend URL loaded from config.json:', backendBaseUrl);
                } else {
                    console.warn('Invalid backend_url format in config.json. Must start with http:// or https://. Using default:', backendBaseUrl);
                }
            } else {
                console.warn('config.json found, but backend_url is missing or invalid. Using default:', backendBaseUrl);
            }
        } else {
            // config.json not found is not an error, just use default.
            if (response.status === 404) {
                 console.log('config.json not found. Using default backend URL:', backendBaseUrl);
            } else {
                 console.warn(`config.json not accessible (status: ${response.status}). Using default backend URL:`, backendBaseUrl);
            }
        }
    } catch (error) {
        // This catches network errors or if config.json is malformed JSON
        console.warn('Error loading or parsing config.json. Using default backend URL:', backendBaseUrl, error);
    }
}

document.addEventListener('DOMContentLoaded', async function () {
    await loadBackendConfig(); // Load config first

    // Tab switching logic
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all tab buttons and content
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to the clicked button
            button.classList.add('active');

            // Add active class to the corresponding tab content
            const tabId = button.getAttribute('data-tab');
            const activeContent = document.getElementById(tabId);
            if (activeContent) {
                activeContent.classList.add('active');
            } else {
                console.error('Error: No tab content found for ID:', tabId);
            }
        });
    });

    // Ensure default active tab content is shown based on HTML classes
    // This step is mostly a safeguard as CSS should handle initial state.
    // However, explicitly activating the content for the initially active button
    // ensures consistency if HTML classes were somehow incorrect on load.
    const initialActiveButton = document.querySelector('.tab-button.active');
    if (initialActiveButton) {
        const initialTabId = initialActiveButton.getAttribute('data-tab');
        const initialActiveContent = document.getElementById(initialTabId);
        if (initialActiveContent) {
            // Ensure all others are inactive
            tabContents.forEach(content => {
                if (content.id !== initialTabId) {
                    content.classList.remove('active');
                }
            });
            // Ensure the correct one is active
            initialActiveContent.classList.add('active');
        }
    }

    // --- Translation ---
    const translateButton = document.getElementById('translate-button');
    const textToTranslateInput = document.getElementById('text-to-translate');
    const targetLanguageInput = document.getElementById('target-language');
    const translationResultDiv = document.getElementById('translation-result');

    if (translateButton) {
        translateButton.addEventListener('click', function () {
            const text = textToTranslateInput.value;
            const targetLanguage = targetLanguageInput.value;

            if (!text.trim()) {
                translationResultDiv.textContent = 'Error: Text to translate cannot be empty.';
                translationResultDiv.className = 'result-area error';
                return;
            }
            if (!targetLanguage.trim()) {
                translationResultDiv.textContent = 'Error: Target language cannot be empty.';
                translationResultDiv.className = 'result-area error';
                return;
            }

            translationResultDiv.textContent = 'Translating...';
            translationResultDiv.className = 'result-area loading';

            fetch(`${backendBaseUrl}/api/translate`, { // MODIFIED URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    target_language: targetLanguage,
                }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || `HTTP error! status: ${response.status}`) });
                }
                return response.json();
            })
            .then(data => {
                if (data.translated_text) {
                    translationResultDiv.textContent = data.translated_text;
                    translationResultDiv.className = 'result-area success';
                } else if (data.error) {
                    translationResultDiv.textContent = `Error: ${data.error}`;
                    translationResultDiv.className = 'result-area error';
                } else {
                    translationResultDiv.textContent = 'Error: Unexpected response from server.';
                    translationResultDiv.className = 'result-area error';
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                translationResultDiv.textContent = `Error: ${error.message || 'Could not connect to the server.'}`;
                translationResultDiv.className = 'result-area error';
            });
        });
    } else {
        console.error("Translate button not found");
    }

    // --- Document Conversion ---
    const convertDocumentButton = document.getElementById('convert-document-button');
    const documentFileInput = document.getElementById('document-file-input');
    const documentConversionResultDiv = document.getElementById('document-conversion-result');

    if (convertDocumentButton) {
        convertDocumentButton.addEventListener('click', function () {
            const file = documentFileInput.files[0];

            if (!file) {
                documentConversionResultDiv.textContent = 'Error: No file selected.';
                documentConversionResultDiv.className = 'result-area error';
                return;
            }

            documentConversionResultDiv.textContent = 'Uploading and analyzing...';
            documentConversionResultDiv.className = 'result-area loading';

            const formData = new FormData();
            formData.append('document', file);

            fetch(`${backendBaseUrl}/api/convert-document`, { // MODIFIED URL
                method: 'POST',
                body: formData,
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || `HTTP error! status: ${response.status}`) });
                }
                return response.json();
            })
            .then(data => {
                if (data.message) {
                    let resultText = `Message: ${data.message}\n`;
                    if (data.filename) resultText += `Filename: ${data.filename}\n`;
                    if (data.content_type) resultText += `Content-Type: ${data.content_type}\n`;
                    if (data.analysis_preview) resultText += `Analysis Preview: ${data.analysis_preview}`;

                    documentConversionResultDiv.textContent = resultText;
                    documentConversionResultDiv.className = 'result-area success';
                    documentFileInput.value = null;
                } else if (data.error) {
                    documentConversionResultDiv.textContent = `Error: ${data.error}`;
                    documentConversionResultDiv.className = 'result-area error';
                } else {
                    documentConversionResultDiv.textContent = 'Error: Unexpected response from server.';
                    documentConversionResultDiv.className = 'result-area error';
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                documentConversionResultDiv.textContent = `Error: ${error.message || 'Could not connect to the server.'}`;
                documentConversionResultDiv.className = 'result-area error';
            });
        });
    } else {
        console.error("Convert document button not found");
    }

    // --- Intelligent Search ---
    const searchButton = document.getElementById('search-button');
    const searchQueryInput = document.getElementById('search-query-input');
    const searchResultDiv = document.getElementById('search-result');

    if (searchButton) {
        searchButton.addEventListener('click', function () {
            const query = searchQueryInput.value;

            if (!query.trim()) {
                searchResultDiv.textContent = 'Error: Search query cannot be empty.';
                searchResultDiv.className = 'result-area error';
                return;
            }

            searchResultDiv.textContent = 'Searching...';
            searchResultDiv.className = 'result-area loading';

            fetch(`${backendBaseUrl}/api/search`, { // MODIFIED URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || `HTTP error! status: ${response.status}`) });
                }
                return response.json();
            })
            .then(data => {
                if (data.results) {
                    searchResultDiv.textContent = `Results: ${data.results}`;
                    searchResultDiv.className = 'result-area success';
                } else if (data.error) {
                    searchResultDiv.textContent = `Error: ${data.error}`;
                    searchResultDiv.className = 'result-area error';
                } else {
                    searchResultDiv.textContent = 'Error: Unexpected response from server.';
                    searchResultDiv.className = 'result-area error';
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                searchResultDiv.textContent = `Error: ${error.message || 'Could not connect to the server.'}`;
                searchResultDiv.className = 'result-area error';
            });
        });
    } else {
        console.error("Search button not found");
    }
});
