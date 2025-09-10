<template>
  <div class="min-h-screen">
    <header class="sticky top-0 z-10 backdrop-blur bg-slate-900/70 border-b border-white/5">
      <div class="mx-auto max-w-4xl px-4 py-3 flex items-center justify-between">
        <NuxtLink to="/" class="font-semibold tracking-wide">
          <span class="text-brand-500">Fast</span>Mix
        </NuxtLink>
        <nav class="text-sm text-slate-300">
          <NuxtLink class="hover:text-white transition" to="/">Новая заявка</NuxtLink>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-4xl px-4 py-8">
      <NuxtPage />
    </main>

    <footer class="mx-auto max-w-4xl px-4 py-6 text-xs text-slate-400 opacity-70">
      © FastMix. Все права защищены.
    </footer>
  </div>
</template>