<script lang="ts">
  import '../app.postcss'

  import { applyAction, enhance } from '$app/forms'
  import { pb } from '$lib/pocketbase'
  import { currentUser } from '$lib/stores/user'
  import type { PageData } from './$types'

  export let data: PageData

  // Set the current user from the data passed in from the server
  $: currentUser.set(data.user)
</script>

<div class="bg-neutral text-neutral-content fixed top-0 left-0 w-full z-10">
  <div class="max-w-full px-4 navbar">
    <div class="navbar-start">
      <a href="/" class="btn btn-ghost text-xl">Text Extracter</a>
    </div>
    <div class="navbar-end">
      <ul class="menu menu-horizontal">
        {#if $currentUser}
          <li><a href="/">{$currentUser.email}</a></li>
          <li>
            <form
              method="POST"
              action="/logout"
              use:enhance={() => {
                return async ({ result }) => {
                  pb.authStore.clear()
                  await applyAction(result)
                }
              }}
            >
              <button>Log out</button>
            </form>
          </li>
        {:else}
          <li><a href="/login">Log in</a></li>
          <li><a href="/register">Register</a></li>
        {/if}
      </ul>
    </div>
  </div>
</div>

<div class="max-w-xl mx-auto py-8 px-4 mt-16">
  <slot />
</div>