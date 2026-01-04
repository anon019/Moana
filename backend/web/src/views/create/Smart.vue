<template>
  <div class="page-container">
    <!-- 装饰背景 -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <div class="deco-blob w-80 h-80 from-lavender-200 to-lavender-100 -top-20 -right-20" />
      <div class="deco-blob w-64 h-64 from-sky-200 to-sky-100 top-1/3 -left-20" />
      <div class="deco-blob w-72 h-72 from-coral-200 to-coral-100 bottom-20 right-1/4" />
    </div>

    <div class="page-content relative">
      <!-- 返回按钮 -->
      <router-link
        to="/create"
        class="inline-flex items-center gap-2 text-pencil hover:text-forest transition-colors mb-8 group"
      >
        <svg class="w-5 h-5 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span>返回创作中心</span>
      </router-link>

      <!-- 页面标题 -->
      <header class="text-center mb-10 animate-fade-in">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-lavender-400 to-lavender-500 text-white mb-4 shadow-card">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h1 class="page-title text-center justify-center">智能创作</h1>
        <p class="page-subtitle text-center">告诉 AI 你的想法，智能生成创意内容</p>
      </header>

      <!-- 步骤指示器 -->
      <div class="step-indicator mb-10 animate-fade-in">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="step-item"
        >
          <div
            class="step-number"
            :class="{
              'active': currentStep === index + 1,
              'completed': currentStep > index + 1,
              'pending': currentStep < index + 1
            }"
          >
            <svg v-if="currentStep > index + 1" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span
            class="text-sm hidden sm:inline ml-2"
            :class="currentStep === index + 1 ? 'text-forest font-medium' : 'text-eraser'"
          >
            {{ step }}
          </span>
          <div
            v-if="index < steps.length - 1"
            class="step-line ml-4"
            :class="{ 'completed': currentStep > index + 1 }"
          />
        </div>
      </div>

      <!-- 主要内容卡片 -->
      <div class="card p-6 sm:p-8 animate-slide-up">
        <!-- 步骤 1：输入创意描述 -->
        <div v-if="currentStep === 1">
          <h2 class="section-title mb-6">
            <span class="w-8 h-8 rounded-lg bg-lavender-100 flex items-center justify-center text-lavender-600 mr-3">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </span>
            描述你的创意
          </h2>

          <textarea
            v-model="customPrompt"
            rows="4"
            class="input input-lg resize-none"
            placeholder="例如：一个关于小熊学会分享的故事..."
          />
          <div class="text-right text-sm text-eraser mt-2">
            {{ customPrompt.length }}/200
          </div>

          <!-- 灵感标签 -->
          <div class="mt-8">
            <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
              <span class="w-1.5 h-1.5 rounded-full bg-lavender mr-2" />
              快速灵感
            </h3>
            <!-- 分类选择 -->
            <div class="flex flex-wrap gap-2 mb-4">
              <button
                v-for="category in inspirationCategories"
                :key="category.id"
                class="tag"
                :class="selectedInspirationCategory === category.id ? 'tag-active' : 'tag-default'"
                @click="selectedInspirationCategory = category.id"
              >
                {{ category.icon }} {{ category.name }}
              </button>
            </div>
            <!-- 当前分类的标签 -->
            <div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
              <button
                v-for="tag in currentInspirationTags"
                :key="tag.text"
                class="inspiration-tag text-sm"
                :class="{ 'active': customPrompt === tag.prompt }"
                @click="customPrompt = tag.prompt"
              >
                <span class="text-lg">{{ tag.icon }}</span>
                <span class="truncate">{{ tag.text }}</span>
              </button>
            </div>
          </div>

          <!-- 故事灵感卡片 -->
          <div class="mt-10">
            <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
              <span class="w-1.5 h-1.5 rounded-full bg-coral mr-2" />
              故事灵感
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div
                v-for="inspiration in inspirations"
                :key="inspiration.title"
                class="group relative p-5 bg-canvas rounded-2xl border-2 cursor-pointer transition-all duration-300"
                :class="customPrompt === inspiration.prompt
                  ? 'border-forest bg-forest-50 shadow-card'
                  : 'border-transparent hover:border-forest-200 hover:bg-paper'"
                @click="customPrompt = inspiration.prompt"
              >
                <!-- 装饰角标 -->
                <div class="absolute -top-2 -right-2 w-8 h-8 rounded-lg rotate-12 transition-transform group-hover:rotate-0"
                  :class="inspiration.color"
                />
                <div class="flex items-start relative">
                  <span class="text-3xl mr-4 transition-transform group-hover:scale-110">{{ inspiration.icon }}</span>
                  <div>
                    <h4 class="font-bold text-ink mb-1">{{ inspiration.title }}</h4>
                    <p class="text-sm text-pencil leading-relaxed">{{ inspiration.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤 2：选择内容类型 -->
        <div v-else-if="currentStep === 2">
          <h2 class="section-title mb-6">
            <span class="w-8 h-8 rounded-lg bg-forest-100 flex items-center justify-center text-forest mr-3">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            选择创作类型
          </h2>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <button
              v-for="type in contentTypes"
              :key="type.id"
              class="relative overflow-hidden rounded-2xl p-6 text-left transition-all duration-300"
              :class="selectedContentType === type.id
                ? `${type.activeClass} shadow-float scale-[1.02]`
                : 'bg-canvas hover:bg-paper border-2 border-bark-100 hover:border-forest-200'"
              @click="selectedContentType = type.id as 'picture_book' | 'nursery_rhyme' | 'video'"
            >
              <!-- 背景装饰 -->
              <div v-if="selectedContentType === type.id" class="absolute inset-0 opacity-20">
                <div class="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-white/30" />
                <div class="absolute -bottom-4 -left-4 w-20 h-20 rounded-full bg-white/20" />
              </div>
              <!-- 图标 -->
              <div
                class="w-14 h-14 rounded-xl flex items-center justify-center mb-4 transition-transform"
                :class="selectedContentType === type.id ? 'bg-white/20 scale-110' : 'bg-bark-100'"
              >
                <component :is="type.iconComponent" class="w-7 h-7" :class="selectedContentType === type.id ? 'text-white' : type.iconColor" />
              </div>
              <h3
                class="font-bold text-lg mb-2"
                :class="selectedContentType === type.id ? 'text-white' : 'text-ink'"
              >
                {{ type.name }}
              </h3>
              <p
                class="text-sm leading-relaxed"
                :class="selectedContentType === type.id ? 'text-white/80' : 'text-pencil'"
              >
                {{ type.description }}
              </p>
            </button>
          </div>

          <!-- 创意描述预览 -->
          <div class="mt-8 p-5 bg-forest-50 rounded-2xl border border-forest-100">
            <div class="flex items-start">
              <div class="w-10 h-10 rounded-xl bg-forest-100 flex items-center justify-center text-forest mr-4 flex-shrink-0">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div class="min-w-0">
                <p class="text-sm text-forest font-medium mb-1">创意描述</p>
                <p class="text-ink break-words">{{ customPrompt }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤 3：高级设置 -->
        <div v-else-if="currentStep === 3">
          <h2 class="section-title mb-6">
            <span class="w-8 h-8 rounded-lg bg-sage-100 flex items-center justify-center text-sage-600 mr-3">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </span>
            创作设置
          </h2>

          <!-- 绘本设置 -->
          <div v-if="selectedContentType === 'picture_book'" class="space-y-8">
            <!-- 艺术风格 -->
            <div>
              <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-coral mr-2" />
                艺术风格
              </h3>
              <!-- 风格分类选择 -->
              <div class="flex flex-wrap gap-2 mb-4">
                <button
                  v-for="category in artStyleCategories"
                  :key="category.id"
                  class="tag text-xs"
                  :class="selectedArtStyleCategory === category.id ? 'tag-coral' : 'tag-default'"
                  @click="selectedArtStyleCategory = category.id"
                >
                  {{ category.icon }} {{ category.name }}
                </button>
              </div>
              <!-- 当前分类的风格选项 -->
              <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                <button
                  v-for="style in currentArtStyles"
                  :key="style.id"
                  class="p-3 rounded-xl text-center border-2 transition-all duration-200"
                  :class="pictureBookSettings.artStyle === style.id
                    ? 'bg-coral-50 border-coral text-coral-700 shadow-soft'
                    : 'bg-paper border-bark-100 text-pencil hover:border-coral-200 hover:bg-coral-50/50'"
                  @click="pictureBookSettings.artStyle = style.id"
                >
                  <div class="text-sm font-medium">{{ style.name }}</div>
                </button>
              </div>
            </div>

            <!-- 故事主角 -->
            <div>
              <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-sky mr-2" />
                故事主角
              </h3>
              <div class="grid grid-cols-3 sm:grid-cols-6 gap-3">
                <button
                  v-for="p in protagonistOptions"
                  :key="p.animal"
                  class="p-4 rounded-xl text-center border-2 transition-all duration-200 group"
                  :class="pictureBookSettings.protagonist === p.animal
                    ? 'bg-sky-50 border-sky text-sky-700 shadow-soft'
                    : 'bg-paper border-bark-100 hover:border-sky-200 hover:bg-sky-50/50'"
                  @click="pictureBookSettings.protagonist = p.animal"
                >
                  <div class="text-3xl mb-2 transition-transform group-hover:scale-110">{{ p.emoji }}</div>
                  <div class="text-xs font-medium">{{ p.name }}</div>
                </button>
              </div>
            </div>

            <!-- 配音音色 -->
            <div>
              <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-lavender mr-2" />
                配音音色
              </h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <button
                  v-for="voice in voiceOptions"
                  :key="voice.id"
                  class="p-4 rounded-xl text-left border-2 transition-all duration-200"
                  :class="pictureBookSettings.voiceId === voice.id
                    ? 'bg-lavender-50 border-lavender text-lavender-700 shadow-soft'
                    : 'bg-paper border-bark-100 hover:border-lavender-200 hover:bg-lavender-50/50'"
                  @click="pictureBookSettings.voiceId = voice.id"
                >
                  <div class="flex items-center mb-2">
                    <span class="text-xl mr-2">{{ voice.icon }}</span>
                    <span class="font-semibold">{{ voice.name }}</span>
                  </div>
                  <div class="text-xs text-pencil line-clamp-2 leading-relaxed">{{ voice.desc }}</div>
                </button>
              </div>
            </div>
          </div>

          <!-- 儿歌设置 -->
          <div v-else-if="selectedContentType === 'nursery_rhyme'" class="space-y-8">
            <!-- 音乐风格 -->
            <div>
              <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-sky mr-2" />
                音乐风格
              </h3>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <button
                  v-for="mood in musicMoodOptions"
                  :key="mood.id"
                  class="p-4 rounded-xl text-center border-2 transition-all duration-200 group"
                  :class="nurseryRhymeSettings.musicMood === mood.id
                    ? 'bg-sky-50 border-sky text-sky-700 shadow-soft'
                    : 'bg-paper border-bark-100 hover:border-sky-200 hover:bg-sky-50/50'"
                  @click="nurseryRhymeSettings.musicMood = mood.id"
                >
                  <div class="text-3xl mb-2 transition-transform group-hover:scale-110">{{ mood.icon }}</div>
                  <div class="text-sm font-medium">{{ mood.name }}</div>
                </button>
              </div>
            </div>

            <!-- 人声类型 -->
            <div>
              <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-coral mr-2" />
                人声类型
              </h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <button
                  v-for="vocal in vocalTypeOptions"
                  :key="vocal.id"
                  class="p-4 rounded-xl text-center border-2 transition-all duration-200 group"
                  :class="nurseryRhymeSettings.vocalType === vocal.id
                    ? 'bg-coral-50 border-coral text-coral-700 shadow-soft'
                    : 'bg-paper border-bark-100 hover:border-coral-200 hover:bg-coral-50/50'"
                  @click="nurseryRhymeSettings.vocalType = vocal.id"
                >
                  <div class="text-2xl mb-2 transition-transform group-hover:scale-110">{{ vocal.icon }}</div>
                  <div class="text-sm font-medium">{{ vocal.name }}</div>
                </button>
              </div>
            </div>

            <!-- 时长 -->
            <div>
              <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-sage mr-2" />
                歌曲时长
              </h3>
              <div class="flex flex-wrap gap-3">
                <button
                  v-for="dur in durationOptions"
                  :key="dur.value"
                  class="px-5 py-3 rounded-xl border-2 font-medium transition-all duration-200"
                  :class="nurseryRhymeSettings.duration === dur.value
                    ? 'bg-sage-50 border-sage text-sage-700 shadow-soft'
                    : 'bg-paper border-bark-100 text-pencil hover:border-sage-200 hover:bg-sage-50/50'"
                  @click="nurseryRhymeSettings.duration = dur.value"
                >
                  {{ dur.label }}
                </button>
              </div>
            </div>
          </div>

          <!-- 视频设置 -->
          <div v-else-if="selectedContentType === 'video'" class="space-y-8">
            <!-- 画面比例 -->
            <div>
              <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-sage mr-2" />
                画面比例
              </h3>
              <div class="flex gap-4">
                <button
                  v-for="ratio in aspectRatioOptions"
                  :key="ratio.value"
                  class="flex-1 max-w-[200px] p-5 rounded-xl border-2 transition-all duration-200 flex items-center justify-center gap-3"
                  :class="videoSettings.aspectRatio === ratio.value
                    ? 'bg-sage-50 border-sage text-sage-700 shadow-soft'
                    : 'bg-paper border-bark-100 text-pencil hover:border-sage-200 hover:bg-sage-50/50'"
                  @click="videoSettings.aspectRatio = ratio.value as '16:9' | '9:16'"
                >
                  <span class="text-2xl">{{ ratio.icon }}</span>
                  <span class="font-medium">{{ ratio.label }}</span>
                </button>
              </div>
            </div>

            <!-- 运动模式 -->
            <div>
              <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-sky mr-2" />
                运动模式
              </h3>
              <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
                <button
                  v-for="mode in motionModeOptions"
                  :key="mode.id"
                  class="p-4 rounded-xl text-center border-2 transition-all duration-200 group"
                  :class="videoSettings.motionMode === mode.id
                    ? 'bg-sky-50 border-sky text-sky-700 shadow-soft'
                    : 'bg-paper border-bark-100 hover:border-sky-200 hover:bg-sky-50/50'"
                  @click="videoSettings.motionMode = mode.id"
                >
                  <div class="text-2xl mb-2 transition-transform group-hover:scale-110">{{ mode.icon }}</div>
                  <div class="text-sm font-medium">{{ mode.name }}</div>
                </button>
              </div>
            </div>

            <!-- 视频时长 -->
            <div>
              <h3 class="text-sm font-semibold text-ink mb-4 flex items-center">
                <span class="w-1.5 h-1.5 rounded-full bg-coral mr-2" />
                视频时长
              </h3>
              <div class="flex flex-wrap gap-3">
                <button
                  v-for="dur in videoDurationOptions"
                  :key="dur.value"
                  class="px-5 py-3 rounded-xl border-2 font-medium transition-all duration-200"
                  :class="videoSettings.duration === dur.value
                    ? 'bg-coral-50 border-coral text-coral-700 shadow-soft'
                    : 'bg-paper border-bark-100 text-pencil hover:border-coral-200 hover:bg-coral-50/50'"
                  @click="videoSettings.duration = dur.value"
                >
                  {{ dur.label }}
                </button>
              </div>
            </div>
          </div>

          <!-- 确认信息 -->
          <div class="mt-10 p-5 bg-gradient-to-br from-forest-50 to-sage-50 rounded-2xl border border-forest-100">
            <h3 class="font-semibold text-ink mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2 text-forest" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              创作确认
            </h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center py-2 border-b border-forest-100/50">
                <span class="text-pencil">宝贝名字</span>
                <span class="font-medium text-ink">{{ childStore.currentChild?.name }}</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-forest-100/50">
                <span class="text-pencil">内容类型</span>
                <span class="font-medium text-ink">{{ selectedContentTypeName }}</span>
              </div>
              <div class="flex justify-between items-start py-2">
                <span class="text-pencil flex-shrink-0">创意描述</span>
                <span class="font-medium text-ink text-right ml-4 max-w-[60%]">{{ customPrompt }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="flex justify-between items-center mt-10 pt-6 border-t border-bark-100">
          <button
            v-if="currentStep > 1"
            class="btn btn-secondary flex items-center gap-2"
            @click="prevStep"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            上一步
          </button>
          <div v-else />

          <button
            v-if="currentStep < 3"
            :disabled="!canNextStep"
            class="btn btn-primary flex items-center gap-2"
            @click="nextStep"
          >
            下一步
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
          <button
            v-else
            :disabled="isGenerating"
            class="btn btn-primary flex items-center gap-2"
            @click="startGenerate"
          >
            <svg v-if="isGenerating" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3l14 9-14 9V3z" />
            </svg>
            <span>开始创作</span>
          </button>
        </div>
      </div>

      <!-- 提示说明 -->
      <div class="mt-8 p-5 bg-paper/60 rounded-2xl border border-bark-100 text-center">
        <p class="text-sm text-pencil flex items-center justify-center gap-2">
          <svg class="w-4 h-4 text-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          智能创作会根据你的描述自动优化生成参数，打造最佳效果
        </p>
      </div>
    </div>

    <!-- 生成弹窗 -->
    <GeneratingModal
      :visible="createStore.isGenerating || createStore.generatingStatus === 'completed' || createStore.generatingStatus === 'failed'"
      :status="createStore.generatingStatus"
      :progress="createStore.generatingProgress"
      :stage="createStore.generatingStage"
      :error="createStore.generatingError"
      :content-type="selectedContentType"
      @play="handlePlay"
      @close="handleClose"
      @retry="startGenerate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { useChildStore } from '@/stores/child'
import { useCreateStore } from '@/stores/create'
import GeneratingModal from '@/components/create/GeneratingModal.vue'
import type { ProtagonistAnimal } from '@/api/create'

const router = useRouter()
const childStore = useChildStore()
const createStore = useCreateStore()

const steps = ['描述创意', '选择类型', '设置确认']
const currentStep = ref(1)
const customPrompt = ref('')
const selectedContentType = ref<'picture_book' | 'nursery_rhyme' | 'video'>('picture_book')

// 灵感分类（8类共80个）
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

const selectedInspirationCategory = ref('habit')

const currentInspirationTags = computed(() => {
  const category = inspirationCategories.find(c => c.id === selectedInspirationCategory.value)
  return category?.tags || []
})

// 故事灵感
const inspirations = [
  {
    icon: '🌟',
    title: '勇气与冒险',
    description: '小动物克服恐惧，勇敢探索新世界',
    prompt: '一只害羞的小兔子，鼓起勇气独自去森林探险，遇到了很多新朋友',
    color: 'bg-coral-200'
  },
  {
    icon: '💖',
    title: '友谊与分享',
    description: '学会分享，收获更多快乐',
    prompt: '小熊有一个漂亮的气球，一开始不想分享，后来学会了和朋友一起玩更开心',
    color: 'bg-sky-200'
  },
  {
    icon: '🌈',
    title: '认识自己',
    description: '发现自己的独特之处',
    prompt: '一只觉得自己很普通的小毛毛虫，后来发现自己可以变成美丽的蝴蝶',
    color: 'bg-lavender-200'
  },
  {
    icon: '🏠',
    title: '家庭温暖',
    description: '感受家人的爱与陪伴',
    prompt: '小猫咪出去玩迷路了，在家人的帮助下找到回家的路，感受到家的温暖',
    color: 'bg-sage-200'
  }
]

// 内容类型图标组件
const BookIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' })
    ])
  }
}

const MusicIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3' })
    ])
  }
}

const VideoIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' })
    ])
  }
}

// 内容类型
const contentTypes = [
  {
    id: 'picture_book',
    iconComponent: BookIcon,
    iconColor: 'text-coral',
    name: '绘本',
    description: 'AI 生成精美插画故事书',
    activeClass: 'bg-gradient-to-br from-coral-400 to-coral-500 text-white'
  },
  {
    id: 'nursery_rhyme',
    iconComponent: MusicIcon,
    iconColor: 'text-sky',
    name: '儿歌',
    description: 'AI 作曲演唱专属音乐',
    activeClass: 'bg-gradient-to-br from-sky-400 to-sky-500 text-white'
  },
  {
    id: 'video',
    iconComponent: VideoIcon,
    iconColor: 'text-sage-600',
    name: '视频',
    description: 'AI 生成精彩动画视频',
    activeClass: 'bg-gradient-to-br from-sage-400 to-sage-500 text-white'
  }
]

// 绘本设置
const pictureBookSettings = ref({
  artStyle: 'pixar_3d',
  protagonist: 'bunny',
  voiceId: 'Kore'
})

// 艺术风格分类
const artStyleCategories = [
  {
    id: 'threed',
    name: '3D风格',
    icon: '🎬',
    styles: [
      { id: 'pixar_3d', name: '皮克斯3D' },
      { id: 'pixar', name: '皮克斯电影' },
      { id: 'dreamworks', name: 'DreamWorks' },
      { id: 'disney_3d', name: '迪士尼3D' },
      { id: 'clay', name: '粘土动画' },
      { id: 'figurine', name: '手办模型' },
      { id: 'low_poly', name: '低多边形' }
    ]
  },
  {
    id: 'illustration',
    name: '手绘风格',
    icon: '🖌️',
    styles: [
      { id: 'storybook', name: '故事书' },
      { id: 'watercolor', name: '水彩手绘' },
      { id: 'cartoon', name: '卡通插画' },
      { id: 'flat_vector', name: '扁平插画' },
      { id: 'crayon', name: '蜡笔涂鸦' },
      { id: 'colored_pencil', name: '彩铅' }
    ]
  },
  {
    id: 'anime',
    name: '动漫风格',
    icon: '✨',
    styles: [
      { id: 'anime', name: '日系动漫' },
      { id: 'chibi', name: 'Q版萌系' },
      { id: 'ghibli', name: '吉卜力' },
      { id: 'shinkai', name: '新海诚' },
      { id: 'manga', name: '漫画' },
      { id: 'comic_book', name: '欧美漫画' }
    ]
  },
  {
    id: 'artistic',
    name: '绘画风格',
    icon: '🎨',
    styles: [
      { id: 'oil_painting', name: '油画' },
      { id: 'impressionist', name: '印象派' },
      { id: 'sketch', name: '素描' },
      { id: 'ink_wash', name: '水墨' },
      { id: 'pop_art', name: '波普艺术' },
      { id: 'pixel_art', name: '像素' }
    ]
  },
  {
    id: 'craft',
    name: '工艺风格',
    icon: '🧵',
    styles: [
      { id: 'papercut', name: '剪纸' },
      { id: 'felt_craft', name: '毛毡' },
      { id: 'origami', name: '折纸' },
      { id: 'embroidery', name: '刺绣' },
      { id: 'mosaic', name: '马赛克' },
      { id: 'stained_glass', name: '彩绘玻璃' }
    ]
  }
]

const selectedArtStyleCategory = ref('threed')

const currentArtStyles = computed(() => {
  const category = artStyleCategories.find(c => c.id === selectedArtStyleCategory.value)
  return category?.styles || []
})

const protagonistOptions = [
  { animal: 'bunny', emoji: '🐰', name: '小兔子' },
  { animal: 'bear', emoji: '🐻', name: '小熊' },
  { animal: 'cat', emoji: '🐱', name: '小猫咪' },
  { animal: 'dog', emoji: '🐶', name: '小狗狗' },
  { animal: 'fox', emoji: '🦊', name: '小狐狸' },
  { animal: 'elephant', emoji: '🐘', name: '小象' }
]

const voiceOptions = [
  { id: 'Kore', icon: '👩', name: '柯瑞', desc: '温柔女声，如妈妈般温暖，适合睡前故事' },
  { id: 'Leda', icon: '👩', name: '蕾达', desc: '优雅女声，咬字清晰有韵律，适合童话故事' },
  { id: 'Aoede', icon: '👩', name: '艾欧德', desc: '清新女声，明快自然，适合自然探索' },
  { id: 'Puck', icon: '👦', name: '帕克', desc: '活泼男声，俏皮有趣，适合调皮故事' },
  { id: 'Charon', icon: '👨', name: '卡戎', desc: '沉稳男声，冷静可靠，适合冒险故事' },
  { id: 'Fenrir', icon: '👨', name: '芬里尔', desc: '雄浑男声，气势磅礴，适合英雄传说' }
]

// 儿歌设置
const nurseryRhymeSettings = ref({
  musicMood: 'cheerful',
  vocalType: 'soft_female',
  duration: 60
})

const musicMoodOptions = [
  { id: 'cheerful', icon: '😄', name: '欢乐活泼' },
  { id: 'gentle', icon: '😊', name: '温柔舒缓' },
  { id: 'playful', icon: '🤪', name: '俏皮可爱' },
  { id: 'dreamy', icon: '🌙', name: '梦幻安静' }
]

const vocalTypeOptions = [
  { id: 'soft_female', icon: '👩‍🎤', name: '甜美女声' },
  { id: 'warm_male', icon: '👨‍🎤', name: '温暖男声' },
  { id: 'child', icon: '🧒', name: '童声' },
  { id: 'chorus', icon: '👥', name: '欢乐合唱' },
  { id: 'duet', icon: '👫', name: '亲子对唱' },
  { id: 'instrumental', icon: '🎹', name: '纯音乐' }
]

const durationOptions = [
  { value: 30, label: '30秒' },
  { value: 60, label: '1分钟' },
  { value: 90, label: '1.5分钟' },
  { value: 120, label: '2分钟' }
]

// 视频设置
const videoSettings = ref({
  aspectRatio: '16:9' as '16:9' | '9:16',
  motionMode: 'normal',
  duration: 5
})

const aspectRatioOptions = [
  { value: '16:9', icon: '📺', label: '横屏 16:9' },
  { value: '9:16', icon: '📱', label: '竖屏 9:16' }
]

const motionModeOptions = [
  { id: 'static', icon: '🖼️', name: '静态' },
  { id: 'slow', icon: '🐢', name: '缓慢' },
  { id: 'normal', icon: '🚶', name: '正常' },
  { id: 'dynamic', icon: '🏃', name: '动感' },
  { id: 'cinematic', icon: '🎬', name: '电影' }
]

const videoDurationOptions = [
  { value: 4, label: '4秒' },
  { value: 5, label: '5秒' },
  { value: 6, label: '6秒' },
  { value: 8, label: '8秒' }
]

// 计算属性
const canNextStep = computed(() => {
  if (currentStep.value === 1) {
    return customPrompt.value.trim().length > 0
  }
  if (currentStep.value === 2) {
    return !!selectedContentType.value
  }
  return true
})

const selectedContentTypeName = computed(() => {
  const type = contentTypes.find(t => t.id === selectedContentType.value)
  return type?.name || ''
})

const isGenerating = computed(() => createStore.isGenerating)

// 方法
function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

function nextStep() {
  if (currentStep.value < 3 && canNextStep.value) {
    currentStep.value++
  }
}

async function startGenerate() {
  try {
    if (selectedContentType.value === 'picture_book') {
      // 设置绘本参数
      createStore.pictureBookParams.themeCategory = 'custom'
      createStore.pictureBookParams.themeTopic = 'smart_creation'
      createStore.pictureBookParams.customPrompt = customPrompt.value
      createStore.pictureBookParams.artStyle = pictureBookSettings.value.artStyle
      createStore.pictureBookParams.protagonist = {
        animal: pictureBookSettings.value.protagonist as ProtagonistAnimal,
        color: 'default',
        accessory: 'default'
      }
      createStore.pictureBookParams.voiceId = pictureBookSettings.value.voiceId
      createStore.pictureBookParams.creationMode = 'smart'

      await createStore.generatePictureBook()
    } else if (selectedContentType.value === 'nursery_rhyme') {
      // 设置儿歌参数
      createStore.nurseryRhymeParams.themeCategory = 'custom'
      createStore.nurseryRhymeParams.themeTopic = 'smart_creation'
      createStore.nurseryRhymeParams.customPrompt = customPrompt.value
      createStore.nurseryRhymeParams.musicMood = nurseryRhymeSettings.value.musicMood
      createStore.nurseryRhymeParams.vocalType = nurseryRhymeSettings.value.vocalType
      createStore.nurseryRhymeParams.durationPreference = nurseryRhymeSettings.value.duration
      createStore.nurseryRhymeParams.creationMode = 'smart'

      await createStore.generateNurseryRhyme()
    } else if (selectedContentType.value === 'video') {
      // 设置视频参数
      createStore.videoParams.customPrompt = customPrompt.value
      createStore.videoParams.aspectRatio = videoSettings.value.aspectRatio
      createStore.videoParams.motionMode = videoSettings.value.motionMode as any
      createStore.videoParams.durationSeconds = videoSettings.value.duration as any
      createStore.videoParams.creationMode = 'standalone'

      await createStore.generateVideo()
    }
  } catch (e) {
    console.error('生成失败:', e)
  }
}

function handlePlay() {
  if (createStore.generatedContentId) {
    router.push(`/play/${selectedContentType.value}/${createStore.generatedContentId}`)
  }
}

function handleClose() {
  createStore.resetParams(selectedContentType.value)
  currentStep.value = 1
  customPrompt.value = ''
}

// 生命周期
onMounted(async () => {
  await createStore.loadOptions()
})

onUnmounted(() => {
  createStore.stopPolling()
})
</script>
