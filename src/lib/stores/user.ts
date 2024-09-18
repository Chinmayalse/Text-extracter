import PocketBase from 'pocketbase';
import { writable } from 'svelte/store';

// Define a type that includes both Record and Admin
type User = PocketBase['authStore']['model'];

export const currentUser = writable<User | null>(null);