<script setup lang="ts">
</script>

<template>
  <div class="container mx-auto px-4 py-10 md:py-16">
    <div class="grid gap-6 md:gap-8 md:grid-cols-2 items-start">
      <!-- ЛЕВАЯ КОЛОНКА: форма заявки -->
      <div class="order-1">
        <RequestForm />
      </div>

      <!-- ПРАВАЯ КОЛОНКА: информационный блок -->
      <div class="order-2">
        <HomeInfo />
      </div>
    </div>
  </div>
</template>
