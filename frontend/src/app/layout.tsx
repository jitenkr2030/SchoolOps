import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SchoolOps - AI-Powered School Management System',
  description: 'Comprehensive school management with AI capabilities',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
