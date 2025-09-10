<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const count = ref<number | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
let timer: ReturnType<typeof setInterval> | null = null

const config = useRuntimeConfig()
const apiBase = config.public.apiBase || '/api'

async function load() {
  loading.value = true
  error.value = null
  try {
    const r: any = await $fetch(`${apiBase}/stats`, { server: false })
    count.value = typeof r?.completed === 'number' ? r.completed : 0
  } catch (e) {
    error.value = 'Не удалось получить статистику'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
  timer = setInterval(load, 15000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<template>
  <div class="rounded-2xl border border-white/10 bg-white/5 p-6 text-center shadow-glass">
    <div class="text-3xl font-semibold">{{ count ?? '—' }}</div>
    <div class="text-xs uppercase tracking-wide text-white/60 mt-1">Успешных сделок</div>
    <div v-if="loading" class="text-xs text-white/50 mt-2">обновляем…</div>
    <div v-else-if="error" class="text-xs text-rose-300 mt-2">{{ error }}</div>
  </div>
</template>
