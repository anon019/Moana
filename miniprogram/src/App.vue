<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'

onLaunch(async () => {
  console.log('🌊 Moana App Launch')

  // 尝试自动登录
  const userStore = useUserStore()
  const token = uni.getStorageSync('access_token')

  if (token) {
    try {
      await userStore.fetchUser()
    } catch (e) {
      console.log('自动登录失败，需要重新登录')
    }
  }
})

onShow(() => {
  console.log('🌊 Moana App Show')
})

onHide(() => {
  console.log('🌊 Moana App Hide')
})
</script>

<style lang="scss">
/* 全局样式已在 uni.scss 中引入 */
</style>
