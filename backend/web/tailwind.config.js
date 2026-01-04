/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 「童趣工坊」设计系统

        // 背景色系
        'cream': '#FFFBF5',
        'paper': '#FFF8F0',
        'canvas': '#F7F3ED',

        // 主色调
        'forest': {
          50: '#F2F7F4',
          100: '#E0EBE4',
          200: '#C1D7C9',
          300: '#9BB8A5',
          400: '#6B9678',
          500: '#3D5A4C',
          600: '#2D4A3E',
          700: '#243D33',
          800: '#1C2F28',
          900: '#14211C',
          DEFAULT: '#3D5A4C',
        },
        'bark': {
          50: '#FAF7F5',
          100: '#F0EAE4',
          200: '#DED3C8',
          300: '#C4B5A5',
          400: '#A69480',
          500: '#8B7355',
          600: '#6B5344',
          700: '#574438',
          800: '#43352C',
          900: '#2F2520',
          DEFAULT: '#6B5344',
        },

        // 类型点缀色
        'coral': {
          50: '#FEF5F2',
          100: '#FDE8E2',
          200: '#FBCFC3',
          300: '#F5AC98',
          400: '#E8846B',
          500: '#D65F45',
          600: '#B84A33',
          700: '#943C2A',
          800: '#6F2E21',
          900: '#4A1F16',
          DEFAULT: '#E8846B',
        },
        'sky': {
          50: '#F3FAFB',
          100: '#E4F3F6',
          200: '#C4E5EC',
          300: '#9DD2DE',
          400: '#7FBCD2',
          500: '#5BA3BC',
          600: '#4589A3',
          700: '#3A7085',
          800: '#2E5768',
          900: '#203E4B',
          DEFAULT: '#7FBCD2',
        },
        'sage': {
          50: '#F5F9F6',
          100: '#E8F1EB',
          200: '#D0E3D6',
          300: '#B5D2BE',
          400: '#9BB8A5',
          500: '#7A9C86',
          600: '#5F7F6A',
          700: '#4C6555',
          800: '#3A4D41',
          900: '#28352D',
          DEFAULT: '#9BB8A5',
        },
        'lavender': {
          50: '#F9F8FB',
          100: '#F1EEF5',
          200: '#E2DCEA',
          300: '#CEC5DB',
          400: '#B8A9C9',
          500: '#9E8BB3',
          600: '#826E99',
          700: '#69587B',
          800: '#50445E',
          900: '#372F41',
          DEFAULT: '#B8A9C9',
        },

        // 文字色
        'ink': '#2C2C2C',
        'pencil': '#666666',
        'eraser': '#999999',
        'chalk': '#CCCCCC',
      },
      fontFamily: {
        'display': ['"Noto Sans SC"', 'system-ui', 'sans-serif'],
        'body': ['"Noto Sans SC"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'sm': '6px',
        'DEFAULT': '10px',
        'md': '12px',
        'lg': '16px',
        'xl': '20px',
        '2xl': '24px',
        '3xl': '32px',
        'blob': '60% 40% 50% 50% / 50% 60% 40% 50%',
      },
      boxShadow: {
        'soft': '0 2px 8px rgba(45, 74, 62, 0.06)',
        'card': '0 4px 16px rgba(45, 74, 62, 0.08)',
        'lifted': '0 8px 32px rgba(45, 74, 62, 0.12)',
        'float': '0 12px 40px rgba(45, 74, 62, 0.15)',
        'inner-soft': 'inset 0 2px 4px rgba(45, 74, 62, 0.04)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'wiggle': 'wiggle 0.5s ease-in-out',
        'bounce-soft': 'bounce-soft 2s ease-in-out infinite',
        'fade-in': 'fade-in 0.4s ease-out forwards',
        'slide-up': 'slide-up 0.5s ease-out forwards',
        'scale-in': 'scale-in 0.3s ease-out forwards',
      },
      keyframes: {
        'float': {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '50%': { transform: 'translateY(-10px) rotate(2deg)' },
        },
        'wiggle': {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        'bounce-soft': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      backgroundImage: {
        'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E\")",
        'dots': "url(\"data:image/svg+xml,%3Csvg width='20' height='20' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='2' cy='2' r='1' fill='%233D5A4C' fill-opacity='0.1'/%3E%3C/svg%3E\")",
        'grid-paper': "url(\"data:image/svg+xml,%3Csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 40V0h40' fill='none' stroke='%233D5A4C' stroke-opacity='0.05'/%3E%3C/svg%3E\")",
      },
    },
  },
  plugins: [],
}
