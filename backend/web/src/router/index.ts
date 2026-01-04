import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/children',
      name: 'Children',
      component: () => import('@/views/Children.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/children/add',
      name: 'AddChild',
      component: () => import('@/views/AddChild.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/children/:id',
      name: 'ChildDetail',
      component: () => import('@/views/ChildDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/library',
      name: 'Library',
      component: () => import('@/views/Library.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/favorites',
      name: 'Favorites',
      component: () => import('@/views/Favorites.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/play/:type/:id',
      name: 'Play',
      component: () => import('@/views/Play.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/report',
      name: 'Report',
      component: () => import('@/views/Report.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('@/views/Settings.vue'),
      meta: { requiresAuth: true }
    },
    // 创作中心路由
    {
      path: '/create',
      name: 'Create',
      component: () => import('@/views/create/Index.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/create/picture-book',
      name: 'CreatePictureBook',
      component: () => import('@/views/create/PictureBook.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/create/nursery-rhyme',
      name: 'CreateNurseryRhyme',
      component: () => import('@/views/create/NurseryRhyme.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/create/video',
      name: 'CreateVideo',
      component: () => import('@/views/create/Video.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/create/smart',
      name: 'CreateSmart',
      component: () => import('@/views/create/Smart.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const isLoggedIn = localStorage.getItem('admin_token')

  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && isLoggedIn) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
