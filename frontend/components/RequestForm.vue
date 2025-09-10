<script setup lang="ts">
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

const currencies = ['BITCOIN','ETHEREUM','TRC-20','ERC-20','MONERO']
const currency = ref('BITCOIN')
const payoutAddress = ref('')
const contact = ref('')
const pending = ref(false)
const error = ref<string | null>(null)

const api = useApi()

async function submitForm() {
  error.value = null
  pending.value = true
  try {
    const r: any = await api.post('/requests', {
      currency: currency.value,
      payout_address: payoutAddress.value,
      contact: contact.value || null
    })
    await navigateTo(`/status/${r.id}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Ошибка создания заявки'
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <form @submit.prevent="submitForm" class="card p-6 md:p-8 space-y-6">
    <h1 class="text-2xl font-semibold">Создать заявку</h1>

    <div class="grid md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm text-[var(--muted)] mb-1">Валюта</label>
        <select v-model="currency" class="input">
          <option v-for="c in currencies" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm text-[var(--muted)] mb-1">Ваш адрес для получения</label>
        <input v-model="payoutAddress" required placeholder="Введите адрес вашего кошелька" class="input" />
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm text-[var(--muted)] mb-1">Контакт для связи (опционально)</label>
        <input v-model="contact" placeholder="@Telegram или @Matrix" class="input" />
      </div>
    </div>

    <div v-if="error" class="text-sm text-rose-300">{{ error }}</div>

    <div class="flex items-center gap-4">
      <button :disabled="pending" class="btn">
        {{ pending ? 'Создание…' : 'Создать заявку' }}
      </button>
      <span class="text-xs text-[var(--muted)]">После создания вы получите адрес для перевода.</span>
    </div>
  </form>
</template>
