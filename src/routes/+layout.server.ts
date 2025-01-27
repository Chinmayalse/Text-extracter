import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  if (locals.pb.authStore.isValid) {
    return {
      user: structuredClone(locals.pb.authStore.model)
    };
  }
  return {
    user: null
  };
};