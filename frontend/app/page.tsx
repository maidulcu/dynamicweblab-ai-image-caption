'use client'

import { useState } from 'react'
import { Upload, Zap, TrendingUp, Globe } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="text-center text-white mb-12">
          <h1 className="text-5xl md:text-6xl font-bold mb-4">
            AI Image Caption Generator
          </h1>
          <p className="text-xl md:text-2xl opacity-90 mb-8">
            Generate alt-text, social media captions, and SEO metadata automatically
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/single"
              className="bg-white text-primary-600 px-8 py-4 rounded-lg font-semibold hover:shadow-xl transition-all transform hover:scale-105"
            >
              Single Image
            </Link>
            <Link
              href="/batch"
              className="bg-primary-800 text-white px-8 py-4 rounded-lg font-semibold hover:shadow-xl transition-all transform hover:scale-105 border-2 border-white"
            >
              Bulk Upload
            </Link>
          </div>
        </header>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <FeatureCard
            icon={<Zap className="w-12 h-12" />}
            title="Alt-Text Generation"
            description="Automatic generation of descriptive, keyword-rich alt-text for product images. Improves accessibility and SEO."
            example="Red A-line cotton dress with floral pattern"
          />
          <FeatureCard
            icon={<TrendingUp className="w-12 h-12" />}
            title="Social Media Captions"
            description="Engaging, platform-optimized captions with relevant hashtags. 71% of shoppers consider images essential."
            example="Instagram: 2,200 chars, Twitter: 280 chars"
          />
          <FeatureCard
            icon={<Globe className="w-12 h-12" />}
            title="SEO Optimization"
            description="Keyword integration for improved search visibility and organic traffic through intelligent content optimization."
            example="SEO score: 90/100"
          />
        </div>

        {/* Technology Stack */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            Powered By Advanced AI
          </h2>
          <div className="grid md:grid-cols-4 gap-6 text-center">
            <TechBadge name="BLIP Model" description="Image Analysis" />
            <TechBadge name="FastAPI" description="High Performance" />
            <TechBadge name="Next.js" description="Modern Frontend" />
            <TechBadge name="Batch Processing" description="Large Inventories" />
          </div>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 text-white text-center">
          <StatCard number="100" label="Images per batch" />
          <StatCard number="5" label="Platforms supported" />
          <StatCard number="2-5s" label="Processing time" />
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description, example }: any) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-xl hover:shadow-2xl transition-all transform hover:scale-105">
      <div className="text-primary-600 mb-4">{icon}</div>
      <h3 className="text-2xl font-bold text-gray-800 mb-3">{title}</h3>
      <p className="text-gray-600 mb-4">{description}</p>
      <div className="bg-primary-50 rounded-lg p-3">
        <p className="text-sm text-primary-700 font-mono">{example}</p>
      </div>
    </div>
  )
}

function TechBadge({ name, description }: any) {
  return (
    <div className="bg-gradient-to-br from-primary-50 to-purple-50 rounded-lg p-4">
      <div className="text-lg font-bold text-primary-700">{name}</div>
      <div className="text-sm text-gray-600">{description}</div>
    </div>
  )
}

function StatCard({ number, label }: any) {
  return (
    <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl p-6">
      <div className="text-4xl font-bold mb-2">{number}</div>
      <div className="text-lg opacity-90">{label}</div>
    </div>
  )
}
