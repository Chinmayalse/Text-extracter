import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
  default: async ({ request, locals }) => {
    const data = await request.formData();
    const email = data.get('email');

    if (!email) {
      return fail(400, { email, missing: true });
    }

    try {
      await locals.pb.collection('users').requestPasswordReset(email.toString());
      return { success: true };
    } catch (err) {
      console.error('Password reset error:', err);
      return fail(500, { email, error: true });
    }
  }
};