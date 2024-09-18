<script lang="ts">
  import { applyAction, enhance } from '$app/forms';
  import { pb } from '$lib/pocketbase';
  import { fade } from 'svelte/transition';
  import { goto } from '$app/navigation';
  export let form;

  let loading = false;
  async function handleGoogleSignIn() {
    try {
      const authMethods = await pb.collection('users').listAuthMethods();
      const googleAuthProvider = authMethods.authProviders.find(provider => provider.name === 'google');
      
      if (googleAuthProvider) {
        const redirectUrl = `${pb.baseUrl}/api/oauth2/auth/google?redirect=${encodeURIComponent(window.location.origin + '/oauth')}`;

        const url = `${googleAuthProvider.authUrl}${encodeURIComponent(redirectUrl)}`;
        const state = googleAuthProvider.state;
        const verifier = googleAuthProvider.codeVerifier;
        
        // Store the state and code verifier in localStorage
        localStorage.setItem('oauth_state', state);
        localStorage.setItem('oauth_code_verifier', verifier);
        
        window.location.href = url;
      } else {
        console.error("Google OAuth provider not found.");
      }
    } catch (error) {
      console.error("Error initiating OAuth2:", error);
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-500 to-indigo-600 p-4">
  <form
    method="POST"
    class="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md transform hover:scale-105 transition-all duration-300"
    use:enhance={() => {
      loading = true;
      return async ({ result }) => {
        pb.authStore.loadFromCookie(document.cookie);
        await applyAction(result);
        loading = false;
      };
    }}
    transition:fade
  >
    <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">Welcome Back</h1>
    <div class="space-y-4">
      <div class="relative">
        <input
          type="email"
          name="email"
          placeholder="Email"
          class="input input-bordered w-full pr-10 py-3"
          required
        />
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
        </svg>
      </div>
      <div class="relative">
        <input
          type="password"
          name="password"
          placeholder="Password"
          class="input input-bordered w-full pr-10 py-3"
          required
        />
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      </div>
      <button class="btn btn-primary w-full py-3 relative overflow-hidden group" disabled={loading}>
        <span class="absolute right-0 w-8 h-32 -mt-12 transition-all duration-1000 transform translate-x-12 bg-white opacity-10 rotate-12 group-hover:-translate-x-40 ease"></span>
        <span class="relative">{loading ? 'Logging in...' : 'Log in'}</span>
      </button>
    </div>
    
    <div class="mt-6 text-center">
      <a href="/forgot-password" class="text-sm text-indigo-600 hover:text-indigo-800 transition-colors">Forgot your password?</a>
    </div>
    
    <div class="mt-8">
      <div class="relative">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-300"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-white text-gray-500">Or continue with</span>
        </div>
      </div>
      <div class="mt-6">
        <button 
          type="button" 
          class="google-btn"
          on:click={handleGoogleSignIn}
        >
          <div class="google-icon-wrapper">
            <svg class="google-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
              <path fill="none" d="M0 0h48v48H0z"/>
            </svg>
          </div>
          <span class="btn-text">Sign up with Google</span>
        </button>
      </div>
      
    </div>
  </form>
</div>

<style>
  .input {
    border: 1px solid #D1D5DB; /* Tailwind default gray-300 */
    border-radius: 0.375rem; /* Tailwind default rounded-md */
    padding-right: 2.5rem; /* For icon padding */
  }
  .input:focus {
    border-color: #6366F1; /* Tailwind default indigo-500 */
    outline: none;
  }
  .google-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: white;
    color: #757575;
    padding: 10px;
    font-size: 16px;
    width: 100%;
    border-radius: 4px;
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
    transition: background-color 0.3s ease;
    cursor: pointer;
  }
  
  .google-btn:hover {
    background-color: #f1f1f1;
  }

  .google-icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
  }
  
  .google-icon {
    width: 20px;
    height: 20px;
  }
  .btn {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    border-radius: 0.375rem;
    background-color: #4F46E5; /* Tailwind indigo-600 */
    color: white;
    cursor: pointer;
    padding: 0.75rem 1.25rem;
    transition: all 0.2s ease-in-out;
  }
  .btn:hover {
    background-color: #4338CA; /* Tailwind indigo-700 */
  }
  .btn-outline {
    background-color: white;
    border: 1px solid #D1D5DB;
    color: #374151; /* Tailwind gray-700 */
  }
  .btn-outline:hover {
    background-color: #F3F4F6; /* Tailwind gray-100 */
  }
</style>
