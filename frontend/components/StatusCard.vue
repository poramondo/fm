<script setup lang="ts">
import { computed, ref } from 'vue'
import { useStatusLabel } from '@/composables/useStatusLabel'

const props = defineProps<{ data: any }>()
const label = useStatusLabel()
const copied = ref(false)

const payin = computed(() => props.data?.payin_address || props.data?.payinAddress || '—')

async function copy() {
  if (!payin.value || payin.value === '—') return
  try {
    await navigator.clipboard.writeText(payin.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 1200)
  } catch {}
}
</script>

<template>
  <div class="card p-6 md:p-8 space-y-5">
    <div class="flex items-start justify-between gap-4">
      <h2 class="text-xl font-semibold">Статус заявки</h2>
      <span :class="['px-2.5 py-1 rounded-full text-xs font-medium ring-1', label(props.data?.status).cls]">
        {{ label(props.data?.status).label }}
      </span>
    </div>

    <div class="grid md:grid-cols-2 gap-y-3 gap-x-6 text-sm">
      <div class="text-[var(--muted)]">ID</div>
      <div><code class="code">{{ props.data?.id }}</code></div>

      <div class="text-[var(--muted)]">Валюта</div>
      <div>{{ props.data?.currency }}</div>

      <div class="text-[var(--muted)]">Адрес для перевода</div>
      <div class="flex items-center gap-2 min-w-0">
        <code class="code truncate">{{ payin }}</code>
        <button @click="copy" class="btn-secondary text-xs px-2 py-1">
          {{ copied ? 'Скопировано' : 'Копировать' }}
        </button>
      </div>

      <template v-if="props.data?.reserved_until">
        <div class="text-[var(--muted)]">Резерв до</div>
        <div>{{ new Date(props.data.reserved_until).toLocaleString() }}</div>
      </template>
    </div>

    <div class="pt-2">
      <NuxtLink class="text-sm text-[var(--text)]/80 hover:text-[var(--text)] transition" to="/">← Новая заявка</NuxtLink>
    </div>
  </div>
</template>
