import PocketBase from 'pocketbase';

declare global {
  namespace App {
      interface Locals {
          pb: PocketBase;
          user: any; // You can replace 'any' with a more specific type if you know the structure of your user object
      }
      // interface PageData {}
      // interface Error {}
      // interface Platform {}
  }
}

export {};