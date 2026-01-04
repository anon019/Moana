<template>
  <div class="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50">
    <div class="max-w-4xl mx-auto px-4 py-8">
      <!-- 返回按钮 -->
      <router-link
        to="/create"
        class="inline-flex items-center text-gray-500 hover:text-pink-600 mb-6"
      >
        <span class="mr-2">←</span>
        返回创作中心
      </router-link>

      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent mb-2">
          🎵 儿歌创作
        </h1>
        <p class="text-gray-500">为 {{ childStore.currentChild?.name || '宝贝' }} 创作专属音乐</p>
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
              :class="createStore.nurseryRhymeParams.creationMode === 'preset'
                ? 'border-pink-500 bg-pink-50 text-pink-700'
                : 'border-gray-200 text-gray-500 hover:border-pink-200'"
              @click="createStore.nurseryRhymeParams.creationMode = 'preset'"
            >
              <div class="text-lg mb-1">🎶</div>
              <div class="font-medium">预设主题</div>
              <div class="text-xs opacity-70">从精选主题中选择</div>
            </button>
            <button
              class="flex-1 py-3 px-4 rounded-2xl border-2 transition-all text-center"
              :class="createStore.nurseryRhymeParams.creationMode === 'smart'
                ? 'border-pink-500 bg-pink-50 text-pink-700'
                : 'border-gray-200 text-gray-500 hover:border-pink-200'"
              @click="createStore.nurseryRhymeParams.creationMode = 'smart'"
            >
              <div class="text-lg mb-1">✨</div>
              <div class="font-medium">智能创作</div>
              <div class="text-xs opacity-70">自由描述你的想法</div>
            </button>
          </div>

          <!-- 预设模式：主题选择 -->
          <div v-if="createStore.nurseryRhymeParams.creationMode === 'preset'">
            <h2 class="text-xl font-bold text-gray-800 mb-6">选择儿歌主题</h2>
            <ThemeSelector
              :themes="createStore.themes"
              :selected-category="createStore.nurseryRhymeParams.themeCategory"
              :selected-topic="createStore.nurseryRhymeParams.themeTopic"
              @update:selected-category="createStore.nurseryRhymeParams.themeCategory = $event"
              @update:selected-topic="createStore.nurseryRhymeParams.themeTopic = $event"
            />
          </div>

          <!-- 智能模式：自由描述 -->
          <div v-else>
            <h2 class="text-xl font-bold text-gray-800 mb-6">描述你的创意</h2>
            <textarea
              v-model="createStore.nurseryRhymeParams.customPrompt"
              rows="4"
              class="w-full px-4 py-3 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none text-lg"
              placeholder="例如：一首关于刷牙的欢快儿歌..."
            />
            <div class="text-right text-sm text-gray-400 mt-2">
              {{ createStore.nurseryRhymeParams.customPrompt?.length || 0 }}/200
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
                    ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-md'
                    : 'bg-white border border-gray-200 text-gray-600 hover:border-pink-300'"
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
                  :class="createStore.nurseryRhymeParams.customPrompt === tag.prompt
                    ? 'bg-pink-100 border-pink-300 text-pink-700'
                    : 'bg-white border-gray-200 text-gray-600 hover:border-pink-200'"
                  @click="createStore.nurseryRhymeParams.customPrompt = tag.prompt"
                >
                  {{ tag.icon }} {{ tag.text }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤 2：音乐参数 -->
        <div v-else-if="createStore.currentStep === 2">
          <h2 class="text-xl font-bold text-gray-800 mb-6">选择音乐风格</h2>

          <!-- 音乐情绪 -->
          <div class="mb-8">
            <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
              <span class="mr-2">🎭</span>
              音乐情绪
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div
                v-for="mood in createStore.styleOptions?.music_moods || []"
                :key="mood.id"
                class="p-4 rounded-2xl cursor-pointer transition-all duration-300 hover:scale-105 text-center"
                :class="createStore.nurseryRhymeParams.musicMood === mood.id
                  ? 'bg-gradient-to-br from-pink-100 to-rose-100 border-2 border-pink-400 shadow-md'
                  : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
                @click="createStore.nurseryRhymeParams.musicMood = mood.id"
              >
                <p class="font-medium text-gray-800">{{ mood.name }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ mood.description }}</p>
              </div>
            </div>
          </div>

          <!-- 节奏速度 -->
          <div class="mb-8">
            <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
              <span class="mr-2">⚡</span>
              节奏速度
            </h3>
            <div class="px-4">
              <input
                type="range"
                v-model.number="createStore.nurseryRhymeParams.tempo"
                min="60"
                max="180"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
              />
              <div class="flex justify-between text-sm text-gray-500 mt-2">
                <span>慢速 60</span>
                <span class="font-medium text-pink-600">{{ createStore.nurseryRhymeParams.tempo }} BPM</span>
                <span>快速 180</span>
              </div>
            </div>
          </div>

          <!-- 歌曲时长 -->
          <div class="mb-8">
            <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
              <span class="mr-2">⏱️</span>
              歌曲时长
            </h3>
            <div class="grid grid-cols-4 gap-3">
              <div
                v-for="duration in [30, 60, 90, 120]"
                :key="duration"
                class="p-3 rounded-2xl cursor-pointer transition-all text-center"
                :class="createStore.nurseryRhymeParams.durationPreference === duration
                  ? 'bg-gradient-to-br from-pink-100 to-rose-100 border-2 border-pink-400'
                  : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
                @click="createStore.nurseryRhymeParams.durationPreference = duration"
              >
                <p class="font-medium text-gray-800">{{ duration }}秒</p>
              </div>
            </div>
          </div>

          <!-- 人声类型 -->
          <div>
            <h3 class="text-lg font-medium text-gray-800 mb-4 flex items-center">
              <span class="mr-2">🎤</span>
              人声类型
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div
                v-for="vocal in vocalTypes"
                :key="vocal.id"
                class="p-4 rounded-2xl cursor-pointer transition-all text-center"
                :class="createStore.nurseryRhymeParams.vocalType === vocal.id
                  ? 'bg-gradient-to-br from-pink-100 to-rose-100 border-2 border-pink-400'
                  : 'bg-white/80 border border-gray-200 hover:shadow-sm'"
                @click="createStore.nurseryRhymeParams.vocalType = vocal.id"
              >
                <span class="text-2xl">{{ vocal.icon }}</span>
                <p class="font-medium text-gray-800 mt-2">{{ vocal.name }}</p>
              </div>
            </div>
          </div>

          <!-- 高级设置 -->
          <NurseryRhymeAdvanced
            :params="advancedParams"
            @update="handleAdvancedUpdate"
            @update-array="handleAdvancedArrayUpdate"
          />
        </div>

        <!-- 步骤 3：确认创作 -->
        <div v-else-if="createStore.currentStep === 3">
          <h2 class="text-xl font-bold text-gray-800 mb-6">确认创作参数</h2>

          <div class="space-y-4">
            <!-- 基础信息 -->
            <div class="bg-gradient-to-r from-pink-50 to-rose-50 rounded-2xl p-4">
              <h3 class="font-medium text-gray-800 mb-3">🎵 基础信息</h3>
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">创作模式：</span>
                  <span class="text-gray-800">
                    {{ createStore.nurseryRhymeParams.creationMode === 'preset' ? '🎶 预设主题' : '✨ 智能创作' }}
                  </span>
                </div>
                <div v-if="createStore.nurseryRhymeParams.creationMode === 'preset'">
                  <span class="text-gray-500">主题：</span>
                  <span class="text-gray-800">{{ selectedThemeName }}</span>
                </div>
                <div v-else class="col-span-2">
                  <span class="text-gray-500">创意描述：</span>
                  <span class="text-gray-800">{{ createStore.nurseryRhymeParams.customPrompt }}</span>
                </div>
                <div>
                  <span class="text-gray-500">情绪：</span>
                  <span class="text-gray-800">{{ selectedMoodName }}</span>
                </div>
                <div>
                  <span class="text-gray-500">节奏：</span>
                  <span class="text-gray-800">{{ createStore.nurseryRhymeParams.tempo }} BPM</span>
                </div>
                <div>
                  <span class="text-gray-500">时长：</span>
                  <span class="text-gray-800">{{ createStore.nurseryRhymeParams.durationPreference }}秒</span>
                </div>
                <div>
                  <span class="text-gray-500">人声：</span>
                  <span class="text-gray-800">{{ selectedVocalName }}</span>
                </div>
              </div>
            </div>

            <!-- 高级设置摘要 -->
            <div v-if="advancedSettingsTags.length > 0" class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-4">
              <h3 class="font-medium text-gray-800 mb-3">⚙️ 高级设置</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="tag in advancedSettingsTags"
                  :key="tag"
                  class="px-3 py-1 bg-white/80 rounded-full text-sm text-gray-700"
                >
                  {{ tag }}
                </span>
              </div>
            </div>

            <!-- 生成提示 -->
            <div class="bg-blue-50 rounded-2xl p-4">
              <p class="text-sm text-blue-700">
                <span class="font-medium">提示：</span>
                AI 将根据以上参数为您生成专属儿歌，生成过程约需 1-3 分钟，请耐心等待。
              </p>
            </div>
          </div>
        </div>

        <!-- 步骤 4：生成中 -->
        <div v-else-if="createStore.currentStep === 4">
          <div class="text-center py-12">
            <div class="text-6xl mb-4 animate-bounce">🎶</div>
            <p class="text-gray-500">AI 正在创作专属儿歌...</p>
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
            :disabled="!canNextStep"
            class="px-8 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            @click="nextStep"
          >
            下一步 →
          </button>
          <button
            v-else-if="createStore.currentStep === 2"
            class="px-8 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl transition-all"
            @click="nextStep"
          >
            下一步 →
          </button>
          <button
            v-else-if="createStore.currentStep === 3"
            class="px-8 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl transition-all"
            @click="startGenerate"
          >
            🎵 开始创作
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
      content-type="nursery_rhyme"
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
import GeneratingModal from '@/components/create/GeneratingModal.vue'
import NurseryRhymeAdvanced from '@/components/create/NurseryRhymeAdvanced.vue'

const router = useRouter()
const childStore = useChildStore()
const createStore = useCreateStore()

const steps = ['选择灵感', '音乐参数', '确认创作', '生成中']

const vocalTypes = [
  { id: 'soft_female', name: '温柔女声', icon: '👩' },
  { id: 'warm_male', name: '温暖男声', icon: '👨' },
  { id: 'child', name: '童声', icon: '👧' },
  { id: 'chorus', name: '合唱', icon: '👥' },
  { id: 'duet', name: '对唱', icon: '👫' },
  { id: 'instrumental', name: '纯音乐', icon: '🎹' }
]

// 高级参数映射
const advancedParams = computed(() => ({
  musicGenre: createStore.nurseryRhymeParams.musicGenre,
  energyLevel: createStore.nurseryRhymeParams.energyLevel,
  vocalRange: createStore.nurseryRhymeParams.vocalRange,
  vocalEmotion: createStore.nurseryRhymeParams.vocalEmotion,
  vocalStyle: createStore.nurseryRhymeParams.vocalStyle,
  instruments: createStore.nurseryRhymeParams.instruments,
  lyricComplexity: createStore.nurseryRhymeParams.lyricComplexity,
  repetitionLevel: createStore.nurseryRhymeParams.repetitionLevel,
  songStructure: createStore.nurseryRhymeParams.songStructure,
  actionTypes: createStore.nurseryRhymeParams.actionTypes,
  language: createStore.nurseryRhymeParams.language,
  culturalStyle: createStore.nurseryRhymeParams.culturalStyle,
  styleWeight: createStore.nurseryRhymeParams.styleWeight,
  creativity: createStore.nurseryRhymeParams.creativity
}))

// 显示名称计算
const selectedThemeName = computed(() => {
  if (!createStore.themes || !createStore.nurseryRhymeParams.themeCategory) return ''
  const category = createStore.themes[createStore.nurseryRhymeParams.themeCategory]
  const theme = category?.themes?.find(t => t.id === createStore.nurseryRhymeParams.themeTopic)
  return theme?.name || createStore.nurseryRhymeParams.themeTopic
})

const selectedMoodName = computed(() => {
  const mood = createStore.styleOptions?.music_moods?.find(
    m => m.id === createStore.nurseryRhymeParams.musicMood
  )
  return mood?.name || createStore.nurseryRhymeParams.musicMood
})

const selectedVocalName = computed(() => {
  const vocal = vocalTypes.find(v => v.id === createStore.nurseryRhymeParams.vocalType)
  return vocal?.name || createStore.nurseryRhymeParams.vocalType
})

// 高级设置标签
const advancedSettingsTags = computed(() => {
  const tags: string[] = []
  const params = createStore.nurseryRhymeParams

  // 音乐流派
  const genreMap: Record<string, string> = {
    nursery_folk: '民谣童谣',
    pop_kids: '流行童歌',
    classical_kids: '古典童乐',
    electronic_kids: '电子童趣',
    jazz_kids: '爵士童韵',
    world_music: '世界音乐'
  }
  if (params.musicGenre && genreMap[params.musicGenre]) {
    tags.push(genreMap[params.musicGenre])
  }

  // 音域
  const rangeMap: Record<string, string> = {
    soprano: '高音',
    mezzo: '中音',
    alto: '低音'
  }
  if (params.vocalRange && rangeMap[params.vocalRange]) {
    tags.push(rangeMap[params.vocalRange])
  }

  // 演唱技巧
  const styleMap: Record<string, string> = {
    clear: '清晰',
    breathy: '轻柔',
    vibrato: '颤音',
    whisper: '轻声'
  }
  if (params.vocalStyle && styleMap[params.vocalStyle]) {
    tags.push(styleMap[params.vocalStyle])
  }

  // 乐器
  if (params.instruments.length > 0) {
    tags.push(`${params.instruments.length}种乐器`)
  }

  // 歌曲结构
  const structureMap: Record<string, string> = {
    simple: 'A-A-A 简单重复',
    verse_chorus: 'A-B-A-B 主副歌',
    aaba: 'A-A-B-A 经典结构',
    through: 'A-B-C-D 通篇发展'
  }
  if (params.songStructure && structureMap[params.songStructure]) {
    tags.push(structureMap[params.songStructure])
  }

  // 动作指引
  const actionMap: Record<string, string> = {
    clap: '拍手',
    dance: '跳舞',
    finger: '手指游戏'
  }
  if (params.actionTypes && actionMap[params.actionTypes]) {
    tags.push(actionMap[params.actionTypes])
  }

  // 文化风格
  const cultureMap: Record<string, string> = {
    chinese_folk: '中国民谣',
    western_nursery: '西方童谣',
    japanese_style: '日式童歌',
    korean_style: '韩式童歌',
    modern_fusion: '现代融合'
  }
  if (params.culturalStyle && cultureMap[params.culturalStyle]) {
    tags.push(cultureMap[params.culturalStyle])
  }

  // 创意调节
  if (params.styleWeight !== 0.5) {
    tags.push(`风格权重${Math.round(params.styleWeight * 100)}%`)
  }
  if (params.creativity !== 0.5) {
    tags.push(`创意程度${Math.round(params.creativity * 100)}%`)
  }

  return tags
})

// 儿歌灵感标签分类（8类共80个）
const inspirationCategories = [
  {
    id: 'habit',
    name: '生活习惯',
    icon: '🏠',
    tags: [
      { icon: '🦷', text: '刷牙歌', prompt: '欢快节奏教小朋友正确刷牙，上刷刷下刷刷里刷刷外刷刷' },
      { icon: '🧼', text: '洗手歌', prompt: '搓搓手心搓搓手背，七步洗手法变成朗朗上口的旋律' },
      { icon: '🍚', text: '吃饭歌', prompt: '鼓励宝宝自己吃饭，不挑食营养好，身体棒棒' },
      { icon: '😴', text: '睡觉歌', prompt: '温柔摇篮曲，月亮星星伴入眠' },
      { icon: '🧺', text: '穿衣歌', prompt: '教宝宝自己穿衣服的步骤，伸胳膊套衣袖' },
      { icon: '🚽', text: '如厕歌', prompt: '轻松活泼的如厕训练歌，告别纸尿裤' },
      { icon: '🧹', text: '收拾歌', prompt: '玩具回家歌，培养收拾整理好习惯' },
      { icon: '👋', text: '礼貌歌', prompt: '早上好、谢谢你、对不起，礼貌用语唱出来' },
      { icon: '⏰', text: '作息歌', prompt: '太阳起床我起床，月亮睡觉我睡觉' },
      { icon: '🚶', text: '走路歌', prompt: '小脚丫走路歌，一步一步向前走' }
    ]
  },
  {
    id: 'emotion',
    name: '情感表达',
    icon: '💕',
    tags: [
      { icon: '💗', text: '我爱妈妈', prompt: '表达对妈妈的爱，妈妈的爱像阳光温暖' },
      { icon: '💙', text: '我爱爸爸', prompt: '爸爸是超人，爸爸的肩膀最宽广' },
      { icon: '👨‍👩‍👧', text: '全家福', prompt: '唱出家庭成员，爷爷奶奶爸爸妈妈和我' },
      { icon: '🤗', text: '抱抱歌', prompt: '想要抱抱的时候就大声说出来' },
      { icon: '😊', text: '开心歌', prompt: '开心的时候可以笑哈哈唱出来' },
      { icon: '😢', text: '不哭歌', prompt: '安慰情绪的歌曲，哭完擦干眼泪' },
      { icon: '🫂', text: '好朋友', prompt: '你是我的好朋友，我们一起手拉手' },
      { icon: '💝', text: '分享歌', prompt: '分享让快乐变两倍，好东西和朋友一起' },
      { icon: '🙏', text: '感谢歌', prompt: '感谢爸妈感谢老师感谢朋友' },
      { icon: '🌈', text: '勇气歌', prompt: '我很勇敢我不怕，困难来了打败它' }
    ]
  },
  {
    id: 'cognitive',
    name: '认知启蒙',
    icon: '🧒',
    tags: [
      { icon: '🔢', text: '数字歌', prompt: '一二三四五，上山打老虎风格的数数歌' },
      { icon: '🔤', text: '字母歌', prompt: 'ABC字母歌，配合简单英文单词' },
      { icon: '🎨', text: '颜色歌', prompt: '红橙黄绿蓝靛紫，七彩颜色唱出来' },
      { icon: '🔷', text: '形状歌', prompt: '圆圆的太阳方方的窗，认识各种形状' },
      { icon: '🐕', text: '动物叫', prompt: '小狗汪汪小猫喵，各种动物怎么叫' },
      { icon: '🚗', text: '交通工具', prompt: '汽车嘀嘀火车呜呜，各种交通工具声音' },
      { icon: '🍎', text: '水果歌', prompt: '苹果红香蕉黄，各种水果甜又香' },
      { icon: '🥕', text: '蔬菜歌', prompt: '胡萝卜青菜西红柿，蔬菜营养要多吃' },
      { icon: '👆', text: '身体歌', prompt: '头肩膀膝脚趾，认识自己身体部位' },
      { icon: '📅', text: '星期歌', prompt: '星期一到星期天，一周七天要记全' }
    ]
  },
  {
    id: 'action',
    name: '动作律动',
    icon: '🏃',
    tags: [
      { icon: '👏', text: '拍手歌', prompt: '跟着节奏拍拍手，拍拍头拍拍肩' },
      { icon: '🦶', text: '跺脚歌', prompt: '小脚丫跺一跺，左跺跺右跺跺' },
      { icon: '🙆', text: '伸懒腰', prompt: '早上起床伸懒腰，扭扭脖子踢踢腿' },
      { icon: '🤸', text: '做操歌', prompt: '一二三四五六七八，跟着音乐做早操' },
      { icon: '💃', text: '转圈歌', prompt: '转呀转呀转圈圈，像陀螺一样转' },
      { icon: '🐰', text: '蹦蹦跳', prompt: '像小兔子一样蹦蹦跳跳' },
      { icon: '🦆', text: '摇摆歌', prompt: '像小鸭子一样摇摇摆摆走' },
      { icon: '✋', text: '手指歌', prompt: '大拇哥二拇弟，手指家族做游戏' },
      { icon: '🤜', text: '打拳歌', prompt: '小拳头左打打右打打，运动身体好' },
      { icon: '🚶‍♂️', text: '踏步歌', prompt: '一二一一二一，齐步走向前进' }
    ]
  },
  {
    id: 'nature',
    name: '自然万物',
    icon: '🌿',
    tags: [
      { icon: '☀️', text: '太阳歌', prompt: '太阳公公起得早，照亮大地暖洋洋' },
      { icon: '🌙', text: '月亮歌', prompt: '弯弯的月亮像小船，挂在天边亮晶晶' },
      { icon: '⭐', text: '星星歌', prompt: '一闪一闪亮晶晶，满天都是小星星' },
      { icon: '🌧️', text: '下雨歌', prompt: '滴答滴答下雨啦，小雨点落下来' },
      { icon: '🌈', text: '彩虹歌', prompt: '雨后彩虹真美丽，红橙黄绿青蓝紫' },
      { icon: '🌸', text: '花朵歌', prompt: '春天花儿开，红的黄的紫的白' },
      { icon: '🦋', text: '蝴蝶歌', prompt: '蝴蝶蝴蝶真美丽，飞来飞去花丛里' },
      { icon: '🐦', text: '小鸟歌', prompt: '小鸟小鸟叽叽叫，一早起来把歌唱' },
      { icon: '🌊', text: '大海歌', prompt: '大海大海蓝蓝的，浪花朵朵向我来' },
      { icon: '🍃', text: '风儿歌', prompt: '风儿风儿轻轻吹，树叶沙沙在跳舞' }
    ]
  },
  {
    id: 'festival',
    name: '节日庆祝',
    icon: '🎉',
    tags: [
      { icon: '🧧', text: '新年歌', prompt: '过新年真热闹，穿新衣戴新帽放鞭炮' },
      { icon: '🥮', text: '中秋歌', prompt: '八月十五月儿圆，一家团圆吃月饼' },
      { icon: '🐲', text: '端午歌', prompt: '五月五端午节，划龙舟吃粽子' },
      { icon: '🏮', text: '元宵歌', prompt: '正月十五闹元宵，花灯高高挂' },
      { icon: '🎂', text: '生日歌', prompt: '祝你生日快乐，许个愿望吹蜡烛' },
      { icon: '👩‍🏫', text: '教师节歌', prompt: '老师老师我爱你，教我知识教我道理' },
      { icon: '💐', text: '母亲节歌', prompt: '我的好妈妈，下班回到家，我给您倒杯茶' },
      { icon: '👔', text: '父亲节歌', prompt: '我的好爸爸，工作回到家，我给您捶捶背' },
      { icon: '🎄', text: '圣诞歌', prompt: '铃儿响叮当，快乐圣诞节分享礼物' },
      { icon: '🏳️', text: '国庆歌', prompt: '祖国妈妈生日到，我们一起庆祝她' }
    ]
  },
  {
    id: 'roleplay',
    name: '角色扮演',
    icon: '🎭',
    tags: [
      { icon: '👨‍⚕️', text: '小医生', prompt: '我是小医生，听诊器挂胸前' },
      { icon: '👨‍🍳', text: '小厨师', prompt: '我是小厨师，围裙系身上炒菜香' },
      { icon: '👮', text: '小警察', prompt: '我是小警察，指挥交通保平安' },
      { icon: '👨‍🚒', text: '消防员', prompt: '我是消防员，灭火救人冲在前' },
      { icon: '🧑‍🚀', text: '宇航员', prompt: '我是宇航员，飞上太空看星星' },
      { icon: '👸', text: '小公主', prompt: '我是小公主，穿着裙子转圈圈' },
      { icon: '🦸', text: '小超人', prompt: '我是小超人，帮助别人我最行' },
      { icon: '🧚', text: '小仙女', prompt: '我是小仙女，挥动魔法棒' },
      { icon: '🤴', text: '小王子', prompt: '我是小王子，勇敢善良有礼貌' },
      { icon: '🧙', text: '魔法师', prompt: '我是魔法师，变出惊喜送给你' }
    ]
  },
  {
    id: 'sleep',
    name: '睡前安抚',
    icon: '🌙',
    tags: [
      { icon: '💤', text: '晚安歌', prompt: '宝贝晚安，月亮婆婆陪你睡' },
      { icon: '🌟', text: '数星星', prompt: '一颗两颗三颗星，数着星星入梦乡' },
      { icon: '🐑', text: '数绵羊', prompt: '一只羊两只羊，数着绵羊睡觉觉' },
      { icon: '🧸', text: '抱抱熊', prompt: '抱着我的小熊熊，甜甜入睡到天明' },
      { icon: '🌛', text: '月亮船', prompt: '弯弯月亮是小船，载着宝宝梦里玩' },
      { icon: '☁️', text: '云朵床', prompt: '躺在软软云朵上，做个美梦到天亮' },
      { icon: '🎐', text: '风铃声', prompt: '叮叮当当风铃响，伴你入睡香又甜' },
      { icon: '🦉', text: '猫头鹰', prompt: '猫头鹰轻轻叫，森林静悄悄睡觉了' },
      { icon: '🌺', text: '梦花园', prompt: '梦里有个花园，开满鲜花等你玩' },
      { icon: '💫', text: '星星守护', prompt: '星星宝宝眨眼睛，守护你到天亮明' }
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

const canNextStep = computed(() => {
  if (createStore.nurseryRhymeParams.creationMode === 'preset') {
    return !!createStore.nurseryRhymeParams.themeCategory && !!createStore.nurseryRhymeParams.themeTopic
  } else {
    return !!createStore.nurseryRhymeParams.customPrompt?.trim()
  }
})

function handleAdvancedUpdate(key: string, value: any) {
  (createStore.nurseryRhymeParams as any)[key] = value
}

function handleAdvancedArrayUpdate(key: 'instruments', value: string[]) {
  createStore.nurseryRhymeParams[key] = value
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
    await createStore.generateNurseryRhyme()
  } catch (e) {
    console.error('生成儿歌失败:', e)
  }
}

function handlePlay() {
  if (createStore.generatedContentId) {
    router.push(`/play/nursery_rhyme/${createStore.generatedContentId}`)
  }
}

function handleClose() {
  createStore.resetParams('nursery_rhyme')
}

onMounted(async () => {
  createStore.resetParams('nursery_rhyme')
  await createStore.loadOptions()
})

onUnmounted(() => {
  createStore.stopPolling()
})
</script>
