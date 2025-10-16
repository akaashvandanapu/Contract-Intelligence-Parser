'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

interface ContractUploadProps {
  onUploadSuccess: (contractId: string) => void
}

export default function ContractUpload({ onUploadSuccess }: ContractUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Please upload a PDF file')
      return
    }

    // Validate file size (50MB limit)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB')
      return
    }

    setUploading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`${API_BASE_URL}/contracts/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            setUploadProgress(progress)
          }
        },
      })

      onUploadSuccess(response.data.contract_id)
    } catch (error: any) {
      console.error('Upload error:', error)
      toast.error(error.response?.data?.detail || 'Failed to upload contract')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }, [onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: uploading
  })

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Upload Contract
          </h2>
          <p className="text-gray-600">
            Upload a PDF contract to extract and analyze its data
          </p>
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          
          {uploading ? (
            <div className="space-y-4">
              <div className="w-16 h-16 mx-auto bg-primary-100 rounded-full flex items-center justify-center">
                <Upload className="w-8 h-8 text-primary-600 animate-pulse" />
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">Uploading...</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500 mt-1">{uploadProgress}%</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
                <FileText className="w-8 h-8 text-gray-400" />
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? 'Drop the PDF here' : 'Drag & drop a PDF file here'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or click to select a file
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Supported formats:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>PDF files only</li>
                <li>Maximum file size: 50MB</li>
                <li>Processing may take a few minutes</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
