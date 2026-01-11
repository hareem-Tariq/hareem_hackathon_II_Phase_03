import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Todo Chatbot',
  description: 'Manage your tasks with AI-powered natural language interface',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
