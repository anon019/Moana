<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
    <div class="max-w-4xl mx-auto px-4 py-8">
      <!-- 返回按钮 -->
      <router-link
        to="/create"
        class="inline-flex items-center text-gray-500 hover:text-purple-600 mb-6"
      >
        <span class="mr-2">←</span>
        返回创作中心
      </router-link>

      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
          📖 绘本创作
        </h1>
        <p class="text-gray-500">为 {{ childStore.currentChild?.name || '宝贝' }} 创作专属绘本故事</p>
      </div>

      <!-- 步骤指示器 -->
      <StepIndicator :steps="steps" :current-step="createStore.currentStep" />

      <!-- 步骤内容 -->
      <div class="bg-white/80 backdrop-blur-sm rounded-3xl p-6 sm:p-8 shadow-xl">
        <!-- 步骤 1：选择主题或输入描述 -->
        <div v-if="createStore.currentStep === 1">
          <!-- 模式切换 -->
          <div class="flex gap-4 mb-6">
            <button
              class="flex-1 py-3 px-4 rounded-2xl border-2 transition-all text-center"
              :class="createStore.pictureBookParams.creationMode === 'preset'
                ? 'border-purple-500 bg-purple-50 text-purple-700'
                : 'border-gray-200 text-gray-500 hover:border-purple-200'"
              @click="createStore.pictureBookParams.creationMode = 'preset'"
            >
              <div class="text-lg mb-1">📚</div>
              <div class="font-medium">预设主题</div>
              <div class="text-xs opacity-70">从精选主题中选择</div>
            </button>
            <button
              class="flex-1 py-3 px-4 rounded-2xl border-2 transition-all text-center"
              :class="createStore.pictureBookParams.creationMode === 'smart'
                ? 'border-purple-500 bg-purple-50 text-purple-700'
                : 'border-gray-200 text-gray-500 hover:border-purple-200'"
              @click="createStore.pictureBookParams.creationMode = 'smart'"
            >
              <div class="text-lg mb-1">✨</div>
              <div class="font-medium">智能创作</div>
              <div class="text-xs opacity-70">自由描述你的想法</div>
            </button>
          </div>

          <!-- 预设模式：主题选择 -->
          <div v-if="createStore.pictureBookParams.creationMode === 'preset'">
            <h2 class="text-xl font-bold text-gray-800 mb-6">选择故事主题</h2>
            <ThemeSelector
              :themes="createStore.themes"
              :selected-category="createStore.pictureBookParams.themeCategory"
              :selected-topic="createStore.pictureBookParams.themeTopic"
              @update:selected-category="createStore.pictureBookParams.themeCategory = $event"
              @update:selected-topic="createStore.pictureBookParams.themeTopic = $event"
              @select="handleThemeSelect"
            />
          </div>

          <!-- 智能模式：自由描述 -->
          <div v-else>
            <h2 class="text-xl font-bold text-gray-800 mb-6">描述你的创意</h2>
            <textarea
              v-model="createStore.pictureBookParams.customPrompt"
              rows="4"
              class="w-full px-4 py-3 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none text-lg"
              placeholder="例如：一个关于小熊学会分享的故事..."
            />
            <div class="text-right text-sm text-gray-400 mt-2">
              {{ createStore.pictureBookParams.customPrompt?.length || 0 }}/200
            </div>

            <!-- 灵感标签 -->
            <div class="mt-6">
              <h3 class="text-sm font-medium text-gray-700 mb-3">快速灵感</h3>

              <!-- 灵感分类标签 -->
              <div class="flex flex-wrap gap-2 mb-4">
                <button
                  v-for="category in inspirationCategories"
                  :key="category.id"
                  class="px-3 py-1.5 rounded-full text-xs font-medium transition-all"
                  :class="selectedInspirationCategory === category.id
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md'
                    : 'bg-white border border-gray-200 text-gray-600 hover:border-purple-300'"
                  @click="selectedInspirationCategory = category.id"
                >
                  {{ category.icon }} {{ category.name }}
                </button>
              </div>

              <!-- 当前分类的灵感标签 -->
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="tag in currentInspirationTags"
                  :key="tag.text"
                  class="px-4 py-2 rounded-full text-sm border transition-all hover:shadow-md"
                  :class="createStore.pictureBookParams.customPrompt === tag.prompt
                    ? 'bg-purple-100 border-purple-300 text-purple-700'
                    : 'bg-white border-gray-200 text-gray-600 hover:border-purple-200'"
                  @click="createStore.pictureBookParams.customPrompt = tag.prompt"
                >
                  {{ tag.icon }} {{ tag.text }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤 2：风格设置 -->
        <div v-else-if="createStore.currentStep === 2">
          <h2 class="text-xl font-bold text-gray-800 mb-6">选择绘本风格</h2>
          <StyleSelector
            v-if="createStore.styleOptions"
            :art-styles="createStore.styleOptions.art_styles"
            :art-style-categories="createStore.styleOptions.art_style_categories"
            :protagonists="createStore.styleOptions.protagonists"
            :color-palettes="createStore.styleOptions.color_palettes"
            :voices="createStore.styleOptions.tts_voices"
            :selected-art-style="createStore.pictureBookParams.artStyle"
            :selected-protagonist="createStore.pictureBookParams.protagonist.animal"
            :selected-color-palette="createStore.pictureBookParams.colorPalette"
            :selected-voice="createStore.pictureBookParams.voiceId"
            :show-voice="true"
            @update:selected-art-style="createStore.pictureBookParams.artStyle = $event"
            @update:selected-protagonist="updateProtagonist"
            @update:selected-color-palette="createStore.pictureBookParams.colorPalette = $event"
            @update:selected-voice="createStore.pictureBookParams.voiceId = $event"
          />

          <!-- 故事风格面板 -->
          <div class="mt-6 border border-purple-100 rounded-2xl overflow-hidden">
            <div
              class="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 cursor-pointer"
              @click="storyPanelExpanded = !storyPanelExpanded"
            >
              <div class="flex items-center">
                <span class="text-xl mr-3">📖</span>
                <div>
                  <h3 class="font-medium text-gray-800">故事风格</h3>
                  <p class="text-sm text-gray-500">{{ storyEnhancementSummary }}</p>
                </div>
              </div>
              <span class="text-gray-400 transition-transform" :class="{ 'rotate-90': storyPanelExpanded }">›</span>
            </div>
            <div v-if="storyPanelExpanded" class="p-4 space-y-4 bg-white">
              <!-- 叙事节奏 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">叙事节奏</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in narrativePaceOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.storyEnhancement.narrative_pace === opt.value
                      ? 'bg-purple-100 border-purple-300 text-purple-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-purple-200'"
                    @click="toggleStoryOption('narrative_pace', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
              <!-- 互动密度 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">互动密度</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in interactionDensityOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.storyEnhancement.interaction_density === opt.value
                      ? 'bg-purple-100 border-purple-300 text-purple-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-purple-200'"
                    @click="toggleStoryOption('interaction_density', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
              <!-- 教育侧重 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">教育侧重</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in educationalFocusOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.storyEnhancement.educational_focus === opt.value
                      ? 'bg-purple-100 border-purple-300 text-purple-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-purple-200'"
                    @click="toggleStoryOption('educational_focus', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
              <!-- 语言风格 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">语言风格</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in languageStyleOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.storyEnhancement.language_style === opt.value
                      ? 'bg-purple-100 border-purple-300 text-purple-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-purple-200'"
                    @click="toggleStoryOption('language_style', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
              <!-- 情节复杂度 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">情节复杂度</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in plotComplexityOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.storyEnhancement.plot_complexity === opt.value
                      ? 'bg-purple-100 border-purple-300 text-purple-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-purple-200'"
                    @click="toggleStoryOption('plot_complexity', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
              <!-- 结局风格 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">结局风格</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in endingStyleOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.storyEnhancement.ending_style === opt.value
                      ? 'bg-purple-100 border-purple-300 text-purple-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-purple-200'"
                    @click="toggleStoryOption('ending_style', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 画面设置面板 -->
          <div class="mt-4 border border-blue-100 rounded-2xl overflow-hidden">
            <div
              class="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-cyan-50 cursor-pointer"
              @click="visualPanelExpanded = !visualPanelExpanded"
            >
              <div class="flex items-center">
                <span class="text-xl mr-3">🎬</span>
                <div>
                  <h3 class="font-medium text-gray-800">画面设置</h3>
                  <p class="text-sm text-gray-500">{{ visualEnhancementSummary }}</p>
                </div>
              </div>
              <span class="text-gray-400 transition-transform" :class="{ 'rotate-90': visualPanelExpanded }">›</span>
            </div>
            <div v-if="visualPanelExpanded" class="p-4 space-y-4 bg-white">
              <!-- 时间氛围 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">时间氛围</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in timeAtmosphereOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.visualEnhancement.time_atmosphere === opt.value
                      ? 'bg-blue-100 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-blue-200'"
                    @click="toggleVisualOption('time_atmosphere', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
              <!-- 场景环境 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">场景环境</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in sceneEnvironmentOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.visualEnhancement.scene_environment === opt.value
                      ? 'bg-blue-100 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-blue-200'"
                    @click="toggleVisualOption('scene_environment', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
              <!-- 情感基调 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">情感基调</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in emotionalToneOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.visualEnhancement.emotional_tone === opt.value
                      ? 'bg-blue-100 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-blue-200'"
                    @click="toggleVisualOption('emotional_tone', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
              <!-- 画面构图 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">画面构图</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in compositionStyleOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.visualEnhancement.composition_style === opt.value
                      ? 'bg-blue-100 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-blue-200'"
                    @click="toggleVisualOption('composition_style', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
              <!-- 光照效果 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">光照效果</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="opt in lightingEffectOptions"
                    :key="opt.value"
                    class="px-3 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.pictureBookParams.visualEnhancement.lighting_effect === opt.value
                      ? 'bg-blue-100 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-blue-200'"
                    @click="toggleVisualOption('lighting_effect', opt.value)"
                  >
                    {{ opt.emoji }} {{ opt.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤 3：确认信息 -->
        <div v-else-if="createStore.currentStep === 3">
          <h2 class="text-xl font-bold text-gray-800 mb-6">确认创作信息</h2>
          <div class="space-y-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6">
            <div class="flex justify-between items-center py-2 border-b border-purple-100">
              <span class="text-gray-600">宝贝名字</span>
              <span class="font-medium text-gray-800">{{ childStore.currentChild?.name }}</span>
            </div>
            <div class="flex justify-between items-center py-2 border-b border-purple-100">
              <span class="text-gray-600">创作模式</span>
              <span class="font-medium text-gray-800">
                {{ createStore.pictureBookParams.creationMode === 'preset' ? '📚 预设主题' : '✨ 智能创作' }}
              </span>
            </div>
            <div v-if="createStore.pictureBookParams.creationMode === 'preset'" class="flex justify-between items-center py-2 border-b border-purple-100">
              <span class="text-gray-600">故事主题</span>
              <span class="font-medium text-gray-800">{{ selectedThemeName }}</span>
            </div>
            <div v-else class="py-2 border-b border-purple-100">
              <span class="text-gray-600 block mb-2">创意描述</span>
              <span class="font-medium text-gray-800 text-sm">{{ createStore.pictureBookParams.customPrompt }}</span>
            </div>
            <div class="flex justify-between items-center py-2 border-b border-purple-100">
              <span class="text-gray-600">艺术风格</span>
              <span class="font-medium text-gray-800">{{ selectedStyleName }}</span>
            </div>
            <div class="flex justify-between items-center py-2 border-b border-purple-100">
              <span class="text-gray-600">故事主角</span>
              <span class="font-medium text-gray-800">{{ selectedProtagonistName }}</span>
            </div>
            <div class="flex justify-between items-center py-2">
              <span class="text-gray-600">配音音色</span>
              <span class="font-medium text-gray-800">{{ selectedVoiceName }}</span>
            </div>
          </div>

          <!-- 故事风格确认 -->
          <div v-if="hasStoryEnhancement" class="mt-4 bg-purple-50 rounded-2xl p-4">
            <div class="flex items-center mb-3">
              <span class="text-lg mr-2">📖</span>
              <span class="font-medium text-gray-800">故事风格</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in storyEnhancementTags"
                :key="tag"
                class="px-3 py-1 bg-white rounded-full text-sm text-purple-700 border border-purple-200"
              >
                {{ tag }}
              </span>
            </div>
          </div>

          <!-- 画面设置确认 -->
          <div v-if="hasVisualEnhancement" class="mt-4 bg-blue-50 rounded-2xl p-4">
            <div class="flex items-center mb-3">
              <span class="text-lg mr-2">🎬</span>
              <span class="font-medium text-gray-800">画面设置</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in visualEnhancementTags"
                :key="tag"
                class="px-3 py-1 bg-white rounded-full text-sm text-blue-700 border border-blue-200"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <!-- 步骤 4：生成中（由 Modal 接管） -->
        <div v-else-if="createStore.currentStep === 4">
          <div class="text-center py-12">
            <div class="text-6xl mb-4 animate-bounce">✨</div>
            <p class="text-gray-500">正在为宝贝创作专属绘本...</p>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="flex justify-between mt-8 pt-6 border-t border-gray-100">
          <button
            v-if="createStore.currentStep > 1 && createStore.currentStep < 4"
            class="px-6 py-3 text-gray-600 hover:text-gray-800"
            @click="prevStep"
          >
            ← 上一步
          </button>
          <div v-else />

          <button
            v-if="createStore.currentStep < 3"
            :disabled="!canNextStep"
            class="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            @click="nextStep"
          >
            下一步 →
          </button>
          <button
            v-else-if="createStore.currentStep === 3"
            class="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl transition-all"
            @click="startGenerate"
          >
            ✨ 开始创作
          </button>
        </div>
      </div>
    </div>

    <!-- 生成弹窗 -->
    <GeneratingModal
      :visible="createStore.isGenerating || createStore.generatingStatus === 'completed' || createStore.generatingStatus === 'failed'"
      :status="createStore.generatingStatus"
      :progress="createStore.generatingProgress"
      :stage="createStore.generatingStage"
      :error="createStore.generatingError"
      content-type="picture_book"
      @play="handlePlay"
      @close="handleClose"
      @retry="startGenerate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChildStore } from '@/stores/child'
import { useCreateStore } from '@/stores/create'
import StepIndicator from '@/components/create/StepIndicator.vue'
import ThemeSelector from '@/components/create/ThemeSelector.vue'
import StyleSelector from '@/components/create/StyleSelector.vue'
import GeneratingModal from '@/components/create/GeneratingModal.vue'

const router = useRouter()
const childStore = useChildStore()
const createStore = useCreateStore()

const steps = ['选择主题', '风格设置', '确认信息', '生成中']

// 面板展开状态
const storyPanelExpanded = ref(false)
const visualPanelExpanded = ref(false)

// 故事增强选项
const narrativePaceOptions = [
  { value: 'relaxed', label: '轻松舒缓', emoji: '😌' },
  { value: 'lively', label: '紧凑活泼', emoji: '🎵' },
  { value: 'progressive', label: '循序渐进', emoji: '📖' }
]

const interactionDensityOptions = [
  { value: 'minimal', label: '少互动', emoji: '📕' },
  { value: 'moderate', label: '适中', emoji: '📗' },
  { value: 'intensive', label: '多互动', emoji: '📘' }
]

const educationalFocusOptions = [
  { value: 'cognitive', label: '认知学习', emoji: '🧠' },
  { value: 'behavioral', label: '行为引导', emoji: '🌟' },
  { value: 'emotional', label: '情感培养', emoji: '💕' },
  { value: 'imaginative', label: '想象激发', emoji: '🦋' }
]

const languageStyleOptions = [
  { value: 'simple', label: '简洁直白', emoji: '💬' },
  { value: 'rhythmic', label: '韵律押韵', emoji: '🎶' },
  { value: 'onomatopoeia', label: '拟声丰富', emoji: '🔔' },
  { value: 'repetitive', label: '重复强化', emoji: '🔄' }
]

const plotComplexityOptions = [
  { value: 'linear', label: '简单线性', emoji: '➡️' },
  { value: 'twist', label: '有小波折', emoji: '🌊' },
  { value: 'ensemble', label: '多角色', emoji: '👥' }
]

const endingStyleOptions = [
  { value: 'warm', label: '温馨收尾', emoji: '🤗' },
  { value: 'open', label: '开放想象', emoji: '✨' },
  { value: 'summary', label: '总结回顾', emoji: '📝' }
]

// 视觉增强选项
const timeAtmosphereOptions = [
  { value: 'morning', label: '清晨阳光', emoji: '🌅' },
  { value: 'afternoon', label: '午后温暖', emoji: '☀️' },
  { value: 'sunset', label: '傍晚金色', emoji: '🌇' },
  { value: 'night', label: '夜晚星空', emoji: '🌙' },
  { value: 'dreamy', label: '梦幻魔法', emoji: '✨' }
]

const sceneEnvironmentOptions = [
  { value: 'indoor', label: '温馨室内', emoji: '🏠' },
  { value: 'garden', label: '花园户外', emoji: '🌷' },
  { value: 'forest', label: '森林探险', emoji: '🌲' },
  { value: 'beach', label: '海边沙滩', emoji: '🏖️' },
  { value: 'clouds', label: '云端梦境', emoji: '☁️' }
]

const emotionalToneOptions = [
  { value: 'cheerful', label: '欢乐活泼', emoji: '😄' },
  { value: 'cozy', label: '温馨甜蜜', emoji: '🥰' },
  { value: 'playful', label: '轻松幽默', emoji: '😜' },
  { value: 'peaceful', label: '安静祥和', emoji: '😊' },
  { value: 'curious', label: '神秘好奇', emoji: '🤔' }
]

const compositionStyleOptions = [
  { value: 'close_up', label: '角色特写', emoji: '👤' },
  { value: 'panorama', label: '全景场景', emoji: '🏞️' },
  { value: 'interaction', label: '互动场景', emoji: '🤝' },
  { value: 'narrative', label: '故事叙事', emoji: '📽️' }
]

const lightingEffectOptions = [
  { value: 'soft_natural', label: '柔和自然', emoji: '🌤️' },
  { value: 'warm_sunlight', label: '温暖阳光', emoji: '🌞' },
  { value: 'dreamy_glow', label: '梦幻光晕', emoji: '💫' },
  { value: 'cozy_lamp', label: '夜灯温馨', emoji: '🪔' }
]

// 灵感标签分类（8类共80个）
const inspirationCategories = [
  {
    id: 'habit',
    name: '生活习惯',
    icon: '🏠',
    tags: [
      { icon: '🦷', text: '刷牙小卫士', prompt: '小动物学习正确刷牙方法，打败蛀牙小怪兽，保护洁白牙齿' },
      { icon: '🥬', text: '爱上蔬菜', prompt: '不爱吃蔬菜的小朋友发现蔬菜王国的秘密，学会爱上健康食物' },
      { icon: '😴', text: '乖乖睡觉', prompt: '月亮姐姐带着小动物进入甜蜜梦乡，学会自己安心入睡' },
      { icon: '🧹', text: '收拾玩具', prompt: '玩具们晚上会开派对，但只有被整理好的玩具才能参加' },
      { icon: '🚿', text: '快乐洗澡', prompt: '泡泡王国的冒险故事，让洗澡变成有趣的游戏时光' },
      { icon: '👋', text: '礼貌问好', prompt: '小动物学会说请、谢谢、对不起，交到更多好朋友' },
      { icon: '🧺', text: '自己穿衣', prompt: '衣服们在衣柜里等待被选中，学习自己穿衣搭配' },
      { icon: '⏰', text: '按时作息', prompt: '时钟爷爷教小动物认识时间，养成规律的生活习惯' },
      { icon: '🍚', text: '好好吃饭', prompt: '食物精灵的营养大冒险，让挑食的孩子爱上吃饭' },
      { icon: '💪', text: '坚持运动', prompt: '小动物们组建运动队，发现运动的快乐和好处' }
    ]
  },
  {
    id: 'emotion',
    name: '情感社交',
    icon: '💕',
    tags: [
      { icon: '🤝', text: '学会分享', prompt: '小熊发现分享玩具后，快乐变成了两倍' },
      { icon: '🫂', text: '拥抱的力量', prompt: '一个温暖的拥抱可以赶走所有不开心' },
      { icon: '😢', text: '接纳情绪', prompt: '小动物学会认识和表达自己的情绪，哭泣也是OK的' },
      { icon: '🙏', text: '学会感恩', prompt: '小兔子给帮助过自己的人准备感谢礼物' },
      { icon: '🤗', text: '交新朋友', prompt: '害羞的小动物第一天上幼儿园，学会主动交朋友' },
      { icon: '💔', text: '和好如初', prompt: '好朋友吵架了，学会道歉和原谅的故事' },
      { icon: '👶', text: '迎接弟妹', prompt: '家里要有新成员啦，学会做一个好哥哥好姐姐' },
      { icon: '🎁', text: '送出祝福', prompt: '给朋友准备生日惊喜，付出比收获更快乐' },
      { icon: '🏠', text: '想念家人', prompt: '小动物第一次离开家，学会独立也学会想念' },
      { icon: '🤜', text: '团队合作', prompt: '一个人做不到的事，一群好朋友一起可以完成' }
    ]
  },
  {
    id: 'cognitive',
    name: '认知学习',
    icon: '🧒',
    tags: [
      { icon: '🔢', text: '数字游戏', prompt: '数字精灵带小朋友玩数数游戏，认识1到10' },
      { icon: '🔤', text: '字母冒险', prompt: '26个字母的奇妙探险，每个字母都有超能力' },
      { icon: '🎨', text: '认识颜色', prompt: '彩虹仙子教小动物认识七种颜色的魔法' },
      { icon: '🔷', text: '形状世界', prompt: '圆形、方形、三角形组成的奇妙世界' },
      { icon: '🌡️', text: '冷热感知', prompt: '小动物体验四季变化，认识冷和热' },
      { icon: '📏', text: '大小比较', prompt: '谁大谁小？小动物们的比较大赛' },
      { icon: '⏰', text: '认识时间', prompt: '跟着太阳公公学习早中晚和时钟' },
      { icon: '🗺️', text: '方向认知', prompt: '上下左右前后，小动物的方向大冒险' },
      { icon: '🎵', text: '声音探索', prompt: '各种动物和物品会发出什么声音呢' },
      { icon: '🧩', text: '逻辑思维', prompt: '小侦探找规律，培养观察和推理能力' }
    ]
  },
  {
    id: 'safety',
    name: '安全教育',
    icon: '🛡️',
    tags: [
      { icon: '🚗', text: '交通安全', prompt: '斑马线上的小卫士，学会看红绿灯安全过马路' },
      { icon: '🔥', text: '消防安全', prompt: '小小消防员学习火灾逃生和消防知识' },
      { icon: '👤', text: '陌生人警惕', prompt: '不跟陌生人走，不吃陌生人给的东西' },
      { icon: '🏊', text: '水边安全', prompt: '小动物学习游泳安全规则，不私自下水' },
      { icon: '⚡', text: '用电安全', prompt: '电精灵教导正确使用电器，远离危险' },
      { icon: '🚪', text: '居家安全', prompt: '独自在家时怎样保护自己' },
      { icon: '🎢', text: '游乐安全', prompt: '游乐场的安全规则，开心玩耍不受伤' },
      { icon: '🍬', text: '食品安全', prompt: '不吃过期食物，认识食品保质期' },
      { icon: '📱', text: '求助方法', prompt: '遇到危险时怎样拨打110、120、119' },
      { icon: '🤕', text: '防止意外', prompt: '不在危险的地方玩耍，学会保护自己' }
    ]
  },
  {
    id: 'adventure',
    name: '想象冒险',
    icon: '🚀',
    tags: [
      { icon: '🌙', text: '月球探险', prompt: '小宇航员乘坐火箭去月球，遇见月亮上的朋友' },
      { icon: '🏰', text: '城堡奇遇', prompt: '进入魔法城堡，和王子公主一起冒险' },
      { icon: '🌊', text: '海底世界', prompt: '潜入深海探索神秘的海底王国和美人鱼' },
      { icon: '🦕', text: '恐龙时代', prompt: '穿越回恐龙时代，和恐龙做朋友' },
      { icon: '✨', text: '魔法森林', prompt: '在魔法森林里遇见会说话的树和精灵' },
      { icon: '🎪', text: '玩具复活', prompt: '午夜十二点，玩具们都活过来开派对' },
      { icon: '☁️', text: '云端王国', prompt: '爬上云朵，探索云端上的神秘世界' },
      { icon: '🗝️', text: '寻宝冒险', prompt: '跟着藏宝图，解开谜题找到神秘宝藏' },
      { icon: '🚂', text: '奇幻列车', prompt: '登上魔法列车，每一站都是新世界' },
      { icon: '🔮', text: '时光穿梭', prompt: '乘坐时光机，回到过去或去到未来' }
    ]
  },
  {
    id: 'nature',
    name: '自然探索',
    icon: '🌿',
    tags: [
      { icon: '🦋', text: '蝴蝶成长', prompt: '毛毛虫变蝴蝶的神奇蜕变之旅' },
      { icon: '🌱', text: '种子发芽', prompt: '一颗小种子的成长日记，从发芽到开花' },
      { icon: '🐜', text: '蚂蚁王国', prompt: '探索蚂蚁的地下城市，学习勤劳和团结' },
      { icon: '🌧️', text: '小水滴旅行', prompt: '小水滴的循环之旅，从云到雨再到河流' },
      { icon: '🐦', text: '鸟类迁徙', prompt: '跟着候鸟飞越千山万水的迁徙之旅' },
      { icon: '🌻', text: '向日葵秘密', prompt: '为什么向日葵总是朝着太阳微笑' },
      { icon: '🐝', text: '蜜蜂采蜜', prompt: '小蜜蜂辛勤工作，酿造甜甜蜂蜜' },
      { icon: '🍂', text: '四季变换', prompt: '感受春夏秋冬的美丽变化' },
      { icon: '🌈', text: '彩虹由来', prompt: '雨后为什么会出现美丽的彩虹' },
      { icon: '🌳', text: '大树故事', prompt: '一棵百年老树见证的温暖故事' }
    ]
  },
  {
    id: 'festival',
    name: '节日文化',
    icon: '🎉',
    tags: [
      { icon: '🧧', text: '春节拜年', prompt: '小动物们穿新衣、贴春联、收红包过大年' },
      { icon: '🥮', text: '中秋团圆', prompt: '一起赏月亮、吃月饼、听嫦娥的故事' },
      { icon: '🎂', text: '生日快乐', prompt: '小动物的生日派对，学会感恩父母' },
      { icon: '🐲', text: '端午节', prompt: '划龙舟、吃粽子、纪念屈原的故事' },
      { icon: '🏮', text: '元宵节', prompt: '猜灯谜、赏花灯、吃汤圆的欢乐夜晚' },
      { icon: '🌾', text: '丰收节', prompt: '秋天到了，小动物们收获劳动的果实' },
      { icon: '👨‍👩‍👧', text: '父母节', prompt: '用行动表达对爸爸妈妈的爱' },
      { icon: '👩‍🏫', text: '教师节', prompt: '感谢老师辛勤付出的故事' },
      { icon: '🎄', text: '圣诞分享', prompt: '学习分享和给予的快乐' },
      { icon: '🎃', text: '万圣派对', prompt: '有趣不吓人的装扮派对' }
    ]
  },
  {
    id: 'character',
    name: '品格培养',
    icon: '⭐',
    tags: [
      { icon: '💪', text: '勇敢面对', prompt: '害怕黑暗或打针的小动物学会勇敢' },
      { icon: '🎯', text: '坚持不懈', prompt: '小乌龟的故事，坚持就会成功' },
      { icon: '💡', text: '诚实守信', prompt: '做一个诚实的孩子，信守承诺' },
      { icon: '🌟', text: '自信闪耀', prompt: '发现自己的独特，相信自己很棒' },
      { icon: '🙋', text: '勇于尝试', prompt: '不怕失败，大胆尝试新事物' },
      { icon: '🎨', text: '创意无限', prompt: '发挥想象力，创造独一无二的作品' },
      { icon: '🤔', text: '独立思考', prompt: '学会自己思考问题，不人云亦云' },
      { icon: '💝', text: '善良待人', prompt: '帮助有困难的人，传递温暖' },
      { icon: '🏆', text: '公平竞争', prompt: '比赛中学会尊重对手，输赢都坦然' },
      { icon: '🌈', text: '乐观积极', prompt: '遇到困难也要微笑面对' }
    ]
  }
]

// 当前选中的灵感分类
const selectedInspirationCategory = ref('habit')

// 当前分类下的灵感标签
const currentInspirationTags = computed(() => {
  const category = inspirationCategories.find(c => c.id === selectedInspirationCategory.value)
  return category?.tags || []
})

// 计算属性
const canNextStep = computed(() => {
  if (createStore.currentStep === 1) {
    if (createStore.pictureBookParams.creationMode === 'preset') {
      return !!createStore.pictureBookParams.themeCategory && !!createStore.pictureBookParams.themeTopic
    } else {
      return !!createStore.pictureBookParams.customPrompt?.trim()
    }
  }
  return true
})

const selectedThemeName = computed(() => {
  if (!createStore.themes || !createStore.pictureBookParams.themeCategory) return ''
  const category = createStore.themes[createStore.pictureBookParams.themeCategory]
  const theme = category?.themes?.find(t => t.id === createStore.pictureBookParams.themeTopic)
  return theme?.name || ''
})

const selectedStyleName = computed(() => {
  const style = createStore.styleOptions?.art_styles?.find(
    s => s.id === createStore.pictureBookParams.artStyle
  )
  return style?.name || ''
})

const selectedProtagonistName = computed(() => {
  const protagonist = createStore.styleOptions?.protagonists?.find(
    p => p.animal === createStore.pictureBookParams.protagonist.animal
  )
  return protagonist?.name || ''
})

const selectedVoiceName = computed(() => {
  const voice = createStore.styleOptions?.tts_voices?.find(
    v => v.id === createStore.pictureBookParams.voiceId
  )
  return voice?.name || ''
})

// 故事增强相关
const storyEnhancementSummary = computed(() => {
  const se = createStore.pictureBookParams.storyEnhancement
  const count = Object.values(se).filter(v => v !== null).length
  return count === 0 ? '可选，由 AI 智能推断' : `已选 ${count} 项`
})

const hasStoryEnhancement = computed(() => {
  const se = createStore.pictureBookParams.storyEnhancement
  return Object.values(se).some(v => v !== null)
})

const storyEnhancementTags = computed(() => {
  const se = createStore.pictureBookParams.storyEnhancement
  const tags: string[] = []
  const allOptions = {
    narrative_pace: narrativePaceOptions,
    interaction_density: interactionDensityOptions,
    educational_focus: educationalFocusOptions,
    language_style: languageStyleOptions,
    plot_complexity: plotComplexityOptions,
    ending_style: endingStyleOptions
  }
  for (const [key, value] of Object.entries(se)) {
    if (value) {
      const opts = allOptions[key as keyof typeof allOptions]
      const opt = opts?.find(o => o.value === value)
      if (opt) tags.push(`${opt.emoji} ${opt.label}`)
    }
  }
  return tags
})

// 视觉增强相关
const visualEnhancementSummary = computed(() => {
  const ve = createStore.pictureBookParams.visualEnhancement
  const count = Object.values(ve).filter(v => v !== null).length
  return count === 0 ? '可选，由 AI 智能推断' : `已选 ${count} 项`
})

const hasVisualEnhancement = computed(() => {
  const ve = createStore.pictureBookParams.visualEnhancement
  return Object.values(ve).some(v => v !== null)
})

const visualEnhancementTags = computed(() => {
  const ve = createStore.pictureBookParams.visualEnhancement
  const tags: string[] = []
  const allOptions = {
    time_atmosphere: timeAtmosphereOptions,
    scene_environment: sceneEnvironmentOptions,
    emotional_tone: emotionalToneOptions,
    composition_style: compositionStyleOptions,
    lighting_effect: lightingEffectOptions
  }
  for (const [key, value] of Object.entries(ve)) {
    if (value) {
      const opts = allOptions[key as keyof typeof allOptions]
      const opt = opts?.find(o => o.value === value)
      if (opt) tags.push(`${opt.emoji} ${opt.label}`)
    }
  }
  return tags
})

// 方法
function handleThemeSelect() {
  // 主题选择后可以自动进入下一步
}

function updateProtagonist(animal: string) {
  const protagonist = createStore.styleOptions?.protagonists?.find(p => p.animal === animal)
  if (protagonist) {
    createStore.pictureBookParams.protagonist = {
      animal: protagonist.animal,
      color: protagonist.default_color,
      accessory: protagonist.default_accessory
    }
  }
}

function toggleStoryOption(key: keyof typeof createStore.pictureBookParams.storyEnhancement, value: string) {
  const se = createStore.pictureBookParams.storyEnhancement
  if (se[key] === value) {
    se[key] = null
  } else {
    se[key] = value
  }
}

function toggleVisualOption(key: keyof typeof createStore.pictureBookParams.visualEnhancement, value: string) {
  const ve = createStore.pictureBookParams.visualEnhancement
  if (ve[key] === value) {
    ve[key] = null
  } else {
    ve[key] = value
  }
}

function prevStep() {
  if (createStore.currentStep > 1) {
    createStore.currentStep--
  }
}

function nextStep() {
  if (createStore.currentStep < 4) {
    createStore.currentStep++
  }
}

async function startGenerate() {
  createStore.currentStep = 4
  try {
    await createStore.generatePictureBook()
  } catch (e) {
    console.error('生成绘本失败:', e)
  }
}

function handlePlay() {
  if (createStore.generatedContentId) {
    router.push(`/play/picture_book/${createStore.generatedContentId}`)
  }
}

function handleClose() {
  createStore.resetParams('picture_book')
}

// 生命周期
onMounted(async () => {
  createStore.resetParams('picture_book')
  await createStore.loadOptions()
})

onUnmounted(() => {
  createStore.stopPolling()
})
</script>
