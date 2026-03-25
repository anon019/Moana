<template>
  <view class="page-container">
    <!-- 装饰背景 -->
    <view class="decor-bg">
      <view class="decor-shape shape-1"></view>
      <view class="decor-shape shape-2"></view>
      <view class="decor-shape shape-3"></view>
    </view>

    <!-- 导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <view class="back-btn" @tap="goBack">
          <text>‹</text>
        </view>
        <text class="nav-title">创作视频</text>
        <view class="nav-right"></view>
      </view>
    </view>
    <view class="nav-placeholder" :style="{ height: navHeight + 'px' }"></view>

    <!-- 模式选择（首次进入时显示） -->
    <scroll-view v-if="showModeSelector" class="main-scroll" scroll-y>
      <CreationModeSelector
        content-type="video"
        @select="handleModeSelect"
      />
    </scroll-view>

    <!-- 主内容（选择模式后显示） -->
    <scroll-view v-else class="main-scroll" scroll-y>
      <!-- 模式切换 Tab -->
      <view class="mode-tabs">
        <view
          class="mode-tab"
          :class="{ active: creationMode === 'from_book' }"
          @tap="switchCreationMode('from_book')"
        >
          <text class="tab-icon">📚</text>
          <text class="tab-text">基于绘本</text>
        </view>
        <view
          class="mode-tab"
          :class="{ active: creationMode === 'standalone' }"
          @tap="switchCreationMode('standalone')"
        >
          <text class="tab-icon">✨</text>
          <text class="tab-text">独立创作</text>
        </view>
      </view>

      <!-- 步骤指示器 - 基于绘本模式 3步 -->
      <view v-if="creationMode === 'from_book'" class="step-indicator">
        <view class="step" :class="{ active: true, completed: currentStep > 0 }">
          <view class="step-dot">{{ currentStep > 0 ? '✓' : '1' }}</view>
          <text class="step-text">选择绘本</text>
        </view>
        <view class="step-line" :class="{ active: currentStep >= 1 }"></view>
        <view class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
          <view class="step-dot">{{ currentStep > 1 ? '✓' : '2' }}</view>
          <text class="step-text">选择画面</text>
        </view>
        <view class="step-line" :class="{ active: currentStep >= 2 }"></view>
        <view class="step" :class="{ active: currentStep >= 2 }">
          <view class="step-dot">3</view>
          <text class="step-text">生成视频</text>
        </view>
      </view>

      <!-- 步骤指示器 - 独立创作模式 2步 -->
      <view v-else class="step-indicator">
        <view class="step" :class="{ active: true, completed: currentStep > 0 }">
          <view class="step-dot">{{ currentStep > 0 ? '✓' : '1' }}</view>
          <text class="step-text">描述场景</text>
        </view>
        <view class="step-line" :class="{ active: currentStep >= 1 }"></view>
        <view class="step" :class="{ active: currentStep >= 1 }">
          <view class="step-dot">2</view>
          <text class="step-text">配置生成</text>
        </view>
      </view>

      <!-- 第一步：选择绘本（基于绘本模式） -->
      <view class="section" v-show="currentStep === 0 && creationMode === 'from_book'">
        <text class="section-title">选择要转换的绘本</text>
        <text class="section-desc">将绘本故事转化为精彩动画视频</text>

        <!-- 加载状态 -->
        <view v-if="loading" class="loading-state">
          <text class="loading-icon animate-spin">🔄</text>
          <text>加载中...</text>
        </view>

        <!-- 空状态 -->
        <view v-else-if="pictureBooks.length === 0" class="empty-state">
          <text class="empty-icon">📚</text>
          <text class="empty-title">暂无绘本</text>
          <text class="empty-desc">请先创作一本绘本，再来生成视频</text>
          <view class="empty-action" @tap="goToCreateBook">
            <text>去创作绘本</text>
          </view>
        </view>

        <!-- 绘本列表 -->
        <view v-else class="book-list">
          <view
            v-for="book in pictureBooks"
            :key="book.id"
            class="book-card"
            :class="{ selected: selectedBook?.id === book.id }"
            @tap="selectBook(book)"
          >
            <view class="book-cover">
              <image v-if="book.cover_url" :src="book.cover_url" mode="aspectFill" class="cover-image" />
              <view v-else class="cover-placeholder">
                <text>📖</text>
              </view>
              <view v-if="selectedBook?.id === book.id" class="selected-badge">
                <text>✓</text>
              </view>
            </view>
            <view class="book-info">
              <text class="book-title">{{ book.title }}</text>
              <text class="book-meta">
                <text v-if="loadingDetail && selectedBook?.id === book.id">加载中...</text>
                <text v-else-if="book.pages && book.pages.length > 0">{{ book.pages.length }} 页</text>
                <text v-else-if="selectedBook?.id === book.id">获取详情中...</text>
                <text v-else>{{ formatDuration(book.total_duration) }}</text>
              </text>
            </view>
          </view>
        </view>
      </view>

      <!-- 第一步：输入描述（独立创作模式） -->
      <view class="section" v-show="currentStep === 0 && creationMode === 'standalone'">
        <text class="section-title">描述你想要的视频</text>
        <text class="section-desc">AI 将根据描述生成专属动画视频</text>

        <view class="standalone-input-area">
          <view class="input-container">
            <textarea
              v-model="customPrompt"
              class="prompt-input"
              placeholder="例如：小兔子在花园里开心地吃蔬菜，旁边有蝴蝶飞舞..."
              :maxlength="500"
              auto-height
            />
            <view class="input-footer">
              <text class="char-count">{{ customPrompt.length }}/500</text>
            </view>
          </view>

          <!-- 首帧预览 -->
          <view v-if="generatedFirstFrame" class="first-frame-preview">
            <text class="preview-label">首帧预览</text>
            <image :src="generatedFirstFrame" mode="aspectFit" class="preview-image" />
            <view class="preview-actions">
              <view class="regenerate-btn" @tap="handleGenerateFirstFrame">
                <text>🔄 重新生成</text>
              </view>
            </view>
          </view>

          <!-- 生成首帧按钮 -->
          <view
            v-else
            class="generate-first-frame-btn"
            :class="{ disabled: !customPrompt.trim() || generatingFirstFrame }"
            @tap="handleGenerateFirstFrame"
          >
            <text v-if="generatingFirstFrame">🔄 生成中...</text>
            <text v-else>✨ 预览首帧（可选）</text>
          </view>
          <text class="first-frame-hint">生成首帧可以预览效果，跳过则由 AI 自动生成</text>
        </view>
      </view>

      <!-- 第二步：选择画面（基于绘本模式） -->
      <view class="section" v-show="currentStep === 1 && selectedBook && creationMode === 'from_book'">
        <text class="section-title">选择视频首帧画面</text>
        <text class="section-desc">选择一张绘本图片作为视频的起始画面</text>

        <!-- 绘本页面缩略图 -->
        <view class="page-selector">
          <view
            v-for="(page, index) in selectedBook?.pages || []"
            :key="index"
            class="page-thumb"
            :class="{
              'is-first-frame': selectedPageIndex === index,
              'is-reference': referencePageIndexes.includes(index) && selectedPageIndex !== index
            }"
            @tap="handlePageSelect(index)"
          >
            <image :src="page.image_url" mode="aspectFill" class="thumb-image" />
            <view v-if="selectedPageIndex === index" class="thumb-badge first-frame">
              <text>首帧</text>
            </view>
            <view v-else-if="referencePageIndexes.includes(index)" class="thumb-badge reference">
              <text>参考</text>
            </view>
            <text class="thumb-num">{{ index + 1 }}</text>
          </view>
        </view>

        <!-- 角色参考图选择 -->
        <view class="reference-section" v-if="selectedPageIndex !== null">
          <view class="reference-header">
            <text class="reference-title">角色参考图</text>
            <text class="reference-hint">可选，最多再选 {{ maxReferenceCount }} 张</text>
          </view>
          <text class="reference-desc">选择其他页面作为角色参考，帮助保持角色一致性</text>

          <view class="reference-list">
            <view
              v-for="(page, index) in availableReferencePages"
              :key="index"
              class="reference-thumb"
              :class="{ selected: referencePageIndexes.includes(page.originalIndex) }"
              @tap="toggleReference(page.originalIndex)"
            >
              <image :src="page.image_url" mode="aspectFill" class="thumb-image" />
              <view v-if="referencePageIndexes.includes(page.originalIndex)" class="ref-check">
                <text>✓</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 第三步：生成配置（基于绘本模式） -->
      <view class="section" v-show="currentStep === 2 && selectedBook && creationMode === 'from_book'">
        <!-- 预览信息 -->
        <view class="preview-card">
          <view class="preview-header">
            <image
              v-if="selectedPageIndex !== null && selectedBook?.pages?.[selectedPageIndex]"
              :src="selectedBook.pages[selectedPageIndex].image_url"
              mode="aspectFill"
              class="preview-image"
            />
            <view class="preview-info">
              <text class="preview-title">{{ selectedBook?.title }}</text>
              <text class="preview-meta">首帧: 第 {{ (selectedPageIndex || 0) + 1 }} 页</text>
              <text class="preview-meta" v-if="referencePageIndexes.length > 0">
                参考图: {{ referencePageIndexes.length }} 张
              </text>
            </view>
          </view>
        </view>

        <!-- 场景模板 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">🎬</text>
            场景模板
          </text>
          <text class="style-hint">选择模板自动应用最佳参数，也可手动调整</text>
          <view class="template-list">
            <view
              v-for="template in sceneTemplates"
              :key="template.id"
              class="template-card"
              :class="{ active: selectedTemplate === template.id, recommended: template.recommended }"
              @tap="handleTemplateSelect(template.id)"
            >
              <view v-if="template.recommended" class="recommend-badge">推荐</view>
              <text class="template-icon">{{ template.icon }}</text>
              <text class="template-name">{{ template.name }}</text>
              <text class="template-desc">{{ template.description }}</text>
              <view v-if="selectedTemplate === template.id" class="template-check">
                <text>✓</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 宽高比选择 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">📐</text>
            画面比例
          </text>
          <view class="aspect-ratio-list">
            <view
              v-for="ratio in aspectRatioOptions"
              :key="ratio.value"
              class="aspect-ratio-item"
              :class="{ active: selectedAspectRatio === ratio.value }"
              @tap="selectedAspectRatio = ratio.value"
            >
              <view class="ratio-preview" :style="{ aspectRatio: ratio.value.replace(':', '/') }"></view>
              <text class="ratio-label">{{ ratio.label }}</text>
              <text v-if="ratio.recommended" class="ratio-badge">推荐</text>
            </view>
          </view>
        </view>

        <!-- 运动模式选择 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">🎭</text>
            运动模式
          </text>
          <view class="motion-mode-list">
            <view
              v-for="mode in motionModes"
              :key="mode.value"
              class="motion-mode-item"
              :class="{ active: selectedMotionMode === mode.value }"
              @tap="selectedMotionMode = mode.value"
            >
              <view class="mode-info">
                <text class="mode-name">{{ mode.label }}</text>
                <text class="mode-desc">{{ mode.desc }}</text>
              </view>
              <view v-if="mode.recommended" class="mode-badge">推荐</view>
              <view v-if="selectedMotionMode === mode.value" class="mode-check">
                <text>✓</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 分辨率选择 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">🎞️</text>
            视频分辨率
          </text>
          <view class="resolution-tabs">
            <view
              v-for="res in resolutionOptions"
              :key="res.value"
              class="resolution-tab"
              :class="{ active: selectedResolution === res.value }"
              @tap="selectedResolution = res.value"
            >
              <text class="res-value">{{ res.label }}</text>
              <text v-if="res.note" class="res-note">{{ res.note }}</text>
              <text v-if="res.recommended" class="res-badge">推荐</text>
            </view>
          </view>
        </view>

        <!-- 视频时长选择 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">⏱️</text>
            视频时长
          </text>
          <view class="duration-tabs">
            <view
              v-for="dur in durationOptions"
              :key="dur.value"
              class="duration-tab"
              :class="{ active: selectedDuration === dur.value }"
              @tap="selectedDuration = dur.value"
            >
              <text class="dur-value">{{ dur.label }}</text>
              <text class="dur-desc">{{ dur.desc }}</text>
            </view>
          </view>
        </view>

        <!-- 音效选择 (Veo 3.1 暂不支持自定义，已隐藏) -->
        <!--
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">🔊</text>
            音效设置
          </text>
          <view class="audio-toggle-row">
            <view class="audio-info">
              <text class="audio-label">{{ audioEnabled ? '启用音效' : '静音模式' }}</text>
              <text class="audio-desc">{{ audioEnabled ? 'AI 生成配套环境音效' : '无声视频，适合后期配音' }}</text>
            </view>
            <switch
              :checked="audioEnabled"
              @change="audioEnabled = $event.detail.value"
              color="#F5A623"
            />
          </view>
        </view>
        -->

        <!-- 高级设置折叠 -->
        <view class="advanced-section">
          <view class="advanced-header" @tap="showAdvanced = !showAdvanced">
            <text class="advanced-title">{{ showAdvanced ? '▼' : '▶' }} 高级设置</text>
          </view>

          <view v-if="showAdvanced" class="advanced-content">
            <!-- AI 优化开关 -->
            <view class="advanced-item">
              <view class="advanced-row">
                <view class="advanced-info">
                  <text class="advanced-label">AI 自动优化提示词</text>
                  <text class="advanced-desc">分析图片风格，自动添加镜头语言</text>
                </view>
                <switch
                  :checked="autoEnhancePrompt"
                  @change="autoEnhancePrompt = $event.detail.value"
                  color="#F5A623"
                />
              </view>
            </view>

            <!-- 排除内容 -->
            <view class="advanced-item">
              <text class="advanced-label">排除内容</text>
              <text class="advanced-desc">选择要避免生成的内容类型</text>
              <view class="negative-presets">
                <view
                  v-for="preset in negativePresetOptions"
                  :key="preset.id"
                  class="negative-chip"
                  :class="{ active: selectedNegativePresets.includes(preset.id) }"
                  @tap="toggleNegativePreset(preset.id)"
                >
                  <text>{{ preset.label }}</text>
                </view>
              </view>
            </view>

            <!-- 结束帧 -->
            <view class="advanced-item">
              <text class="advanced-label">结束帧图片（可选）</text>
              <text class="advanced-desc">选择绘本中的一张图片作为结束帧</text>
              <view class="end-frame-selector">
                <view
                  class="end-frame-option"
                  :class="{ active: endPageIndex === null }"
                  @tap="endPageIndex = null"
                >
                  <text class="end-frame-text">AI 自然结束</text>
                </view>
                <view
                  v-for="(page, index) in selectedBook?.pages || []"
                  :key="index"
                  class="end-frame-thumb"
                  :class="{ active: endPageIndex === index }"
                  @tap="endPageIndex = index"
                >
                  <image :src="page.image_url" mode="aspectFill" class="thumb-image" />
                  <view v-if="endPageIndex === index" class="end-check">
                    <text>✓</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <text class="preview-tip">视频生成需要 1-5 分钟，请耐心等待</text>
      </view>

      <!-- 第二步：生成配置（独立创作模式） -->
      <view class="section" v-show="currentStep === 1 && creationMode === 'standalone'">
        <!-- 预览信息 -->
        <view class="preview-card">
          <view class="preview-header">
            <image
              v-if="generatedFirstFrame"
              :src="generatedFirstFrame"
              mode="aspectFill"
              class="preview-image"
            />
            <view v-else class="preview-placeholder">
              <text>🎬</text>
            </view>
            <view class="preview-info">
              <text class="preview-title">独立创作视频</text>
              <text class="preview-meta">"{{ customPrompt.slice(0, 30) }}{{ customPrompt.length > 30 ? '...' : '' }}"</text>
              <text class="preview-meta" v-if="generatedFirstFrame">已生成首帧</text>
              <text class="preview-meta" v-else>AI 将自动生成首帧</text>
            </view>
          </view>
        </view>

        <!-- 场景模板 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">🎬</text>
            场景模板
          </text>
          <text class="style-hint">选择模板自动应用最佳参数</text>
          <view class="template-list">
            <view
              v-for="template in sceneTemplates"
              :key="template.id"
              class="template-card"
              :class="{ active: selectedTemplate === template.id, recommended: template.recommended }"
              @tap="handleTemplateSelect(template.id)"
            >
              <view v-if="template.recommended" class="recommend-badge">推荐</view>
              <text class="template-icon">{{ template.icon }}</text>
              <text class="template-name">{{ template.name }}</text>
              <text class="template-desc">{{ template.description }}</text>
              <view v-if="selectedTemplate === template.id" class="template-check">
                <text>✓</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 宽高比选择 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">📐</text>
            画面比例
          </text>
          <view class="aspect-ratio-list">
            <view
              v-for="ratio in aspectRatioOptions"
              :key="ratio.value"
              class="aspect-ratio-item"
              :class="{ active: selectedAspectRatio === ratio.value, recommended: ratio.recommended }"
              @tap="selectedAspectRatio = ratio.value"
            >
              <view class="ratio-preview" :style="{ aspectRatio: ratio.value.replace(':', '/') }"></view>
              <text class="ratio-label">{{ ratio.label }}</text>
              <text v-if="ratio.recommended" class="ratio-badge">推荐</text>
            </view>
          </view>
        </view>

        <!-- 运动模式选择 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">🎭</text>
            运动模式
          </text>
          <view class="motion-mode-list">
            <view
              v-for="mode in motionModes"
              :key="mode.value"
              class="motion-mode-item"
              :class="{ active: selectedMotionMode === mode.value }"
              @tap="selectedMotionMode = mode.value"
            >
              <view class="mode-info">
                <text class="mode-name">{{ mode.label }}</text>
                <text class="mode-desc">{{ mode.desc }}</text>
              </view>
              <view v-if="mode.recommended" class="mode-badge">推荐</view>
              <view v-if="selectedMotionMode === mode.value" class="mode-check">
                <text>✓</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 分辨率选择 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">🎞️</text>
            视频分辨率
          </text>
          <view class="resolution-tabs">
            <view
              v-for="res in resolutionOptions"
              :key="res.value"
              class="resolution-tab"
              :class="{ active: selectedResolution === res.value }"
              @tap="selectedResolution = res.value"
            >
              <text class="res-value">{{ res.label }}</text>
              <text v-if="res.note" class="res-note">{{ res.note }}</text>
              <text v-if="res.recommended" class="res-badge">推荐</text>
            </view>
          </view>
        </view>

        <!-- 视频时长选择 -->
        <view class="style-section">
          <text class="style-title">
            <text class="title-icon">⏱️</text>
            视频时长
          </text>
          <view class="duration-tabs">
            <view
              v-for="dur in durationOptions"
              :key="dur.value"
              class="duration-tab"
              :class="{ active: selectedDuration === dur.value }"
              @tap="selectedDuration = dur.value"
            >
              <text class="dur-value">{{ dur.label }}</text>
              <text class="dur-desc">{{ dur.desc }}</text>
            </view>
          </view>
        </view>

        <text class="preview-tip">视频生成需要 1-5 分钟，请耐心等待</text>
      </view>

      <!-- 底部占位 -->
      <view class="bottom-placeholder"></view>
    </scroll-view>

    <!-- 底部按钮（模式选择器隐藏后显示） -->
    <view v-if="!showModeSelector" class="bottom-bar">
      <!-- 步骤导航按钮 -->
      <view v-if="currentStep > 0" class="step-back-btn" @tap="goToPrevStep">
        <text>上一步</text>
      </view>
      <view
        class="generate-btn"
        :class="{
          disabled: !canProceed || generating || loadingDetail,
          'flex-1': currentStep > 0
        }"
        @tap="handleNextStep"
      >
        <text>{{ actionBtnText }}</text>
      </view>
    </view>

    <!-- 生成进度 -->
    <GeneratingProgress
      v-if="generating"
      :progress="generateProgress"
      :stage="generatingStage"
      :message="generatingMessage"
      type="video"
    />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import type { PictureBook, Video, VideoPage, VideoTaskStatus, SceneTemplateId, NegativePresetId, ArtStyle } from '@/api/content'
import {
  getGeneratedList,
  getContentDetail,
  generateVideoAsync,
  getVideoTaskStatus,
  generateFirstFrame,
  generateStandaloneVideoAsync
} from '@/api/content'
import { useChildStore } from '@/stores/child'
import GeneratingProgress from '@/components/GeneratingProgress/GeneratingProgress.vue'
import CreationModeSelector from '@/components/CreationModeSelector/CreationModeSelector.vue'

const childStore = useChildStore()

// 模式选择
const showModeSelector = ref(true)

// 基础状态
const statusBarHeight = ref(20)
const navHeight = ref(88)
const loading = ref(true)
const loadingDetail = ref(false)
const generating = ref(false)
const generateProgress = ref(0)
const generatingStage = ref('')
const generatingMessage = ref('')
const pictureBooks = ref<PictureBook[]>([])
const selectedBook = ref<PictureBook | null>(null)
const currentTaskId = ref<string | null>(null)

// 创作模式: 'from_book' | 'standalone'
const creationMode = ref<'from_book' | 'standalone'>('from_book')

// 独立创作相关状态
const customPrompt = ref('')
const generatedFirstFrame = ref<string | null>(null)
const generatingFirstFrame = ref(false)
const selectedArtStyle = ref<ArtStyle>('storybook')

// 步骤控制
const currentStep = ref(0)

// 第二步：画面选择
const selectedPageIndex = ref<number | null>(null)
const referencePageIndexes = ref<number[]>([])
const maxReferenceCount = 2

// 第三步：配置选项
const selectedTemplate = ref<SceneTemplateId | null>('action_scene')
const showAdvanced = ref(false)
const autoEnhancePrompt = ref(true)
const selectedNegativePresets = ref<NegativePresetId[]>(['realistic', 'blur', 'style_change'])
const endPageIndex = ref<number | null>(null)

// 场景模板配置 (Veo 3.1 专版)
const sceneTemplates = [
  {
    id: 'cover_subtle' as SceneTemplateId,
    name: '封面微动',
    icon: '🎬',
    description: '轻微呼吸感，适合封面',
    preset: {
      duration: 4,
      resolution: '1080P',
      motion_mode: 'slow'
    }
  },
  {
    id: 'character_dialogue' as SceneTemplateId,
    name: '角色对话',
    icon: '💬',
    description: '轻微动作和表情变化',
    preset: {
      duration: 6,
      resolution: '720P',
      motion_mode: 'normal'
    }
  },
  {
    id: 'scene_transition' as SceneTemplateId,
    name: '场景转换',
    icon: '🔄',
    description: '场景推进，带镜头运动',
    preset: {
      duration: 6,
      resolution: '720P',
      motion_mode: 'cinematic'
    }
  },
  {
    id: 'action_scene' as SceneTemplateId,
    name: '动作场景',
    icon: '🏃',
    description: '丰富动作，高潮情节',
    recommended: true,
    preset: {
      duration: 5,
      resolution: '720P',
      motion_mode: 'normal'
    }
  },
  {
    id: 'emotional_moment' as SceneTemplateId,
    name: '情感特写',
    icon: '💖',
    description: '角色表情细腻变化',
    preset: {
      duration: 6,
      resolution: '1080P',
      motion_mode: 'slow'
    }
  }
]

// 负面提示词预设选项
const negativePresetOptions = [
  { id: 'realistic' as NegativePresetId, label: '写实风格', value: 'realistic, photographic, photo-real, lifelike' },
  { id: 'blur' as NegativePresetId, label: '模糊画面', value: 'blur, out of focus, blurry, unfocused' },
  { id: 'style_change' as NegativePresetId, label: '风格突变', value: 'style change, inconsistent style, style shift' },
  { id: 'shaky' as NegativePresetId, label: '镜头抖动', value: 'camera shake, jerky motion, unstable, shaky cam' },
  { id: 'dark' as NegativePresetId, label: '暗色调', value: 'dark, dimly lit, shadowy, low key lighting' },
  { id: 'fast' as NegativePresetId, label: '快速运动', value: 'fast motion, rapid movement, speed blur' },
  { id: 'distortion' as NegativePresetId, label: '画面变形', value: 'distortion, warped, stretched, morphing artifacts' }
]

// 宽高比选项 (Veo 3.1 主要支持 16:9 和 9:16)
const aspectRatioOptions = [
  { value: '16:9', label: '横屏 16:9', desc: '视频、电影', icon: '📺' },
  { value: '9:16', label: '竖屏 9:16', desc: '手机、短视频', icon: '📱', recommended: true }
]
const selectedAspectRatio = ref('9:16')

// 分辨率选项
const resolutionOptions = [
  { value: '720P', label: '720P 高清', recommended: true },
  { value: '1080P', label: '1080P 全高清', note: '生成时间更长' }
]
const selectedResolution = ref('720P')

// 时长选项 (Veo 3.1 支持 4-8 秒)
const durationOptions = [
  { value: 4, label: '4秒', desc: '封面微动' },
  { value: 5, label: '5秒', desc: '标准时长', recommended: true },
  { value: 6, label: '6秒', desc: '角色对话' },
  { value: 8, label: '8秒', desc: '完整动画' }
]
const selectedDuration = ref(5)

// 运动模式选项
const motionModes = [
  { value: 'static', label: '静态', desc: '几乎无运动，展示静态场景' },
  { value: 'slow', label: '缓慢', desc: '轻微运动，氛围感' },
  { value: 'normal', label: '正常', desc: '自然运动', recommended: true },
  { value: 'dynamic', label: '动态', desc: '较多运动，动作场景' },
  { value: 'cinematic', label: '电影感', desc: '电影级镜头运动' }
]
const selectedMotionMode = ref('normal')

// 音效选项
const audioEnabled = ref(true)

// 可选择作为参考图的页面（排除首帧）
const availableReferencePages = computed(() => {
  if (!selectedBook.value?.pages || selectedPageIndex.value === null) return []
  return selectedBook.value.pages
    .map((page, index) => ({ ...page, originalIndex: index }))
    .filter(page => page.originalIndex !== selectedPageIndex.value)
})

// 格式化时长
function formatDuration(seconds?: number): string {
  if (!seconds || seconds <= 0) return '点击查看'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  if (mins > 0) {
    return `约${mins}分${secs > 0 ? secs + '秒' : ''}`
  }
  return `约${secs}秒`
}

// 当前步骤是否可以继续
const canProceed = computed(() => {
  if (creationMode.value === 'standalone') {
    // 独立创作模式
    if (currentStep.value === 0) {
      return customPrompt.value.trim().length > 0
    }
    if (currentStep.value === 1) {
      return true
    }
  } else {
    // 基于绘本模式
    if (currentStep.value === 0) {
      return selectedBook.value && selectedBook.value.pages && selectedBook.value.pages.length > 0
    }
    if (currentStep.value === 1) {
      return selectedPageIndex.value !== null
    }
    if (currentStep.value === 2) {
      return true
    }
  }
  return false
})

// 按钮文字
const actionBtnText = computed(() => {
  if (generating.value) return '生成中...'
  if (loadingDetail.value) return '加载中...'
  if (generatingFirstFrame.value) return '生成首帧中...'

  if (creationMode.value === 'standalone') {
    // 独立创作模式
    if (currentStep.value === 0) {
      if (!customPrompt.value.trim()) return '请输入视频描述'
      return '下一步：配置参数'
    }
    return '开始生成视频'
  } else {
    // 基于绘本模式
    if (currentStep.value === 0) {
      if (!selectedBook.value) return '请选择绘本'
      if (!canProceed.value) return '绘本无内容'
      return '下一步：选择画面'
    }
    if (currentStep.value === 1) {
      if (selectedPageIndex.value === null) return '请选择首帧画面'
      return '下一步：配置参数'
    }
    return '开始生成视频'
  }
})

function goBack() {
  if (generating.value) {
    uni.showModal({
      title: '提示',
      content: '视频正在生成中，确定要离开吗？',
      success: (res) => {
        if (res.confirm) {
          stopPolling()
          generating.value = false
          currentTaskId.value = null
          uni.navigateBack()
        }
      }
    })
  } else {
    uni.navigateBack()
  }
}

function goToCreateBook() {
  uni.navigateTo({ url: '/pages/create/picture-book' })
}

function goToPrevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function handleNextStep() {
  if (!canProceed.value || generating.value || loadingDetail.value || generatingFirstFrame.value) return

  if (creationMode.value === 'standalone') {
    // 独立创作模式
    if (currentStep.value === 0) {
      currentStep.value = 1
    } else if (currentStep.value === 1) {
      handleStandaloneGenerate()
    }
  } else {
    // 基于绘本模式
    if (currentStep.value === 0) {
      currentStep.value = 1
      // 默认选择第一页作为首帧
      if (selectedBook.value?.pages?.length && selectedPageIndex.value === null) {
        selectedPageIndex.value = 0
      }
    } else if (currentStep.value === 1) {
      currentStep.value = 2
    } else if (currentStep.value === 2) {
      handleGenerate()
    }
  }
}

// 处理页面选择（首帧）
function handlePageSelect(index: number) {
  // 如果点击的是当前首帧，不做任何操作
  if (selectedPageIndex.value === index) return

  // 如果之前选的页面现在被设为首帧，从参考图中移除
  if (referencePageIndexes.value.includes(index)) {
    referencePageIndexes.value = referencePageIndexes.value.filter(i => i !== index)
  }

  selectedPageIndex.value = index
}

// 切换参考图选择
function toggleReference(index: number) {
  if (index === selectedPageIndex.value) return // 首帧不能作为参考图

  const currentIndex = referencePageIndexes.value.indexOf(index)
  if (currentIndex > -1) {
    referencePageIndexes.value.splice(currentIndex, 1)
  } else if (referencePageIndexes.value.length < maxReferenceCount) {
    referencePageIndexes.value.push(index)
  } else {
    uni.showToast({ title: `最多选择 ${maxReferenceCount} 张参考图`, icon: 'none' })
  }
}

// 处理场景模板选择 (Veo 3.1 专版)
function handleTemplateSelect(templateId: SceneTemplateId) {
  if (selectedTemplate.value === templateId) {
    selectedTemplate.value = null
    return
  }

  selectedTemplate.value = templateId
  const template = sceneTemplates.find(t => t.id === templateId)
  if (template) {
    // 自动填充参数 (仅 duration, resolution, motion_mode)
    selectedDuration.value = template.preset.duration
    selectedResolution.value = template.preset.resolution
    selectedMotionMode.value = template.preset.motion_mode
    // 注意: 新版文档中模板不再包含 negative_presets，保持用户已选择的设置

    uni.showToast({ title: `已应用「${template.name}」设置`, icon: 'none' })
  }
}

// 切换负面提示词预设
function toggleNegativePreset(presetId: NegativePresetId) {
  const index = selectedNegativePresets.value.indexOf(presetId)
  if (index > -1) {
    selectedNegativePresets.value.splice(index, 1)
  } else {
    selectedNegativePresets.value.push(presetId)
  }
}

async function selectBook(book: PictureBook) {
  // 重置选择状态
  selectedPageIndex.value = null
  referencePageIndexes.value = []
  endPageIndex.value = null
  selectedTemplate.value = null

  // 如果已经有完整的 pages 数据，直接使用
  if (book.pages && book.pages.length > 0) {
    selectedBook.value = book
    return
  }

  // 否则需要获取完整详情
  loadingDetail.value = true
  try {
    const fullBook = await getContentDetail(book.id)
    selectedBook.value = fullBook

    // 更新列表中的数据
    const index = pictureBooks.value.findIndex(b => b.id === book.id)
    if (index !== -1) {
      pictureBooks.value[index] = fullBook
    }
  } catch (e) {
    console.error('获取绘本详情失败:', e)
    uni.showToast({ title: '获取详情失败', icon: 'none' })
  } finally {
    loadingDetail.value = false
  }
}

async function loadPictureBooks() {
  loading.value = true
  try {
    const result = await getGeneratedList({ type: 'picture_book', limit: 50 })
    pictureBooks.value = result.items || []
  } catch (e) {
    console.error('加载绘本列表失败:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

// 轮询任务状态
let pollingTimer: number | null = null
let pollErrorCount = 0
const POLL_INTERVAL = 3000
const MAX_POLL_ERRORS = 10

function stopPolling() {
  if (pollingTimer) {
    clearTimeout(pollingTimer)
    pollingTimer = null
  }
  pollErrorCount = 0
}

async function pollTaskStatus(taskId: string) {
  try {
    const status = await getVideoTaskStatus(taskId)
    console.log('[视频生成] 状态:', status)

    pollErrorCount = 0
    generateProgress.value = status.progress || 0
    generatingStage.value = status.stage || ''
    generatingMessage.value = status.message || ''

    if (status.status === 'completed' && status.result) {
      stopPolling()
      generateProgress.value = 100
      generatingStage.value = 'completed'
      generatingMessage.value = '视频生成完成'

      uni.setStorageSync('temp_video', status.result)

      setTimeout(() => {
        generating.value = false
        currentTaskId.value = null
        uni.navigateTo({
          url: `/pages/play/video?id=${status.result!.id}&fromGenerate=1`
        })
      }, 500)
      return
    }

    if (status.status === 'failed') {
      stopPolling()
      generating.value = false
      currentTaskId.value = null
      const errMsg = status.error || '视频生成失败'
      uni.showToast({ title: errMsg, icon: 'none', duration: 3000 })
      return
    }

    pollingTimer = setTimeout(() => pollTaskStatus(taskId), POLL_INTERVAL) as unknown as number
  } catch (e: any) {
    console.error('[视频生成] 轮询错误:', e)
    pollErrorCount++

    generatingMessage.value = `网络不稳定，正在重试... (${pollErrorCount}/${MAX_POLL_ERRORS})`

    if (pollErrorCount >= MAX_POLL_ERRORS) {
      stopPolling()
      generating.value = false
      currentTaskId.value = null
      uni.showModal({
        title: '网络异常',
        content: '轮询超时次数过多，请检查网络后重试。任务可能仍在后台运行。',
        showCancel: false
      })
      return
    }

    const retryInterval = POLL_INTERVAL + pollErrorCount * 1000
    pollingTimer = setTimeout(() => pollTaskStatus(taskId), retryInterval) as unknown as number
  }
}

async function handleGenerate() {
  if (!canProceed.value || generating.value || loadingDetail.value) return

  const child = childStore.currentChild
  if (!child) {
    uni.showToast({ title: '请先添加宝贝信息', icon: 'none' })
    return
  }

  if (!selectedBook.value?.pages || selectedBook.value.pages.length === 0) {
    uni.showToast({ title: '绘本内容为空，无法生成视频', icon: 'none' })
    return
  }

  if (selectedPageIndex.value === null) {
    uni.showToast({ title: '请选择首帧画面', icon: 'none' })
    return
  }

  generating.value = true
  generateProgress.value = 0
  generatingStage.value = 'init'
  generatingMessage.value = '正在提交任务...'

  try {
    // 准备参数
    const pages: VideoPage[] = (selectedBook.value.pages || []).map((page, index) => ({
      page_num: index + 1,
      text: page.text,
      image_url: page.image_url,
      audio_url: page.audio_url
    }))

    const selectedPage = selectedBook.value.pages[selectedPageIndex.value]

    // 构建负面提示词
    const negativePromptValues = selectedNegativePresets.value
      .map(id => negativePresetOptions.find(p => p.id === id)?.value)
      .filter(Boolean)
      .join(', ')

    // 构建参考图 URL 列表
    const referenceImageUrls = referencePageIndexes.value
      .map(idx => selectedBook.value?.pages?.[idx]?.image_url)
      .filter(Boolean) as string[]

    const params = {
      picture_book: {
        title: selectedBook.value.title,
        pages
      },
      child_name: child.name,
      theme_topic: selectedBook.value.theme_topic || '',
      theme_category: selectedBook.value.theme_category || 'habit',
      // 基础视频配置
      aspect_ratio: selectedAspectRatio.value,
      resolution: selectedResolution.value,
      duration_seconds: selectedDuration.value,
      motion_mode: selectedMotionMode.value,
      // enable_audio: audioEnabled.value,  // Veo 3.1 暂不支持自定义音效，暂时不发送此参数
      // Veo 3.1 增强参数
      image_url: selectedPage.image_url,
      prompt: selectedPage.text,
      reference_images: referenceImageUrls.length > 0 ? referenceImageUrls : undefined,
      scene_template: selectedTemplate.value || undefined,
      auto_enhance_prompt: autoEnhancePrompt.value,
      negative_prompt: negativePromptValues || undefined,
      last_frame_url: endPageIndex.value !== null
        ? selectedBook.value.pages[endPageIndex.value]?.image_url
        : undefined
    }

    // 提交异步任务
    const response = await generateVideoAsync(params)
    console.log('[视频生成] 任务已提交:', response.task_id)

    currentTaskId.value = response.task_id
    generatingMessage.value = '任务已提交，正在生成...'

    // 开始轮询
    pollTaskStatus(response.task_id)

  } catch (e: any) {
    console.error('提交视频任务失败:', e)
    generating.value = false
    currentTaskId.value = null

    const errMsg = e?.message || '提交失败，请重试'
    uni.showToast({ title: errMsg, icon: 'none', duration: 3000 })
  }
}

// 独立创作模式：生成首帧
async function handleGenerateFirstFrame() {
  if (!customPrompt.value.trim()) {
    uni.showToast({ title: '请输入视频描述', icon: 'none' })
    return
  }

  const child = childStore.currentChild
  if (!child) {
    uni.showToast({ title: '请先添加宝贝信息', icon: 'none' })
    return
  }

  generatingFirstFrame.value = true
  generatedFirstFrame.value = null

  try {
    const result = await generateFirstFrame({
      prompt: customPrompt.value,
      child_name: child.name,
      art_style: selectedArtStyle.value,
      aspect_ratio: selectedAspectRatio.value as '16:9' | '9:16' | '1:1'
    })

    generatedFirstFrame.value = result.image_url
    uni.showToast({ title: '首帧生成成功', icon: 'success' })
  } catch (e: any) {
    console.error('生成首帧失败:', e)
    uni.showToast({ title: e?.message || '生成首帧失败', icon: 'none' })
  } finally {
    generatingFirstFrame.value = false
  }
}

// 独立创作模式：生成视频
async function handleStandaloneGenerate() {
  if (!customPrompt.value.trim()) {
    uni.showToast({ title: '请输入视频描述', icon: 'none' })
    return
  }

  const child = childStore.currentChild
  if (!child) {
    uni.showToast({ title: '请先添加宝贝信息', icon: 'none' })
    return
  }

  generating.value = true
  generateProgress.value = 0
  generatingStage.value = 'init'
  generatingMessage.value = '正在提交任务...'

  try {
    // 构建负面提示词
    const negativePromptValues = selectedNegativePresets.value
      .map(id => negativePresetOptions.find(p => p.id === id)?.value)
      .filter(Boolean)
      .join(', ')

    const params = {
      child_name: child.name,
      age_months: child.age_months || 36,
      custom_prompt: customPrompt.value,
      first_frame_url: generatedFirstFrame.value || undefined,
      generate_first_frame: !generatedFirstFrame.value,
      aspect_ratio: selectedAspectRatio.value as '16:9' | '9:16' | '4:3' | '3:4' | '1:1',
      resolution: selectedResolution.value as '720P' | '1080P',
      duration_seconds: selectedDuration.value as 4 | 5 | 6 | 8,
      motion_mode: selectedMotionMode.value as 'static' | 'slow' | 'normal' | 'dynamic' | 'cinematic',
      enable_audio: audioEnabled.value,
      art_style: selectedArtStyle.value,
      auto_enhance_prompt: autoEnhancePrompt.value,
      negative_prompt: negativePromptValues || undefined,
      scene_template: selectedTemplate.value || undefined
    }

    const response = await generateStandaloneVideoAsync(params)
    console.log('[独立视频生成] 任务已提交:', response.task_id)

    currentTaskId.value = response.task_id
    generatingMessage.value = '任务已提交，正在生成...'

    // 开始轮询（复用相同的轮询逻辑）
    pollTaskStatus(response.task_id)

  } catch (e: any) {
    console.error('提交独立视频任务失败:', e)
    generating.value = false
    currentTaskId.value = null

    const errMsg = e?.message || '提交失败，请重试'
    uni.showToast({ title: errMsg, icon: 'none', duration: 3000 })
  }
}

// 切换创作模式
function switchCreationMode(mode: 'from_book' | 'standalone') {
  creationMode.value = mode
  currentStep.value = 0
  // 重置状态
  selectedBook.value = null
  selectedPageIndex.value = null
  referencePageIndexes.value = []
  generatedFirstFrame.value = null
}

// 模式选择处理（来自 CreationModeSelector 组件）
function handleModeSelect(mode: 'preset' | 'smart', prompt?: string) {
  showModeSelector.value = false

  if (mode === 'smart') {
    // 智能创作模式 -> 独立创作
    creationMode.value = 'standalone'
    if (prompt) {
      customPrompt.value = prompt
    }
  } else {
    // 预设模式 -> 基于绘本
    creationMode.value = 'from_book'
  }

  currentStep.value = 0
}

onLoad((options) => {
  const sysInfo = uni.getSystemInfoSync()
  statusBarHeight.value = sysInfo.statusBarHeight || 20
  navHeight.value = statusBarHeight.value + 44

  // 从智能创作页面跳转过来（带完整参数）
  if (options?.creation_mode === 'smart' && options?.custom_prompt) {
    showModeSelector.value = false  // 隐藏模式选择器
    creationMode.value = 'standalone'
    customPrompt.value = decodeURIComponent(options.custom_prompt)

    if (options.art_style) {
      selectedArtStyle.value = options.art_style as ArtStyle
    }
    if (options.duration) {
      selectedDuration.value = parseInt(options.duration) || 5
    }

    // 直接进入配置步骤
    setTimeout(() => {
      currentStep.value = 1
    }, 100)

    return
  }

  // 处理旧版参数（兼容）
  if (options?.mode === 'standalone') {
    showModeSelector.value = false
    creationMode.value = 'standalone'
  }
  if (options?.custom_prompt) {
    customPrompt.value = decodeURIComponent(options.custom_prompt)
  }
  if (options?.art_style) {
    selectedArtStyle.value = options.art_style as ArtStyle
  }
  if (options?.duration) {
    selectedDuration.value = parseInt(options.duration) || 5
  }

  // 如果有任何参数，隐藏模式选择器
  if (options?.mode || options?.custom_prompt || options?.book_id) {
    showModeSelector.value = false
  }
})

onMounted(() => {
  loadPictureBooks()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

// 模式切换 Tab
.mode-tabs {
  display: flex;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  padding: $spacing-xs;
  box-shadow: $shadow-card;
}

.mode-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-md;
  transition: all $duration-base;

  &.active {
    background: $video-gradient;
    box-shadow: $shadow-colored-video;

    .tab-text {
      color: $text-white;
      font-weight: $font-semibold;
    }

    .tab-icon {
      transform: scale(1.1);
    }
  }

  &:active:not(.active) {
    background: rgba($video-primary, 0.08);
  }
}

.tab-icon {
  font-size: 28rpx;
  transition: transform $duration-base;
}

.tab-text {
  font-size: $font-sm;
  color: $text-secondary;
  transition: color $duration-base;
}

// 独立创作输入区域
.standalone-input-area {
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  padding: $spacing-md;
  box-shadow: $shadow-card;
}

.input-container {
  position: relative;
  margin-bottom: $spacing-md;
}

.prompt-input {
  width: 100%;
  min-height: 160rpx;
  padding: $spacing-md;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  font-size: $font-base;
  color: $text-primary;
  line-height: 1.6;
  box-sizing: border-box;

  &::placeholder {
    color: $text-placeholder;
  }
}

.input-footer {
  position: absolute;
  bottom: $spacing-sm;
  right: $spacing-md;
}

.char-count {
  font-size: $font-xs;
  color: $text-placeholder;
}

// 首帧预览
.first-frame-preview {
  margin-bottom: $spacing-md;
}

.preview-label {
  display: block;
  font-size: $font-sm;
  font-weight: $font-medium;
  color: $text-secondary;
  margin-bottom: $spacing-sm;
}

.first-frame-preview .preview-image {
  width: 100%;
  height: 300rpx;
  border-radius: $radius-md;
  background: $bg-soft;
}

.preview-actions {
  display: flex;
  justify-content: center;
  margin-top: $spacing-sm;
}

.regenerate-btn {
  padding: $spacing-xs $spacing-md;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-full;

  text {
    font-size: $font-sm;
    color: $text-secondary;
  }

  &:active {
    background: $border-light;
  }
}

.generate-first-frame-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-md;
  background: rgba($video-primary, 0.1);
  border: 1rpx dashed $video-primary;
  border-radius: $radius-md;
  margin-bottom: $spacing-sm;

  text {
    font-size: $font-base;
    color: $video-primary;
  }

  &.disabled {
    background: $bg-soft;
    border-color: $border-light;

    text {
      color: $text-placeholder;
    }
  }

  &:active:not(.disabled) {
    background: rgba($video-primary, 0.15);
  }
}

.first-frame-hint {
  display: block;
  font-size: $font-xs;
  color: $text-tertiary;
  text-align: center;
}

// 预览占位符
.preview-placeholder {
  width: 120rpx;
  height: 120rpx;
  border-radius: $radius-md;
  background: $bg-soft;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  text {
    font-size: 48rpx;
  }
}

.page-container {
  min-height: 100vh;
  background: $bg-cream;
  width: 750rpx;
  box-sizing: border-box;
  overflow-x: hidden;
  position: relative;
}

// 装饰背景
.decor-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 750rpx;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.decor-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.12;
}

.shape-1 {
  width: 300rpx;
  height: 300rpx;
  background: radial-gradient(circle, $video-primary 0%, transparent 70%);
  top: -80rpx;
  right: -60rpx;
  animation: floatDecor 15s ease-in-out infinite;
}

.shape-2 {
  width: 200rpx;
  height: 200rpx;
  background: radial-gradient(circle, $song-primary 0%, transparent 70%);
  bottom: 30%;
  left: -40rpx;
  animation: floatDecor 18s ease-in-out infinite reverse;
}

.shape-3 {
  width: 150rpx;
  height: 150rpx;
  background: radial-gradient(circle, $book-primary 0%, transparent 70%);
  top: 40%;
  right: -30rpx;
  animation: floatDecor 20s ease-in-out infinite 2s;
}

@keyframes floatDecor {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(20rpx, -15rpx) scale(1.05); }
}

.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  z-index: $z-sticky;
  background: rgba($bg-card, 0.95);
  width: 750rpx;
  box-sizing: border-box;
  border-bottom: 1rpx solid $border-light;
}

.nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  padding: 0 $spacing-md;
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;

  text {
    font-size: 48rpx;
    color: $text-primary;
    line-height: 1;
  }
}

.nav-title {
  font-size: $font-md;
  font-weight: $font-semibold;
  color: $text-primary;
}

.nav-right {
  width: 64rpx;
}

.nav-placeholder {
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.main-scroll {
  width: 750rpx;
  padding: $spacing-lg $spacing-md;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}

// 步骤指示器 - 3步
.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: $spacing-xl;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  padding: $spacing-md $spacing-sm;
  box-shadow: $shadow-card;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
  opacity: 0.5;
  transition: opacity $duration-base;

  &.active {
    opacity: 1;
  }

  &.completed .step-dot {
    background: $success;
    font-size: $font-xs;
  }
}

.step-dot {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: $border-light;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-sm;
  font-weight: $font-bold;
  color: $text-tertiary;
  transition: all $duration-base;

  .active & {
    background: $video-primary;
    color: $text-white;
    box-shadow: $shadow-colored-video;
  }
}

.step-text {
  font-size: 20rpx;
  color: $text-tertiary;
  white-space: nowrap;

  .active & {
    color: $text-primary;
  }
}

.step-line {
  width: 60rpx;
  height: 4rpx;
  background: $border-light;
  margin: 0 $spacing-xs;
  margin-bottom: 28rpx;
  transition: background $duration-base;
  border-radius: 2rpx;

  &.active {
    background: $video-primary;
  }
}

// 区块
.section {
  margin-bottom: $spacing-xl;
}

.section-title {
  display: block;
  font-size: $font-lg;
  font-weight: $font-bold;
  color: $text-primary;
  margin-bottom: $spacing-xs;
}

.section-desc {
  display: block;
  font-size: $font-sm;
  color: $text-tertiary;
  margin-bottom: $spacing-md;
}

// 加载状态
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-xl;
  gap: $spacing-sm;

  text {
    font-size: $font-base;
    color: $text-tertiary;
  }
}

.loading-icon {
  font-size: 48rpx;
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-xl;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  box-shadow: $shadow-card;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: $spacing-sm;
}

.empty-title {
  font-size: $font-md;
  font-weight: $font-semibold;
  color: $text-primary;
  margin-bottom: $spacing-xs;
}

.empty-desc {
  font-size: $font-sm;
  color: $text-tertiary;
  margin-bottom: $spacing-md;
}

.empty-action {
  padding: $spacing-sm $spacing-lg;
  background: $video-gradient;
  border-radius: $radius-lg;
  box-shadow: $shadow-colored-video;

  text {
    font-size: $font-base;
    font-weight: $font-semibold;
    color: $text-white;
  }

  &:active {
    transform: scale(0.95);
  }
}

// 绘本列表
.book-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.book-card {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-md;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  transition: all $duration-base;
  box-shadow: $shadow-card;

  &.selected {
    border-color: $video-primary;
    background: rgba($video-primary, 0.08);
    box-shadow: $shadow-colored-video;
  }

  &:active {
    transform: scale(0.98);
  }
}

.book-cover {
  position: relative;
  width: 140rpx;
  height: 140rpx;
  border-radius: $radius-md;
  overflow: hidden;
  flex-shrink: 0;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-soft;

  text {
    font-size: 56rpx;
  }
}

.selected-badge {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: $video-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-colored-video;

  text {
    font-size: 22rpx;
    color: $text-white;
    font-weight: $font-bold;
  }
}

.book-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: $spacing-xs;
}

.book-title {
  font-size: $font-md;
  font-weight: $font-semibold;
  color: $text-primary;
}

.book-meta {
  font-size: $font-sm;
  color: $text-tertiary;
}

// 页面选择器
.page-selector {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
  margin-bottom: $spacing-lg;
}

.page-thumb {
  position: relative;
  width: calc((100% - #{$spacing-sm} * 3) / 4);
  aspect-ratio: 1;
  border-radius: $radius-md;
  overflow: hidden;
  border: 3rpx solid transparent;
  transition: all $duration-base;

  &.is-first-frame {
    border-color: $video-primary;
    box-shadow: $shadow-colored-video;
  }

  &.is-reference {
    border-color: $success;
    box-shadow: 0 4rpx 12rpx rgba($success, 0.3);
  }

  &:active {
    transform: scale(0.95);
  }
}

.thumb-image {
  width: 100%;
  height: 100%;
}

.thumb-badge {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 4rpx 0;
  text-align: center;
  font-size: 18rpx;
  color: $text-white;
  font-weight: $font-medium;

  &.first-frame {
    background: $video-primary;
  }

  &.reference {
    background: $success;
  }
}

.thumb-num {
  position: absolute;
  bottom: 4rpx;
  right: 6rpx;
  font-size: 18rpx;
  color: $text-white;
  text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.5);
}

// 参考图选择
.reference-section {
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  padding: $spacing-md;
  margin-bottom: $spacing-md;
}

.reference-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: $spacing-xs;
}

.reference-title {
  font-size: $font-base;
  font-weight: $font-semibold;
  color: $text-primary;
}

.reference-hint {
  font-size: $font-xs;
  color: $text-tertiary;
}

.reference-desc {
  display: block;
  font-size: $font-xs;
  color: $text-tertiary;
  margin-bottom: $spacing-md;
}

.reference-list {
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

.reference-thumb {
  position: relative;
  width: 100rpx;
  height: 100rpx;
  border-radius: $radius-sm;
  overflow: hidden;
  border: 2rpx solid $border-light;
  transition: all $duration-base;

  &.selected {
    border-color: $success;
    box-shadow: 0 4rpx 12rpx rgba($success, 0.3);
  }

  &:active {
    transform: scale(0.95);
  }
}

.ref-check {
  position: absolute;
  top: 4rpx;
  right: 4rpx;
  width: 28rpx;
  height: 28rpx;
  border-radius: 50%;
  background: $success;
  display: flex;
  align-items: center;
  justify-content: center;

  text {
    font-size: 18rpx;
    color: $text-white;
    font-weight: $font-bold;
  }
}

// 预览卡片
.preview-card {
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  padding: $spacing-md;
  box-shadow: $shadow-card;
  margin-bottom: $spacing-lg;
}

.preview-header {
  display: flex;
  gap: $spacing-md;
  align-items: center;
}

.preview-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: $radius-md;
  flex-shrink: 0;
}

.preview-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.preview-title {
  font-size: $font-md;
  font-weight: $font-semibold;
  color: $text-primary;
}

.preview-meta {
  font-size: $font-sm;
  color: $text-tertiary;
}

.preview-tip {
  display: block;
  font-size: $font-xs;
  color: $text-tertiary;
  text-align: center;
  margin-top: $spacing-md;
}

// 场景模板
.template-list {
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

.template-card {
  position: relative;
  width: calc((100% - #{$spacing-sm} * 2) / 3);
  padding: $spacing-sm;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  transition: all $duration-base;
  box-shadow: $shadow-sm;

  &.active {
    border-color: $video-primary;
    background: rgba($video-primary, 0.08);
    box-shadow: $shadow-colored-video;
  }

  &.recommended {
    border-color: rgba($video-primary, 0.3);
  }

  &:active {
    transform: scale(0.96);
  }
}

.recommend-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  background: linear-gradient(135deg, #FF6B6B, #FF8E53);
  color: white;
  font-size: 18rpx;
  padding: 4rpx 10rpx;
  border-radius: 12rpx;
  font-weight: 600;
  box-shadow: 0 2rpx 8rpx rgba(255, 107, 107, 0.4);
}

.template-icon {
  font-size: 36rpx;
}

.template-name {
  font-size: $font-xs;
  font-weight: $font-semibold;
  color: $text-primary;
  text-align: center;
}

.template-desc {
  font-size: 18rpx;
  color: $text-tertiary;
  text-align: center;
  line-height: 1.3;
}

.template-check {
  position: absolute;
  top: 4rpx;
  right: 4rpx;
  width: 28rpx;
  height: 28rpx;
  border-radius: 50%;
  background: $video-primary;
  display: flex;
  align-items: center;
  justify-content: center;

  text {
    font-size: 18rpx;
    color: $text-white;
    font-weight: $font-bold;
  }
}

// 风格选择区块
.style-section {
  margin-top: $spacing-lg;
}

.style-title {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: $font-base;
  font-weight: $font-semibold;
  color: $text-primary;
  margin-bottom: $spacing-sm;

  .title-icon {
    font-size: $font-md;
  }
}

.style-hint {
  display: block;
  font-size: $font-xs;
  color: $text-tertiary;
  margin-bottom: $spacing-md;
  margin-top: -$spacing-xs;
}

// 宽高比选择
.aspect-ratio-list {
  display: flex;
  gap: $spacing-xs;
  flex-wrap: wrap;
}

.aspect-ratio-item {
  flex: 1;
  min-width: 110rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-sm;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  transition: all $duration-base;
  position: relative;
  box-shadow: $shadow-sm;

  &.active {
    border-color: $video-primary;
    background: rgba($video-primary, 0.08);
    box-shadow: $shadow-colored-video;
  }

  &:active {
    transform: scale(0.96);
  }
}

.ratio-preview {
  width: 40rpx;
  max-height: 40rpx;
  background: linear-gradient(135deg, rgba($video-primary, 0.3), rgba($video-primary, 0.1));
  border: 2rpx solid rgba($video-primary, 0.5);
  border-radius: $radius-xs;
}

.ratio-label {
  font-size: 20rpx;
  font-weight: $font-medium;
  color: $text-primary;
  text-align: center;
}

.ratio-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  padding: 4rpx 8rpx;
  background: $video-primary;
  border-radius: $radius-sm;
  font-size: 16rpx;
  color: $text-white;
  font-weight: $font-medium;
}

// 运动模式选择
.motion-mode-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.motion-mode-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-md;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  transition: all $duration-base;
  position: relative;
  box-shadow: $shadow-sm;

  &.active {
    border-color: $video-primary;
    background: rgba($video-primary, 0.08);
    box-shadow: $shadow-colored-video;
  }

  &:active {
    transform: scale(0.98);
  }
}

.mode-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.mode-name {
  font-size: $font-base;
  font-weight: $font-semibold;
  color: $text-primary;
}

.mode-desc {
  font-size: $font-xs;
  color: $text-tertiary;
  line-height: 1.4;
}

.mode-badge {
  padding: 4rpx 12rpx;
  background: rgba($video-primary, 0.15);
  border-radius: $radius-sm;
  font-size: 20rpx;
  color: $video-primary;
  font-weight: $font-medium;
}

.mode-check {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: $video-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: $shadow-colored-video;

  text {
    font-size: 22rpx;
    color: $text-white;
    font-weight: $font-bold;
  }
}

// 分辨率选择
.resolution-tabs {
  display: flex;
  gap: $spacing-sm;
}

.resolution-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  padding: $spacing-md;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  transition: all $duration-base;
  position: relative;
  box-shadow: $shadow-sm;

  &.active {
    border-color: $video-primary;
    background: rgba($video-primary, 0.08);
    box-shadow: $shadow-colored-video;

    .res-value {
      color: $video-primary;
    }
  }

  &:active {
    transform: scale(0.96);
  }
}

.res-value {
  font-size: $font-base;
  font-weight: $font-semibold;
  color: $text-primary;
  transition: color $duration-base;
}

.res-note {
  font-size: 20rpx;
  color: $text-tertiary;
}

.res-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  padding: 4rpx 12rpx;
  background: $video-primary;
  border-radius: $radius-sm;
  font-size: 20rpx;
  color: $text-white;
  font-weight: $font-medium;
}

// 时长选择
.duration-tabs {
  display: flex;
  gap: $spacing-xs;
  background: $bg-soft;
  padding: $spacing-xs;
  border-radius: $radius-md;
  border: 1rpx solid $border-light;
}

.duration-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  padding: $spacing-sm $spacing-xs;
  border-radius: $radius-sm;
  transition: all $duration-base;

  &.active {
    background: rgba($video-primary, 0.12);
    box-shadow: $shadow-sm;

    .dur-value {
      color: $video-primary;
    }
  }

  &:active {
    transform: scale(0.96);
  }
}

.dur-value {
  font-size: $font-sm;
  font-weight: $font-semibold;
  color: $text-primary;
  transition: color $duration-base;
}

.dur-desc {
  font-size: 20rpx;
  color: $text-tertiary;
}

// 音效开关
.audio-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-md;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;
}

.audio-info {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.audio-label {
  font-size: $font-base;
  font-weight: $font-semibold;
  color: $text-primary;
}

.audio-desc {
  font-size: $font-xs;
  color: $text-tertiary;
}

// 高级设置
.advanced-section {
  margin-top: $spacing-lg;
  background: $bg-card;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;
  overflow: hidden;
}

.advanced-header {
  padding: $spacing-md;
  display: flex;
  align-items: center;

  &:active {
    background: rgba($video-primary, 0.05);
  }
}

.advanced-title {
  font-size: $font-base;
  font-weight: $font-semibold;
  color: $text-primary;
}

.advanced-content {
  border-top: 1rpx solid $border-light;
  padding: $spacing-md;
}

.advanced-item {
  margin-bottom: $spacing-lg;

  &:last-child {
    margin-bottom: 0;
  }
}

.advanced-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.advanced-info {
  flex: 1;
}

.advanced-label {
  display: block;
  font-size: $font-base;
  font-weight: $font-medium;
  color: $text-primary;
  margin-bottom: 4rpx;
}

.advanced-desc {
  display: block;
  font-size: $font-xs;
  color: $text-tertiary;
  margin-bottom: $spacing-sm;
}

// 负面提示词预设
.negative-presets {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
}

.negative-chip {
  padding: $spacing-xs $spacing-sm;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  transition: all $duration-base;

  text {
    font-size: $font-xs;
    color: $text-secondary;
  }

  &.active {
    background: rgba($video-primary, 0.12);
    border-color: $video-primary;

    text {
      color: $video-primary;
      font-weight: $font-medium;
    }
  }

  &:active {
    transform: scale(0.95);
  }
}

// 结束帧选择
.end-frame-selector {
  display: flex;
  gap: $spacing-xs;
  flex-wrap: wrap;
}

.end-frame-option {
  padding: $spacing-sm $spacing-md;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-md;
  transition: all $duration-base;

  &.active {
    background: rgba($video-primary, 0.12);
    border-color: $video-primary;

    .end-frame-text {
      color: $video-primary;
      font-weight: $font-medium;
    }
  }

  &:active {
    transform: scale(0.95);
  }
}

.end-frame-text {
  font-size: $font-xs;
  color: $text-secondary;
}

.end-frame-thumb {
  position: relative;
  width: 80rpx;
  height: 80rpx;
  border-radius: $radius-sm;
  overflow: hidden;
  border: 2rpx solid $border-light;
  transition: all $duration-base;

  &.active {
    border-color: $video-primary;
    box-shadow: $shadow-colored-video;
  }

  &:active {
    transform: scale(0.95);
  }
}

.end-check {
  position: absolute;
  top: 4rpx;
  right: 4rpx;
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  background: $video-primary;
  display: flex;
  align-items: center;
  justify-content: center;

  text {
    font-size: 16rpx;
    color: $text-white;
    font-weight: $font-bold;
  }
}

// 底部
.bottom-placeholder {
  height: 180rpx;
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: $spacing-md;
  padding-bottom: calc(#{$spacing-md} + env(safe-area-inset-bottom));
  background: rgba($bg-card, 0.98);
  border-top: 1rpx solid $border-light;
  z-index: $z-sticky;
  display: flex;
  gap: $spacing-sm;
}

.step-back-btn {
  padding: 0 $spacing-lg;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-soft;
  border: 1rpx solid $border-light;
  border-radius: $radius-lg;

  text {
    font-size: $font-md;
    font-weight: $font-medium;
    color: $text-secondary;
  }

  &:active {
    transform: scale(0.98);
    background: $border-light;
  }
}

.generate-btn {
  flex: 1;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $video-gradient;
  border-radius: $radius-lg;
  box-shadow: $shadow-colored-video;

  text {
    font-size: $font-md;
    font-weight: $font-bold;
    color: $text-white;
  }

  &.disabled {
    background: $border-light;
    box-shadow: none;

    text {
      color: $text-tertiary;
    }
  }

  &:active:not(.disabled) {
    transform: scale(0.98);
  }

  &.flex-1 {
    flex: 1;
  }
}

// 动画
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
