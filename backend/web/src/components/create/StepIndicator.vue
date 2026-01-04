<template>
  <div class="flex items-center justify-center mb-8">
    <div class="flex items-center space-x-2">
      <template v-for="(step, index) in steps" :key="index">
        <!-- 步骤圆点 -->
        <div
          class="flex items-center justify-center w-10 h-10 rounded-full text-sm font-medium transition-all duration-300"
          :class="getStepClass(index + 1)"
        >
          <span v-if="currentStep > index + 1">✓</span>
          <span v-else>{{ index + 1 }}</span>
        </div>

        <!-- 步骤标题（大屏显示） -->
        <span
          class="hidden sm:inline text-sm font-medium transition-colors"
          :class="currentStep >= index + 1 ? 'text-purple-600' : 'text-gray-400'"
        >
          {{ step }}
        </span>

        <!-- 连接线 -->
        <div
          v-if="index < steps.length - 1"
          class="w-8 sm:w-12 h-0.5 transition-colors duration-300"
          :class="currentStep > index + 1 ? 'bg-purple-500' : 'bg-gray-200'"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  steps: string[]
  currentStep: number
}>()

function getStepClass(step: number): string {
  if (props.currentStep > step) {
    return 'bg-purple-500 text-white'
  } else if (props.currentStep === step) {
    return 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
  } else {
    return 'bg-gray-100 text-gray-400'
  }
}
</script>
