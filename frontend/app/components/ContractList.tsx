'use client'

import { useState, useEffect } from 'react'
import { Eye, Download, RefreshCw, Clock, CheckCircle, XCircle, AlertCircle, Search, Filter, BarChart3, Star, Calendar, DollarSign, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'
import { motion } from 'framer-motion'
import { format } from 'date-fns'

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
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      {/* Enhanced Header */}
      <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl p-6 border border-indigo-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <FileText className="w-8 h-8 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Contract Intelligence Dashboard</h2>
              <p className="text-gray-600 mt-1">Manage and analyze your contract portfolio</p>
            </div>
          </div>
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onRefresh}
            className="flex items-center px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </motion.button>
        </div>
        
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Contracts</p>
                <p className="text-2xl font-bold text-gray-900">{contracts.length}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Completed</p>
                <p className="text-2xl font-bold text-green-600">
                  {contracts.filter(c => c.status === 'completed').length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Processing</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {contracts.filter(c => c.status === 'processing').length}
                </p>
              </div>
              <Clock className="w-8 h-8 text-yellow-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Failed</p>
                <p className="text-2xl font-bold text-red-600">
                  {contracts.filter(c => c.status === 'failed').length}
                </p>
              </div>
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Contract List */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-900">Contract Portfolio</h3>
          <p className="text-sm text-gray-500">Click on any contract to view detailed analysis</p>
        </div>
        <div className="divide-y divide-gray-200">
          {contracts.map((contract, index) => (
            <motion.div
              key={contract.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="px-6 py-6 hover:bg-gray-50 transition-colors cursor-pointer"
              onClick={() => onSelectContract(contract.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <FileText className="w-6 h-6 text-blue-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <h4 className="text-lg font-semibold text-gray-900 truncate">
                        {contract.filename}
                      </h4>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(contract.status)}`}>
                        {contract.status}
                      </span>
                      {contract.score && (
                        <div className="flex items-center space-x-1">
                          <Star className="w-4 h-4 text-yellow-500" />
                          <span className="text-sm font-medium text-gray-900">{contract.score}%</span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {format(new Date(contract.uploaded_at), 'MMM dd, yyyy')}
                      </div>
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {format(new Date(contract.uploaded_at), 'HH:mm')}
                      </div>
                      {contract.extracted_data?.financial_details?.total_contract_value && (
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-1" />
                          ${contract.extracted_data.financial_details.total_contract_value.toLocaleString()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={(e) => {
                      e.stopPropagation()
                      onSelectContract(contract.id)
                    }}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Eye className="w-5 h-5" />
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDownload(contract.id)
                    }}
                    className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  >
                    <Download className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
