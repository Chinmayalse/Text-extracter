<script lang="ts">
    import { page } from '$app/stores';
    import { pb } from '$lib/pocketbase';
    import { onMount } from 'svelte';

    let newPassword = '';
    let confirmPassword = '';
    let message = '';
    let error = '';
    let token: string | null = null;

    $: token = $page.url.searchParams.get('TOKEN');

    async function handleSubmit() {
      if (newPassword !== confirmPassword) {
        error = 'Passwords do not match';
        return;
      }

      if (!token) {
        error = 'No reset token provided.';
        return;
      }

      try {
        await pb.collection('users').confirmPasswordReset(
          token,
          newPassword,
          confirmPassword
        );
        message = 'Password has been reset successfully. You can now log in with your new password.';
        error = '';
      } catch (err) {
        console.error('Error:', err);
        error = 'Failed to reset password. Please try again or request a new reset link.';
        message = '';
      }
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-indigo-600 p-4">
  <div class="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md">
    <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">Reset Password</h1>
    <form on:submit|preventDefault={handleSubmit} class="space-y-4">
      <div>
        <label for="newPassword" class="block text-sm font-medium text-gray-700">New Password</label>
        <input
          type="password"
          id="newPassword"
          bind:value={newPassword}
          required
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>
      <div>
        <label for="confirmPassword" class="block text-sm font-medium text-gray-700">Confirm New Password</label>
        <input
          type="password"
          id="confirmPassword"
          bind:value={confirmPassword}
          required
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>
      <button type="submit" class="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
        Reset Password
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
