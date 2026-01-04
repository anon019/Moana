<template>
  <div class="mt-6 border border-pink-100 rounded-2xl overflow-hidden">
    <!-- 高级设置头部 -->
    <div
      class="flex items-center justify-between p-4 bg-gradient-to-r from-pink-50 to-rose-50 cursor-pointer"
      @click="isExpanded = !isExpanded"
    >
      <div class="flex items-center">
        <span class="text-xl mr-3">⚙️</span>
        <div>
          <h3 class="font-medium text-gray-800">高级设置</h3>
          <p class="text-sm text-gray-500">{{ advancedSummary }}</p>
        </div>
      </div>
      <span class="text-gray-400 transition-transform" :class="{ 'rotate-90': isExpanded }">›</span>
    </div>

    <div v-if="isExpanded" class="bg-white divide-y divide-gray-100">
      <!-- 音乐风格面板 -->
      <CollapsiblePanel title="音乐风格" icon="🎵" :open="openPanels.music" @toggle="togglePanel('music')">
        <!-- 音乐流派 -->
        <div class="mb-4">
          <label class="text-sm font-medium text-gray-700 mb-2 block">音乐流派</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="genre in musicGenres"
              :key="genre.value"
              class="px-3 py-1.5 text-sm rounded-full border transition-all"
              :class="params.musicGenre === genre.value
                ? 'bg-pink-100 border-pink-300 text-pink-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-pink-200'"
              @click="emit('update', 'musicGenre', params.musicGenre === genre.value ? '' : genre.value)"
            >
              {{ genre.label }}
            </button>
          </div>
        </div>

        <!-- 能量强度 -->
        <div>
          <div class="flex justify-between mb-2">
            <label class="text-sm font-medium text-gray-700">能量强度</label>
            <span class="text-sm text-pink-600">{{ params.energyLevel }} · {{ energyHint }}</span>
          </div>
          <input
            type="range"
            :value="params.energyLevel"
            min="1"
            max="10"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
            @input="emit('update', 'energyLevel', Number(($event.target as HTMLInputElement).value))"
          />
          <div class="flex justify-between text-xs text-gray-400 mt-1">
            <span>静谧</span>
            <span>轻柔</span>
            <span>温和</span>
            <span>活力</span>
            <span>激昂</span>
          </div>
        </div>
      </CollapsiblePanel>

      <!-- 人声演唱面板 -->
      <CollapsiblePanel title="人声演唱" icon="🎤" :open="openPanels.vocal" @toggle="togglePanel('vocal')">
        <!-- 音域 -->
        <div class="mb-4">
          <label class="text-sm font-medium text-gray-700 mb-2 block">音域选择</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="range in vocalRanges"
              :key="range.value"
              class="p-3 text-center rounded-xl border transition-all"
              :class="params.vocalRange === range.value
                ? 'bg-pink-50 border-pink-300'
                : 'bg-gray-50 border-gray-200 hover:border-pink-200'"
              @click="emit('update', 'vocalRange', params.vocalRange === range.value ? '' : range.value)"
            >
              <div class="text-sm font-medium text-gray-800">{{ range.label }}</div>
              <div class="text-xs text-gray-500">{{ range.desc }}</div>
            </button>
          </div>
        </div>

        <!-- 情感表达 -->
        <div class="mb-4">
          <label class="text-sm font-medium text-gray-700 mb-2 block">情感表达</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="emotion in vocalEmotions"
              :key="emotion.value"
              class="px-3 py-1.5 text-sm rounded-full border transition-all"
              :class="params.vocalEmotion === emotion.value
                ? 'bg-pink-100 border-pink-300 text-pink-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-pink-200'"
              @click="emit('update', 'vocalEmotion', emotion.value)"
            >
              {{ emotion.label }}
            </button>
          </div>
        </div>

        <!-- 演唱技巧 -->
        <div>
          <label class="text-sm font-medium text-gray-700 mb-2 block">演唱技巧</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tech in vocalTechniques"
              :key="tech.value"
              class="px-3 py-1.5 text-sm rounded-full border transition-all"
              :class="params.vocalStyle === tech.value
                ? 'bg-pink-100 border-pink-300 text-pink-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-pink-200'"
              @click="emit('update', 'vocalStyle', params.vocalStyle === tech.value ? '' : tech.value)"
            >
              {{ tech.label }}
            </button>
          </div>
        </div>
      </CollapsiblePanel>

      <!-- 乐器配置面板 -->
      <CollapsiblePanel title="乐器配置" icon="🎹" :open="openPanels.instruments" @toggle="togglePanel('instruments')">
        <!-- 乐器分类标签 -->
        <div class="flex flex-wrap gap-2 mb-4">
          <button
            v-for="category in INSTRUMENT_CATEGORIES"
            :key="category.id"
            class="px-3 py-1.5 rounded-full text-xs font-medium transition-all"
            :class="selectedInstrumentCategory === category.id
              ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-md'
              : 'bg-white border border-gray-200 text-gray-600 hover:border-pink-300'"
            @click="selectedInstrumentCategory = category.id"
          >
            {{ category.icon }} {{ category.name }}
          </button>
        </div>

        <!-- 当前分类的乐器选项 -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <div
            v-for="instrument in currentCategoryInstruments"
            :key="instrument.id"
            class="p-3 rounded-xl cursor-pointer transition-all text-center"
            :class="params.instruments.includes(instrument.id)
              ? 'bg-pink-100 border-2 border-pink-400'
              : 'bg-white border border-gray-200 hover:border-pink-200'"
            @click="toggleInstrument(instrument.id)"
          >
            <span class="text-2xl">{{ instrument.emoji }}</span>
            <p class="text-sm font-medium text-gray-800 mt-1">{{ instrument.name }}</p>
            <p class="text-xs text-gray-500">{{ instrument.description }}</p>
          </div>
        </div>

        <!-- 已选乐器显示 -->
        <div v-if="params.instruments.length > 0" class="mt-4 pt-4 border-t border-gray-100">
          <p class="text-xs text-gray-500 mb-2">已选择 {{ params.instruments.length }} 个乐器</p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="instId in params.instruments"
              :key="instId"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-pink-100 text-pink-700"
            >
              {{ getInstrumentName(instId) }}
              <button
                class="ml-1 hover:text-pink-900"
                @click.stop="toggleInstrument(instId)"
              >
                &times;
              </button>
            </span>
          </div>
        </div>
      </CollapsiblePanel>

      <!-- 歌词设置面板 -->
      <CollapsiblePanel title="歌词设置" icon="📝" :open="openPanels.lyrics" @toggle="togglePanel('lyrics')">
        <!-- 歌词复杂度 -->
        <div class="mb-4">
          <div class="flex justify-between mb-2">
            <label class="text-sm font-medium text-gray-700">歌词复杂度</label>
            <span class="text-sm text-pink-600">{{ lyricComplexityHint }}</span>
          </div>
          <input
            type="range"
            :value="params.lyricComplexity"
            min="1"
            max="10"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
            @input="emit('update', 'lyricComplexity', Number(($event.target as HTMLInputElement).value))"
          />
        </div>

        <!-- 重复程度 -->
        <div>
          <div class="flex justify-between mb-2">
            <label class="text-sm font-medium text-gray-700">重复程度</label>
            <span class="text-sm text-pink-600">{{ repetitionHint }}</span>
          </div>
          <input
            type="range"
            :value="params.repetitionLevel"
            min="1"
            max="10"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
            @input="emit('update', 'repetitionLevel', Number(($event.target as HTMLInputElement).value))"
          />
        </div>
      </CollapsiblePanel>

      <!-- 歌曲结构面板 -->
      <CollapsiblePanel title="歌曲结构" icon="🎼" :open="openPanels.structure" @toggle="togglePanel('structure')">
        <!-- 结构类型 -->
        <div class="mb-4">
          <label class="text-sm font-medium text-gray-700 mb-2 block">结构类型</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="structure in songStructures"
              :key="structure.value"
              class="p-3 text-left rounded-xl border transition-all"
              :class="params.songStructure === structure.value
                ? 'bg-pink-50 border-pink-300'
                : 'bg-gray-50 border-gray-200 hover:border-pink-200'"
              @click="emit('update', 'songStructure', structure.value)"
            >
              <div class="text-sm font-medium text-gray-800">{{ structure.pattern }}</div>
              <div class="text-xs text-gray-500">{{ structure.label }}</div>
            </button>
          </div>
        </div>

        <!-- 动作指引 -->
        <div>
          <label class="text-sm font-medium text-gray-700 mb-2 block">动作指引</label>
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="action in actionTypes"
              :key="action.value"
              class="p-2 text-center rounded-xl border transition-all"
              :class="params.actionTypes === action.value
                ? 'bg-pink-50 border-pink-300'
                : 'bg-gray-50 border-gray-200 hover:border-pink-200'"
              @click="emit('update', 'actionTypes', params.actionTypes === action.value ? '' : action.value)"
            >
              <div class="text-xl">{{ action.icon }}</div>
              <div class="text-xs text-gray-600">{{ action.label }}</div>
            </button>
          </div>
        </div>
      </CollapsiblePanel>

      <!-- 语言文化面板 -->
      <CollapsiblePanel title="语言文化" icon="🌍" :open="openPanels.language" @toggle="togglePanel('language')">
        <!-- 语言 -->
        <div class="mb-4">
          <label class="text-sm font-medium text-gray-700 mb-2 block">歌曲语言</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="lang in languages"
              :key="lang.value"
              class="px-3 py-1.5 text-sm rounded-full border transition-all"
              :class="params.language === lang.value
                ? 'bg-pink-100 border-pink-300 text-pink-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-pink-200'"
              @click="emit('update', 'language', lang.value)"
            >
              {{ lang.label }}
            </button>
          </div>
        </div>

        <!-- 文化风格 -->
        <div>
          <label class="text-sm font-medium text-gray-700 mb-2 block">文化风格</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="style in culturalStyles"
              :key="style.value"
              class="px-3 py-1.5 text-sm rounded-full border transition-all"
              :class="params.culturalStyle === style.value
                ? 'bg-pink-100 border-pink-300 text-pink-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-pink-200'"
              @click="emit('update', 'culturalStyle', params.culturalStyle === style.value ? '' : style.value)"
            >
              {{ style.label }}
            </button>
          </div>
        </div>
      </CollapsiblePanel>

      <!-- Suno 进阶面板 -->
      <CollapsiblePanel title="创意调节" icon="🎛️" :open="openPanels.suno" @toggle="togglePanel('suno')">
        <!-- 风格权重 -->
        <div class="mb-4">
          <div class="flex justify-between mb-2">
            <label class="text-sm font-medium text-gray-700">风格权重</label>
            <span class="text-sm text-pink-600">{{ Math.round(params.styleWeight * 100) }}%</span>
          </div>
          <input
            type="range"
            :value="params.styleWeight * 100"
            min="0"
            max="100"
            step="5"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
            @input="emit('update', 'styleWeight', Number(($event.target as HTMLInputElement).value) / 100)"
          />
          <p class="text-xs text-gray-500 mt-1">控制生成音乐对风格标签的遵循程度</p>
        </div>

        <!-- 创意程度 -->
        <div>
          <div class="flex justify-between mb-2">
            <label class="text-sm font-medium text-gray-700">创意程度</label>
            <span class="text-sm text-pink-600">{{ Math.round(params.creativity * 100) }}%</span>
          </div>
          <input
            type="range"
            :value="params.creativity * 100"
            min="0"
            max="100"
            step="5"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
            @input="emit('update', 'creativity', Number(($event.target as HTMLInputElement).value) / 100)"
          />
          <p class="text-xs text-gray-500 mt-1">更高的创意程度会产生更多变化</p>
        </div>
      </CollapsiblePanel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import CollapsiblePanel from './CollapsiblePanel.vue'
import { INSTRUMENT_OPTIONS, INSTRUMENT_CATEGORIES } from '@/api/create'

interface NurseryRhymeParams {
  musicGenre: string
  energyLevel: number
  vocalRange: string
  vocalEmotion: string
  vocalStyle: string
  instruments: string[]
  lyricComplexity: number
  repetitionLevel: number
  songStructure: string
  actionTypes: string
  language: string
  culturalStyle: string
  styleWeight: number
  creativity: number
}

const props = defineProps<{
  params: NurseryRhymeParams
}>()

const emit = defineEmits<{
  (e: 'update', key: keyof NurseryRhymeParams, value: any): void
  (e: 'updateArray', key: 'instruments', value: string[]): void
}>()

const isExpanded = ref(false)
const openPanels = reactive({
  music: false,
  vocal: false,
  instruments: false,
  lyrics: false,
  structure: false,
  language: false,
  suno: false
})
const selectedInstrumentCategory = ref('keyboard')

// 配置选项
const musicGenres = [
  { value: 'nursery_folk', label: '民谣童谣' },
  { value: 'pop_kids', label: '流行童歌' },
  { value: 'classical_kids', label: '古典童乐' },
  { value: 'electronic_kids', label: '电子童趣' },
  { value: 'jazz_kids', label: '爵士童韵' },
  { value: 'world_music', label: '世界音乐' }
]

const vocalRanges = [
  { value: 'soprano', label: '高音', desc: '明亮清脆' },
  { value: 'mezzo', label: '中音', desc: '温暖圆润' },
  { value: 'alto', label: '低音', desc: '沉稳柔和' }
]

const vocalEmotions = [
  { value: 'happy', label: '欢快' },
  { value: 'gentle', label: '温柔' },
  { value: 'playful', label: '俏皮' },
  { value: 'dreamy', label: '梦幻' },
  { value: 'energetic', label: '活力' },
  { value: 'calm', label: '平静' }
]

const vocalTechniques = [
  { value: 'clear', label: '清晰' },
  { value: 'breathy', label: '轻柔' },
  { value: 'vibrato', label: '颤音' },
  { value: 'whisper', label: '轻声' }
]

// 根据分类筛选乐器
const currentCategoryInstruments = computed(() => {
  return INSTRUMENT_OPTIONS.filter(i => i.category === selectedInstrumentCategory.value)
})

// 获取乐器名称
function getInstrumentName(id: string): string {
  const instrument = INSTRUMENT_OPTIONS.find(i => i.id === id)
  return instrument ? `${instrument.emoji} ${instrument.name}` : id
}

// 切换乐器选择
function toggleInstrument(id: string) {
  const current = [...props.params.instruments]
  const index = current.indexOf(id)
  if (index > -1) {
    current.splice(index, 1)
  } else {
    current.push(id)
  }
  emit('updateArray', 'instruments', current)
}

const songStructures = [
  { value: 'simple', pattern: 'A-A-A', label: '简单重复' },
  { value: 'verse_chorus', pattern: 'A-B-A-B', label: '主副歌' },
  { value: 'aaba', pattern: 'A-A-B-A', label: '经典结构' },
  { value: 'through', pattern: 'A-B-C-D', label: '通篇发展' }
]

const actionTypes = [
  { value: 'none', icon: '🎵', label: '无动作' },
  { value: 'clap', icon: '👏', label: '拍手' },
  { value: 'dance', icon: '💃', label: '跳舞' },
  { value: 'finger', icon: '👆', label: '手指游戏' }
]

const languages = [
  { value: 'mandarin', label: '普通话' },
  { value: 'cantonese', label: '粤语' },
  { value: 'english', label: '英语' },
  { value: 'bilingual', label: '中英双语' }
]

const culturalStyles = [
  { value: 'chinese_folk', label: '中国民谣' },
  { value: 'western_nursery', label: '西方童谣' },
  { value: 'japanese_style', label: '日式童歌' },
  { value: 'korean_style', label: '韩式童歌' },
  { value: 'modern_fusion', label: '现代融合' }
]

// 计算提示
const energyHint = computed(() => {
  const level = props.params.energyLevel
  if (level <= 2) return '静谧舒缓'
  if (level <= 4) return '轻柔温和'
  if (level <= 6) return '中等活力'
  if (level <= 8) return '活泼明快'
  return '热情激昂'
})

const lyricComplexityHint = computed(() => {
  const level = props.params.lyricComplexity
  if (level <= 3) return '简单词汇'
  if (level <= 6) return '适中难度'
  return '丰富表达'
})

const repetitionHint = computed(() => {
  const level = props.params.repetitionLevel
  if (level <= 3) return '少重复'
  if (level <= 6) return '适度重复'
  return '高重复记忆'
})

const advancedSummary = computed(() => {
  let count = 0
  if (props.params.musicGenre) count++
  if (props.params.vocalRange) count++
  if (props.params.vocalStyle) count++
  if (props.params.instruments.length > 0) count++
  if (props.params.actionTypes) count++
  if (props.params.culturalStyle) count++
  if (props.params.styleWeight !== 0.5 || props.params.creativity !== 0.5) count++
  return count === 0 ? '可选，展开自定义更多参数' : `已自定义 ${count} 项设置`
})

function togglePanel(panel: keyof typeof openPanels) {
  openPanels[panel] = !openPanels[panel]
}
</script>
