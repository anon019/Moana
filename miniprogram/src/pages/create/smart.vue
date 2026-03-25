<template>
  <view class="page-container">
    <!-- 装饰背景 -->
    <view class="decor-bg">
      <view class="decor-shape shape-1"></view>
      <view class="decor-shape shape-2"></view>
    </view>

    <!-- 主内容区 -->
    <scroll-view class="main-scroll" scroll-y enhanced :show-scrollbar="false">
      <!-- 顶部返回按钮区 -->
      <view class="top-bar">
        <view class="back-btn" @tap="goBack">
          <text>&larr;</text>
        </view>
        <view class="step-indicator">
          <view
            v-for="i in 3"
            :key="i"
            class="step-dot"
            :class="{ active: currentStep >= i, current: currentStep === i }"
          ></view>
        </view>
      </view>

      <!-- 页面标题区 -->
      <view class="header-section">
        <view class="header-badge">
          <text class="badge-icon">🔮</text>
          <text class="badge-text">智能创作</text>
        </view>
        <text class="header-title">{{ stepTitles[currentStep - 1] }}</text>
        <text class="header-desc">{{ stepDescs[currentStep - 1] }}</text>
      </view>

      <!-- Step 1: 输入创意描述 -->
      <view v-show="currentStep === 1" class="step-content">
        <view class="input-section">
          <view class="input-container">
            <textarea
              v-model="customPrompt"
              class="prompt-input"
              placeholder="描述你想要创作的内容..."
              :maxlength="500"
              auto-height
              :focus="currentStep === 1"
            />
            <view class="input-footer">
              <text class="char-count">{{ customPrompt.length }}/500</text>
            </view>
          </view>

          <!-- 灵感标签 -->
          <view class="inspiration-section">
            <text class="section-label">快捷灵感</text>
            <view class="inspiration-tags">
              <view
                v-for="(tag, index) in inspirationTags"
                :key="index"
                class="tag-item"
                @tap="fillInspiration(tag)"
              >
                <text class="tag-emoji">{{ tag.emoji }}</text>
                <text class="tag-text">{{ tag.label }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="step-actions">
          <view
            class="next-btn"
            :class="{ disabled: !customPrompt.trim() }"
            @tap="goToStep(2)"
          >
            <text>下一步：选择内容类型</text>
            <text class="btn-arrow">&rarr;</text>
          </view>
        </view>
      </view>

      <!-- Step 2: 选择内容类型 -->
      <view v-show="currentStep === 2" class="step-content">
        <view class="type-selection">
          <view
            v-for="type in contentTypes"
            :key="type.id"
            class="type-card"
            :class="{ selected: selectedType === type.id }"
            @tap="selectType(type.id)"
          >
            <view class="type-icon-wrap">
              <text class="type-icon">{{ type.icon }}</text>
            </view>
            <view class="type-info">
              <text class="type-name">{{ type.name }}</text>
              <text class="type-desc">{{ type.description }}</text>
            </view>
            <view class="type-check" v-if="selectedType === type.id">
              <text>✓</text>
            </view>
          </view>

          <!-- 视频子选项 -->
          <view v-if="selectedType === 'video'" class="video-mode-section">
            <text class="section-label">视频创作模式</text>
            <view class="video-modes">
              <view
                v-for="mode in videoModes"
                :key="mode.id"
                class="mode-option"
                :class="{ selected: selectedVideoMode === mode.id }"
                @tap="selectedVideoMode = mode.id"
              >
                <view class="mode-radio">
                  <view v-if="selectedVideoMode === mode.id" class="radio-inner"></view>
                </view>
                <view class="mode-content">
                  <text class="mode-name">{{ mode.name }}</text>
                  <text class="mode-desc">{{ mode.description }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view class="step-actions">
          <view class="prev-btn" @tap="goToStep(1)">
            <text class="btn-arrow">&larr;</text>
            <text>上一步</text>
          </view>
          <view
            class="next-btn"
            :class="{ disabled: !selectedType }"
            @tap="goToStep(3)"
          >
            <text>下一步：高级设置</text>
            <text class="btn-arrow">&rarr;</text>
          </view>
        </view>
      </view>

      <!-- Step 3: 高级设置 & 确认创作 -->
      <view v-show="currentStep === 3" class="step-content">
        <!-- 创作预览 -->
        <view class="preview-section">
          <view class="preview-card">
            <view class="preview-header">
              <text class="preview-type-icon">{{ getTypeIcon(selectedType) }}</text>
              <text class="preview-type-name">{{ getTypeName(selectedType) }}</text>
            </view>
            <view class="preview-prompt">
              <text>"{{ customPrompt }}"</text>
            </view>
          </view>
        </view>

        <!-- 绘本设置 -->
        <view v-if="selectedType === 'picture_book'" class="style-sections">
          <!-- 艺术风格 - 分类展示 -->
          <view class="style-section art-section">
            <view class="section-header">
              <view class="section-icon-wrap">
                <text class="section-icon">🎨</text>
              </view>
              <text class="section-title">艺术风格</text>
            </view>
            <!-- 风格分类 Tab -->
            <view class="style-category-tabs">
              <view
                v-for="cat in styleCategories"
                :key="cat.id"
                class="style-tab-item"
                :class="{ active: selectedStyleCategory === cat.id }"
                @tap="selectedStyleCategory = cat.id"
              >
                <text class="style-tab-icon">{{ cat.icon }}</text>
                <text class="style-tab-name">{{ cat.name }}</text>
              </view>
            </view>
            <!-- 风格卡片 -->
            <view class="art-style-carousel">
              <view
                v-for="style in currentCategoryStyles"
                :key="style.value"
                class="art-card"
                :class="{ selected: selectedArtStyle === style.value, recommended: style.recommended }"
                @tap="selectedArtStyle = style.value"
              >
                <view class="art-card-bg" :class="style.cssClass || style.value"></view>
                <view class="art-card-content">
                  <text class="art-icon">{{ style.icon }}</text>
                  <text class="art-name">{{ style.label }}</text>
                  <text class="art-desc">{{ style.desc }}</text>
                </view>
                <view v-if="selectedArtStyle === style.value" class="art-check">
                  <text>✓</text>
                </view>
                <view v-if="style.recommended" class="art-badge">推荐</view>
              </view>
            </view>
          </view>

          <!-- 故事主角 - 可爱动物选择 -->
          <view class="style-section character-section">
            <view class="section-header">
              <view class="section-icon-wrap bunny">
                <text class="section-icon">🐰</text>
              </view>
              <view class="section-header-text">
                <text class="section-title">故事主角</text>
                <text class="section-hint">选择陪伴宝贝的小动物</text>
              </view>
            </view>
            <view class="character-carousel">
              <view
                v-for="animal in protagonistAnimals"
                :key="animal.value"
                class="character-card"
                :class="{ selected: selectedProtagonist === animal.value }"
                @tap="selectedProtagonist = animal.value"
              >
                <!-- 选中时的背景光晕 -->
                <view class="char-glow"></view>
                <!-- 角色头像区域 -->
                <view class="character-avatar-wrap">
                  <view class="character-avatar">
                    <text class="char-emoji">{{ animal.emoji }}</text>
                  </view>
                  <!-- 选中时的星星徽章 -->
                  <view v-if="selectedProtagonist === animal.value" class="char-star">⭐</view>
                </view>
                <!-- 彩色舞台底座 -->
                <view class="char-stage"></view>
                <text class="char-name">{{ animal.label }}</text>
              </view>
            </view>
          </view>

          <!-- 旁白音色 - 音波效果 -->
          <view class="style-section voice-section">
            <view class="section-header">
              <view class="section-icon-wrap voice">
                <text class="section-icon">🔊</text>
              </view>
              <view class="section-header-text">
                <text class="section-title">旁白音色</text>
                <text class="section-hint">选择讲故事的声音</text>
              </view>
            </view>
            <view class="voice-list">
              <view
                v-for="voice in voiceOptions"
                :key="voice.id"
                class="voice-card"
                :class="{
                  selected: selectedVoice === voice.id,
                  playing: playingVoiceId === voice.id,
                  [voice.gender]: true
                }"
                @tap="selectedVoice = voice.id"
              >
                <view class="voice-avatar">
                  <text class="voice-emoji">{{ getVoiceEmoji(voice.id) }}</text>
                  <!-- 播放时显示声波动画 -->
                  <view v-if="playingVoiceId === voice.id" class="voice-waves playing">
                    <view class="wave"></view>
                    <view class="wave"></view>
                    <view class="wave"></view>
                  </view>
                </view>
                <view class="voice-content">
                  <view class="voice-name-row">
                    <text class="voice-name">{{ voice.name_cn }}</text>
                    <text class="voice-id">{{ voice.name }}</text>
                    <text v-if="voice.recommended" class="voice-badge">推荐</text>
                    <text class="voice-gender-tag" :class="voice.gender">
                      {{ voice.gender === 'female' ? '女声' : voice.gender === 'male' ? '男声' : '中性' }}
                    </text>
                  </view>
                  <view class="voice-detail-row">
                    <text class="voice-detail-label">🎯</text>
                    <text class="voice-detail-text">{{ getVoiceDesc(voice.id).scenes }}</text>
                  </view>
                  <view class="voice-detail-row">
                    <text class="voice-detail-label">📚</text>
                    <text class="voice-detail-text">{{ getVoiceDesc(voice.id).stories }}</text>
                  </view>
                </view>
                <!-- 试听按钮 -->
                <view
                  class="voice-preview-btn"
                  :class="{ loading: loadingVoiceId === voice.id }"
                  @tap.stop="previewVoice(voice.id)"
                >
                  <text v-if="loadingVoiceId === voice.id" class="preview-icon">⏳</text>
                  <text v-else-if="playingVoiceId === voice.id" class="preview-icon playing">⏹</text>
                  <text v-else class="preview-icon">▶</text>
                </view>
                <view v-if="selectedVoice === voice.id" class="voice-check">
                  <text>✓</text>
                </view>
              </view>
            </view>
          </view>

          <!-- 故事风格面板 -->
          <view class="enhancement-panel" :class="{ expanded: storyPanelExpanded }">
            <view class="panel-header" @tap="storyPanelExpanded = !storyPanelExpanded">
              <view class="panel-header-left">
                <view class="panel-icon-wrap story">
                  <text class="panel-icon">📖</text>
                </view>
                <view class="panel-header-text">
                  <text class="panel-title">故事风格</text>
                  <text class="panel-hint">{{ storyEnhancementSummary }}</text>
                </view>
              </view>
              <view class="panel-arrow" :class="{ expanded: storyPanelExpanded }">
                <text>›</text>
              </view>
            </view>
            <view class="panel-content" :class="{ expanded: storyPanelExpanded }">
              <!-- 叙事节奏 -->
              <view class="enhancement-group">
                <text class="group-label">叙事节奏</text>
                <view class="option-cards">
                  <view
                    v-for="opt in narrativePaceOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: storyEnhancement.narrative_pace === opt.value }"
                    @tap="toggleStoryOption('narrative_pace', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
              <!-- 互动密度 -->
              <view class="enhancement-group">
                <text class="group-label">互动密度</text>
                <view class="option-cards">
                  <view
                    v-for="opt in interactionDensityOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: storyEnhancement.interaction_density === opt.value }"
                    @tap="toggleStoryOption('interaction_density', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
              <!-- 教育侧重 -->
              <view class="enhancement-group">
                <text class="group-label">教育侧重</text>
                <view class="option-cards">
                  <view
                    v-for="opt in educationalFocusOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: storyEnhancement.educational_focus === opt.value }"
                    @tap="toggleStoryOption('educational_focus', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
              <!-- 语言风格 -->
              <view class="enhancement-group">
                <text class="group-label">语言风格</text>
                <view class="option-cards">
                  <view
                    v-for="opt in languageStyleOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: storyEnhancement.language_style === opt.value }"
                    @tap="toggleStoryOption('language_style', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
              <!-- 情节复杂度 -->
              <view class="enhancement-group">
                <text class="group-label">情节复杂度</text>
                <view class="option-cards">
                  <view
                    v-for="opt in plotComplexityOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: storyEnhancement.plot_complexity === opt.value }"
                    @tap="toggleStoryOption('plot_complexity', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
              <!-- 结局风格 -->
              <view class="enhancement-group">
                <text class="group-label">结局风格</text>
                <view class="option-cards">
                  <view
                    v-for="opt in endingStyleOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: storyEnhancement.ending_style === opt.value }"
                    @tap="toggleStoryOption('ending_style', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>

          <!-- 画面设置面板 -->
          <view class="enhancement-panel" :class="{ expanded: visualPanelExpanded }">
            <view class="panel-header" @tap="visualPanelExpanded = !visualPanelExpanded">
              <view class="panel-header-left">
                <view class="panel-icon-wrap visual">
                  <text class="panel-icon">🎬</text>
                </view>
                <view class="panel-header-text">
                  <text class="panel-title">画面设置</text>
                  <text class="panel-hint">{{ visualEnhancementSummary }}</text>
                </view>
              </view>
              <view class="panel-arrow" :class="{ expanded: visualPanelExpanded }">
                <text>›</text>
              </view>
            </view>
            <view class="panel-content" :class="{ expanded: visualPanelExpanded }">
              <!-- 时间氛围 -->
              <view class="enhancement-group">
                <text class="group-label">时间氛围</text>
                <view class="option-cards">
                  <view
                    v-for="opt in timeAtmosphereOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: visualEnhancement.time_atmosphere === opt.value }"
                    @tap="toggleVisualOption('time_atmosphere', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
              <!-- 场景环境 -->
              <view class="enhancement-group">
                <text class="group-label">场景环境</text>
                <view class="option-cards">
                  <view
                    v-for="opt in sceneEnvironmentOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: visualEnhancement.scene_environment === opt.value }"
                    @tap="toggleVisualOption('scene_environment', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
              <!-- 情感基调 -->
              <view class="enhancement-group">
                <text class="group-label">情感基调</text>
                <view class="option-cards">
                  <view
                    v-for="opt in emotionalToneOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: visualEnhancement.emotional_tone === opt.value }"
                    @tap="toggleVisualOption('emotional_tone', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
              <!-- 画面构图 -->
              <view class="enhancement-group">
                <text class="group-label">画面构图</text>
                <view class="option-cards">
                  <view
                    v-for="opt in compositionStyleOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: visualEnhancement.composition_style === opt.value }"
                    @tap="toggleVisualOption('composition_style', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
              <!-- 光照效果 -->
              <view class="enhancement-group">
                <text class="group-label">光照效果</text>
                <view class="option-cards">
                  <view
                    v-for="opt in lightingEffectOptions"
                    :key="opt.value"
                    class="option-card"
                    :class="{ selected: visualEnhancement.lighting_effect === opt.value }"
                    @tap="toggleVisualOption('lighting_effect', opt.value)"
                  >
                    <text class="option-emoji">{{ opt.emoji }}</text>
                    <text class="option-label">{{ opt.label }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 儿歌高级设置组件 -->
        <view v-if="selectedType === 'nursery_rhyme'">
          <NurseryRhymeAdvanced
            :model-value="nurseryRhymeAdvancedParams"
            @update:model-value="onNurseryRhymeAdvancedUpdate"
          />
        </view>

        <!-- 视频高级设置（暂时保留简化版，可以后续扩展） -->
        <view v-if="selectedType === 'video'" class="advanced-section">
          <view class="advanced-header" @tap="showAdvanced = !showAdvanced">
            <text class="advanced-title">高级设置</text>
            <text class="advanced-toggle">{{ showAdvanced ? '收起' : '展开' }}</text>
          </view>

          <view v-show="showAdvanced" class="advanced-content">
            <!-- 视频时长 -->
            <view v-if="selectedVideoMode === 'standalone'" class="setting-group">
              <text class="setting-label">视频时长</text>
              <view class="duration-options">
                <view
                  v-for="d in [5, 6, 8]"
                  :key="d"
                  class="duration-item"
                  :class="{ selected: selectedDuration === d }"
                  @tap="selectedDuration = d"
                >
                  <text>{{ d }}秒</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view class="step-actions">
          <view class="prev-btn" @tap="goToStep(2)">
            <text class="btn-arrow">&larr;</text>
            <text>上一步</text>
          </view>
          <view class="submit-btn" @tap="handleSubmit">
            <view class="btn-shine"></view>
            <view class="btn-content">
              <text class="btn-icon">✨</text>
              <text class="btn-text">开始创作</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 底部安全区 -->
      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useChildStore } from '@/stores/child'
import NurseryRhymeAdvanced from '@/components/NurseryRhymeAdvanced/NurseryRhymeAdvanced.vue'
import {
  getStyleOptions,
  getTTSVoices,
  type ArtStyle,
  type ProtagonistAnimal,
  type MusicMood,
  type VoiceId,
  type GenerateNurseryRhymeParams
} from '@/api/content'

const childStore = useChildStore()

// 步骤控制
const currentStep = ref(1)
const stepTitles = ['描述你的创意', '选择内容类型', '确认创作']
const stepDescs = [
  '告诉 AI 你想要什么样的内容',
  '选择绘本、儿歌或视频',
  '调整设置并开始创作'
]

// Step 1: 用户输入
const customPrompt = ref('')
const inspirationTags = [
  // 生活习惯 (10)
  { emoji: '🦷', label: '刷牙习惯', text: '宝宝不爱刷牙，做一个关于刷牙的有趣内容' },
  { emoji: '🥦', label: '爱吃蔬菜', text: '宝宝挑食不吃蔬菜，帮我做一个关于蔬菜的故事' },
  { emoji: '🛏', label: '早睡早起', text: '宝宝晚上不愿意睡觉，需要一个睡前故事' },
  { emoji: '🚿', label: '洗澡洗手', text: '教宝宝养成爱干净的好习惯' },
  { emoji: '🧹', label: '整理玩具', text: '教宝宝玩完玩具后要自己整理收拾' },
  { emoji: '👕', label: '自己穿衣', text: '帮助宝宝学会自己穿衣服和鞋子' },
  { emoji: '🍽', label: '好好吃饭', text: '宝宝吃饭不专心，需要培养好好吃饭的习惯' },
  { emoji: '💧', label: '多喝水', text: '教宝宝养成多喝水的好习惯' },
  { emoji: '⚽', label: '爱运动', text: '鼓励宝宝多做户外运动和锻炼' },
  { emoji: '🚦', label: '交通安全', text: '教宝宝过马路要看红绿灯，遵守交通规则' },

  // 社交情感 (10)
  { emoji: '💬', label: '礼貌用语', text: '教宝宝说请、谢谢、对不起等礼貌用语' },
  { emoji: '🖐', label: '学会分享', text: '宝宝不愿意和小朋友分享玩具' },
  { emoji: '👭', label: '交朋友', text: '帮助宝宝学会和其他小朋友交朋友' },
  { emoji: '😌', label: '情绪管理', text: '宝宝容易发脾气，教他管理情绪' },
  { emoji: '💝', label: '同理心', text: '培养宝宝理解和关心他人感受的能力' },
  { emoji: '🙏', label: '学会道歉', text: '教宝宝做错事要勇敢道歉' },
  { emoji: '⏰', label: '学会等待', text: '培养宝宝的耐心，学会等待和排队' },
  { emoji: '🎯', label: '轮流游戏', text: '教宝宝玩游戏要学会轮流和遵守规则' },
  { emoji: '🤝', label: '互相帮助', text: '鼓励宝宝帮助别人，培养助人为乐的品质' },
  { emoji: '👨‍👩‍👧', label: '团队合作', text: '教宝宝和其他小朋友一起合作完成任务' },

  // 认知学习 (10)
  { emoji: '🌈', label: '认识颜色', text: '教宝宝认识和区分不同的颜色' },
  { emoji: '⭐', label: '认识形状', text: '帮助宝宝学会辨认圆形、方形、三角形等形状' },
  { emoji: '🔢', label: '学习数字', text: '用有趣的方式教宝宝认识数字和数数' },
  { emoji: '🔤', label: '认识字母', text: '教宝宝认识和记忆英文字母' },
  { emoji: '🦁', label: '认识动物', text: '教宝宝认识各种动物及它们的特点' },
  { emoji: '🌳', label: '认识植物', text: '带宝宝认识花草树木和大自然' },
  { emoji: '☀️', label: '天气变化', text: '教宝宝认识晴天、雨天、雪天等天气' },
  { emoji: '🍂', label: '四季变换', text: '帮助宝宝理解春夏秋冬的变化' },
  { emoji: '⌚', label: '时间概念', text: '教宝宝认识时间和时钟' },
  { emoji: '📍', label: '方位认知', text: '教宝宝理解上下左右前后等方位' },

  // 品德教育 (10)
  { emoji: '✨', label: '诚实守信', text: '教宝宝做一个诚实不说谎的好孩子' },
  { emoji: '🦸', label: '勇敢坚强', text: '培养宝宝勇敢面对困难的品质' },
  { emoji: '💪', label: '自信独立', text: '帮助宝宝建立自信心，学会独立' },
  { emoji: '🎨', label: '耐心专注', text: '培养宝宝做事专心、有耐心的习惯' },
  { emoji: '🙏', label: '感恩之心', text: '教宝宝学会感恩父母和他人的付出' },
  { emoji: '📝', label: '责任担当', text: '培养宝宝的责任感，自己的事情自己做' },
  { emoji: '💰', label: '节约节俭', text: '教宝宝珍惜物品，不浪费食物和资源' },
  { emoji: '❤️', label: '爱心善良', text: '培养宝宝有爱心，善待小动物和他人' },
  { emoji: '⏱', label: '守时守约', text: '教宝宝遵守时间约定，不迟到' },
  { emoji: '🎖', label: '尊重他人', text: '教宝宝尊重长辈和其他小朋友' },

  // 安全知识 (10)
  { emoji: '🚸', label: '陌生人', text: '教宝宝如何应对陌生人，不跟陌生人走' },
  { emoji: '🔥', label: '火灾逃生', text: '教宝宝火灾时如何保护自己，正确逃生' },
  { emoji: '🏊', label: '防溺水', text: '教宝宝远离危险水域，学会保护自己' },
  { emoji: '⚡', label: '用电安全', text: '教宝宝不乱摸电器插座，注意用电安全' },
  { emoji: '🤕', label: '防跌倒', text: '教宝宝走路注意安全，避免跌倒受伤' },
  { emoji: '🗺', label: '不走丢', text: '教宝宝如果和爸妈走散了该怎么办' },
  { emoji: '📱', label: '网络安全', text: '教宝宝安全使用电子设备，保护个人信息' },
  { emoji: '🐕', label: '动物安全', text: '教宝宝如何安全地接触小动物，避免被咬伤' },
  { emoji: '🏥', label: '紧急求助', text: '教宝宝记住父母电话，遇到危险会求助' },
  { emoji: '🧯', label: '防烫伤', text: '教宝宝远离热水、热汤等，避免烫伤' }
]

// Step 2: 内容类型选择
const selectedType = ref<'picture_book' | 'nursery_rhyme' | 'video' | ''>('')
const contentTypes = [
  { id: 'picture_book', icon: '📚', name: 'AI 绘本', description: '个性化故事配精美插画' },
  { id: 'nursery_rhyme', icon: '🎵', name: 'AI 儿歌', description: '原创旋律专属歌词' },
  { id: 'video', icon: '🎬', name: 'AI 视频', description: '动态视频内容' }
]

const selectedVideoMode = ref<'from_book' | 'standalone'>('standalone')
const videoModes = [
  { id: 'standalone', name: '独立创作', description: '根据描述直接生成视频' },
  { id: 'from_book', name: '基于绘本', description: '先创作绘本，再生成视频' }
]

// Step 3: 高级设置
const showAdvanced = ref(false)
const selectedArtStyle = ref<ArtStyle>('pixar_3d')
const selectedProtagonist = ref<ProtagonistAnimal>('bunny')
const selectedVoice = ref<VoiceId>('Cherry')
const selectedMood = ref<MusicMood>('cheerful')
const selectedDuration = ref(5)

// 绘本高级设置 - 故事风格
interface StoryEnhancement {
  narrative_pace: string | null
  interaction_density: string | null
  educational_focus: string | null
  language_style: string | null
  plot_complexity: string | null
  ending_style: string | null
}

const storyPanelExpanded = ref(false)
const storyEnhancement = ref<StoryEnhancement>({
  narrative_pace: null,
  interaction_density: null,
  educational_focus: null,
  language_style: null,
  plot_complexity: null,
  ending_style: null
})

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

function toggleStoryOption(key: keyof StoryEnhancement, value: string) {
  if (storyEnhancement.value[key] === value) {
    storyEnhancement.value[key] = null
  } else {
    storyEnhancement.value[key] = value
  }
}

const storyEnhancementSummary = computed(() => {
  const selected = Object.values(storyEnhancement.value).filter(v => v !== null)
  if (selected.length === 0) return '可选，由 AI 智能推断'
  return `已选 ${selected.length} 项`
})

// 绘本高级设置 - 画面设置
interface VisualEnhancement {
  time_atmosphere: string | null
  scene_environment: string | null
  emotional_tone: string | null
  composition_style: string | null
  lighting_effect: string | null
}

const visualPanelExpanded = ref(false)
const visualEnhancement = ref<VisualEnhancement>({
  time_atmosphere: null,
  scene_environment: null,
  emotional_tone: null,
  composition_style: null,
  lighting_effect: null
})

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

function toggleVisualOption(key: keyof VisualEnhancement, value: string) {
  if (visualEnhancement.value[key] === value) {
    visualEnhancement.value[key] = null
  } else {
    visualEnhancement.value[key] = value
  }
}

const visualEnhancementSummary = computed(() => {
  const selected = Object.values(visualEnhancement.value).filter(v => v !== null)
  if (selected.length === 0) return '可选，由 AI 智能推断'
  return `已选 ${selected.length} 项`
})

// 儿歌高级设置
const nurseryRhymeAdvancedParams = ref<Partial<GenerateNurseryRhymeParams>>({})

function onNurseryRhymeAdvancedUpdate(params: Partial<GenerateNurseryRhymeParams>) {
  nurseryRhymeAdvancedParams.value = params
}

// 绘本基础设置 - 故事主角
const protagonistAnimals = [
  { value: 'bunny' as ProtagonistAnimal, label: '小兔子', emoji: '🐰' },
  { value: 'bear' as ProtagonistAnimal, label: '小熊', emoji: '🐻' },
  { value: 'cat' as ProtagonistAnimal, label: '小猫咪', emoji: '🐱' },
  { value: 'dog' as ProtagonistAnimal, label: '小狗狗', emoji: '🐶' },
  { value: 'panda' as ProtagonistAnimal, label: '熊猫', emoji: '🐼' },
  { value: 'fox' as ProtagonistAnimal, label: '小狐狸', emoji: '🦊' },
  { value: 'elephant' as ProtagonistAnimal, label: '小象', emoji: '🐘' },
  { value: 'penguin' as ProtagonistAnimal, label: '企鹅', emoji: '🐧' },
  { value: 'monkey' as ProtagonistAnimal, label: '小猴子', emoji: '🐵' }
]

// 绘本基础设置 - 旁白音色
const voiceOptions = ref<any[]>([])
const playingVoiceId = ref<VoiceId | null>(null)
const loadingVoiceId = ref<VoiceId | null>(null)
const previewAudioContext = ref<UniApp.InnerAudioContext | null>(null)

const voiceEmojis: Record<string, string> = {
  Kore: '🌟',
  Leda: '🌙',
  Aoede: '☀️',
  Puck: '🎭',
  Charon: '🎸',
  Fenrir: '🦁',
  Cherry: '🍒'
}

const voiceDescMap: Record<string, { scenes: string; stories: string }> = {
  Kore: { scenes: '睡前故事、温馨场景', stories: '适合温暖治愈的绘本' },
  Leda: { scenes: '科普、自然探索', stories: '适合知识性绘本' },
  Aoede: { scenes: '冒险、探索', stories: '适合冒险类绘本' },
  Puck: { scenes: '搞笑、幽默', stories: '适合幽默搞笑绘本' },
  Charon: { scenes: '神秘、魔法', stories: '适合奇幻冒险绘本' },
  Fenrir: { scenes: '勇气、力量', stories: '适合英雄冒险绘本' },
  Cherry: { scenes: '通用场景', stories: '各类儿童故事' }
}

function getVoiceEmoji(voiceId: string): string {
  return voiceEmojis[voiceId] || '🎵'
}

function getVoiceDesc(voiceId: string): { scenes: string; stories: string } {
  return voiceDescMap[voiceId] || { scenes: '通用场景', stories: '各类故事' }
}

function selectVoice(voiceId: VoiceId) {
  selectedVoice.value = voiceId
}

function previewVoice(voiceId: VoiceId) {
  // 如果正在播放同一个，停止播放
  if (playingVoiceId.value === voiceId) {
    stopPreview()
    return
  }

  // 停止之前的播放
  stopPreview()

  loadingVoiceId.value = voiceId
  const voice = voiceOptions.value.find((v: any) => v.id === voiceId)
  if (!voice?.preview_url) {
    uni.showToast({ title: '预览暂不可用', icon: 'none' })
    loadingVoiceId.value = null
    return
  }

  const audioContext = uni.createInnerAudioContext()
  previewAudioContext.value = audioContext
  audioContext.src = voice.preview_url
  audioContext.onCanplay(() => {
    loadingVoiceId.value = null
    playingVoiceId.value = voiceId
  })
  audioContext.onEnded(() => {
    playingVoiceId.value = null
  })
  audioContext.onError((err: any) => {
    console.error('[playPreviewAudio] 播放错误:', err)
    playingVoiceId.value = null
    loadingVoiceId.value = null
    uni.showToast({ title: '播放失败', icon: 'none' })
  })
  audioContext.play()
}

function stopPreview() {
  if (previewAudioContext.value) {
    previewAudioContext.value.stop()
    previewAudioContext.value.destroy()
    previewAudioContext.value = null
  }
  playingVoiceId.value = null
}

// 加载音色选项
async function loadVoiceOptions() {
  try {
    const result = await getTTSVoices()
    const VOICE_ORDER = ['Kore', 'Leda', 'Aoede', 'Puck', 'Charon', 'Fenrir']
    if (result.providers?.length > 0) {
      const voices = result.providers[0].voices
      voiceOptions.value = voices.sort((a: any, b: any) => {
        const indexA = VOICE_ORDER.indexOf(a.id)
        const indexB = VOICE_ORDER.indexOf(b.id)
        return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB)
      })
    } else {
      voiceOptions.value = [
        { id: 'Kore' as VoiceId, name: 'Kore', name_cn: '温暖女声', gender: 'female', style: '温暖亲切', description: '适合儿童故事（推荐）', recommended: true, preview_url: 'https://your-api.example.com/media/voice-preview/gemini/Kore.wav' }
      ]
    }
  } catch (error) {
    console.error('[loadVoiceOptions] 加载音色选项失败:', error)
    voiceOptions.value = [
      { id: 'Kore' as VoiceId, name: 'Kore', name_cn: '温暖女声', gender: 'female', style: '温暖亲切', description: '适合儿童故事（推荐）', recommended: true, preview_url: 'https://your-api.example.com/media/voice-preview/gemini/Kore.wav' }
    ]
  }
}

// 风格分类（与 picture-book.vue 保持一致）
const styleCategories = [
  { id: 'threed', name: '3D 风格', icon: '🎬' },
  { id: 'illustration', name: '插画风格', icon: '📚' },
  { id: 'anime', name: '动漫风格', icon: '🌸' },
  { id: 'artistic', name: '艺术风格', icon: '🎨' },
  { id: 'craft', name: '手工风格', icon: '✂️' }
]
const selectedStyleCategory = ref('threed')

// 艺术风格选项（与 picture-book.vue 保持一致）
type StyleOption = { value: ArtStyle; label: string; icon: string; desc: string }
const artStylesByCategory: Record<string, StyleOption[]> = {
  threed: [
    { value: 'pixar_3d', label: '皮克斯3D', icon: '🧸', desc: '圆润可爱' },
    { value: 'pixar', label: '皮克斯电影', icon: '🎬', desc: '电影质感' },
    { value: 'dreamworks', label: '梦工厂', icon: '🌙', desc: '夸张活泼' },
    { value: 'disney_3d', label: '迪士尼3D', icon: '🏰', desc: '童话梦幻' },
    { value: 'clay', label: '粘土风格', icon: '🎭', desc: '定格动画' },
    { value: 'figurine', label: '手办风格', icon: '🎎', desc: '精致手办' },
    { value: 'low_poly', label: '低多边形', icon: '💎', desc: '几何简约' }
  ],
  illustration: [
    { value: 'storybook', label: '绘本风格', icon: '📖', desc: '温暖治愈' },
    { value: 'watercolor', label: '水彩风格', icon: '💧', desc: '透明梦幻' },
    { value: 'cartoon', label: '卡通风格', icon: '🎨', desc: '鲜艳明快' },
    { value: 'flat', label: '扁平风格', icon: '✨', desc: '简洁现代' },
    { value: 'crayon', label: '蜡笔风格', icon: '🖍️', desc: '童趣涂鸦' },
    { value: 'colored_pencil', label: '彩铅风格', icon: '✏️', desc: '细腻柔和' }
  ],
  anime: [
    { value: 'anime', label: '日式动漫', icon: '🌸', desc: '精致细腻' },
    { value: 'chibi', label: 'Q版萌系', icon: '🎀', desc: '大头超萌' },
    { value: 'ghibli', label: '吉卜力', icon: '🏰', desc: '宫崎骏风' },
    { value: 'shinkai', label: '新海诚', icon: '🌅', desc: '光影唯美' },
    { value: 'manga', label: '漫画风格', icon: '📔', desc: '黑白张力' },
    { value: 'comic_book', label: '美式漫画', icon: '💥', desc: '英雄风格' }
  ],
  artistic: [
    { value: 'oil_painting', label: '油画', icon: '🖼️', desc: '古典厚重' },
    { value: 'impressionist', label: '印象派', icon: '🌻', desc: '莫奈光影' },
    { value: 'sketch', label: '素描', icon: '✏️', desc: '铅笔手绘' },
    { value: 'ink_wash', label: '水墨画', icon: '🖌️', desc: '中国意境' },
    { value: 'pop_art', label: '波普艺术', icon: '🎪', desc: '大胆撞色' },
    { value: 'art_nouveau', label: '新艺术', icon: '🌿', desc: '曲线装饰' },
    { value: 'pixel_art', label: '像素艺术', icon: '👾', desc: '复古游戏' }
  ],
  craft: [
    { value: 'papercut', label: '剪纸风格', icon: '✂️', desc: '传统民间' },
    { value: 'felt_craft', label: '不织布', icon: '🧵', desc: '毛绒温暖' },
    { value: 'origami', label: '折纸风格', icon: '🦢', desc: '几何折叠' },
    { value: 'embroidery', label: '刺绣风格', icon: '🪡', desc: '精致针线' },
    { value: 'mosaic', label: '马赛克', icon: '🎨', desc: '色块拼贴' },
    { value: 'stained_glass', label: '彩色玻璃', icon: '🪟', desc: '彩窗光影' }
  ]
}

// 当前分类的风格列表
const currentCategoryStyles = computed(() => {
  return artStylesByCategory[selectedStyleCategory.value] || artStylesByCategory.threed
})

// 其他选项（从 API 加载）
const protagonists = ref<Array<{ animal: ProtagonistAnimal; name: string }>>([])
const ttsVoices = ref<Array<{ id: VoiceId; name: string; style: string }>>([])
const musicMoods = ref<Array<{ id: MusicMood; name: string }>>([])

// 页面参数
onLoad((options) => {
  if (options?.input) {
    customPrompt.value = decodeURIComponent(options.input)
  }
})

onMounted(async () => {
  try {
    const options = await getStyleOptions()
    // 艺术风格使用本地硬编码数据，不从 API 加载
    protagonists.value = options.protagonists.map(p => ({ animal: p.animal, name: p.name }))
    ttsVoices.value = options.tts_voices.map(v => ({ id: v.id, name: v.name, style: v.style }))
    musicMoods.value = options.music_moods.map(m => ({ id: m.id, name: m.name }))

    // 加载绘本音色选项
    await loadVoiceOptions()
  } catch (e) {
    console.error('加载选项失败:', e)
  }
})

function goBack() {
  if (currentStep.value > 1) {
    currentStep.value--
  } else {
    uni.navigateBack({
      fail: () => uni.switchTab({ url: '/pages/create/index' })
    })
  }
}

function goToStep(step: number) {
  if (step === 2 && !customPrompt.value.trim()) return
  if (step === 3 && !selectedType.value) return
  currentStep.value = step
}

function fillInspiration(tag: { text: string }) {
  customPrompt.value = tag.text
}

function selectType(type: 'picture_book' | 'nursery_rhyme' | 'video') {
  selectedType.value = type
}

function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    picture_book: '📚',
    nursery_rhyme: '🎵',
    video: '🎬'
  }
  return icons[type] || '✨'
}

function getTypeName(type: string): string {
  const names: Record<string, string> = {
    picture_book: 'AI 绘本',
    nursery_rhyme: 'AI 儿歌',
    video: 'AI 视频'
  }
  return names[type] || '智能创作'
}

function getProtagonistEmoji(animal: string): string {
  const emojis: Record<string, string> = {
    bunny: '🐰',
    bear: '🐻',
    cat: '🐱',
    dog: '🐶',
    panda: '🐼',
    fox: '🦊'
  }
  return emojis[animal] || '🐰'
}

async function handleSubmit() {
  if (!customPrompt.value.trim() || !selectedType.value) return

  const child = childStore.currentChild
  if (!child) {
    uni.showToast({ title: '请先添加宝贝', icon: 'none' })
    return
  }

  // 构建参数并跳转到对应创作页面
  // 基础参数（不含艺术风格，因为儿歌不需要）
  const baseParams = {
    creation_mode: 'smart',
    custom_prompt: customPrompt.value,
    protagonist: selectedProtagonist.value
  }

  let url = ''
  let params: Record<string, string> = {}

  switch (selectedType.value) {
    case 'picture_book':
      url = '/pages/create/picture-book'
      params = {
        ...baseParams,
        art_style: selectedArtStyle.value,  // 绘本需要艺术风格
        voice_id: selectedVoice.value
      } as Record<string, string>
      break

    case 'nursery_rhyme':
      url = '/pages/create/nursery-rhyme'
      params = {
        ...baseParams,
        // 儿歌不传 art_style，只传音乐情绪
        music_mood: selectedMood.value
      } as Record<string, string>
      break

    case 'video':
      if (selectedVideoMode.value === 'standalone') {
        url = '/pages/create/video'
        params = {
          ...baseParams,
          art_style: selectedArtStyle.value,  // 视频需要艺术风格
          mode: 'standalone',
          duration: String(selectedDuration.value)
        } as Record<string, string>
      } else {
        // 基于绘本模式：先跳转到绘本创作
        url = '/pages/create/picture-book'
        params = {
          ...baseParams,
          art_style: selectedArtStyle.value,  // 绘本需要艺术风格
          voice_id: selectedVoice.value,
          auto_video: 'true'  // 标记创作完成后自动跳转视频
        } as Record<string, string>
      }
      break
  }

  // 构建 query string
  const queryString = Object.entries(params)
    .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
    .join('&')

  uni.navigateTo({ url: `${url}?${queryString}` })
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.page-container {
  min-height: 100vh;
  background: $bg-cream;
  width: 750rpx;
  position: relative;
  overflow: hidden;
}

// 装饰背景
.decor-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.decor-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.4;

  &.shape-1 {
    width: 300rpx;
    height: 300rpx;
    background: linear-gradient(135deg, #A78BFA, #818CF8);
    top: -80rpx;
    right: -60rpx;
  }

  &.shape-2 {
    width: 250rpx;
    height: 250rpx;
    background: linear-gradient(135deg, #F472B6, #EC4899);
    bottom: 20%;
    left: -80rpx;
  }
}

// 主滚动区
.main-scroll {
  position: relative;
  z-index: 1;
  height: 100vh;
  padding: 0 32rpx;
  box-sizing: border-box;
}

// 顶部栏
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: calc(env(safe-area-inset-top) + 20rpx);
  padding-bottom: 16rpx;
}

.back-btn {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;

  text {
    font-size: 36rpx;
    color: $text-secondary;
  }

  &:active {
    transform: scale(0.92);
  }
}

.step-indicator {
  display: flex;
  gap: 12rpx;
}

.step-dot {
  width: 24rpx;
  height: 8rpx;
  border-radius: 4rpx;
  background: $border-light;
  transition: all 0.3s ease;

  &.active {
    background: $primary-light;
  }

  &.current {
    width: 48rpx;
    background: $primary;
  }
}

// 页面标题区
.header-section {
  text-align: center;
  padding: 24rpx 0 40rpx;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 20rpx;
  background: rgba($primary, 0.1);
  border: 1rpx solid rgba($primary, 0.2);
  border-radius: $radius-full;
  margin-bottom: 16rpx;
}

.badge-icon {
  font-size: 24rpx;
}

.badge-text {
  font-size: 24rpx;
  color: $primary;
  font-weight: $font-medium;
}

.header-title {
  display: block;
  font-size: 44rpx;
  font-weight: $font-bold;
  color: $text-primary;
  margin-bottom: 8rpx;
}

.header-desc {
  display: block;
  font-size: 28rpx;
  color: $text-tertiary;
}

// Step 内容区
.step-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}

// Step 1: 输入区
.input-section {
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  padding: 24rpx;
  margin-bottom: 32rpx;
}

.input-container {
  position: relative;
  margin-bottom: 24rpx;
}

.prompt-input {
  width: 100%;
  min-height: 160rpx;
  padding: 20rpx;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  font-size: $font-base;
  color: $text-primary;
  line-height: 1.6;
  box-sizing: border-box;
}

.input-footer {
  position: absolute;
  bottom: 12rpx;
  right: 16rpx;
}

.char-count {
  font-size: 22rpx;
  color: $text-placeholder;
}

.inspiration-section {
  margin-top: 20rpx;
}

.section-label {
  display: block;
  font-size: 26rpx;
  color: $text-secondary;
  margin-bottom: 16rpx;
}

.inspiration-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 12rpx 16rpx;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-full;

  &:active {
    background: rgba($primary, 0.08);
    border-color: $primary-light;
  }
}

.tag-emoji {
  font-size: 20rpx;
}

.tag-text {
  font-size: 24rpx;
  color: $text-secondary;
}

// Step 2: 类型选择
.type-selection {
  margin-bottom: 32rpx;
}

.type-card {
  display: flex;
  align-items: center;
  padding: 28rpx;
  background: $bg-card;
  border: 2rpx solid $border-light;
  border-radius: $radius-lg;
  margin-bottom: 16rpx;
  transition: all 0.2s ease;

  &.selected {
    border-color: $primary;
    background: rgba($primary, 0.04);
  }

  &:active {
    transform: scale(0.98);
  }
}

.type-icon-wrap {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-soft;
  border-radius: $radius-md;
  margin-right: 20rpx;
}

.type-icon {
  font-size: 40rpx;
}

.type-info {
  flex: 1;
}

.type-name {
  display: block;
  font-size: 32rpx;
  font-weight: $font-bold;
  color: $text-primary;
  margin-bottom: 4rpx;
}

.type-desc {
  display: block;
  font-size: 26rpx;
  color: $text-tertiary;
}

.type-check {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $primary;
  border-radius: 50%;

  text {
    color: white;
    font-size: 28rpx;
    font-weight: bold;
  }
}

.video-mode-section {
  margin-top: 24rpx;
  padding: 20rpx;
  background: $bg-soft;
  border-radius: $radius-md;
}

.video-modes {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.mode-option {
  display: flex;
  align-items: center;
  padding: 16rpx;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;

  &.selected {
    border-color: $primary;
    background: rgba($primary, 0.04);
  }
}

.mode-radio {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid $border-light;
  border-radius: 50%;
  margin-right: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;

  .radio-inner {
    width: 20rpx;
    height: 20rpx;
    background: $primary;
    border-radius: 50%;
  }
}

.mode-content {
  flex: 1;
}

.mode-name {
  display: block;
  font-size: 28rpx;
  font-weight: $font-medium;
  color: $text-primary;
}

.mode-desc {
  display: block;
  font-size: 24rpx;
  color: $text-tertiary;
}

// Step 3: 高级设置
.preview-section {
  margin-bottom: 24rpx;
}

.preview-card {
  background: linear-gradient(135deg, rgba($primary, 0.08), rgba($primary, 0.02));
  border: 1rpx solid rgba($primary, 0.2);
  border-radius: $radius-lg;
  padding: 24rpx;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.preview-type-icon {
  font-size: 32rpx;
}

.preview-type-name {
  font-size: 28rpx;
  font-weight: $font-medium;
  color: $primary;
}

.preview-prompt {
  text {
    font-size: 28rpx;
    color: $text-secondary;
    line-height: 1.6;
    font-style: italic;
  }
}

.advanced-section {
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  margin-bottom: 32rpx;
  overflow: hidden;
}

.advanced-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  background: $bg-soft;
}

.advanced-title {
  font-size: 28rpx;
  font-weight: $font-medium;
  color: $text-primary;
}

.advanced-toggle {
  font-size: 26rpx;
  color: $primary;
}

.advanced-content {
  padding: 24rpx;
}

.setting-group {
  margin-bottom: 28rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

// 绘本高级设置 - 增强面板
.enhancement-panel {
  margin: $spacing-lg 0;
  background: $bg-card;
  border-radius: $radius-lg;
  border: 1rpx solid $border-light;
  overflow: hidden;
  transition: all $duration-base;

  &.expanded {
    box-shadow: $shadow-md;
    border-color: rgba($primary, 0.15);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md $spacing-lg;
  background: linear-gradient(135deg, rgba($primary, 0.05) 0%, rgba($bg-soft, 0.8) 100%);
  cursor: pointer;
  transition: background $duration-fast;

  &:active {
    background: rgba($primary, 0.1);
  }

  .panel-header-left {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    flex: 1;
  }

  .panel-icon-wrap {
    width: 48rpx;
    height: 48rpx;
    background: linear-gradient(135deg, $primary, lighten($primary, 10%));
    border-radius: $radius-md;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4rpx 12rpx rgba($primary, 0.25);

    &.story {
      background: linear-gradient(135deg, #FF6B6B, #FFA07A);
    }

    &.visual {
      background: linear-gradient(135deg, #4ECDC4, #44A08D);
    }

    .panel-icon {
      font-size: 24rpx;
    }
  }

  .panel-header-text {
    flex: 1;

    .panel-title {
      display: block;
      font-size: $font-md;
      font-weight: $font-semibold;
      color: $text-primary;
    }

    .panel-hint {
      display: block;
      font-size: $font-xs;
      color: $text-tertiary;
      margin-top: 4rpx;
    }
  }

  .panel-arrow {
    width: 36rpx;
    height: 36rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba($primary, 0.1);
    border-radius: $radius-sm;
    transition: all $duration-base $ease-bounce;

    text {
      font-size: 28rpx;
      color: $primary;
      font-weight: $font-bold;
      transform: rotate(90deg);
      transition: transform $duration-base $ease-bounce;
    }

    &.expanded text {
      transform: rotate(-90deg);
    }
  }
}

.panel-content {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: all $duration-base;

  &.expanded {
    max-height: 3000rpx;
    opacity: 1;
    padding: $spacing-md $spacing-lg;
    border-top: 1rpx solid $border-light;
  }
}

.enhancement-group {
  margin-bottom: $spacing-lg;

  &:last-child {
    margin-bottom: 0;
  }

  .group-label {
    display: block;
    font-size: $font-sm;
    font-weight: $font-medium;
    color: $text-primary;
    margin-bottom: $spacing-sm;

    &::before {
      content: '';
      display: inline-block;
      width: 6rpx;
      height: 6rpx;
      background: $primary;
      border-radius: 50%;
      margin-right: 8rpx;
    }
  }
}

.option-cards {
  display: flex;
  flex-wrap: nowrap;
  gap: $spacing-sm;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 8rpx;

  // 隐藏滚动条但保持可滚动
  &::-webkit-scrollbar {
    display: none;
  }
}

.option-card {
  flex-shrink: 0;
  min-width: 140rpx;
  padding: $spacing-md $spacing-sm;
  background: $bg-soft;
  border-radius: $radius-md;
  border: 2rpx solid transparent;
  text-align: center;
  transition: all $duration-fast $ease-bounce;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;

  &:active {
    transform: scale(0.97);
  }

  &.selected {
    background: linear-gradient(135deg, rgba($primary, 0.15), rgba($primary, 0.08));
    border-color: $primary;
    box-shadow: 0 4rpx 16rpx rgba($primary, 0.15);

    .option-label {
      color: $primary;
      font-weight: $font-medium;
    }

    .option-emoji {
      transform: scale(1.1);
    }
  }

  .option-emoji {
    font-size: 32rpx;
    transition: transform $duration-fast $ease-bounce;
  }

  .option-label {
    font-size: $font-xs;
    color: $text-secondary;
    transition: all $duration-fast;
  }
}

.setting-label {
  display: block;
  font-size: 26rpx;
  color: $text-secondary;
  margin-bottom: 16rpx;
}

// 艺术风格分类 Tab
.art-style-group {
  .setting-label {
    margin-bottom: 12rpx;
  }
}

.style-category-tabs {
  display: flex;
  gap: 8rpx;
  margin-bottom: 16rpx;
  padding: 8rpx;
  background: $bg-soft;
  border-radius: $radius-md;
  overflow-x: auto;

  &::-webkit-scrollbar { display: none; }
}

.style-tab-item {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8rpx 16rpx;
  border-radius: $radius-sm;
  transition: all 0.2s;

  &.active {
    background: $bg-card;
    box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.08);
  }
}

.style-tab-icon {
  font-size: 20rpx;
  margin-bottom: 2rpx;
}

.style-tab-name {
  font-size: 20rpx;
  color: $text-tertiary;
  white-space: nowrap;

  .active & {
    color: $primary;
    font-weight: 500;
  }
}

// 艺术风格卡片
.art-style-scroll {
  margin: 0 -24rpx;
  padding: 0 24rpx;
}

.art-style-list {
  display: flex;
  gap: 12rpx;
  padding-bottom: 8rpx;
}

.art-card {
  position: relative;
  flex-shrink: 0;
  width: 180rpx;
  padding: 16rpx 12rpx;
  background: $bg-soft;
  border: 2rpx solid $border-light;
  border-radius: $radius-md;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  transition: all 0.2s;

  &.selected {
    border-color: $primary;
    background: rgba($primary, 0.08);
  }

  &:active {
    transform: scale(0.96);
  }
}

.art-icon {
  font-size: 32rpx;
}

.art-name {
  font-size: 24rpx;
  font-weight: 500;
  color: $text-primary;
}

.art-desc {
  font-size: 18rpx;
  color: $text-tertiary;
  background: rgba(0,0,0,0.04);
  padding: 2rpx 8rpx;
  border-radius: $radius-full;
  text-align: center;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.art-check {
  position: absolute;
  top: 6rpx;
  right: 6rpx;
  width: 28rpx;
  height: 28rpx;
  background: $primary;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16rpx;
  color: white;
}

.style-options,
.protagonist-options,
.voice-options,
.mood-options,
.duration-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.style-item,
.mood-item,
.duration-item {
  padding: 12rpx 24rpx;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-full;
  font-size: 26rpx;
  color: $text-secondary;

  &.selected {
    background: rgba($primary, 0.1);
    border-color: $primary;
    color: $primary;
  }
}

.protagonist-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  padding: 16rpx 20rpx;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;

  &.selected {
    background: rgba($primary, 0.1);
    border-color: $primary;
  }
}

.protagonist-emoji {
  font-size: 32rpx;
}

.protagonist-name {
  font-size: 22rpx;
  color: $text-secondary;
}

.voice-item {
  display: flex;
  flex-direction: column;
  padding: 16rpx 20rpx;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;

  &.selected {
    background: rgba($primary, 0.1);
    border-color: $primary;
  }
}

.voice-name {
  font-size: 26rpx;
  color: $text-primary;
}

.voice-style {
  font-size: 22rpx;
  color: $text-tertiary;
}

// 步骤操作按钮
.step-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 24rpx;
}

.prev-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 24rpx 32rpx;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-xl;
  font-size: 28rpx;
  color: $text-secondary;

  &:active {
    background: $bg-soft;
  }
}

.next-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 24rpx 32rpx;
  background: $primary;
  border-radius: $radius-xl;
  font-size: 28rpx;
  color: white;
  font-weight: $font-medium;

  &.disabled {
    background: $bg-soft;
    color: $text-placeholder;
  }

  &:active:not(.disabled) {
    transform: scale(0.98);
  }
}

.btn-arrow {
  font-size: 24rpx;
}

.submit-btn {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100rpx;
  background: $gradient-primary;
  border-radius: $radius-xl;
  box-shadow: $shadow-button;
  overflow: hidden;

  &:active {
    transform: scale(0.98);
  }
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shine 2s infinite;
}

@keyframes shine {
  0% { left: -100%; }
  50%, 100% { left: 100%; }
}

.btn-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.btn-icon {
  font-size: 32rpx;
}

.btn-text {
  font-size: 32rpx;
  font-weight: $font-semibold;
  color: white;
}

// 底部安全区
.safe-bottom {
  height: calc(env(safe-area-inset-bottom) + 100rpx);
}

// ==========================================
// 绘本设置 - 风格区域样式
// ==========================================
.style-sections {
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.style-section {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $spacing-md;
  box-shadow: $shadow-card;
}

.section-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
}

.section-header-text {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.section-icon-wrap {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: $book-light;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.bunny { background: $book-light; }
  &.palette { background: $song-light; }
  &.voice { background: $video-light; }
}

.section-icon {
  font-size: 28rpx;
}

.section-title {
  font-size: $font-md;
  font-weight: $font-bold;
  color: $text-primary;
}

.section-hint {
  font-size: $font-xs;
  color: $text-tertiary;
}

// 艺术风格卡片
.art-style-carousel {
  display: flex;
  gap: $spacing-sm;
  overflow-x: auto;
  padding-bottom: $spacing-xs;
  margin: 0 -#{$spacing-md};
  padding-left: $spacing-md;
  padding-right: $spacing-md;

  &::-webkit-scrollbar { display: none; }
}

.art-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.15;

  // 3D 风格
  &.pixar_3d { background: linear-gradient(145deg, #74B9FF 0%, #A29BFE 50%, #81ECEC 100%); }
  &.pixar { background: linear-gradient(145deg, #FF7B54 0%, #7FB285 50%, #F5A623 100%); }
  &.dreamworks { background: linear-gradient(145deg, #45B7D1 0%, #96E6A1 50%, #DFE6E9 100%); }
  &.disney_3d { background: linear-gradient(145deg, #E8A4C9 0%, #87CEEB 50%, #FFD700 100%); }
  &.clay { background: linear-gradient(145deg, #E8A87C 0%, #D4A574 50%, #C9956C 100%); }
  &.figurine { background: linear-gradient(145deg, #DFE6E9 0%, #B2BEC3 50%, #636E72 100%); }
  &.low_poly { background: linear-gradient(145deg, #00CEC9 0%, #6C5CE7 50%, #FD79A8 100%); }
  // 插画风格
  &.storybook { background: linear-gradient(145deg, #FFE4C4 0%, #F5A623 50%, #7FB285 100%); }
  &.watercolor { background: linear-gradient(145deg, #74B9FF 0%, #FFB347 50%, #4ECDC4 100%); }
  &.cartoon { background: linear-gradient(145deg, #FF7B54 0%, #FFE66D 50%, #4ECDC4 100%); }
  &.flat { background: linear-gradient(145deg, #FFE66D 0%, #FF7B54 50%, #7FB285 100%); }
  &.flat_vector { background: linear-gradient(145deg, #FFE66D 0%, #FF7B54 50%, #7FB285 100%); }
  &.crayon { background: linear-gradient(145deg, #F5A623 0%, #FF7B54 50%, #7FB285 100%); }
  &.colored_pencil { background: linear-gradient(145deg, #FFEAA7 0%, #FDCB6E 50%, #E17055 100%); }
  // 动漫风格
  &.anime { background: linear-gradient(145deg, #FFB6C1 0%, #7FB285 50%, #74B9FF 100%); }
  &.chibi { background: linear-gradient(145deg, #FFB5BA 0%, #FFF5BA 50%, #B5D8FF 100%); }
  &.ghibli { background: linear-gradient(145deg, #7FB285 0%, #74B9FF 50%, #F5A623 100%); }
  &.shinkai { background: linear-gradient(145deg, #667EEA 0%, #764BA2 50%, #F093FB 100%); }
  &.manga { background: linear-gradient(145deg, #2D3436 0%, #636E72 50%, #FFFFFF 100%); }
  &.comic_book { background: linear-gradient(145deg, #FF4757 0%, #2ED573 50%, #3742FA 100%); }
  // 艺术风格
  &.oil_painting { background: linear-gradient(145deg, #8B4513 0%, #D4A574 50%, #FFE4C4 100%); }
  &.impressionist { background: linear-gradient(145deg, #F9CA24 0%, #6AB04C 50%, #686DE0 100%); }
  &.sketch { background: linear-gradient(145deg, #2D3436 0%, #636E72 50%, #DFE6E9 100%); }
  &.ink_wash { background: linear-gradient(145deg, #2D3436 0%, #B2BEC3 50%, #DFE6E9 100%); }
  &.pop_art { background: linear-gradient(145deg, #FF6B6B 0%, #4ECDC4 50%, #FFE66D 100%); }
  &.art_nouveau { background: linear-gradient(145deg, #C8A962 0%, #7D8471 50%, #2C3E50 100%); }
  &.pixel_art { background: linear-gradient(145deg, #2ED573 0%, #3742FA 50%, #FF4757 100%); }
  // 手工风格
  &.papercut { background: linear-gradient(145deg, #E74C3C 0%, #F39C12 50%, #27AE60 100%); }
  &.felt_craft { background: linear-gradient(145deg, #FFB8B8 0%, #A8E6CF 50%, #FDFFAB 100%); }
  &.origami { background: linear-gradient(145deg, #74B9FF 0%, #FFFFFF 50%, #FF7675 100%); }
  &.embroidery { background: linear-gradient(145deg, #D63031 0%, #00B894 50%, #FDCB6E 100%); }
  &.mosaic { background: linear-gradient(145deg, #6C5CE7 0%, #00CEC9 50%, #FDCB6E 100%); }
  &.stained_glass { background: linear-gradient(145deg, #0984E3 0%, #6C5CE7 50%, #E84393 100%); }
}

// 角色选择
.character-carousel {
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
  justify-content: space-between;
}

.character-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: calc(33.33% - 16rpx);
  padding: $spacing-sm 0;
  padding-top: $spacing-md;
  position: relative;
  transition: all $duration-base $ease-bounce;

  &.selected {
    .char-glow {
      opacity: 1;
      transform: scale(1);
    }
    .character-avatar-wrap {
      transform: translateY(-8rpx) scale(1.08);
    }
    .character-avatar {
      background: rgba($book-primary, 0.15);
      border-color: $book-primary;
      box-shadow: 0 8rpx 24rpx rgba($book-primary, 0.25);
    }
    .char-emoji {
      animation: char-bounce 0.5s $ease-bounce;
    }
    .char-star {
      opacity: 1;
      transform: scale(1) rotate(0deg);
    }
    .char-stage {
      opacity: 1;
      transform: scaleX(1);
    }
    .char-name {
      color: $book-primary;
      font-weight: $font-semibold;
    }
  }

  &:active {
    transform: scale(0.92);
  }
}

.char-glow {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%) scale(0.8);
  width: 120rpx;
  height: 120rpx;
  background: radial-gradient(circle, rgba($book-primary, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: all $duration-base $ease-bounce;
  pointer-events: none;
}

.character-avatar-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: $spacing-xs;
  transition: all $duration-base $ease-bounce;
  z-index: 2;
}

.character-avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: $bg-soft;
  border: 3rpx solid $border-light;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all $duration-base $ease-bounce;
}

.char-emoji {
  font-size: 48rpx;
  transition: transform $duration-base;
}

.char-star {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  font-size: 28rpx;
  opacity: 0;
  transform: scale(0) rotate(-180deg);
  transition: all 0.35s $ease-bounce;
  filter: drop-shadow(0 2rpx 4rpx rgba($accent, 0.4));
  z-index: 3;
}

.char-stage {
  width: 80rpx;
  height: 8rpx;
  background: linear-gradient(90deg, transparent, $book-primary, transparent);
  border-radius: 4rpx;
  margin-top: -4rpx;
  margin-bottom: 4rpx;
  opacity: 0;
  transform: scaleX(0);
  transition: all $duration-base $ease-bounce;
}

.char-name {
  font-size: $font-xs;
  color: $text-primary;
  font-weight: $font-medium;
  transition: all $duration-base;
}

@keyframes char-bounce {
  0%, 100% { transform: translateY(0); }
  25% { transform: translateY(-12rpx); }
  50% { transform: translateY(-4rpx); }
  75% { transform: translateY(-8rpx); }
}

// 音色选择
.voice-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.voice-card {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-md;
  background: $bg-soft;
  border-radius: $radius-md;
  border: 2rpx solid $border-light;
  transition: all $duration-fast;

  &.selected {
    border-color: $book-primary;
    background: rgba($book-primary, 0.08);
    box-shadow: $shadow-colored-book;

    .voice-waves .wave {
      animation: waveAnim 0.8s ease-in-out infinite;
    }
  }

  &:active {
    transform: scale(0.98);
  }
}

.voice-avatar {
  position: relative;
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.voice-emoji {
  font-size: 40rpx;
  position: relative;
  z-index: 1;
}

.voice-waves {
  position: absolute;
  right: -8rpx;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 4rpx;
  align-items: center;
}

.wave {
  width: 4rpx;
  height: 16rpx;
  background: $book-primary;
  border-radius: 2rpx;
  opacity: 0.3;

  &:nth-child(1) { animation-delay: 0s; }
  &:nth-child(2) { animation-delay: 0.15s; height: 24rpx; }
  &:nth-child(3) { animation-delay: 0.3s; }
}

@keyframes waveAnim {
  0%, 100% { transform: scaleY(0.5); opacity: 0.3; }
  50% { transform: scaleY(1); opacity: 1; }
}

.voice-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  min-width: 0;
}

.voice-name-row {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  flex-wrap: wrap;
}

.voice-name {
  font-size: $font-base;
  font-weight: $font-semibold;
  color: $text-primary;
}

.voice-id {
  font-size: $font-xs;
  color: $text-tertiary;
  font-weight: $font-normal;
}

.voice-badge {
  font-size: 18rpx;
  padding: 2rpx 8rpx;
  background: $accent;
  color: $text-white;
  border-radius: $radius-xs;
  font-weight: $font-semibold;
}

.voice-gender-tag {
  font-size: 18rpx;
  padding: 2rpx 8rpx;
  border-radius: $radius-xs;
  font-weight: $font-medium;
  flex-shrink: 0;

  &.female { background: $book-light; color: $book-primary; }
  &.male { background: rgba(91, 164, 217, 0.2); color: #5ba4d9; }
  &.neutral { background: rgba(168, 149, 214, 0.2); color: #8875bf; }
}

.voice-detail-row {
  display: flex;
  align-items: flex-start;
  gap: 6rpx;
}

.voice-detail-label {
  font-size: 20rpx;
  flex-shrink: 0;
  line-height: 1.4;
}

.voice-detail-text {
  font-size: $font-xs;
  color: $text-secondary;
  line-height: 1.4;
}

.voice-check {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: $book-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  text {
    font-size: 20rpx;
    color: $text-white;
  }
}

.voice-preview-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: rgba($book-primary, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all $duration-fast;

  &:active {
    transform: scale(0.9);
    background: rgba($book-primary, 0.2);
  }

  &.loading {
    pointer-events: none;
  }

  .preview-icon {
    font-size: 24rpx;
    color: $book-primary;

    &.playing {
      animation: pulse 1s ease-in-out infinite;
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
