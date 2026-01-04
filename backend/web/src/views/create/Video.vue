<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-purple-50">
    <div class="max-w-4xl mx-auto px-4 py-8">
      <!-- 返回按钮 -->
      <router-link
        to="/create"
        class="inline-flex items-center text-gray-500 hover:text-blue-600 mb-6"
      >
        <span class="mr-2">←</span>
        返回创作中心
      </router-link>

      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">
          🎬 视频创作
        </h1>
        <p class="text-gray-500">为 {{ childStore.currentChild?.name || '宝贝' }} 创作专属动画视频</p>
      </div>

      <!-- 步骤指示器 -->
      <StepIndicator :steps="steps" :current-step="createStore.currentStep" />

      <!-- 步骤内容 -->
      <div class="bg-white/80 backdrop-blur-sm rounded-3xl p-6 sm:p-8 shadow-xl">
        <!-- 步骤 1：选择模式 -->
        <div v-if="createStore.currentStep === 1">
          <h2 class="text-xl font-bold text-gray-800 mb-6">选择创作方式</h2>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- 独立创作 -->
            <div
              class="p-6 rounded-2xl cursor-pointer transition-all"
              :class="createStore.videoParams.creationMode === 'standalone'
                ? 'bg-gradient-to-br from-blue-100 to-cyan-100 border-2 border-blue-400 shadow-md'
                : 'bg-white/80 border-2 border-gray-200 hover:border-blue-200 hover:shadow-sm'"
              @click="createStore.videoParams.creationMode = 'standalone'"
            >
              <div class="text-4xl mb-3">🎨</div>
              <h3 class="text-lg font-medium text-gray-800 mb-2">独立创作</h3>
              <p class="text-sm text-gray-500">
                从零开始，用文字描述您想要的视频场景
              </p>
            </div>

            <!-- 基于绘本 -->
            <div
              class="p-6 rounded-2xl cursor-pointer transition-all"
              :class="createStore.videoParams.creationMode === 'from_book'
                ? 'bg-gradient-to-br from-blue-100 to-cyan-100 border-2 border-blue-400 shadow-md'
                : 'bg-white/80 border-2 border-gray-200 hover:border-blue-200 hover:shadow-sm'"
              @click="createStore.videoParams.creationMode = 'from_book'"
            >
              <div class="text-4xl mb-3">📚</div>
              <h3 class="text-lg font-medium text-gray-800 mb-2">基于绘本</h3>
              <p class="text-sm text-gray-500">
                选择已有绘本的页面，让画面动起来
              </p>
            </div>
          </div>

          <!-- 独立创作模式的输入框 -->
          <div v-if="createStore.videoParams.creationMode === 'standalone'" class="mt-8">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              视频场景描述
            </label>
            <textarea
              v-model="createStore.videoParams.customPrompt"
              rows="4"
              class="w-full px-4 py-3 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="例如：小兔子在花园里追蝴蝶，阳光明媚，花朵绽放..."
            />
            <p class="text-xs text-gray-500 mt-2">
              描述越详细，生成的视频越符合预期
            </p>

            <!-- 灵感提示 -->
            <div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-4 mt-4">
              <h3 class="text-sm font-medium text-gray-700 mb-3">💡 灵感提示</h3>

              <!-- 灵感分类标签 -->
              <div class="flex flex-wrap gap-2 mb-4">
                <button
                  v-for="category in inspirationCategories"
                  :key="category.id"
                  class="px-3 py-1.5 rounded-full text-xs font-medium transition-all"
                  :class="selectedInspirationCategory === category.id
                    ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-md'
                    : 'bg-white border border-gray-200 text-gray-600 hover:border-blue-300'"
                  @click="selectedInspirationCategory = category.id"
                >
                  {{ category.icon }} {{ category.name }}
                </button>
              </div>

              <!-- 当前分类的灵感提示 -->
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="prompt in currentInspirationPrompts"
                  :key="prompt"
                  class="px-3 py-1.5 bg-white rounded-full text-sm transition-colors"
                  :class="createStore.videoParams.customPrompt === prompt
                    ? 'bg-blue-100 text-blue-700 border border-blue-300'
                    : 'text-gray-600 hover:bg-blue-100 hover:text-blue-600'"
                  @click="createStore.videoParams.customPrompt = prompt"
                >
                  {{ prompt.length > 20 ? prompt.slice(0, 20) + '...' : prompt }}
                </button>
              </div>
            </div>
          </div>

          <!-- 基于绘本模式的选择 -->
          <div v-if="createStore.videoParams.creationMode === 'from_book'" class="mt-8">
            <!-- 加载中 -->
            <div v-if="loadingBooks" class="text-center py-8">
              <div class="text-4xl animate-bounce">📚</div>
              <p class="text-gray-500 mt-2">加载绘本列表中...</p>
            </div>

            <!-- 无绘本 -->
            <div v-else-if="pictureBooks.length === 0" class="text-center py-8">
              <div class="text-4xl">📭</div>
              <p class="text-gray-500 mt-2">暂无已创作的绘本</p>
              <router-link
                to="/create/picture-book"
                class="inline-block mt-4 px-4 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors"
              >
                去创作绘本
              </router-link>
            </div>

            <!-- 绘本列表 -->
            <div v-else>
              <h3 class="text-lg font-medium text-gray-800 mb-4">选择绘本</h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
                <div
                  v-for="book in pictureBooks"
                  :key="book.id"
                  class="rounded-2xl overflow-hidden cursor-pointer transition-all"
                  :class="createStore.videoParams.selectedBookId === book.id
                    ? 'ring-2 ring-blue-400 shadow-lg'
                    : 'hover:shadow-md'"
                  @click="selectBook(book)"
                >
                  <img
                    :src="book.cover_url"
                    :alt="book.title"
                    class="w-full aspect-square object-cover"
                  />
                  <div class="p-2 bg-white">
                    <p class="text-sm font-medium text-gray-800 truncate">{{ book.title }}</p>
                  </div>
                </div>
              </div>

              <!-- 选择页面 -->
              <div v-if="selectedBook && selectedBook.pages?.length" class="mt-6">
                <h3 class="text-lg font-medium text-gray-800 mb-4">选择页面</h3>
                <div class="grid grid-cols-3 sm:grid-cols-5 gap-3">
                  <div
                    v-for="(page, index) in selectedBook.pages"
                    :key="index"
                    class="rounded-xl overflow-hidden cursor-pointer transition-all"
                    :class="createStore.videoParams.selectedPageIndex === index
                      ? 'ring-2 ring-blue-400 shadow-md'
                      : 'hover:shadow-sm'"
                    @click="createStore.videoParams.selectedPageIndex = index"
                  >
                    <img
                      :src="page.image_url"
                      :alt="`页面 ${index + 1}`"
                      class="w-full aspect-square object-cover"
                    />
                    <div class="p-1 bg-gray-100 text-center">
                      <span class="text-xs text-gray-600">第 {{ index + 1 }} 页</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤 2：视频参数 -->
        <div v-else-if="createStore.currentStep === 2">
          <h2 class="text-xl font-bold text-gray-800 mb-6">设置视频参数</h2>

          <!-- 画面比例 -->
          <div class="mb-8">
            <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
              <span class="mr-2">📐</span>
              画面比例
            </h3>
            <div class="grid grid-cols-5 gap-3">
              <div
                v-for="ratio in aspectRatios"
                :key="ratio.id"
                class="p-4 rounded-2xl cursor-pointer transition-all text-center"
                :class="createStore.videoParams.aspectRatio === ratio.id
                  ? 'bg-gradient-to-br from-blue-100 to-cyan-100 border-2 border-blue-400'
                  : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
                @click="createStore.videoParams.aspectRatio = ratio.id"
              >
                <div class="flex justify-center mb-2">
                  <div
                    class="bg-gray-300 rounded"
                    :style="{ width: ratio.previewW + 'px', height: ratio.previewH + 'px' }"
                  />
                </div>
                <p class="text-sm font-medium text-gray-800">{{ ratio.label }}</p>
              </div>
            </div>
          </div>

          <!-- 视频时长 -->
          <div class="mb-8">
            <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
              <span class="mr-2">⏱️</span>
              视频时长
            </h3>
            <div class="grid grid-cols-4 gap-3">
              <div
                v-for="duration in [4, 5, 6, 8]"
                :key="duration"
                class="p-3 rounded-2xl cursor-pointer transition-all text-center"
                :class="createStore.videoParams.durationSeconds === duration
                  ? 'bg-gradient-to-br from-blue-100 to-cyan-100 border-2 border-blue-400'
                  : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
                @click="createStore.videoParams.durationSeconds = duration as 4 | 5 | 6 | 8"
              >
                <p class="font-medium text-gray-800">{{ duration }}秒</p>
              </div>
            </div>
          </div>

          <!-- 运动风格 -->
          <div class="mb-8">
            <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
              <span class="mr-2">🎥</span>
              运动风格
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div
                v-for="motion in motionModes"
                :key="motion.id"
                class="p-4 rounded-2xl cursor-pointer transition-all text-center"
                :class="createStore.videoParams.motionMode === motion.id
                  ? 'bg-gradient-to-br from-blue-100 to-cyan-100 border-2 border-blue-400'
                  : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
                @click="createStore.videoParams.motionMode = motion.id"
              >
                <span class="text-2xl">{{ motion.icon }}</span>
                <p class="font-medium text-gray-800 mt-2">{{ motion.name }}</p>
              </div>
            </div>
          </div>

          <!-- 艺术风格 -->
          <div class="mb-8">
            <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
              <span class="mr-2">🎨</span>
              艺术风格
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div
                v-for="style in createStore.styleOptions?.art_styles?.slice(0, 5) || []"
                :key="style.id"
                class="p-4 rounded-2xl cursor-pointer transition-all text-center"
                :class="createStore.videoParams.artStyle === style.id
                  ? 'bg-gradient-to-br from-blue-100 to-cyan-100 border-2 border-blue-400'
                  : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
                @click="createStore.videoParams.artStyle = style.id"
              >
                <p class="font-medium text-gray-800">{{ style.name }}</p>
              </div>
            </div>
          </div>

          <!-- 场景模板 -->
          <div>
            <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
              <span class="mr-2">🎭</span>
              场景模板
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div
                v-for="template in sceneTemplates"
                :key="template.id"
                class="relative p-4 rounded-2xl cursor-pointer transition-all text-center"
                :class="createStore.videoParams.sceneTemplate === template.id
                  ? 'bg-gradient-to-br from-blue-100 to-cyan-100 border-2 border-blue-400'
                  : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
                @click="createStore.videoParams.sceneTemplate = template.id"
              >
                <!-- 推荐标签 -->
                <div
                  v-if="template.recommended"
                  class="absolute -top-2 -right-2 px-2 py-0.5 bg-gradient-to-r from-orange-400 to-pink-500 text-white text-xs rounded-full"
                >
                  推荐
                </div>
                <span class="text-2xl">{{ template.icon }}</span>
                <p class="font-medium text-gray-800 mt-2">{{ template.name }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ template.desc }}</p>
              </div>
            </div>
          </div>

          <!-- 高级选项 -->
          <div class="mt-6 border border-blue-100 rounded-2xl overflow-hidden">
            <div
              class="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-cyan-50 cursor-pointer"
              @click="advancedExpanded = !advancedExpanded"
            >
              <div class="flex items-center">
                <span class="text-xl mr-3">⚙️</span>
                <div>
                  <h3 class="font-medium text-gray-800">高级选项</h3>
                  <p class="text-sm text-gray-500">分辨率、自动增强等设置</p>
                </div>
              </div>
              <span class="text-gray-400 transition-transform" :class="{ 'rotate-90': advancedExpanded }">›</span>
            </div>
            <div v-if="advancedExpanded" class="p-4 bg-white space-y-4">
              <!-- 分辨率 -->
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">分辨率</h4>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="res in resolutions"
                    :key="res.id"
                    class="px-4 py-2 rounded-xl text-sm border transition-all"
                    :class="createStore.videoParams.resolution === res.id
                      ? 'bg-blue-100 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-blue-200'"
                    @click="createStore.videoParams.resolution = res.id"
                  >
                    {{ res.name }}
                  </button>
                </div>
              </div>
              <!-- 自动增强 -->
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="text-sm font-medium text-gray-700">自动增强提示词</h4>
                  <p class="text-xs text-gray-500">AI 自动优化场景描述，提升画面质量</p>
                </div>
                <button
                  class="relative w-12 h-6 rounded-full transition-colors"
                  :class="createStore.videoParams.autoEnhancePrompt ? 'bg-blue-500' : 'bg-gray-300'"
                  @click="createStore.videoParams.autoEnhancePrompt = !createStore.videoParams.autoEnhancePrompt"
                >
                  <span
                    class="absolute top-1 w-4 h-4 bg-white rounded-full transition-transform"
                    :class="createStore.videoParams.autoEnhancePrompt ? 'left-7' : 'left-1'"
                  />
                </button>
              </div>
              <!-- 启用音频 -->
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="text-sm font-medium text-gray-700">启用音频</h4>
                  <p class="text-xs text-gray-500">为视频添加背景音效</p>
                </div>
                <button
                  class="relative w-12 h-6 rounded-full transition-colors"
                  :class="createStore.videoParams.enableAudio ? 'bg-blue-500' : 'bg-gray-300'"
                  @click="createStore.videoParams.enableAudio = !createStore.videoParams.enableAudio"
                >
                  <span
                    class="absolute top-1 w-4 h-4 bg-white rounded-full transition-transform"
                    :class="createStore.videoParams.enableAudio ? 'left-7' : 'left-1'"
                  />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤 3：确认创作 -->
        <div v-else-if="createStore.currentStep === 3">
          <h2 class="text-xl font-bold text-gray-800 mb-6">确认创作参数</h2>

          <div class="space-y-4">
            <!-- 创作方式 -->
            <div class="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-4">
              <h3 class="font-medium text-gray-800 mb-3">🎬 创作信息</h3>
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">创作方式：</span>
                  <span class="text-gray-800">
                    {{ createStore.videoParams.creationMode === 'standalone' ? '独立创作' : '基于绘本' }}
                  </span>
                </div>
                <div v-if="createStore.videoParams.creationMode === 'from_book' && selectedBook">
                  <span class="text-gray-500">绘本：</span>
                  <span class="text-gray-800">{{ selectedBook.title }}</span>
                </div>
                <div v-if="createStore.videoParams.creationMode === 'from_book' && createStore.videoParams.selectedPageIndex !== null">
                  <span class="text-gray-500">页面：</span>
                  <span class="text-gray-800">第 {{ (createStore.videoParams.selectedPageIndex || 0) + 1 }} 页</span>
                </div>
              </div>
              <div v-if="createStore.videoParams.creationMode === 'standalone'" class="mt-3 text-sm">
                <span class="text-gray-500">场景描述：</span>
                <p class="text-gray-800 mt-1">{{ createStore.videoParams.customPrompt }}</p>
              </div>
            </div>

            <!-- 视频参数 -->
            <div class="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-4">
              <h3 class="font-medium text-gray-800 mb-3">⚙️ 视频参数</h3>
              <div class="flex flex-wrap gap-2">
                <span class="px-3 py-1 bg-white/80 rounded-full text-sm text-gray-700">
                  {{ selectedRatioName }}
                </span>
                <span class="px-3 py-1 bg-white/80 rounded-full text-sm text-gray-700">
                  {{ createStore.videoParams.durationSeconds }}秒
                </span>
                <span class="px-3 py-1 bg-white/80 rounded-full text-sm text-gray-700">
                  {{ selectedMotionName }}
                </span>
                <span class="px-3 py-1 bg-white/80 rounded-full text-sm text-gray-700">
                  {{ selectedStyleName }}
                </span>
                <span class="px-3 py-1 bg-white/80 rounded-full text-sm text-gray-700">
                  {{ selectedTemplateName }}
                </span>
              </div>
            </div>

            <!-- 生成提示 -->
            <div class="bg-amber-50 rounded-2xl p-4">
              <p class="text-sm text-amber-700">
                <span class="font-medium">提示：</span>
                视频生成需要较长时间（约 2-5 分钟），请耐心等待。生成过程中请勿关闭页面。
              </p>
            </div>
          </div>
        </div>

        <!-- 步骤 4：生成中 -->
        <div v-else-if="createStore.currentStep === 4">
          <div class="text-center py-12">
            <div class="text-6xl mb-4 animate-bounce">🎬</div>
            <p class="text-gray-500">AI 正在创作专属视频...</p>
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
            v-if="createStore.currentStep === 1"
            :disabled="!canProceedFromStep1"
            class="px-8 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            @click="nextStep"
          >
            下一步 →
          </button>
          <button
            v-else-if="createStore.currentStep === 2"
            class="px-8 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl transition-all"
            @click="nextStep"
          >
            下一步 →
          </button>
          <button
            v-else-if="createStore.currentStep === 3"
            class="px-8 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl transition-all"
            @click="startGenerate"
          >
            🎬 开始创作
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
      content-type="video"
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
import { getContentList } from '@/api/content'
import type { PictureBook } from '@/api/types'
import StepIndicator from '@/components/create/StepIndicator.vue'
import GeneratingModal from '@/components/create/GeneratingModal.vue'

const router = useRouter()
const childStore = useChildStore()
const createStore = useCreateStore()

const steps = ['创作方式', '视频参数', '确认创作', '生成中']

const loadingBooks = ref(false)
const pictureBooks = ref<PictureBook[]>([])
const selectedBook = ref<PictureBook | null>(null)
const advancedExpanded = ref(false)

// 分辨率选项
const resolutions = [
  { id: '720P', name: '720P 高清' },
  { id: '1080P', name: '1080P 全高清' }
] as const

// 视频灵感分类（5个分类，每个10个标签）
const inspirationCategories = [
  {
    id: 'nature',
    name: '自然风光',
    icon: '🌲',
    prompts: [
      '小动物在樱花树下野餐，花瓣飘落如粉色雨',
      '小动物们在清澈小溪边玩水，阳光洒在水面波光粼粼',
      '小动物在金黄落叶中奔跑，枫叶随风飘落',
      '小动物堆雪人打雪仗，白雪皑皑的童话世界',
      '雨停了，小动物发现天边挂着美丽彩虹',
      '小动物在山顶看日出，金色阳光洒满大地',
      '小动物在月光下散步，萤火虫闪闪发光',
      '小动物穿过金黄向日葵花海，蜜蜂嗡嗡飞舞',
      '小动物在花园追逐蝴蝶，五彩缤纷的花朵盛开',
      '小动物在沙滩玩耍，浪花轻轻拍打海岸'
    ]
  },
  {
    id: 'daily',
    name: '温馨日常',
    icon: '🏠',
    prompts: [
      '小动物在厨房帮妈妈做饭，搅拌面糊烤蛋糕',
      '小动物窝在沙发上看绘本，窗外阳光温暖',
      '小动物专注地画画，画笔在纸上留下彩色印记',
      '小动物和玩具朋友们一起过家家',
      '小动物在浴缸里玩泡泡，开心得笑出声',
      '妈妈给小动物讲故事，温馨的卧室灯光柔和',
      '小动物们围坐享用甜点和果汁，欢声笑语',
      '小动物认真弹钢琴，音符在房间飘荡',
      '小动物在阳台照顾小植物，看它们慢慢长大',
      '一家人手拉手走在乡间小路，幸福满满'
    ]
  },
  {
    id: 'adventure',
    name: '冒险探索',
    icon: '🗺️',
    prompts: [
      '小动物攀登高山，到达山顶俯瞰壮丽景色',
      '小动物拿着藏宝图，穿过丛林寻找宝藏',
      '小动物坐在火车上，窗外风景不断变换',
      '小动物乘坐热气球飞越彩虹和云朵',
      '小动物们在星空下露营，篝火映照笑脸',
      '小动物在森林里迷路，在朋友帮助下找到回家路',
      '小动物划着小船在河流上探险',
      '小动物参观动物园，认识各种神奇动物',
      '小动物在游乐园玩旋转木马和摩天轮',
      '小动物在海边建造宏伟的沙滩城堡'
    ]
  },
  {
    id: 'fantasy',
    name: '奇幻魔法',
    icon: '✨',
    prompts: [
      '小仙女挥动魔法棒，星光闪烁变出惊喜',
      '小动物骑着独角兽在彩虹桥上奔跑',
      '可爱的小龙学习喷火，冒出彩色火焰',
      '美人鱼带着小动物参观珊瑚城堡',
      '小动物进入魔法城堡，每扇门后都有惊喜',
      '小动物跳上云朵，发现云端有座美丽城市',
      '小动物对着流星许愿，愿望神奇地实现了',
      '午夜钟声响起，玩具们都活过来开派对',
      '小动物跳进故事书，和书中角色一起冒险',
      '小动物在水晶球里看到未来的美好画面'
    ]
  },
  {
    id: 'emotion',
    name: '情感故事',
    icon: '🎭',
    prompts: [
      '小动物和好久不见的朋友相遇，激动地拥抱',
      '小动物精心准备礼物送给朋友，对方感动流泪',
      '吵架的两个小动物互相道歉，重新成为好朋友',
      '害怕的小动物鼓起勇气，成功克服了困难',
      '小动物努力练习终于获得冠军，举起奖杯',
      '小动物在车站和朋友依依不舍地告别',
      '小动物帮助摔倒的朋友站起来，传递温暖',
      '小动物们穿上毕业服，庆祝成长的时刻',
      '小动物鼓起勇气对妈妈说我爱你',
      '小动物站在新学校门口，期待美好的未来'
    ]
  }
]

// 当前选中的灵感分类
const selectedInspirationCategory = ref('nature')

// 当前分类下的灵感提示
const currentInspirationPrompts = computed(() => {
  const category = inspirationCategories.find(c => c.id === selectedInspirationCategory.value)
  return category?.prompts || []
})

const aspectRatios = [
  { id: '16:9', label: '横屏', previewW: 32, previewH: 18 },
  { id: '9:16', label: '竖屏', previewW: 18, previewH: 32 },
  { id: '4:3', label: '4:3', previewW: 28, previewH: 21 },
  { id: '3:4', label: '3:4', previewW: 21, previewH: 28 },
  { id: '1:1', label: '方形', previewW: 24, previewH: 24 }
] as const

const motionModes = [
  { id: 'static', name: '静态', icon: '🖼️' },
  { id: 'slow', name: '缓慢', icon: '🐢' },
  { id: 'normal', name: '正常', icon: '🚶' },
  { id: 'dynamic', name: '活泼', icon: '🏃' },
  { id: 'cinematic', name: '电影感', icon: '🎬' }
] as const

const sceneTemplates = [
  { id: 'storybook', name: '故事书', icon: '📖', desc: '经典绘本风格', recommended: true },
  { id: 'adventure', name: '冒险', icon: '🗺️', desc: '户外探险场景' },
  { id: 'fantasy', name: '奇幻', icon: '✨', desc: '魔法梦幻世界' },
  { id: 'everyday', name: '日常', icon: '🏠', desc: '温馨生活场景' },
  { id: 'nature', name: '自然', icon: '🌿', desc: '自然风光场景' },
  { id: 'dialogue', name: '对话', icon: '💬', desc: '角色互动对话' },
  { id: 'action', name: '动作', icon: '🏃', desc: '活泼动感场景' },
  { id: 'emotional', name: '情感', icon: '💕', desc: '温情感人时刻' }
]

// 计算属性
const canProceedFromStep1 = computed(() => {
  if (createStore.videoParams.creationMode === 'standalone') {
    return !!createStore.videoParams.customPrompt.trim()
  } else {
    return createStore.videoParams.selectedBookId !== null &&
           createStore.videoParams.selectedPageIndex !== null
  }
})

const selectedRatioName = computed(() => {
  const ratio = aspectRatios.find(r => r.id === createStore.videoParams.aspectRatio)
  return ratio ? `${ratio.label} (${ratio.id})` : createStore.videoParams.aspectRatio
})

const selectedMotionName = computed(() => {
  const motion = motionModes.find(m => m.id === createStore.videoParams.motionMode)
  return motion?.name || createStore.videoParams.motionMode
})

const selectedStyleName = computed(() => {
  const style = createStore.styleOptions?.art_styles?.find(
    s => s.id === createStore.videoParams.artStyle
  )
  return style?.name || createStore.videoParams.artStyle
})

const selectedTemplateName = computed(() => {
  const template = sceneTemplates.find(t => t.id === createStore.videoParams.sceneTemplate)
  return template?.name || createStore.videoParams.sceneTemplate
})

// 方法
async function loadPictureBooks() {
  loadingBooks.value = true
  try {
    const response = await getContentList({ type: 'picture_book', limit: 20 })
    pictureBooks.value = response.items.filter(
      item => item.content_type === 'picture_book'
    ) as PictureBook[]
  } catch (e) {
    console.error('加载绘本列表失败:', e)
  } finally {
    loadingBooks.value = false
  }
}

function selectBook(book: PictureBook) {
  createStore.videoParams.selectedBookId = book.id
  selectedBook.value = book
  createStore.videoParams.selectedPageIndex = null
}

function prevStep() {
  if (createStore.currentStep > 1) {
    createStore.currentStep--
  }
}

function nextStep() {
  createStore.currentStep++
}

async function startGenerate() {
  createStore.currentStep = 4
  try {
    await createStore.generateVideo()
  } catch (e) {
    console.error('生成视频失败:', e)
  }
}

function handlePlay() {
  if (createStore.generatedContentId) {
    router.push(`/play/video/${createStore.generatedContentId}`)
  }
}

function handleClose() {
  createStore.resetParams('video')
}

onMounted(async () => {
  createStore.resetParams('video')
  await Promise.all([
    createStore.loadOptions(),
    loadPictureBooks()
  ])
})

onUnmounted(() => {
  createStore.stopPolling()
})
</script>
