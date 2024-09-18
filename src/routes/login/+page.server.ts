import { fail, redirect } from '@sveltejs/kit'
import type { Actions } from './$types'

export const actions: Actions = {
  default: async ({ locals, request }) => {
    const data = Object.fromEntries(await request.formData()) as {
      email: string
      password: string
    }

    try {
      await locals.pb
        .collection('users')
        .authWithPassword(data.email, data.password)
    } catch (e) {
      console.error('Authentication error:', e)
      return fail(400, {
        error: true,
        message: 'Incorrect email or password'
      })
    }

    throw redirect(303, '/extracter')
  },
}