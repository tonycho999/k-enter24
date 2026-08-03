import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    // src/ 를 빼고, 최상단에 있는 app과 components 폴더를 바로 바라보게 수정합니다.
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
    },
  },
  plugins: [],
};

export default config;
