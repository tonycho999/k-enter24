import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    // src 폴더 내부의 모든 컴포넌트와 페이지에서 Tailwind 클래스를 인식하도록 경로 지정
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
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
