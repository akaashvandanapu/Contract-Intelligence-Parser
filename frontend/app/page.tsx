'use client'

import { useState, useEffect } from 'react'
import { Upload, FileText, Download, Eye, Clock, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'
import ContractUpload from './components/ContractUpload'
import ContractList from './components/ContractList'
import ContractDetail from './components/ContractDetail'

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

export default function Home() {
  const [contracts, setContracts] = useState<Contract[]>([])
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'upload' | 'list' | 'detail'>('upload')

  useEffect(() => {
    fetchContracts()
  }, [])

  const fetchContracts = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/contracts`)
      setContracts(response.data.contracts)
    } catch (error) {
      console.error('Error fetching contracts:', error)
      toast.error('Failed to fetch contracts')
    } finally {
      setLoading(false)
    }
  }

  const handleUploadSuccess = (contractId: string) => {
    toast.success('Contract uploaded successfully!')
    fetchContracts()
    setActiveTab('list')
  }

  const handleContractSelect = (contract: Contract) => {
    setSelectedContract(contract)
    setActiveTab('detail')
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <Clock className="w-5 h-5 text-blue-500" />
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

  return (
    <div className="space-y-6">
      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('upload')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'upload'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Upload className="w-4 h-4 inline mr-2" />
            Upload Contract
          </button>
          <button
            onClick={() => setActiveTab('list')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'list'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Contract List
          </button>
          {selectedContract && (
            <button
              onClick={() => setActiveTab('detail')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'detail'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Eye className="w-4 h-4 inline mr-2" />
              Contract Details
            </button>
          )}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'upload' && (
        <ContractUpload onUploadSuccess={handleUploadSuccess} />
      )}

      {activeTab === 'list' && (
        <ContractList
          contracts={contracts}
          loading={loading}
          onContractSelect={handleContractSelect}
          onRefresh={fetchContracts}
        />
      )}

      {activeTab === 'detail' && selectedContract && (
        <ContractDetail
          contract={selectedContract}
          onBack={() => setActiveTab('list')}
        />
      )}
    </div>
  )
}
