<template>
  <div class="min-h-screen bg-cream">
    <Sidebar />
    <MobileNav />

    <!-- 主内容区 -->
    <main class="lg:pl-64 pt-14 lg:pt-0 pb-20 lg:pb-0">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import MobileNav from './MobileNav.vue'
</script>
