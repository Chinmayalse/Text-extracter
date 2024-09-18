import type { Handle } from '@sveltejs/kit';
import PocketBase from 'pocketbase';
import { PUBLIC_POCKETBASE_URL } from '$env/static/public';

export const handle: Handle = async ({ event, resolve }) => {
  try {
    const pb = new PocketBase(PUBLIC_POCKETBASE_URL);

    // Attach pb to event.locals so it's accessible in endpoints
    event.locals.pb = pb;

    // load the store data from the request cookie string
    pb.authStore.loadFromCookie(event.request.headers.get('cookie') || '');

    try {
      // get an up-to-date auth store state by verifying and refreshing the loaded auth model (if any)
      if (pb.authStore.isValid) {
        await pb.collection('users').authRefresh();
      }
    } catch (_) {
      // clear the auth store on failed refresh
      pb.authStore.clear();
    }

    event.locals.user = pb.authStore.model;

    const response = await resolve(event);

    // send back the default 'pb_auth' cookie to the client with the latest store state
    response.headers.set('set-cookie', pb.authStore.exportToCookie({ httpOnly: false }));

    return response;
  } catch (error) {
    console.error('Error in hooks.server.ts:', error);
    return await resolve(event);
  }
};