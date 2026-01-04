/**
 * 创作状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  ArtStyle,
  ProtagonistConfig,
  ColorPalette,
  ThemeList,
  StyleOptions,
  TaskStatus
} from '@/api/create'
import {
  DEFAULT_THEMES,
  getStyleOptions,
  generatePictureBookAsync,
  getPictureBookTaskStatus,
  generateNurseryRhymeAsync,
  getNurseryRhymeTaskStatus,
  generateStandaloneVideoAsync,
  getVideoTaskStatus
} from '@/api/create'
import { useChildStore } from './child'

export const useCreateStore = defineStore('create', () => {
  // ========== 基础数据 ==========
  const themes = ref<ThemeList | null>(null)
  const styleOptions = ref<StyleOptions | null>(null)
  const isLoadingOptions = ref(false)

  // ========== 当前步骤 ==========
  const currentStep = ref(1)

  // ========== 绘本参数 ==========
  const pictureBookParams = ref({
    // 创作模式：preset（预设主题）或 smart（智能创作）
    creationMode: 'preset' as 'preset' | 'smart',
    // 预设模式参数
    themeCategory: '',
    themeTopic: '',
    // 智能模式参数
    customPrompt: '',
    // 共用参数
    artStyle: 'pixar_3d' as string,
    protagonist: {
      animal: 'bunny',
      color: 'white',
      accessory: 'blue overalls'
    } as ProtagonistConfig,
    colorPalette: 'pastel' as string,
    voiceId: 'Kore',
    // 故事增强参数
    storyEnhancement: {
      narrative_pace: null as string | null,
      interaction_density: null as string | null,
      educational_focus: null as string | null,
      language_style: null as string | null,
      plot_complexity: null as string | null,
      ending_style: null as string | null
    },
    // 视觉增强参数
    visualEnhancement: {
      time_atmosphere: null as string | null,
      scene_environment: null as string | null,
      emotional_tone: null as string | null,
      composition_style: null as string | null,
      lighting_effect: null as string | null
    }
  })

  // ========== 儿歌参数 ==========
  const nurseryRhymeParams = ref({
    // 创作模式：preset（预设主题）或 smart（智能创作）
    creationMode: 'preset' as 'preset' | 'smart',
    // 预设模式参数
    themeCategory: '',
    themeTopic: '',
    // 智能模式参数
    customPrompt: '',
    // 共用参数
    musicMood: 'cheerful',
    musicGenre: '' as string,
    tempo: 100,
    energyLevel: 5,
    vocalType: 'soft_female',
    vocalEmotion: 'happy',
    vocalRange: '' as string,
    vocalStyle: '' as string,
    instruments: [] as string[],
    soundEffects: [] as string[],
    lyricComplexity: 5,
    repetitionLevel: 6,
    songStructure: 'simple',
    actionTypes: '' as string,
    language: 'mandarin',
    culturalStyle: '' as string,
    educationalFocus: '' as string,
    favoriteColors: [] as string[],
    styleWeight: 0.5,
    creativity: 0.5,
    negativeTags: '' as string,
    durationPreference: 60
  })

  // ========== 视频参数 ==========
  const videoParams = ref({
    // 创作模式
    creationMode: 'standalone' as 'standalone' | 'from_book',
    // 基于绘本模式的参数
    selectedBookId: null as string | null,
    selectedPageIndex: null as number | null,
    referencePageIndexes: [] as number[],
    // 独立创作模式的参数
    customPrompt: '',
    generatedFirstFrame: null as string | null,
    // 共用参数
    aspectRatio: '16:9' as '16:9' | '9:16' | '4:3' | '3:4' | '1:1',
    resolution: '720P' as '720P' | '1080P',
    durationSeconds: 5 as 4 | 5 | 6 | 8,
    motionMode: 'normal' as 'static' | 'slow' | 'normal' | 'dynamic' | 'cinematic',
    enableAudio: true,
    artStyle: 'pixar_3d' as string,
    // 场景模板
    sceneTemplate: 'storybook' as string,
    // 高级设置
    autoEnhancePrompt: true
  })

  // ========== 生成状态 ==========
  const currentTaskId = ref<string | null>(null)
  const generatingStatus = ref<'idle' | 'pending' | 'processing' | 'completed' | 'failed'>('idle')
  const generatingProgress = ref(0)
  const generatingStage = ref('')
  const generatingError = ref('')
  const generatedContentId = ref<string | null>(null)

  // 轮询定时器
  let pollTimer: ReturnType<typeof setInterval> | null = null

  // ========== 计算属性 ==========
  const isGenerating = computed(() =>
    generatingStatus.value === 'pending' || generatingStatus.value === 'processing'
  )

  // ========== 方法 ==========

  /**
   * 加载主题和风格选项
   */
  async function loadOptions() {
    if (themes.value && styleOptions.value) return

    isLoadingOptions.value = true
    try {
      // 主题使用前端本地数据，不依赖后端
      themes.value = DEFAULT_THEMES
      // 风格选项从后端获取，有默认值兜底
      styleOptions.value = await getStyleOptions()
    } catch (e) {
      console.error('加载选项失败:', e)
    } finally {
      isLoadingOptions.value = false
    }
  }

  /**
   * 重置创作参数
   */
  function resetParams(type: 'picture_book' | 'nursery_rhyme' | 'video') {
    currentStep.value = 1
    generatingStatus.value = 'idle'
    generatingProgress.value = 0
    generatingStage.value = ''
    generatingError.value = ''
    currentTaskId.value = null
    generatedContentId.value = null

    if (type === 'picture_book') {
      pictureBookParams.value = {
        creationMode: 'preset',
        themeCategory: '',
        themeTopic: '',
        customPrompt: '',
        artStyle: 'pixar_3d',
        protagonist: { animal: 'bunny', color: 'white', accessory: 'blue overalls' },
        colorPalette: 'pastel',
        voiceId: 'Kore',
        storyEnhancement: {
          narrative_pace: null,
          interaction_density: null,
          educational_focus: null,
          language_style: null,
          plot_complexity: null,
          ending_style: null
        },
        visualEnhancement: {
          time_atmosphere: null,
          scene_environment: null,
          emotional_tone: null,
          composition_style: null,
          lighting_effect: null
        }
      }
    } else if (type === 'nursery_rhyme') {
      nurseryRhymeParams.value = {
        creationMode: 'preset',
        themeCategory: '',
        themeTopic: '',
        customPrompt: '',
        musicMood: 'cheerful',
        musicGenre: '',
        tempo: 100,
        energyLevel: 5,
        vocalType: 'soft_female',
        vocalEmotion: 'happy',
        vocalRange: '',
        vocalStyle: '',
        instruments: [],
        soundEffects: [],
        lyricComplexity: 5,
        repetitionLevel: 6,
        songStructure: 'simple',
        actionTypes: '',
        language: 'mandarin',
        culturalStyle: '',
        educationalFocus: '',
        favoriteColors: [],
        styleWeight: 0.5,
        creativity: 0.5,
        negativeTags: '',
        durationPreference: 60
      }
    } else if (type === 'video') {
      videoParams.value = {
        creationMode: 'standalone',
        selectedBookId: null,
        selectedPageIndex: null,
        referencePageIndexes: [],
        customPrompt: '',
        generatedFirstFrame: null,
        aspectRatio: '16:9',
        resolution: '720P',
        durationSeconds: 5,
        motionMode: 'normal',
        enableAudio: true,
        artStyle: 'pixar_3d',
        sceneTemplate: 'storybook',
        autoEnhancePrompt: true
      }
    }
  }

  /**
   * 停止轮询
   */
  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  /**
   * 开始轮询任务状态
   */
  function startPolling(
    taskId: string,
    getStatus: (id: string) => Promise<TaskStatus & { result?: any }>
  ) {
    stopPolling()

    pollTimer = setInterval(async () => {
      try {
        const status = await getStatus(taskId)
        generatingProgress.value = status.progress
        generatingStage.value = status.stage

        if (status.status === 'completed') {
          generatingStatus.value = 'completed'
          generatedContentId.value = status.content_id || null
          stopPolling()
        } else if (status.status === 'failed') {
          generatingStatus.value = 'failed'
          generatingError.value = status.error || '生成失败'
          stopPolling()
        } else {
          generatingStatus.value = status.status
        }
      } catch (e) {
        console.error('轮询状态失败:', e)
      }
    }, 3000)
  }

  /**
   * 生成绘本
   */
  async function generatePictureBook() {
    const childStore = useChildStore()
    const child = childStore.currentChild
    if (!child) throw new Error('请先选择孩子')

    const params = pictureBookParams.value

    // 验证参数
    if (params.creationMode === 'preset') {
      if (!params.themeCategory || !params.themeTopic) {
        throw new Error('请选择主题')
      }
    } else if (params.creationMode === 'smart') {
      if (!params.customPrompt) {
        throw new Error('请输入创意描述')
      }
    }

    generatingStatus.value = 'pending'
    generatingProgress.value = 0
    generatingError.value = ''

    try {
      // 过滤掉空值的增强参数
      const storyEnhancement = Object.fromEntries(
        Object.entries(params.storyEnhancement).filter(([_, v]) => v !== null)
      )
      const visualEnhancement = Object.fromEntries(
        Object.entries(params.visualEnhancement).filter(([_, v]) => v !== null)
      )

      const response = await generatePictureBookAsync({
        child_name: child.name,
        age_months: childStore.currentChildAgeMonths,
        theme_topic: params.creationMode === 'preset' ? params.themeTopic : 'smart_creation',
        theme_category: params.creationMode === 'preset' ? params.themeCategory : 'custom',
        favorite_characters: child.favorite_characters,
        voice_id: params.voiceId,
        art_style: params.artStyle as ArtStyle,
        protagonist: params.protagonist,
        color_palette: params.colorPalette as ColorPalette,
        creation_mode: params.creationMode,
        custom_prompt: params.creationMode === 'smart' ? params.customPrompt : undefined,
        story_enhancement: Object.keys(storyEnhancement).length > 0 ? storyEnhancement : undefined,
        visual_enhancement: Object.keys(visualEnhancement).length > 0 ? visualEnhancement : undefined
      })

      currentTaskId.value = response.task_id
      startPolling(response.task_id, getPictureBookTaskStatus)
    } catch (e: any) {
      generatingStatus.value = 'failed'
      generatingError.value = e.message || '提交任务失败'
      throw e
    }
  }

  /**
   * 生成儿歌
   */
  async function generateNurseryRhyme() {
    const childStore = useChildStore()
    const child = childStore.currentChild
    if (!child) throw new Error('请先选择孩子')

    const params = nurseryRhymeParams.value

    // 验证参数
    if (params.creationMode === 'preset') {
      if (!params.themeCategory || !params.themeTopic) {
        throw new Error('请选择主题')
      }
    } else if (params.creationMode === 'smart') {
      if (!params.customPrompt) {
        throw new Error('请输入创意描述')
      }
    }

    generatingStatus.value = 'pending'
    generatingProgress.value = 0
    generatingError.value = ''

    try {
      const response = await generateNurseryRhymeAsync({
        child_name: child.name,
        age_months: childStore.currentChildAgeMonths,
        theme_topic: params.creationMode === 'preset' ? params.themeTopic : 'smart_creation',
        theme_category: params.creationMode === 'preset' ? params.themeCategory : 'custom',
        favorite_characters: child.favorite_characters,
        creation_mode: params.creationMode,
        custom_prompt: params.creationMode === 'smart' ? params.customPrompt : undefined,
        // 音乐风格
        music_mood: params.musicMood,
        music_genre: params.musicGenre || undefined,
        tempo: params.tempo,
        energy_level: params.energyLevel,
        // 人声
        vocal_type: params.vocalType,
        vocal_emotion: params.vocalEmotion,
        vocal_range: params.vocalRange || undefined,
        vocal_style: params.vocalStyle || undefined,
        // 乐器和音效
        instruments: params.instruments.length > 0 ? params.instruments : undefined,
        sound_effects: params.soundEffects.length > 0 ? params.soundEffects : undefined,
        // 歌词
        lyric_complexity: params.lyricComplexity,
        repetition_level: params.repetitionLevel,
        // 结构
        song_structure: params.songStructure,
        action_types: params.actionTypes || undefined,
        // 语言文化
        language: params.language,
        cultural_style: params.culturalStyle || undefined,
        // 个性化
        educational_focus: params.educationalFocus || undefined,
        favorite_colors: params.favoriteColors.length > 0 ? params.favoriteColors : undefined,
        // Suno 进阶
        style_weight: params.styleWeight !== 0.5 ? params.styleWeight : undefined,
        creativity: params.creativity !== 0.5 ? params.creativity : undefined,
        negative_tags: params.negativeTags || undefined,
        duration_preference: params.durationPreference
      })

      currentTaskId.value = response.task_id
      startPolling(response.task_id, getNurseryRhymeTaskStatus)
    } catch (e: any) {
      generatingStatus.value = 'failed'
      generatingError.value = e.message || '提交任务失败'
      throw e
    }
  }

  /**
   * 生成视频
   */
  async function generateVideo() {
    const childStore = useChildStore()
    const child = childStore.currentChild
    if (!child) throw new Error('请先选择孩子')

    const params = videoParams.value
    if (!params.customPrompt) {
      throw new Error('请输入视频描述')
    }

    generatingStatus.value = 'pending'
    generatingProgress.value = 0
    generatingError.value = ''

    try {
      const response = await generateStandaloneVideoAsync({
        child_name: child.name,
        age_months: childStore.currentChildAgeMonths,
        custom_prompt: params.customPrompt,
        generate_first_frame: true,
        aspect_ratio: params.aspectRatio,
        resolution: params.resolution,
        duration_seconds: params.durationSeconds,
        motion_mode: params.motionMode,
        enable_audio: params.enableAudio,
        art_style: params.artStyle,
        auto_enhance_prompt: params.autoEnhancePrompt
      })

      currentTaskId.value = response.task_id
      startPolling(response.task_id, getVideoTaskStatus)
    } catch (e: any) {
      generatingStatus.value = 'failed'
      generatingError.value = e.message || '提交任务失败'
      throw e
    }
  }

  return {
    // 基础数据
    themes,
    styleOptions,
    isLoadingOptions,

    // 步骤
    currentStep,

    // 参数
    pictureBookParams,
    nurseryRhymeParams,
    videoParams,

    // 生成状态
    currentTaskId,
    generatingStatus,
    generatingProgress,
    generatingStage,
    generatingError,
    generatedContentId,
    isGenerating,

    // 方法
    loadOptions,
    resetParams,
    stopPolling,
    generatePictureBook,
    generateNurseryRhyme,
    generateVideo
  }
})
