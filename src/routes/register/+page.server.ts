import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { ClientResponseError } from 'pocketbase';

export const actions: Actions = {
  default: async ({ locals, request }) => {
    // Extract form data as an object with email, password, and passwordConfirm
    const data = Object.fromEntries(await request.formData()) as {
      email: string;
      password: string;
      passwordConfirm: string;
    };

    try {
      // Check if the passwords match
      if (data.password !== data.passwordConfirm) {
        return fail(400, {
          error: true,
          message: "Passwords do not match"
        });
      }

      // Attempt to create the user in PocketBase
      await locals.pb.collection('users').create(data);
      
      // If user creation is successful, log in the user
      await locals.pb.collection('users').authWithPassword(data.email, data.password);
    } catch (error: unknown) {
      console.error("Registration error:", error);

      // If the error is from PocketBase (ClientResponseError)
      if (error instanceof ClientResponseError) {
        // Handle specific PocketBase validation errors
        if (error.data?.data?.email?.code === "validation_invalid_email") {
          return fail(400, {
            error: true,
            message: "Please enter a valid email address"
          });
        } else if (error.data?.email?.code === "validation_not_unique") {
          return fail(400, {
            error: true,
            message: "This email is already registered"
          });
        }
      }

      // Return a generic error message for any other type of error
      return fail(400, {
        error: true,
        message: "An error occurred during registration. Please try again."
      });
    }

    // Redirect to the login page after successful registration
    throw redirect(303, '/login');

  }
};
