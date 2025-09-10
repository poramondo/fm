<script setup lang="ts">
import { useApi } from '@/composables/useApi'

const route = useRoute()
const api = useApi()
const data = ref<any>(null)
const error = ref<string | null>(null)

async function load() {
  error.value = null
  try {
    data.value = await api.get(`/requests/${route.params.id}`, { server: false })
  } catch (e: any) {
    error.value = e?.data?.detail || 'Не удалось загрузить заявку'
  }
}

onMounted(() => {
  load()
  const t = setInterval(load, 10000)
  onUnmounted(() => clearInterval(t))
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-semibold">Статус</h1>
    <div v-if="error" class="text-rose-300 text-sm">{{ error }}</div>
    <StatusCard v-else-if="data" :data="data" />
    <div v-else>Загрузка…</div>
  </div>
</template>
