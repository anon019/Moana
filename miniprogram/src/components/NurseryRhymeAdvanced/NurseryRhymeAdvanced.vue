<template>
  <view class="advanced-settings">
    <view class="settings-header" @tap="toggleExpand">
      <view class="header-left">
        <text class="header-icon">⚙️</text>
        <text class="header-title">高级设置</text>
        <text class="header-hint">（可选）</text>
      </view>
      <view class="header-arrow" :class="{ expanded: isExpanded }">
        <text>›</text>
      </view>
    </view>

    <view v-if="isExpanded" class="settings-panels">
      <!-- 音乐风格面板 -->
      <view class="panel">
        <view class="panel-header" @tap="togglePanel('music')">
          <text class="panel-icon">🎵</text>
          <text class="panel-title">音乐风格</text>
          <text class="panel-arrow" :class="{ open: openPanels.music }">›</text>
        </view>
        <view v-if="openPanels.music" class="panel-content">
          <!-- 音乐流派 -->
          <view class="field-group">
            <text class="field-label">音乐流派</text>
            <text class="field-help">{{ getHelp('music_genre') }}</text>
            <scroll-view class="chips-scroll" scroll-x>
              <view class="chips-row">
                <view
                  v-for="group in musicGenres"
                  :key="group.group"
                  class="chip-group"
                >
                  <text class="group-label">{{ group.group }}</text>
                  <view class="group-chips">
                    <view
                      v-for="opt in group.options"
                      :key="opt.value"
                      class="chip"
                      :class="{ selected: params.music_genre === opt.value }"
                      @tap="updateParam('music_genre', opt.value)"
                    >
                      {{ opt.label }}
                    </view>
                  </view>
                </view>
              </view>
            </scroll-view>
          </view>

          <!-- 节奏速度 -->
          <view class="field-group">
            <view class="field-header">
              <text class="field-label">节奏速度</text>
              <text class="field-value">{{ params.tempo || 100 }} BPM · {{ tempoHint }}</text>
            </view>
            <text class="field-help">{{ getHelp('tempo') }}</text>
            <slider
              class="custom-slider"
              :value="params.tempo || 100"
              :min="60"
              :max="180"
              :step="5"
              activeColor="#FF6B6B"
              @change="(e: any) => updateParam('tempo', e.detail.value)"
            />
            <view class="slider-labels">
              <text>60</text>
              <text>极慢</text>
              <text>中速</text>
              <text>快速</text>
              <text>180</text>
            </view>
          </view>

          <!-- 能量强度 -->
          <view class="field-group">
            <view class="field-header">
              <text class="field-label">能量强度</text>
              <text class="field-value">{{ params.energy_level || 5 }} · {{ energyHint }}</text>
            </view>
            <text class="field-help">{{ getHelp('energy_level') }}</text>
            <slider
              class="custom-slider"
              :value="params.energy_level || 5"
              :min="1"
              :max="10"
              :step="1"
              activeColor="#4ECDC4"
              @change="(e: any) => updateParam('energy_level', e.detail.value)"
            />
            <view class="slider-labels">
              <text>静谧</text>
              <text>轻柔</text>
              <text>温和</text>
              <text>活力</text>
              <text>激昂</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 人声演唱面板 -->
      <view class="panel">
        <view class="panel-header" @tap="togglePanel('vocal')">
          <text class="panel-icon">🎤</text>
          <text class="panel-title">人声演唱</text>
          <text class="panel-arrow" :class="{ open: openPanels.vocal }">›</text>
        </view>
        <view v-if="openPanels.vocal" class="panel-content">
          <!-- 音域 -->
          <view class="field-group">
            <text class="field-label">音域选择</text>
            <view class="option-row">
              <view
                v-for="range in vocalRanges"
                :key="range.value"
                class="option-card small"
                :class="{ selected: params.vocal_range === range.value }"
                @tap="updateParam('vocal_range', range.value)"
              >
                <text class="opt-label">{{ range.label }}</text>
                <text class="opt-desc">{{ range.description }}</text>
              </view>
            </view>
          </view>

          <!-- 情感表达 -->
          <view class="field-group">
            <text class="field-label">情感表达</text>
            <view class="chips-wrap">
              <view
                v-for="emotion in vocalEmotions"
                :key="emotion.value"
                class="chip"
                :class="{ selected: params.vocal_emotion === emotion.value }"
                @tap="updateParam('vocal_emotion', emotion.value)"
              >
                {{ emotion.label }}
              </view>
            </view>
          </view>

          <!-- 演唱技巧 -->
          <view class="field-group">
            <text class="field-label">演唱技巧</text>
            <view class="chips-wrap">
              <view
                v-for="tech in vocalTechniques"
                :key="tech.value"
                class="chip"
                :class="{ selected: params.vocal_style === tech.value }"
                @tap="updateParam('vocal_style', tech.value)"
              >
                {{ tech.label }}
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 乐器配置面板 -->
      <view class="panel">
        <view class="panel-header" @tap="togglePanel('instruments')">
          <text class="panel-icon">🎹</text>
          <text class="panel-title">乐器配置</text>
          <text class="panel-arrow" :class="{ open: openPanels.instruments }">›</text>
        </view>
        <view v-if="openPanels.instruments" class="panel-content">
          <scroll-view class="chips-scroll vertical" scroll-y style="max-height: 300rpx;">
            <view
              v-for="group in instrumentsByFamily"
              :key="group.group"
              class="chip-group"
            >
              <text class="group-label">{{ group.icon }} {{ group.group }}</text>
              <view class="chips-wrap">
                <view
                  v-for="inst in group.options"
                  :key="inst.value"
                  class="chip"
                  :class="{ selected: params.instruments?.includes(inst.value) }"
                  @tap="toggleArrayValue('instruments', inst.value)"
                >
                  {{ inst.label }}
                </view>
              </view>
            </view>
          </scroll-view>
        </view>
      </view>

      <!-- 音效元素面板 -->
      <view class="panel">
        <view class="panel-header" @tap="togglePanel('effects')">
          <text class="panel-icon">🔊</text>
          <text class="panel-title">音效元素</text>
          <text class="panel-arrow" :class="{ open: openPanels.effects }">›</text>
        </view>
        <view v-if="openPanels.effects" class="panel-content">
          <scroll-view class="chips-scroll vertical" scroll-y style="max-height: 300rpx;">
            <view
              v-for="group in soundEffects"
              :key="group.group"
              class="chip-group"
            >
              <text class="group-label">{{ group.icon }} {{ group.group }}</text>
              <view class="chips-wrap">
                <view
                  v-for="effect in group.options"
                  :key="effect.value"
                  class="chip"
                  :class="{ selected: params.sound_effects?.includes(effect.value) }"
                  @tap="toggleArrayValue('sound_effects', effect.value)"
                >
                  {{ effect.label }}
                </view>
              </view>
            </view>
          </scroll-view>
        </view>
      </view>

      <!-- 歌词设置面板 -->
      <view class="panel">
        <view class="panel-header" @tap="togglePanel('lyrics')">
          <text class="panel-icon">📝</text>
          <text class="panel-title">歌词设置</text>
          <text class="panel-arrow" :class="{ open: openPanels.lyrics }">›</text>
        </view>
        <view v-if="openPanels.lyrics" class="panel-content">
          <!-- 歌词复杂度 -->
          <view class="field-group">
            <view class="field-header">
              <text class="field-label">歌词复杂度</text>
              <text class="field-value">{{ lyricComplexityHint }}</text>
            </view>
            <text class="field-help">{{ getHelp('lyric_complexity') }}</text>
            <slider
              class="custom-slider"
              :value="params.lyric_complexity || 5"
              :min="1"
              :max="10"
              :step="1"
              activeColor="#9B59B6"
              @change="(e: any) => updateParam('lyric_complexity', e.detail.value)"
            />
          </view>

          <!-- 重复程度 -->
          <view class="field-group">
            <view class="field-header">
              <text class="field-label">重复程度</text>
              <text class="field-value">{{ repetitionHint }}</text>
            </view>
            <text class="field-help">{{ getHelp('repetition_level') }}</text>
            <slider
              class="custom-slider"
              :value="params.repetition_level || 6"
              :min="1"
              :max="10"
              :step="1"
              activeColor="#E74C3C"
              @change="(e: any) => updateParam('repetition_level', e.detail.value)"
            />
          </view>
        </view>
      </view>

      <!-- 歌曲结构面板 -->
      <view class="panel">
        <view class="panel-header" @tap="togglePanel('structure')">
          <text class="panel-icon">🎼</text>
          <text class="panel-title">歌曲结构</text>
          <text class="panel-arrow" :class="{ open: openPanels.structure }">›</text>
        </view>
        <view v-if="openPanels.structure" class="panel-content">
          <!-- 结构类型 -->
          <view class="field-group">
            <text class="field-label">结构类型</text>
            <view class="structure-grid">
              <view
                v-for="structure in songStructures"
                :key="structure.value"
                class="structure-card"
                :class="{ selected: params.song_structure === structure.value }"
                @tap="updateParam('song_structure', structure.value)"
              >
                <text class="structure-pattern">{{ structure.description }}</text>
                <text class="structure-name">{{ structure.label }}</text>
              </view>
            </view>
          </view>

          <!-- 动作指引 -->
          <view class="field-group">
            <text class="field-label">动作指引</text>
            <view class="action-grid">
              <view
                v-for="action in actionTypes"
                :key="action.value"
                class="action-card"
                :class="{ selected: params.action_types === action.value }"
                @tap="updateParam('action_types', action.value)"
              >
                <text class="action-icon">{{ action.icon }}</text>
                <text class="action-label">{{ action.label }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 语言文化面板 -->
      <view class="panel">
        <view class="panel-header" @tap="togglePanel('language')">
          <text class="panel-icon">🌍</text>
          <text class="panel-title">语言文化</text>
          <text class="panel-arrow" :class="{ open: openPanels.language }">›</text>
        </view>
        <view v-if="openPanels.language" class="panel-content">
          <!-- 语言 -->
          <view class="field-group">
            <text class="field-label">歌曲语言</text>
            <view class="chips-wrap">
              <view
                v-for="group in languages"
                :key="group.group"
                class="chip-group-inline"
              >
                <view
                  v-for="lang in group.options"
                  :key="lang.value"
                  class="chip"
                  :class="{ selected: params.language === lang.value }"
                  @tap="updateParam('language', lang.value)"
                >
                  {{ lang.label }}
                </view>
              </view>
            </view>
          </view>

          <!-- 文化风格 -->
          <view class="field-group">
            <text class="field-label">文化风格</text>
            <scroll-view class="chips-scroll vertical" scroll-y style="max-height: 240rpx;">
              <view
                v-for="group in culturalStyles"
                :key="group.group"
                class="chip-group"
              >
                <text class="group-label">{{ group.group }}</text>
                <view class="chips-wrap">
                  <view
                    v-for="style in group.options"
                    :key="style.value"
                    class="chip"
                    :class="{ selected: params.cultural_style === style.value }"
                    @tap="updateParam('cultural_style', style.value)"
                  >
                    {{ style.label }}
                  </view>
                </view>
              </view>
            </scroll-view>
          </view>
        </view>
      </view>

      <!-- 个性化面板 -->
      <view class="panel">
        <view class="panel-header" @tap="togglePanel('personal')">
          <text class="panel-icon">✨</text>
          <text class="panel-title">个性化定制</text>
          <text class="panel-arrow" :class="{ open: openPanels.personal }">›</text>
        </view>
        <view v-if="openPanels.personal" class="panel-content">
          <!-- 教育目标 -->
          <view class="field-group">
            <text class="field-label">教育目标</text>
            <scroll-view class="chips-scroll vertical" scroll-y style="max-height: 200rpx;">
              <view
                v-for="group in educationalFocus"
                :key="group.group"
                class="chip-group"
              >
                <text class="group-label">{{ group.group }}</text>
                <view class="chips-wrap">
                  <view
                    v-for="focus in group.options"
                    :key="focus.value"
                    class="chip"
                    :class="{ selected: params.educational_focus === focus.value }"
                    @tap="updateParam('educational_focus', focus.value)"
                  >
                    {{ focus.label }}
                  </view>
                </view>
              </view>
            </scroll-view>
          </view>

          <!-- 喜欢的颜色 -->
          <view class="field-group">
            <text class="field-label">喜欢的颜色</text>
            <view class="chips-wrap">
              <view
                v-for="group in favoriteColors"
                :key="group.group"
                class="chip-group-inline"
              >
                <view
                  v-for="color in group.options"
                  :key="color.value"
                  class="chip color-chip"
                  :class="{ selected: params.favorite_colors?.includes(color.value) }"
                  @tap="toggleArrayValue('favorite_colors', color.value)"
                >
                  {{ color.icon }} {{ color.label }}
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- Suno 进阶面板 -->
      <view class="panel">
        <view class="panel-header" @tap="togglePanel('suno')">
          <text class="panel-icon">🎛️</text>
          <text class="panel-title">Suno 进阶</text>
          <text class="panel-arrow" :class="{ open: openPanels.suno }">›</text>
        </view>
        <view v-if="openPanels.suno" class="panel-content">
          <!-- 预设组合 -->
          <view class="field-group">
            <text class="field-label">预设组合</text>
            <view class="option-row">
              <view
                v-for="preset in sunoPresets"
                :key="preset.id"
                class="option-card"
                :class="{ selected: currentSunoPreset === preset.id }"
                @tap="applySunoPreset(preset)"
              >
                <text class="opt-icon">{{ preset.icon }}</text>
                <text class="opt-label">{{ preset.name }}</text>
                <text class="opt-desc">{{ preset.description }}</text>
              </view>
            </view>
          </view>

          <!-- 风格权重 -->
          <view class="field-group">
            <view class="field-header">
              <text class="field-label">风格权重</text>
              <text class="field-value">{{ Math.round((params.style_weight || 0.5) * 100) }}%</text>
            </view>
            <text class="field-help">{{ getHelp('style_weight') }}</text>
            <slider
              class="custom-slider"
              :value="(params.style_weight || 0.5) * 100"
              :min="0"
              :max="100"
              :step="5"
              activeColor="#3498DB"
              @change="(e: any) => updateParam('style_weight', e.detail.value / 100)"
            />
          </view>

          <!-- 创意程度 -->
          <view class="field-group">
            <view class="field-header">
              <text class="field-label">创意程度</text>
              <text class="field-value">{{ Math.round((params.creativity || 0.5) * 100) }}%</text>
            </view>
            <text class="field-help">{{ getHelp('creativity') }}</text>
            <slider
              class="custom-slider"
              :value="(params.creativity || 0.5) * 100"
              :min="0"
              :max="100"
              :step="5"
              activeColor="#E67E22"
              @change="(e: any) => updateParam('creativity', e.detail.value / 100)"
            />
          </view>

          <!-- 排除标签 -->
          <view class="field-group">
            <text class="field-label">排除风格</text>
            <view class="chips-wrap">
              <view
                v-for="tag in negativeTagOptions"
                :key="tag.value"
                class="chip negative"
                :class="{ selected: selectedNegativeTags.includes(tag.value) }"
                @tap="toggleNegativeTag(tag.value)"
              >
                {{ tag.label }}
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { GenerateNurseryRhymeParams } from '@/api/content'
import {
  MUSIC_GENRES,
  VOCAL_RANGES,
  VOCAL_EMOTIONS,
  VOCAL_TECHNIQUES,
  INSTRUMENTS_BY_FAMILY,
  SOUND_EFFECTS,
  SONG_STRUCTURES,
  ACTION_TYPES,
  LANGUAGES,
  CULTURAL_STYLES,
  FAVORITE_COLORS,
  EDUCATIONAL_FOCUS,
  SUNO_PRESETS,
  COMMON_NEGATIVE_TAGS,
  PARAM_HELP,
  getTempoHint,
  getEnergyHint,
  getLyricComplexityHint,
  getRepetitionHint
} from '@/config/nurseryRhymeConfig'

const props = defineProps<{
  modelValue: Partial<GenerateNurseryRhymeParams>
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: Partial<GenerateNurseryRhymeParams>): void
}>()

// 面板展开状态
const isExpanded = ref(false)
const openPanels = ref<Record<string, boolean>>({
  music: false,
  vocal: false,
  instruments: false,
  effects: false,
  lyrics: false,
  structure: false,
  language: false,
  personal: false,
  suno: false
})

// 配置数据
const musicGenres = MUSIC_GENRES
const vocalRanges = VOCAL_RANGES
const vocalEmotions = VOCAL_EMOTIONS
const vocalTechniques = VOCAL_TECHNIQUES
const instrumentsByFamily = INSTRUMENTS_BY_FAMILY
const soundEffects = SOUND_EFFECTS
const songStructures = SONG_STRUCTURES
const actionTypes = ACTION_TYPES
const languages = LANGUAGES
const culturalStyles = CULTURAL_STYLES
const favoriteColors = FAVORITE_COLORS
const educationalFocus = EDUCATIONAL_FOCUS
const sunoPresets = SUNO_PRESETS
const negativeTagOptions = COMMON_NEGATIVE_TAGS

// 当前参数
const params = computed(() => props.modelValue)

// 负向标签
const selectedNegativeTags = ref<string[]>([])
const currentSunoPreset = ref<string>('balanced')

// 计算属性
const tempoHint = computed(() => getTempoHint(params.value.tempo || 100))
const energyHint = computed(() => getEnergyHint(params.value.energy_level || 5))
const lyricComplexityHint = computed(() => getLyricComplexityHint(params.value.lyric_complexity || 5))
const repetitionHint = computed(() => getRepetitionHint(params.value.repetition_level || 6))

// 方法
function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

function togglePanel(panel: string) {
  openPanels.value[panel] = !openPanels.value[panel]
}

function getHelp(key: string): string {
  return PARAM_HELP[key] || ''
}

function updateParam(key: keyof GenerateNurseryRhymeParams, value: any) {
  emit('update:modelValue', {
    ...props.modelValue,
    [key]: value
  })
}

function toggleArrayValue(key: keyof GenerateNurseryRhymeParams, value: string) {
  const current = (props.modelValue[key] as string[]) || []
  const index = current.indexOf(value)
  let newArray: string[]

  if (index > -1) {
    newArray = current.filter(v => v !== value)
  } else {
    newArray = [...current, value]
  }

  emit('update:modelValue', {
    ...props.modelValue,
    [key]: newArray
  })
}

function applySunoPreset(preset: typeof SUNO_PRESETS[0]) {
  currentSunoPreset.value = preset.id
  emit('update:modelValue', {
    ...props.modelValue,
    style_weight: preset.style_weight,
    creativity: preset.creativity
  })
}

function toggleNegativeTag(tag: string) {
  const index = selectedNegativeTags.value.indexOf(tag)
  if (index > -1) {
    selectedNegativeTags.value.splice(index, 1)
  } else {
    selectedNegativeTags.value.push(tag)
  }
  // 更新负向标签字符串
  updateParam('negative_tags', selectedNegativeTags.value.join(', '))
}

// 监听外部参数变化同步负向标签
watch(() => props.modelValue.negative_tags, (val) => {
  if (val) {
    selectedNegativeTags.value = val.split(',').map(s => s.trim()).filter(Boolean)
  }
}, { immediate: true })
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

// ============================================
// 高级设置组件 - 温暖童话花园风格
// Warm Storybook Garden Advanced Settings
// ============================================

.advanced-settings {
  margin: $spacing-lg 0;
  background: $bg-card;
  border-radius: $radius-lg;
  border: 1rpx solid $border-light;
  box-shadow: $shadow-card;
  overflow: hidden;

  // 顶部装饰渐变线
  &::before {
    content: '';
    display: block;
    height: 4rpx;
    background: linear-gradient(90deg, $song-primary, $song-secondary, $accent);
    opacity: 0.6;
  }
}

// ==========================================
// 设置头部 - 可点击展开
// ==========================================
.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md $spacing-lg;
  background: linear-gradient(135deg, rgba($song-light, 0.5) 0%, rgba($bg-soft, 0.8) 100%);
  cursor: pointer;
  transition: background $duration-fast;

  &:active {
    background: rgba($song-light, 0.7);
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
  }

  .header-icon {
    width: 48rpx;
    height: 48rpx;
    background: linear-gradient(135deg, $song-primary, $song-secondary);
    border-radius: $radius-md;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24rpx;
    box-shadow: 0 4rpx 12rpx rgba($song-primary, 0.25);
  }

  .header-title {
    font-size: $font-md;
    font-weight: $font-semibold;
    color: $text-primary;
  }

  .header-hint {
    font-size: $font-xs;
    color: $text-tertiary;
    margin-left: 4rpx;
  }

  .header-arrow {
    width: 36rpx;
    height: 36rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba($song-primary, 0.1);
    border-radius: $radius-sm;
    transition: all $duration-base $ease-bounce;

    text {
      font-size: 28rpx;
      color: $song-primary;
      font-weight: $font-bold;
      transform: rotate(90deg);
      transition: transform $duration-base $ease-bounce;
    }

    &.expanded text {
      transform: rotate(-90deg);
    }
  }
}

// ==========================================
// 设置面板容器
// ==========================================
.settings-panels {
  padding: $spacing-md;
  background: $bg-soft;
}

// ==========================================
// 单个面板 - 柔和卡片风格
// ==========================================
.panel {
  margin-bottom: $spacing-sm;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-light;
  box-shadow: $shadow-sm;
  overflow: hidden;
  transition: all $duration-base;

  &:last-child {
    margin-bottom: 0;
  }

  // 展开状态增强
  &:has(.panel-content) {
    box-shadow: $shadow-md;
    border-color: rgba($song-primary, 0.15);
  }
}

.panel-header {
  display: flex;
  align-items: center;
  padding: $spacing-md;
  gap: $spacing-sm;
  cursor: pointer;
  transition: background $duration-fast;

  &:active {
    background: $bg-soft;
  }

  .panel-icon {
    width: 40rpx;
    height: 40rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba($song-primary, 0.1);
    border-radius: $radius-sm;
    font-size: 22rpx;
  }

  .panel-title {
    flex: 1;
    font-size: $font-base;
    font-weight: $font-medium;
    color: $text-primary;
  }

  .panel-arrow {
    font-size: 28rpx;
    color: $text-tertiary;
    transition: transform $duration-fast $ease-bounce;
    transform: rotate(90deg);

    &.open {
      transform: rotate(-90deg);
      color: $song-primary;
    }
  }
}

.panel-content {
  padding: 0 $spacing-md $spacing-md;
  border-top: 1rpx solid $border-light;
  animation: slideDown $duration-base $ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// ==========================================
// 字段组 - 清晰的层次结构
// ==========================================
.field-group {
  margin-bottom: $spacing-lg;
  padding-top: $spacing-md;

  &:last-child {
    margin-bottom: 0;
  }

  &:first-child {
    padding-top: $spacing-sm;
  }
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-xs;
}

.field-label {
  font-size: $font-sm;
  font-weight: $font-medium;
  color: $text-primary;
  margin-bottom: $spacing-xs;
  display: flex;
  align-items: center;
  gap: 6rpx;

  &::before {
    content: '';
    width: 6rpx;
    height: 6rpx;
    background: $song-primary;
    border-radius: 50%;
  }
}

.field-value {
  font-size: $font-xs;
  color: $song-primary;
  font-weight: $font-medium;
  background: rgba($song-primary, 0.1);
  padding: 4rpx 12rpx;
  border-radius: $radius-full;
}

.field-help {
  font-size: $font-xs;
  color: $text-tertiary;
  margin-bottom: $spacing-sm;
  display: block;
  line-height: $line-height-base;
}

// ==========================================
// Chip 标签系统 - 柔和圆润
// ==========================================
.chips-scroll {
  white-space: nowrap;
  margin: 0 -#{$spacing-md};
  padding: 0 $spacing-md;

  &.vertical {
    white-space: normal;
    margin: 0;
    padding: 0;
  }
}

.chips-row {
  display: inline-flex;
  gap: $spacing-md;
}

.chip-group {
  margin-bottom: $spacing-md;

  .group-label {
    font-size: $font-xs;
    color: $text-tertiary;
    margin-bottom: $spacing-xs;
    display: block;
    font-weight: $font-medium;
  }

  .group-chips {
    display: inline-flex;
    gap: $spacing-xs;
    flex-wrap: wrap;
  }
}

.chip-group-inline {
  display: inline;
}

.chips-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 14rpx 24rpx;
  background: $bg-soft;
  border-radius: $radius-full;
  border: 2rpx solid transparent;
  font-size: $font-sm;
  color: $text-secondary;
  transition: all $duration-fast $ease-bounce;

  &:active {
    transform: scale(0.95);
  }

  &.selected {
    background: linear-gradient(135deg, rgba($song-primary, 0.15), rgba($song-secondary, 0.15));
    border-color: $song-primary;
    color: $song-primary;
    font-weight: $font-medium;
    box-shadow: 0 2rpx 8rpx rgba($song-primary, 0.2);
  }

  &.negative {
    background: rgba($error, 0.08);
    border: 2rpx solid rgba($error, 0.2);
    color: $text-secondary;

    &.selected {
      background: rgba($error, 0.15);
      border-color: $error;
      color: $error;
      font-weight: $font-medium;
    }
  }

  &.color-chip {
    gap: 6rpx;
  }
}

// ==========================================
// 选项卡片 - 双列布局
// ==========================================
.option-row {
  display: flex;
  gap: $spacing-sm;
  flex-wrap: nowrap;

  &.wrap {
    flex-wrap: wrap;
  }
}

.option-card {
  flex: 1;
  min-width: 0;
  padding: $spacing-md;
  background: $bg-soft;
  border-radius: $radius-md;
  border: 2rpx solid transparent;
  text-align: center;
  transition: all $duration-fast $ease-bounce;

  &:active {
    transform: scale(0.97);
  }

  &.small {
    padding: $spacing-sm $spacing-xs;

    .opt-label {
      font-size: $font-xs;
    }
    .opt-desc {
      font-size: 20rpx;
    }
  }

  &.selected {
    background: linear-gradient(135deg, rgba($song-primary, 0.1), rgba($song-secondary, 0.1));
    border-color: $song-primary;
    box-shadow: 0 4rpx 16rpx rgba($song-primary, 0.15);

    .opt-label {
      color: $song-primary;
    }
    .opt-icon {
      transform: scale(1.1);
    }
  }

  .opt-icon {
    font-size: 36rpx;
    display: block;
    margin-bottom: $spacing-xs;
    transition: transform $duration-fast $ease-bounce;
  }

  .opt-label {
    font-size: $font-sm;
    color: $text-primary;
    font-weight: $font-medium;
    display: block;
    transition: color $duration-fast;
  }

  .opt-desc {
    font-size: $font-xs;
    color: $text-tertiary;
    margin-top: 4rpx;
    display: block;
    line-height: 1.3;
  }
}

// ==========================================
// 滑块控件 - 温暖色调
// ==========================================
.custom-slider {
  margin: $spacing-sm 0;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 20rpx;
  color: $text-tertiary;
  padding: 0 4rpx;
  margin-top: 4rpx;
}

// ==========================================
// 歌曲结构 - 专用网格布局
// ==========================================
.structure-grid {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
  margin-top: $spacing-xs;
}

.structure-card {
  // 固定宽度：(容器宽度 - 4个间距) / 5 ≈ 每行5个
  // 但考虑到描述文字较长，使用2列布局更合适
  flex: 0 0 calc((100% - #{$spacing-sm}) / 2);
  min-height: 80rpx;
  padding: $spacing-sm $spacing-md;
  background: $bg-soft;
  border-radius: $radius-md;
  border: 2rpx solid transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4rpx;
  transition: all $duration-fast $ease-bounce;
  box-sizing: border-box;

  &:active {
    transform: scale(0.97);
  }

  &.selected {
    background: linear-gradient(135deg, rgba($song-primary, 0.12), rgba($song-secondary, 0.08));
    border-color: $song-primary;
    box-shadow: 0 4rpx 12rpx rgba($song-primary, 0.15);

    .structure-pattern {
      color: $song-primary;
    }

    .structure-name {
      color: $song-primary;
    }
  }

  .structure-pattern {
    font-size: $font-sm;
    font-weight: $font-semibold;
    color: $text-primary;
    font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
    letter-spacing: 1rpx;
    transition: color $duration-fast;
  }

  .structure-name {
    font-size: $font-xs;
    color: $text-tertiary;
    transition: color $duration-fast;
  }
}

// ==========================================
// 动作指引 - 紧凑图标网格
// ==========================================
.action-grid {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
  margin-top: $spacing-xs;
}

.action-card {
  // 每行4个
  flex: 0 0 calc((100% - #{$spacing-sm} * 3) / 4);
  padding: $spacing-sm $spacing-xs;
  background: $bg-soft;
  border-radius: $radius-md;
  border: 2rpx solid transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  transition: all $duration-fast $ease-bounce;
  box-sizing: border-box;

  &:active {
    transform: scale(0.95);
  }

  &.selected {
    background: linear-gradient(135deg, rgba($song-primary, 0.12), rgba($song-secondary, 0.08));
    border-color: $song-primary;
    box-shadow: 0 3rpx 10rpx rgba($song-primary, 0.15);

    .action-icon {
      transform: scale(1.15);
    }

    .action-label {
      color: $song-primary;
      font-weight: $font-medium;
    }
  }

  .action-icon {
    font-size: 32rpx;
    transition: transform $duration-fast $ease-bounce;
  }

  .action-label {
    font-size: $font-xs;
    color: $text-secondary;
    text-align: center;
    transition: all $duration-fast;
  }
}
</style>
