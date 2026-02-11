import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css"; // 👈 이 줄이 반드시 있어야 디자인이 나옵니다!

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "K-ENTER 24",
  description: "Global K-Culture Trend Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
