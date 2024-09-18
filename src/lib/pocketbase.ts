import { PUBLIC_POCKETBASE_URL } from '$env/static/public'
import PocketBase from 'pocketbase'

export function createInstance() {
  return new PocketBase(PUBLIC_POCKETBASE_URL)
}

export const pb = createInstance()

export function isUserAuthenticated() {
  return pb.authStore.isValid
}
