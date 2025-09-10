<template>
  <div>
    <header class="border-b border-slate-200/70 dark:border-slate-800">
      <div class="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <NuxtLink to="/" class="flex items-center gap-2 font-semibold">
          <Icon name="ph:mix-logo" class="hidden" />
          <span>FastMix</span>
        </NuxtLink>
        <div class="text-sm text-slate-500">beta</div>
      </div>
    </header>
    <main>
      <slot />
    </main>
    <footer class="py-8 text-center text-xs text-slate-500">
      © {{ new Date().getFullYear() }} FastMix
    </footer>
  </div>
</template>