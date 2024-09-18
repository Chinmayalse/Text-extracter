<script lang="ts">
    import { pb } from '$lib/pocketbase';
    
    let email = '';
    let message = '';
    let error = '';
    let loading = false;
    
    async function handleSubmit() {
      if (!email) {
        error = 'Please enter your email address';
        return;
      }
    
      loading = true;
      try {
        // Request password reset email from PocketBase
        await pb.collection('users').requestPasswordReset(email);
        message = 'Password reset instructions have been sent to your email.';
        error = '';
        email = '';
      } catch (err) {
        console.error('Error:', err);
        error = 'Failed to send password reset email. Please try again.';
        message = '';
      } finally {
        loading = false;
      }
    }
  </script>
  
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-indigo-600 p-4">
    <div class="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md">
      <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">Forgot Password</h1>
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            id="email"
            bind:value={email}
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <button 
          type="submit"
          class="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'Sending...' : 'Reset Password'}
        </button>
      </form>
      {#if message}
        <p class="mt-4 text-sm text-green-600">{message}</p>
      {/if}
      {#if error}
        <p class="mt-4 text-sm text-red-600">{error}</p>
      {/if}
      <div class="mt-4 text-center">
        <a href="/login" class="text-sm text-indigo-600 hover:text-indigo-500">Back to Login</a>
      </div>
    </div>
  </div>
  