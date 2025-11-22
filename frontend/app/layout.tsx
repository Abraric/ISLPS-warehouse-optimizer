import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ASLPS - Adaptive Storage Location Prediction System',
  description: 'Smart Warehouse Logistics - Industrial Manufacturing',
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

