import { redirect, type RequestEvent } from '@sveltejs/kit';

export const GET = async ({ locals, url, cookies }: RequestEvent) => {
    // Define the redirect URL to OAuth
    const redirectURL = `${url.origin}/oauth`;

    // Retrieve state and verifier from cookies
    const expectedState = cookies.get('state');
    const expectedVerifier = cookies.get('verifier');

    // Extract state and code from query parameters
    const state = url.searchParams.get('state');
    const code = url.searchParams.get('code');

    try {
        // Fetch authentication methods from PocketBase
        const authMethods = await locals.pb?.collection('users').listAuthMethods();

        // Check if authProviders exist
        if (!authMethods?.authProviders) {
            console.log('No Auth Providers');
            throw redirect(303, '/login');
        }

        // Get the first authentication provider
        const provider = authMethods.authProviders[0];
        if (!provider) {
            console.log('Provider Not Found');
            throw redirect(303, '/login');
        }

        // Validate the state parameter
        if (expectedState !== state) {
            console.log('Returned State Does not Match Expected', expectedState, state);
            throw redirect(303, '/login');
        }

        // Attempt to authenticate with OAuth2 code
        await locals.pb?.collection('users').authWithOAuth2Code(
            provider.name,
            code as string,
            expectedVerifier as string,
            redirectURL, // This should match the URI registered with your OAuth provider
            { username: '', name: 'My Awesome User' }
        );

        // Successful authentication, redirect to login page
        throw redirect(303, '/login');
    } catch (err) {
        // Log the error and redirect to login page
        console.log('Error logging in with OAuth2 user', err);
        throw redirect(303, '/login');
    }
};

