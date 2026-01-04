<template>
  <div class="space-y-8">
    <!-- 艺术风格 -->
    <div>
      <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
        <span class="mr-2">🎨</span>
        艺术风格
      </h3>

      <!-- 风格分类标签 -->
      <div class="flex flex-wrap gap-2 mb-4">
        <button
          v-for="category in artStyleCategories"
          :key="category.id"
          class="px-4 py-2 rounded-full text-sm font-medium transition-all"
          :class="selectedStyleCategory === category.id
            ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md'
            : 'bg-white border border-gray-200 text-gray-600 hover:border-purple-300 hover:text-purple-600'"
          @click="selectedStyleCategory = category.id"
        >
          {{ category.icon }} {{ category.name }}
        </button>
      </div>

      <!-- 当前分类下的风格选项 -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        <div
          v-for="style in currentCategoryStyles"
          :key="style.id"
          class="relative p-4 rounded-2xl cursor-pointer transition-all duration-300 hover:scale-105"
          :class="selectedArtStyle === style.id
            ? 'bg-gradient-to-br from-purple-100 to-pink-100 border-2 border-purple-400 shadow-md'
            : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
          @click="emit('update:selectedArtStyle', style.id)"
        >
          <!-- 推荐标签 -->
          <div
            v-if="style.recommended"
            class="absolute -top-2 -right-2 px-2 py-0.5 bg-gradient-to-r from-orange-400 to-pink-500 text-white text-xs rounded-full"
          >
            推荐
          </div>

          <div class="text-center">
            <p class="font-medium text-gray-800">{{ style.name }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ style.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 故事主角 -->
    <div>
      <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
        <span class="mr-2">🐰</span>
        故事主角
      </h3>
      <div class="grid grid-cols-3 sm:grid-cols-6 gap-3">
        <div
          v-for="protagonist in protagonists"
          :key="protagonist.animal"
          class="p-4 rounded-2xl cursor-pointer transition-all duration-300 hover:scale-105 text-center"
          :class="selectedProtagonist === protagonist.animal
            ? 'bg-gradient-to-br from-purple-100 to-pink-100 border-2 border-purple-400 shadow-md'
            : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
          @click="emit('update:selectedProtagonist', protagonist.animal)"
        >
          <div class="text-3xl mb-2">{{ getAnimalEmoji(protagonist.animal) }}</div>
          <p class="text-sm font-medium text-gray-800">{{ protagonist.name }}</p>
        </div>
      </div>
    </div>

    <!-- 色彩风格 -->
    <div>
      <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
        <span class="mr-2">🌈</span>
        色彩风格
      </h3>
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div
          v-for="palette in colorPalettes"
          :key="palette.id"
          class="p-4 rounded-2xl cursor-pointer transition-all duration-300 hover:scale-105"
          :class="selectedColorPalette === palette.id
            ? 'bg-gradient-to-br from-purple-100 to-pink-100 border-2 border-purple-400 shadow-md'
            : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
          @click="emit('update:selectedColorPalette', palette.id)"
        >
          <!-- 颜色预览 -->
          <div class="flex justify-center mb-2 space-x-1">
            <div
              v-for="(color, i) in palette.colors"
              :key="i"
              class="w-5 h-5 rounded-full"
              :style="{ backgroundColor: color }"
            />
          </div>
          <p class="text-sm font-medium text-gray-800 text-center">{{ palette.name }}</p>
          <p class="text-xs text-gray-500 text-center">{{ palette.description }}</p>
        </div>
      </div>
    </div>

    <!-- TTS 音色 -->
    <div v-if="showVoice">
      <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
        <span class="mr-2">🔊</span>
        配音音色
      </h3>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        <div
          v-for="voice in voices"
          :key="voice.id"
          class="p-5 rounded-2xl cursor-pointer transition-all duration-300 hover:scale-105 min-h-[140px] flex flex-col"
          :class="selectedVoice === voice.id
            ? 'bg-gradient-to-br from-purple-100 to-pink-100 border-2 border-purple-400 shadow-md'
            : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
          @click="emit('update:selectedVoice', voice.id)"
          :title="voice.description"
        >
          <div class="text-center flex-1 flex flex-col">
            <span class="text-2xl">{{ voice.gender === 'female' ? '👩' : '👨' }}</span>
            <p class="font-medium text-gray-800 mt-2">{{ voice.name }}</p>
            <p class="text-xs text-gray-500">{{ voice.style }}</p>
            <p v-if="voice.description" class="text-xs text-gray-400 mt-1 line-clamp-2">{{ voice.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ArtStyleOption, ProtagonistOption, ColorPaletteOption, VoiceOption, ArtStyleCategory } from '@/api/create'

const props = defineProps<{
  artStyles: ArtStyleOption[]
  artStyleCategories?: ArtStyleCategory[]
  protagonists: ProtagonistOption[]
  colorPalettes: ColorPaletteOption[]
  voices: VoiceOption[]
  selectedArtStyle: string
  selectedProtagonist: string
  selectedColorPalette: string
  selectedVoice: string
  showVoice?: boolean
}>()

const emit = defineEmits<{
  'update:selectedArtStyle': [value: string]
  'update:selectedProtagonist': [value: string]
  'update:selectedColorPalette': [value: string]
  'update:selectedVoice': [value: string]
}>()

// 当前选中的风格分类
const selectedStyleCategory = ref('threed')

// 当前分类下的风格选项
const currentCategoryStyles = computed(() => {
  if (props.artStyleCategories?.length) {
    const category = props.artStyleCategories.find(c => c.id === selectedStyleCategory.value)
    return category?.styles || []
  }
  // 如果没有分类数据，回退到全部风格
  return props.artStyles
})

// 当选中的风格改变时，自动切换到对应分类
watch(() => props.selectedArtStyle, (newStyle) => {
  if (newStyle && props.artStyleCategories?.length) {
    for (const category of props.artStyleCategories) {
      if (category.styles.some(s => s.id === newStyle)) {
        selectedStyleCategory.value = category.id
        break
      }
    }
  }
}, { immediate: true })

function getAnimalEmoji(animal: string): string {
  const emojis: Record<string, string> = {
    bunny: '🐰',
    bear: '🐻',
    cat: '🐱',
    dog: '🐶',
    panda: '🐼',
    fox: '🦊'
  }
  return emojis[animal] || '🐾'
}
</script>
