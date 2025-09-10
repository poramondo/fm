<script setup lang="ts">
import StatsCounter from '@/components/StatsCounter.vue'
import StatusLookUp from '@/components/StatusLookup.vue'
</script>

<template>
  <section class="space-y-6">
    <!-- Заголовок + подзаголовок -->
    <div class="space-y-3">
      <h1 class="text-3xl md:text-4xl font-bold leading-tight">
        Анонимный обмен — <br class="hidden md:block" /> просто и прозрачно
      </h1>
      <p class="text-slate-300 max-w-xl">
        Создайте заявку за минуту. Контроль статуса в один клик. Работает как в clearnet, так и в .onion.
      </p>
    </div>

    <!-- Бейджи-ссылки -->
    <div class="flex flex-wrap gap-3">
      <NuxtLink to="/" class="rounded-full px-3 py-1 text-sm bg-white/5 border border-white/10 hover:bg-white/10 transition">
        fastmix.io
      </NuxtLink>
      <a href="http://example.onion" target="_blank" rel="noreferrer"
         class="rounded-full px-3 py-1 text-sm bg-white/5 border border-white/10 hover:bg-white/10 transition">
        xxx.onion
      </a>
      <NuxtLink to="/pgp" class="rounded-full px-3 py-1 text-sm bg-white/5 border border-white/10 hover:bg-white/10 transition">
        PGP-ключ поддержки
      </NuxtLink>
    </div>

    <!-- Метрики -->
    <div class="grid gap-4 sm:grid-cols-2">
      <div class="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-glass">
        <div class="text-sm text-slate-400">УСПЕШНЫХ СДЕЛОК</div>
        <div class="mt-2 text-2xl font-semibold"><StatsCounter /></div>
      </div>
      <div class="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-glass">
        <div class="text-sm text-slate-400">СРЕДНЕЕ ВРЕМЯ</div>
        <div class="mt-2 text-2xl font-semibold">20–45 мин</div>
      </div>
    </div>

    <!-- Проверка статуса по ID -->
    <div class="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-glass">
      <StatusLookUp />
    </div>
  </section>
</template>
