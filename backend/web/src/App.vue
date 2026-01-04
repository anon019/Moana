<template>
  <AppLayout v-if="showLayout">
    <router-view />
  </AppLayout>
  <router-view v-else />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/Layout/AppLayout.vue'

const route = useRoute()

const showLayout = computed(() => {
  // 登录页和播放页不显示布局
  return route.path !== '/login' && !route.path.startsWith('/play/')
})
</script>
