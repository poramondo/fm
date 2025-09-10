// tailwind.config.ts
import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './app.vue',
    './plugins/**/*.{js,ts}',
  ],
  theme: {
    extend: {
      colors: {
        // выбери свою палитру brand (ниже — вариант из TS)
        brand: {
          500: '#4b7dff',
          600: '#2f5af7',
        },
        // чтобы работали утилиты вида bg-glass/60
        glass: 'rgb(255 255 255 / <alpha-value>)',
      },
      boxShadow: {
        glass: 'inset 0 1px 0 rgba(255,255,255,0.08), 0 8px 30px rgba(0,0,0,0.35)',
        soft: '0 10px 30px rgba(0,0,0,.15)', // из JS-конфига
      },
    },
  },
  plugins: [],
}
