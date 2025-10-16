'use client'

import { useState, useEffect } from 'react'
import { Eye, Download, RefreshCw, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

interface Contract {
  id: string
  filename: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  uploaded_at: string
  file_size: number
  score: number
  progress: number
}

interface ContractListProps {
  contracts: Contract[]
  loading: boolean
  onContractSelect: (contract: Contract) => void
  onRefresh: () => void
}

export default function ContractList({ contracts, loading, onContractSelect, onRefresh }: ContractListProps) {
  const [processingContracts, setProcessingContracts] = useState<Set<string>>(new Set())

  useEffect(() => {
    // Check for processing contracts and poll their status
    const processingIds = contracts
      .filter(c => c.status === 'processing' || c.status === 'pending')
      .map(c => c.id)
    
    if (processingIds.length > 0) {
      setProcessingContracts(new Set(processingIds))
      const interval = setInterval(() => {
        onRefresh()
      }, 3000) // Poll every 3 seconds
      
      return () => clearInterval(interval)
    } else {
      setProcessingContracts(new Set())
    }
  }, [contracts, onRefresh])

  const handleDownload = async (contractId: string, filename: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/contracts/${contractId}/download`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('Contract downloaded successfully')
    } catch (error) {
      console.error('Download error:', error)
      toast.error('Failed to download contract')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100'
      case 'failed':
        return 'text-red-600 bg-red-100'
      case 'processing':
        return 'text-blue-600 bg-blue-100'
      default:
        return 'text-yellow-600 bg-yellow-100'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <RefreshCw className="w-8 h-8 text-primary-600 animate-spin" />
        <span className="ml-2 text-gray-600">Loading contracts...</span>
      </div>
    )
  }

  if (contracts.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No contracts found</h3>
        <p className="text-gray-500">Upload your first contract to get started</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">
          Contracts ({contracts.length})
        </h2>
        <button
          onClick={onRefresh}
          className="btn-secondary flex items-center"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {contracts.map((contract) => (
            <li key={contract.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {getStatusIcon(contract.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {contract.filename}
                      </p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(contract.status)}`}>
                        {contract.status}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 mt-1">
                      <p className="text-sm text-gray-500">
                        {formatFileSize(contract.file_size)}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDate(contract.uploaded_at)}
                      </p>
                      {contract.status === 'completed' && contract.score > 0 && (
                        <p className={`text-sm font-medium ${getScoreColor(contract.score)}`}>
                          Score: {contract.score}%
                        </p>
                      )}
                    </div>
                    {contract.status === 'processing' && contract.progress > 0 && (
                      <div className="mt-2">
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${contract.progress}%` }}
                          ></div>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{contract.progress}% complete</p>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {contract.status === 'completed' && (
                    <button
                      onClick={() => onContractSelect(contract)}
                      className="btn-primary flex items-center text-sm"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </button>
                  )}
                  <button
                    onClick={() => handleDownload(contract.id, contract.filename)}
                    className="btn-secondary flex items-center text-sm"
                  >
                    <Download className="w-4 h-4 mr-1" />
                    Download
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
