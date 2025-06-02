document.addEventListener('DOMContentLoaded', function () {
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

            fetch('http://localhost:5000/api/translate', {
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

    // Document Conversion Logic
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

            fetch('http://localhost:5000/api/convert-document', {
                method: 'POST',
                body: formData, // No 'Content-Type' header needed for FormData, browser sets it
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
                    // Clear the file input
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

    // Intelligent Search Logic
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

            fetch('http://localhost:5000/api/search', {
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
