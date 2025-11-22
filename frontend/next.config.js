/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  },
  // Enable standalone output for Docker
  experimental: {
    outputFileTracingIncludes: {
      '/': ['./**/*'],
    },
  },
}

module.exports = nextConfig

