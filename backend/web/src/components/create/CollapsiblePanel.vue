<template>
  <div class="border-b border-gray-100 last:border-b-0">
    <!-- 面板头部 -->
    <button
      class="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left"
      @click="emit('toggle')"
    >
      <div class="flex items-center">
        <span class="text-xl mr-3">{{ icon }}</span>
        <span class="font-medium text-gray-800">{{ title }}</span>
      </div>
      <span
        class="text-gray-400 transition-transform duration-200"
        :class="{ 'rotate-90': open }"
      >
        ›
      </span>
    </button>

    <!-- 面板内容 -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-screen"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 max-h-screen"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="open" class="px-4 pb-4 overflow-hidden">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  icon: string
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle'): void
}>()
</script>
