<script lang="ts">
    import { fade, fly } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';
  
    export let extractedData: any;
  
    const dispatch = createEventDispatcher();
  
    let messages: Array<{ text: string; sender: 'user' | 'bot' }> = [];
    let inputMessage = '';
    let isLoading = false;
  
    async function sendMessage() {
  if (inputMessage.trim() === '') return;

  messages = [...messages, { text: inputMessage, sender: 'user' }];
  const userMessage = inputMessage;
  inputMessage = '';
  isLoading = true;

  try {
    console.log("Sending request:", { message: userMessage, extracted_data: extractedData, user_id: null });
    const response = await fetch('http://localhost:8000/chatbot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message: userMessage, 
        extracted_data: extractedData,
        user_id: null  // or provide a user ID if you have one
      })
    });

    const data = await response.json();
    console.log("Received response:", data);

    if (response.ok) {
      messages = [...messages, { text: data.response, sender: 'bot' }];
    } else {
      console.error('Error response from server:', data);
      let errorMessage = 'An error occurred while processing your request.';
      if (data && typeof data === 'object' && data.detail) {
        errorMessage += ' Details: ' + JSON.stringify(data.detail);
      } else if (data) {
        errorMessage += ' ' + String(data);
      }
      throw new Error(errorMessage);
    }
  } catch (error: unknown) {
    console.error('Chatbot error:', error);
    let errorMessage: string;
    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === 'object' && error !== null) {
      errorMessage = 'An unexpected error occurred. Please try again.';
      console.error('Unexpected error object:', error);
    } else {
      errorMessage = String(error);
    }
    messages = [...messages, { text: `Error: ${errorMessage}`, sender: 'bot' }];
  } finally {
    isLoading = false;
  }
}
    function handleClose() {
      dispatch('close');
    }
</script>



<div class="chatbox" transition:fly="{{ y: 50, duration: 300 }}">
    <div class="chat-header">
      <h3>AI Assistant</h3>
      <button class="close-btn" on:click={handleClose}>&times;</button>
    </div>
    <div class="messages">
      {#each messages as message}
        <div class="message {message.sender}" transition:fade>
          {message.text}
        </div>
      {/each}
      {#if isLoading}
        <div class="message bot" transition:fade>
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      {/if}
    </div>
    <div class="input-area">
      <input
        type="text"
        bind:value={inputMessage}
        on:keypress={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
        placeholder="Ask about your test results..."
        disabled={isLoading}
      />
      <button on:click={sendMessage} disabled={isLoading}>
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </div>
  </div>

<style>
    .chatbox {
        width: 350px;
        height: 500px;
        border: 1px solid #ccc;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        background-color: #f9f9f9;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .chat-header {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        font-weight: bold;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .close-btn {
        background: none;
        border: none;
        color: white;
        font-size: 20px;
        cursor: pointer;
    }

    .messages {
        flex-grow: 1;
        overflow-y: auto;
        padding: 10px;
    }

    .message {
        margin-bottom: 10px;
        padding: 8px 12px;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
    }

    .user {
        background-color: #E3F2FD;
        color: #000;
        align-self: flex-end;
        margin-left: auto;
    }

    .bot {
        background-color: #F1F3F4;
        color: #000;
        align-self: flex-start;
    }

    .input-area {
        display: flex;
        padding: 10px;
        border-top: 1px solid #ccc;
    }

    input {
        flex-grow: 1;
        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 20px;
        font-size: 14px;
    }

    button {
        margin-left: 5px;
        padding: 8px 15px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 20px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.3s;
    }

    button:hover {
        background-color: #45a049;
    }

    button:disabled {
        background-color: #a0a0a0;
        cursor: not-allowed;
    }

    .typing-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 20px;
    }

    .typing-indicator span {
        height: 8px;
        width: 8px;
        background-color: #3498db;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: bounce 1.4s infinite ease-in-out;
    }

    .typing-indicator span:nth-child(1) {
        animation-delay: -0.32s;
    }

    .typing-indicator span:nth-child(2) {
        animation-delay: -0.16s;
    }

    @keyframes bounce {
        0%, 80%, 100% { 
            transform: scale(0);
        } 40% { 
            transform: scale(1.0);
        }
    }
</style>