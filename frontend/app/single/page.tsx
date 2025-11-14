'use client'

import { useState } from 'react'
import { Upload, ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'
import axios from 'axios'

export default function SinglePage() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [productName, setProductName] = useState('')
  const [productCategory, setProductCategory] = useState('')
  const [productBrand, setProductBrand] = useState('')
  const [keywords, setKeywords] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'altText' | 'social' | 'seo'>('altText')

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setPreview(URL.createObjectURL(selectedFile))
    }
  }

  const handleGenerate = async () => {
    if (!file) return

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('product_name', productName)
      formData.append('product_category', productCategory)
      formData.append('product_brand', productBrand)
      formData.append('keywords', keywords)

      const response = await axios.post('/api/v1/generate/complete', formData)
      setResults(response.data)
    } catch (error) {
      console.error('Error:', error)
      alert('Error generating content')
    } finally {
      setLoading(false)
    }
  }

  const getSEOScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600 bg-green-100'
    if (score >= 40) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <Link href="/" className="inline-flex items-center text-white hover:text-primary-100 mb-4">
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Home
        </Link>

        <h1 className="text-4xl md:text-5xl font-bold text-white mb-8">
          Single Image Processing
        </h1>

        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
          {/* Upload */}
          <div className="mb-6">
            <label className="flex flex-col items-center justify-center w-full h-64 border-3 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-primary-400 hover:bg-gray-50 transition-all">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                {preview ? (
                  <img src={preview} alt="Preview" className="max-h-48 rounded-lg" />
                ) : (
                  <>
                    <Upload className="w-12 h-12 text-primary-500 mb-3" />
                    <p className="text-lg font-semibold text-gray-700">Click to upload image</p>
                    <p className="text-sm text-gray-500">PNG, JPG, WebP</p>
                  </>
                )}
              </div>
              <input type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />
            </label>
          </div>

          {/* Form */}
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Product Name</label>
              <input
                type="text"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                placeholder="e.g., Cotton Dress"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-primary-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Category</label>
              <input
                type="text"
                value={productCategory}
                onChange={(e) => setProductCategory(e.target.value)}
                placeholder="e.g., Women's Fashion"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-primary-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Brand</label>
              <input
                type="text"
                value={productBrand}
                onChange={(e) => setProductBrand(e.target.value)}
                placeholder="e.g., Your Brand"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-primary-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Keywords</label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="fashion, dress, summer"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-primary-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={!file || loading}
            className="w-full bg-gradient-to-r from-primary-500 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              'Generate Complete Package'
            )}
          </button>
        </div>

        {/* Results */}
        {results && (
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            {/* Tabs */}
            <div className="flex border-b-2 border-gray-200 mb-6">
              <button
                onClick={() => setActiveTab('altText')}
                className={`px-6 py-3 font-semibold transition-colors ${
                  activeTab === 'altText'
                    ? 'text-primary-600 border-b-3 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Alt Text
              </button>
              <button
                onClick={() => setActiveTab('social')}
                className={`px-6 py-3 font-semibold transition-colors ${
                  activeTab === 'social'
                    ? 'text-primary-600 border-b-3 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Social Captions
              </button>
              <button
                onClick={() => setActiveTab('seo')}
                className={`px-6 py-3 font-semibold transition-colors ${
                  activeTab === 'seo'
                    ? 'text-primary-600 border-b-3 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                SEO Metadata
              </button>
            </div>

            {/* Alt Text Tab */}
            {activeTab === 'altText' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-2xl font-bold text-gray-800">Alt Text</h3>
                  <span
                    className={`px-4 py-2 rounded-full font-semibold ${getSEOScoreColor(
                      results.alt_text.seo_score
                    )}`}
                  >
                    SEO Score: {results.alt_text.seo_score}
                  </span>
                </div>
                <ResultBox title="Standard" content={results.alt_text.standard} />
                <ResultBox title="Short" content={results.alt_text.short} />
                <ResultBox title="Medium" content={results.alt_text.medium} />
              </div>
            )}

            {/* Social Tab */}
            {activeTab === 'social' && (
              <div className="space-y-6">
                {Object.entries(results.social_captions).map(([platform, data]: [string, any]) => (
                  <div key={platform} className="border-2 border-gray-200 rounded-lg p-6">
                    <h4 className="text-xl font-bold text-primary-600 capitalize mb-3">
                      {platform}
                    </h4>
                    <p className="text-gray-800 mb-4 whitespace-pre-wrap">{data.caption}</p>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {data.hashtags?.map((tag: string, i: number) => (
                        <span
                          key={i}
                          className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <div className="text-sm text-gray-600">
                      Engagement Score: {data.engagement_score} | Length: {data.length} chars
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* SEO Tab */}
            {activeTab === 'seo' && (
              <div className="space-y-4">
                <ResultBox title="Filename" content={results.seo_metadata.filename} />
                <ResultBox title="Title Tag" content={results.seo_metadata.title} />
                <ResultBox
                  title="Meta Description"
                  content={results.seo_metadata.meta_description}
                />
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-2">Recommendations</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-700">
                    {results.seo_metadata.recommendations.map((rec: string, i: number) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function ResultBox({ title, content }: { title: string; content: string }) {
  return (
    <div className="bg-primary-50 border-l-4 border-primary-600 rounded-lg p-4">
      <div className="font-semibold text-primary-700 mb-2">{title}</div>
      <div className="text-gray-800">{content}</div>
    </div>
  )
}
