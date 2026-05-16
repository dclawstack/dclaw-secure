import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "DClaw Secure — Security & Compliance Platform",
  description:
    "Modern vulnerability management, asset inventory, security scanning, and compliance automation. Open-source. AI-first. Deploy in 48 hours.",
  openGraph: {
    title: "DClaw Secure — Security & Compliance Platform",
    description:
      "Modern vulnerability management, asset inventory, security scanning, and compliance automation.",
    type: "website",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
