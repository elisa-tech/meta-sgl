import { defineConfig } from 'vitepress'
import { getHighlighter } from 'shiki'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "meta-sgl",
  description: "Space Grade Linux",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'GitHub', link: 'https://github.com/elisa-tech/meta-sgl' }
    ],

    sidebar: [
      {
        text: 'Guides',
        items: [
          { text: 'Building', link: '/building' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/elisa-tech/meta-sgl' },
      { icon: 'discord', link: 'https://chat.elisa.tech/' }
    ]
  },
  markdown: {
    async config(md) {
      const highlighter = await getHighlighter({
        themes: [ 'catppuccin-frappe', 'catppuccin-latte' ],
        langs: [
          'bash',
          'python',
          'json',
          'yaml',
          'cpp',
          'dockerfile',
          'makefile',
          'sh'
        ]
      })

      md.options.highlight = (code, lang) => {
        return highlighter.codeToHtml(code, {
          lang,
          theme: {
            light: 'catppuccin-latte',
            dark: 'catppuccin-frappe'
          }
        })
      }
    }
  },
})
