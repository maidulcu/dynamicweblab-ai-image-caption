'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import { Upload, X, Download, CheckCircle, AlertCircle, Loader2, ArrowLeft } from 'lucide-react'
import Link from 'next/link'

interface UploadedFile {
  file: File
  preview: string
}

interface BatchStatus {
  batch_id: string
  status: string
  progress: {
    total: number
    processed: number
    successful: number
    failed: number
    percentage: number
    estimated_completion: string | null
  }
}

export default function BatchPage() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [keywords, setKeywords] = useState('')
  const [platforms, setPlatforms] = useState('instagram,facebook,twitter')
  const [batchId, setBatchId] = useState<string | null>(null)
  const [status, setStatus] = useState<BatchStatus | null>(null)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      preview: URL.createObjectURL(file)
    }))
    setFiles(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp']
    },
    maxFiles: 100
  })

  const removeFile = (index: number) => {
    setFiles(prev => {
      const newFiles = [...prev]
      URL.revokeObjectURL(newFiles[index].preview)
      newFiles.splice(index, 1)
      return newFiles
    })
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please add at least one image')
      return
    }

    setProcessing(true)
    setError(null)

    try {
      const formData = new FormData()
      files.forEach(({ file }) => {
        formData.append('images', file)
      })
      formData.append('keywords', keywords)
      formData.append('platforms', platforms)

      const response = await axios.post('/api/v1/batch/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const { batch_id } = response.data
      setBatchId(batch_id)

      // Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await axios.get(`/api/v1/batch/status/${batch_id}`)
          setStatus(statusResponse.data)

          if (statusResponse.data.status === 'completed') {
            clearInterval(pollInterval)
            setProcessing(false)
          }
        } catch (err) {
          console.error('Error polling status:', err)
          clearInterval(pollInterval)
          setProcessing(false)
        }
      }, 2000)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error uploading images')
      setProcessing(false)
    }
  }

  const handleExport = async (format: 'csv' | 'json') => {
    if (!batchId) return

    try {
      const response = await axios.get(`/api/v1/batch/export/${batchId}?format=${format}`, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `batch_${batchId}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      console.error('Error exporting:', err)
    }
  }

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-white hover:text-primary-100 mb-4">
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Home
          </Link>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
            Bulk Image Processing
          </h1>
          <p className="text-xl text-white opacity-90">
            Process up to 100 images at once with parallel processing
          </p>
        </div>

        {/* Upload Area */}
        {!batchId && (
          <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={`border-3 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
                isDragActive
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-16 h-16 mx-auto mb-4 text-primary-500" />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">
                Drop images here or click to browse
              </h3>
              <p className="text-gray-600">
                Supports JPG, PNG, WebP • Maximum 100 images
              </p>
              <p className="text-sm text-gray-500 mt-2">
                {files.length > 0 && `${files.length} image(s) selected`}
              </p>
            </div>

            {/* File Grid */}
            {files.length > 0 && (
              <div className="mt-6 grid grid-cols-3 md:grid-cols-6 gap-4">
                {files.map((file, index) => (
                  <div key={index} className="relative group">
                    <img
                      src={file.preview}
                      alt={file.file.name}
                      className="w-full h-24 object-cover rounded-lg"
                    />
                    <button
                      onClick={() => removeFile(index)}
                      className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Settings */}
            <div className="mt-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  SEO Keywords (comma-separated)
                </label>
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="e.g., fashion, summer, dress"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-primary-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Social Media Platforms
                </label>
                <input
                  type="text"
                  value={platforms}
                  onChange={(e) => setPlatforms(e.target.value)}
                  placeholder="instagram,facebook,twitter"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-primary-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="mt-4 bg-red-50 border-2 border-red-200 rounded-lg p-4 flex items-center">
                <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                <span className="text-red-700">{error}</span>
              </div>
            )}

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={files.length === 0 || processing}
              className="mt-6 w-full bg-gradient-to-r from-primary-500 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {processing ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5 mr-2" />
                  Process {files.length} Image{files.length !== 1 ? 's' : ''}
                </>
              )}
            </button>
          </div>
        )}

        {/* Progress */}
        {status && (
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold text-gray-800">
                Processing Progress
              </h2>
              {status.status === 'completed' && (
                <div className="flex items-center text-green-600">
                  <CheckCircle className="w-6 h-6 mr-2" />
                  <span className="font-semibold">Completed!</span>
                </div>
              )}
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>
                  {status.progress.processed} / {status.progress.total} images
                </span>
                <span>{Math.round(status.progress.percentage)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-primary-500 to-purple-600 h-full transition-all duration-300 flex items-center justify-end pr-2"
                  style={{ width: `${status.progress.percentage}%` }}
                >
                  {status.progress.percentage > 10 && (
                    <span className="text-xs text-white font-semibold">
                      {Math.round(status.progress.percentage)}%
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-green-600">
                  {status.progress.successful}
                </div>
                <div className="text-sm text-gray-600">Successful</div>
              </div>
              <div className="bg-red-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-red-600">
                  {status.progress.failed}
                </div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {status.progress.estimated_completion || 'N/A'}
                </div>
                <div className="text-sm text-gray-600">ETA</div>
              </div>
            </div>

            {/* Export Buttons */}
            {status.status === 'completed' && (
              <div className="flex gap-4">
                <button
                  onClick={() => handleExport('csv')}
                  className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center justify-center"
                >
                  <Download className="w-5 h-5 mr-2" />
                  Export CSV
                </button>
                <button
                  onClick={() => handleExport('json')}
                  className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center"
                >
                  <Download className="w-5 h-5 mr-2" />
                  Export JSON
                </button>
                <button
                  onClick={() => {
                    setBatchId(null)
                    setStatus(null)
                    setFiles([])
                  }}
                  className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
                >
                  New Batch
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
