<script lang="ts">
    import { fade, fly, scale } from 'svelte/transition';
    import { elasticOut } from 'svelte/easing';
    import Chatbot from '$lib/Chatbot.svelte';
    import { user } from '$lib/stores';
    import { onMount } from 'svelte';
    
    let extractedText: string = '';
    let correctedText: string = '';
    let isLoading: boolean = false;
    let error: string | null = null;
    let jsonData: any = null;
    let fileName: string = '';
    let copySuccess: boolean = false;
    let showChatbot = false;

    async function handleFileUpload(event: Event) {
        event.preventDefault();
        const fileInput = (event.target as HTMLFormElement).elements.namedItem('fileInput') as HTMLInputElement;
        const file = fileInput.files?.[0];

        if (file) {
            const formData = new FormData();
            formData.append('pdf_file', file);

            if (file.type === 'application/pdf') {
                isLoading = true;
                error = null;
                try {
                    const response = await fetch('http://localhost:8000/process_pdf', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error(response.statusText);
                    }

                    const data = await response.json();
                    extractedText = data.extracted_text || 'No text extracted.';
                    correctedText = data.corrected_text || 'No corrected text available.';
                    jsonData = data.json_data || null;
                    
                    console.log("Extracted JSON data:", jsonData);  // For debugging
                    
                    if (jsonData) {
                        showChatbot = true;  // Automatically show chatbot when data is available
                    }
                } catch (err) {
                    console.error('Error:', err);
                    error = 'Failed to process the PDF. Please try again.';
                    extractedText = '';
                    correctedText = '';
                    jsonData = null;
                    showChatbot = false;
                } finally {
                    isLoading = false;
                }
            } else {
                error = 'Unsupported file type. Please upload a .pdf file.';
                extractedText = '';
                correctedText = '';
            }
        }
    }

    function formatMarkdown(text: string): string {
        return text.replace(/\|/g, '</td><td>')
                   .replace(/^/gm, '<tr><td>')
                   .replace(/$/gm, '</td></tr>')
                   .replace(/\n/g, '');
    }

    function downloadJSON() {
        console.log('Download JSON clicked', jsonData);
        if (jsonData) {
            const dataStr = JSON.stringify(jsonData, null, 2);
            const blob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'extracted_results.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } else {
            console.log('No JSON data available');
        }
    }

    function handleFileSelect(event: Event) {
        const fileInput = event.target as HTMLInputElement;
        if (fileInput.files && fileInput.files.length > 0) {
            fileName = fileInput.files[0].name;
        } else {
            fileName = '';
        }
    }

    function toggleChatbot() {
        if (jsonData) {
            showChatbot = !showChatbot;
        } else {
            alert("Please upload and process a document first.");
        }
    }
</script>

    <div class="container mx-auto px-4 py-8 max-w-screen-2xl">
    <form on:submit={handleFileUpload} class="bg-white p-8 rounded-lg shadow-lg w-full max-w-10xl mx-auto" in:fly="{{ y: 50, duration: 500 }}" out:fade>
        <h1 class="text-3xl font-bold mb-6 text-gray-800 text-center">PDF Text Extractor</h1>
        <div class="mb-6">
            <label for="fileInput" class="block text-gray-700 text-sm font-bold mb-2">Upload PDF</label>
            <div class="relative border-2 border-gray-300 border-dashed rounded-lg p-6 hover:border-blue-500 transition-colors duration-300">
                <input id="fileInput" type="file" name="fileInput" accept=".pdf" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" required on:change={handleFileSelect} />
                <div class="text-center">
                    <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <p class="mt-1 text-sm text-gray-600">
                        {fileName ? fileName : 'Click to upload or drag and drop'}
                    </p>
                    <p class="mt-1 text-xs text-gray-500">PDF up to 10MB</p>
                </div>
            </div>
        </div>
        <button type="submit" class="w-full bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300" disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Extract Text'}
        </button>
    </form>


    {#if isLoading}
        <div class="mt-8 text-center" in:fade>
            <div class="loader"></div>
            <p class="mt-4 text-gray-600">Processing PDF, please wait...</p>
        </div>
    {:else if error}
        <div class="mt-8 p-4 bg-red-100 text-red-700 rounded-lg border border-red-300" in:fly="{{ y: 20, duration: 500 }}" out:fade>
            <p class="font-semibold">{error}</p>
        </div>
    {:else if correctedText}
        <div class="mt-8 bg-white rounded-lg shadow-lg overflow-hidden w-full max-w-10xl mx-auto" in:fly="{{ y: 20, duration: 500 }}" out:fade>
            <!-- ... (keep your existing corrected text HTML) ... -->
            <h2 class="text-3xl font-semibold mb-6 text-gray-800 text-center">Corrected and Formatted Results</h2>
            <div class="overflow-x-auto">
                <table class="w-full bg-white rounded-lg overflow-hidden">
                    {@html formatMarkdown(correctedText)}
                </table>
            </div>
        </div>

        {#if jsonData}
                <div class="mt-8 text-center">
                    <button on:click={downloadJSON} class="bg-green-500 text-white font-semibold px-8 py-3 rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 transition-all duration-300" in:scale="{{ duration: 300, easing: elasticOut }}">
                        Download JSON
                    </button>
                </div>
        {/if}

        {#if jsonData}
            <div class="mt-8 text-center">
                <button 
                    on:click={toggleChatbot} 
                    class="bg-blue-500 text-white font-semibold px-8 py-3 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
                >
                    {showChatbot ? 'Hide AI Assistant' : 'Chat with AI Assistant'}
                </button>
            </div>

            {#if showChatbot}
  <div class="fixed bottom-4 right-4 z-50" transition:fly={{ y: 50, duration: 300 }}>
    <Chatbot
      extractedData={jsonData} 
      on:close={() => showChatbot = false}
    />
  </div>
{/if}
        {/if}
    {/if}
</div>
<style>
    .loader {
        border: 5px solid #f3f3f3;
        border-top: 5px solid #3498db;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>