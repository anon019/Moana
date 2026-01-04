<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">学习报告</h1>
    </div>

    <!-- 时间范围选择 -->
    <div class="flex bg-gray-100 rounded-lg p-1 w-fit">
      <button
        v-for="range in timeRanges"
        :key="range.value"
        @click="selectedRange = range.value"
        class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
        :class="selectedRange === range.value ? 'bg-white shadow text-primary-600' : 'text-gray-600 hover:text-gray-900'"
      >
        {{ range.label }}
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-12 text-gray-500">
      加载中...
    </div>

    <!-- 无孩子提示 -->
    <div v-else-if="!childStore.currentChild" class="text-center py-12">
      <div class="text-6xl mb-4">👶</div>
      <p class="text-gray-500 mb-4">请先添加孩子</p>
      <router-link to="/children/add" class="btn btn-primary">
        添加孩子
      </router-link>
    </div>

    <!-- 统计内容 -->
    <template v-else>
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- 总学习时长 -->
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-gray-500">总学习时长</span>
            <span class="text-2xl">🕐</span>
          </div>
          <div class="text-3xl font-bold text-gray-900">
            {{ formatDuration(stats?.total_duration_minutes || 0) }}
          </div>
          <p class="text-sm text-gray-500 mt-1">
            {{ rangeLabel }}
          </p>
        </div>

        <!-- 连续学习天数 -->
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-gray-500">连续学习天数</span>
            <span class="text-2xl">🔥</span>
          </div>
          <div class="text-3xl font-bold text-gray-900">
            {{ stats?.streak_days || 0 }} <span class="text-lg font-normal">天</span>
          </div>
          <p class="text-sm text-gray-500 mt-1">
            保持每日学习习惯
          </p>
        </div>

        <!-- 完成内容数 -->
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <span class="text-gray-500">完成内容数</span>
            <span class="text-2xl">📚</span>
          </div>
          <div class="text-3xl font-bold text-gray-900">
            {{ totalContent }}
          </div>
          <div class="flex gap-4 text-sm text-gray-500 mt-1">
            <span>绘本 {{ stats?.total_books || 0 }}</span>
            <span>儿歌 {{ stats?.total_songs || 0 }}</span>
            <span>视频 {{ stats?.total_videos || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 每日学习时长柱状图 -->
        <div class="card">
          <h3 class="text-lg font-medium text-gray-900 mb-4">每日学习时长</h3>
          <div ref="barChartRef" class="h-64"></div>
        </div>

        <!-- 内容类型分布饼图 -->
        <div class="card">
          <h3 class="text-lg font-medium text-gray-900 mb-4">内容类型分布</h3>
          <div ref="pieChartRef" class="h-64"></div>
        </div>
      </div>

      <!-- 学习日历 -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">学习日历</h3>
        <div class="flex flex-wrap gap-1">
          <div
            v-for="day in stats?.daily_activity || []"
            :key="day.date"
            class="w-8 h-8 rounded flex items-center justify-center text-xs cursor-pointer transition-colors"
            :class="getDayClass(day)"
            :title="`${day.date}: ${day.duration_minutes}分钟`"
          >
            {{ new Date(day.date).getDate() }}
          </div>
        </div>
        <div class="flex items-center gap-4 mt-4 text-sm text-gray-500">
          <div class="flex items-center gap-1">
            <div class="w-4 h-4 rounded bg-gray-100"></div>
            <span>无活动</span>
          </div>
          <div class="flex items-center gap-1">
            <div class="w-4 h-4 rounded bg-primary-200"></div>
            <span>少于30分钟</span>
          </div>
          <div class="flex items-center gap-1">
            <div class="w-4 h-4 rounded bg-primary-400"></div>
            <span>30-60分钟</span>
          </div>
          <div class="flex items-center gap-1">
            <div class="w-4 h-4 rounded bg-primary-600"></div>
            <span>超过60分钟</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useChildStore } from '@/stores/child'
import { getLearningStats } from '@/api/play'
import type { LearningStats } from '@/api/types'

const childStore = useChildStore()

// 时间范围选项
const timeRanges = [
  { value: 7, label: '近7天' },
  { value: 30, label: '近30天' },
  { value: 0, label: '全部' },
]

const selectedRange = ref(7)
const loading = ref(true)
const stats = ref<LearningStats | null>(null)

// 图表引用
const barChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
let barChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

// 计算属性
const rangeLabel = computed(() => {
  const range = timeRanges.find(r => r.value === selectedRange.value)
  return range?.label || ''
})

const totalContent = computed(() => {
  if (!stats.value) return 0
  return stats.value.total_books + stats.value.total_songs + stats.value.total_videos
})

// 格式化时长
function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} 分钟`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours} 小时 ${mins} 分钟` : `${hours} 小时`
}

// 获取日历格子样式
function getDayClass(day: { has_activity: boolean; duration_minutes: number }) {
  if (!day.has_activity || day.duration_minutes === 0) {
    return 'bg-gray-100 text-gray-400'
  }
  if (day.duration_minutes < 30) {
    return 'bg-primary-200 text-primary-800'
  }
  if (day.duration_minutes < 60) {
    return 'bg-primary-400 text-white'
  }
  return 'bg-primary-600 text-white'
}

// 初始化柱状图
function initBarChart() {
  if (!barChartRef.value || !stats.value) return

  if (barChart) {
    barChart.dispose()
  }

  barChart = echarts.init(barChartRef.value)

  const dailyData = stats.value.daily_activity || []
  const dates = dailyData.map(d => {
    const date = new Date(d.date)
    return `${date.getMonth() + 1}/${date.getDate()}`
  })
  const durations = dailyData.map(d => d.duration_minutes)

  barChart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params: unknown) => {
        const data = params as Array<{ name: string; value: number }>
        return `${data[0].name}<br/>学习时长: ${data[0].value} 分钟`
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: dates.length > 15 ? 45 : 0,
        fontSize: 11,
      },
    },
    yAxis: {
      type: 'value',
      name: '分钟',
      minInterval: 1,
    },
    series: [
      {
        type: 'bar',
        data: durations,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#8b5cf6' },
            { offset: 1, color: '#a78bfa' },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#7c3aed' },
              { offset: 1, color: '#8b5cf6' },
            ]),
          },
        },
      },
    ],
  })
}

// 初始化饼图
function initPieChart() {
  if (!pieChartRef.value || !stats.value) return

  if (pieChart) {
    pieChart.dispose()
  }

  pieChart = echarts.init(pieChartRef.value)

  const data = [
    { value: stats.value.total_books, name: '绘本' },
    { value: stats.value.total_songs, name: '儿歌' },
    { value: stats.value.total_videos, name: '视频' },
  ].filter(d => d.value > 0)

  // 如果没有数据，显示空状态
  if (data.length === 0) {
    pieChart.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#9ca3af',
          fontSize: 14,
          fontWeight: 'normal',
        },
      },
    })
    return
  }

  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
          },
        },
        labelLine: {
          show: false,
        },
        data: data,
        color: ['#8b5cf6', '#f97316', '#22c55e'],
      },
    ],
  })
}

// 获取学习统计
async function fetchStats() {
  if (!childStore.currentChild) {
    loading.value = false
    return
  }

  loading.value = true

  try {
    const days = selectedRange.value === 0 ? undefined : selectedRange.value
    stats.value = await getLearningStats(childStore.currentChild.id, days)

    // 等待 DOM 更新后初始化图表
    await nextTick()
    initBarChart()
    initPieChart()
  } catch (e) {
    console.error('获取学习统计失败:', e)
  } finally {
    loading.value = false
  }
}

// 监听时间范围变化
watch(selectedRange, fetchStats)

// 监听当前孩子变化
watch(() => childStore.currentChild, fetchStats)

// 窗口大小变化时重绘图表
function handleResize() {
  barChart?.resize()
  pieChart?.resize()
}

onMounted(async () => {
  await childStore.fetchChildren()
  await fetchStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  barChart?.dispose()
  pieChart?.dispose()
})
</script>
