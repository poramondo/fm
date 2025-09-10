<script setup lang="ts">
import { ref } from 'vue'

const id = ref('')
const loading = ref(false)
const error = ref<string | null>(null)
const preview = ref<any | null>(null)

const config = useRuntimeConfig()
const apiBase = config.public.apiBase || '/api'

async function check() {
  error.value = null
  preview.value = null
  const v = id.value.trim()
  if (!v) { error.value = 'Введите ID заявки'; return }
  loading.value = true
  try {
    const r = await $fetch(`${apiBase}/requests/${encodeURIComponent(v)}`)
    preview.value = r
  } catch (e: any) {
    error.value = e?.data?.detail || 'Заявка не найдена'
  } finally {
    loading.value = false
  }
}

function openStatus() {
  if (preview.value?.id) navigateTo(`/status/${preview.value.id}`)
}
</script>

<template>
  <div class="bg-white/5 rounded-2xl shadow-glass border border-white/10 p-6 md:p-8 space-y-5">
    <h2 class="text-lg font-semibold">Проверить статус заявки</h2>

    <div class="flex gap-3">
      <input
        v-model="id"
        type="text"
        placeholder="Вставьте ID заявки (UUID)"
        class="flex-1 rounded-xl bg-slate-900 border border-white/10 px-3 py-2.5 placeholder-white/40
               focus:outline-none focus:ring-2 focus:ring-brand-500/50"
        @keyup.enter="check"
      />
      <button class="rounded-xl px-4 py-2.5 bg-brand-600 hover:bg-brand-500 transition disabled:opacity-50"
              :disabled="loading" @click="check">
        {{ loading ? 'Проверяем…' : 'Проверить' }}
      </button>
    </div>

    <p v-if="error" class="text-sm text-rose-300">{{ error }}</p>

    <div v-if="preview" class="grid gap-2 text-sm">
      <div class="grid grid-cols-[140px_1fr] gap-2">
        <div class="text-slate-400">ID</div>
        <div><code>{{ preview.id }}</code></div>
      </div>
      <div class="grid grid-cols-[140px_1fr] gap-2">
        <div class="text-slate-400">Валюта</div>
        <div>{{ preview.currency }}</div>
      </div>
      <div class="grid grid-cols-[140px_1fr] gap-2">
        <div class="text-slate-400">Адрес для перевода</div>
        <div><code>{{ preview.payin_address || '—' }}</code></div>
      </div>
      <div class="grid grid-cols-[140px_1fr] gap-2">
        <div class="text-slate-400">Статус</div>
        <div>{{ preview.status }}</div>
      </div>

      <div class="pt-2">
        <button class="rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 px-3 py-2 transition"
                @click="openStatus">
          Открыть страницу
        </button>
      </div>
    </div>
  </div>
</template>
