import { defineConfig } from 'astro/config';
import react from "@astrojs/react";

import tailwind from "@astrojs/tailwind";

import alpinejs from "@astrojs/alpinejs";

// https://astro.build/config
export default defineConfig({
  vite: {
    server: {
      watch: {
        ignored: [/\.astro~$/],
      },
    },
  },
  integrations: [react(), tailwind({
    applyBaseStyles: false,
  }), alpinejs()]
});