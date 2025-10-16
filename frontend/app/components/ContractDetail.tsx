'use client'

import { useState, useEffect, useCallback } from 'react'
import { ArrowLeft, Download, AlertTriangle, CheckCircle, XCircle, Users, DollarSign, CreditCard, TrendingUp, Phone, Calendar, FileText, Shield, Target, BarChart3, Clock, Star, Eye, Search, Filter } from 'lucide-react'
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

interface ContractDetailProps {
  contract: Contract
  onBack: () => void
}

interface Party {
  name: string
  role: string
  email?: string
  phone?: string
  legal_entity?: string
  registration_number?: string
  address?: string
  contact_person?: string
}

interface AccountInfo {
  account_number?: string
  contact_email?: string
  contact_phone?: string
}

interface LineItem {
  description: string
  quantity?: number
  unit_price?: number
  total_price?: number
}

interface FinancialDetails {
  total_contract_value?: number
  currency?: string
  line_items?: LineItem[]
}

interface PaymentTerms {
  payment_terms?: string
  payment_schedule?: string
  due_dates?: string[]
}

interface RevenueClassification {
  payment_type?: string
}

interface SLA {
  response_time?: string
  resolution_time?: string
}

interface ContractData {
  parties: Party[]
  account_info: AccountInfo
  financial_details: FinancialDetails
  payment_terms: PaymentTerms
  revenue_classification: RevenueClassification
  sla: SLA
  contract_start_date: string
  contract_end_date: string
  contract_type: string
  confidence_scores: Record<string, number>
}

export default function ContractDetail({ contract, onBack }: ContractDetailProps) {
  const [contractData, setContractData] = useState<ContractData | null>(null)
  const [loading, setLoading] = useState(false)
  const [gaps, setGaps] = useState<string[]>([])

  const fetchContractData = useCallback(async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/contracts/${contract.id}`)
      setContractData(response.data)
      
      // Get gaps from the contract status endpoint
      const statusResponse = await axios.get(`${API_BASE_URL}/contracts/${contract.id}/status`)
      if (statusResponse.data.gaps) {
        setGaps(statusResponse.data.gaps)
      }
    } catch (error) {
      console.error('Error fetching contract data:', error)
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 404) {
          toast.error('Contract not found')
        } else if (error.response?.status === 500) {
          toast.error('Server error occurred while fetching contract data')
        } else {
          toast.error('Failed to fetch contract data')
        }
      } else {
        toast.error('Failed to fetch contract data')
      }
    } finally {
      setLoading(false)
    }
  }, [contract.id])

  useEffect(() => {
    if (contract.status === 'completed') {
      fetchContractData()
    }
  }, [contract.id, contract.status, fetchContractData])

  const handleDownload = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/contracts/${contract.id}/download`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', contract.filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('Contract downloaded successfully')
    } catch (error) {
      console.error('Download error:', error)
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 404) {
          toast.error('Contract file not found')
        } else if (error.response?.status === 500) {
          toast.error('Server error occurred while downloading')
        } else {
          toast.error('Failed to download contract')
        }
      } else {
        toast.error('Failed to download contract')
      }
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const renderConfidenceScore = (score: number) => {
    const percentage = Math.round(score)
    const color = score >= 80 ? 'text-green-600' : score >= 60 ? 'text-yellow-600' : 'text-red-600'
    return `${percentage}% confidence`
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading contract data...</span>
      </div>
    )
  }

  if (!contractData) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No contract data available</h3>
        <p className="text-gray-500">Contract processing may not be complete</p>
        <button onClick={onBack} className="btn-primary mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to List
        </button>
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
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onBack} 
              className="flex items-center px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to List
            </motion.button>
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{contract.filename}</h2>
                <div className="flex items-center space-x-4 mt-2">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(contract.score)}`}
                  >
                    <Star className="w-4 h-4 mr-1" />
                    Overall Score: {contract.score}%
                  </motion.div>
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="w-4 h-4 mr-1" />
                    {format(new Date(contract.uploaded_at), 'MMM dd, yyyy')}
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <Clock className="w-4 h-4 mr-1" />
                    {format(new Date(contract.uploaded_at), 'HH:mm')}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleDownload} 
            className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-lg"
          >
            <Download className="w-5 h-5 mr-2" />
            Download PDF
          </motion.button>
        </div>
      </div>

      {/* Gaps Section */}
      {gaps.length > 0 && (
        <div className="card border-red-200 bg-red-50">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-red-800 mb-2">Missing Information</h3>
              <ul className="text-sm text-red-700 space-y-1">
                {gaps.map((gap, index) => (
                  <li key={index} className="flex items-start">
                    <XCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                    {gap}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Contract Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Parties Identified</p>
              <p className="text-3xl font-bold text-gray-900">{contractData.parties?.length || 0}</p>
              <p className="text-xs text-gray-400 mt-1">
                {renderConfidenceScore(contractData.confidence_scores?.party_identification || 0)}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Contract Value</p>
              <p className="text-3xl font-bold text-gray-900">
                {contractData.financial_details?.total_contract_value 
                  ? `$${contractData.financial_details.total_contract_value.toLocaleString()}`
                  : 'N/A'
                }
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {renderConfidenceScore(contractData.confidence_scores?.financial_details || 0)}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <DollarSign className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Payment Type</p>
              <p className="text-3xl font-bold text-gray-900">
                {contractData.revenue_classification?.payment_type || 'N/A'}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {renderConfidenceScore(contractData.confidence_scores?.revenue_classification || 0)}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <TrendingUp className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Risk Level</p>
              <p className="text-3xl font-bold text-gray-900">
                {contractData.risk_factors?.length > 0 ? 'High' : 'Low'}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {contractData.risk_factors?.length || 0} factors
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <Shield className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Enhanced Information Tabs */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {['Overview', 'Parties', 'Financial', 'Terms', 'Risk Analysis', 'Metadata'].map((tab) => (
              <button
                key={tab}
                className="py-4 px-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
        
        <div className="p-6">
          {/* Key-Value Pairs Section */}
          {contractData.key_value_pairs && contractData.key_value_pairs.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Target className="w-5 h-5 mr-2 text-blue-600" />
                Extracted Key-Value Pairs
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {contractData.key_value_pairs.map((pair, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{pair.key}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        pair.confidence > 0.8 ? 'bg-green-100 text-green-800' :
                        pair.confidence > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {Math.round(pair.confidence * 100)}% confidence
                      </span>
                    </div>
                    <p className="text-gray-700">{pair.value}</p>
                    <span className="text-xs text-gray-500 capitalize">{pair.field_type}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Analysis Section */}
          {contractData.risk_factors && contractData.risk_factors.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2 text-red-600" />
                Risk Factors Identified
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {contractData.risk_factors.map((risk, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center"
                  >
                    <AlertTriangle className="w-4 h-4 text-red-600 mr-3 flex-shrink-0" />
                    <span className="text-red-800 font-medium capitalize">{risk}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Compliance Issues Section */}
          {contractData.compliance_issues && contractData.compliance_issues.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Shield className="w-5 h-5 mr-2 text-orange-600" />
                Compliance Issues
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {contractData.compliance_issues.map((issue, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-orange-50 border border-orange-200 rounded-lg p-3 flex items-center"
                  >
                    <Shield className="w-4 h-4 text-orange-600 mr-3 flex-shrink-0" />
                    <span className="text-orange-800 font-medium capitalize">{issue}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Important Dates Section */}
          {contractData.important_dates && contractData.important_dates.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Calendar className="w-5 h-5 mr-2 text-blue-600" />
                Important Dates
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {contractData.important_dates.map((date, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-blue-50 border border-blue-200 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-blue-900 capitalize">{date.description}</p>
                        <p className="text-blue-700">{date.date}</p>
                      </div>
                      <Calendar className="w-5 h-5 text-blue-600" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Processing Notes Section */}
          {contractData.processing_notes && contractData.processing_notes.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-gray-600" />
                Processing Notes
              </h3>
              <div className="space-y-2">
                {contractData.processing_notes.map((note, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-gray-50 border border-gray-200 rounded-lg p-3 flex items-start"
                  >
                    <div className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    <span className="text-gray-700">{note}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Parties */}
        {contractData.parties && contractData.parties.length > 0 && (
          <div className="card">
            <div className="flex items-center mb-4">
              <Users className="w-5 h-5 text-gray-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Parties</h3>
              <span className={`ml-auto text-sm font-medium ${getConfidenceColor(contractData.confidence_scores?.party_identification || 0)}`}>
                {contractData.confidence_scores?.party_identification || 0}% confidence
              </span>
            </div>
            <div className="space-y-3">
              {contractData.parties.map((party, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{party.name}</h4>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                      {party.role}
                    </span>
                  </div>
                  {party.email && (
                    <p className="text-sm text-gray-600">Email: {party.email}</p>
                  )}
                  {party.phone && (
                    <p className="text-sm text-gray-600">Phone: {party.phone}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Financial Details */}
        {contractData.financial_details && (
          <div className="card">
            <div className="flex items-center mb-4">
              <DollarSign className="w-5 h-5 text-gray-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Financial Details</h3>
              <span className={`ml-auto text-sm font-medium ${getConfidenceColor(contractData.confidence_scores?.financial_details || 0)}`}>
                {contractData.confidence_scores?.financial_details || 0}% confidence
              </span>
            </div>
            <div className="space-y-3">
              {contractData.financial_details.total_contract_value && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Value:</span>
                  <span className="font-medium">
                    ${contractData.financial_details.total_contract_value.toLocaleString()}
                    {contractData.financial_details.currency && ` ${contractData.financial_details.currency}`}
                  </span>
                </div>
              )}
              {contractData.financial_details.line_items && contractData.financial_details.line_items.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Line Items:</p>
                  <div className="space-y-2">
                    {contractData.financial_details.line_items.slice(0, 3).map((item: LineItem, index: number) => (
                      <div key={index} className="text-sm bg-gray-50 p-2 rounded">
                        <p className="font-medium">{item.description}</p>
                        {item.quantity && item.unit_price && item.total_price && (
                          <p className="text-gray-600">
                            {item.quantity} x ${item.unit_price} = ${item.total_price}
                          </p>
                        )}
                      </div>
                    ))}
                    {contractData.financial_details.line_items.length > 3 && (
                      <p className="text-xs text-gray-500">
                        +{contractData.financial_details.line_items.length - 3} more items
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Payment Terms */}
        {contractData.payment_terms && (
          <div className="card">
            <div className="flex items-center mb-4">
              <CreditCard className="w-5 h-5 text-gray-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Payment Terms</h3>
              <span className={`ml-auto text-sm font-medium ${getConfidenceColor(contractData.confidence_scores?.payment_terms || 0)}`}>
                {contractData.confidence_scores?.payment_terms || 0}% confidence
              </span>
            </div>
            <div className="space-y-2">
              {contractData.payment_terms.payment_terms && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Terms:</span>
                  <span className="font-medium">{contractData.payment_terms.payment_terms}</span>
                </div>
              )}
              {contractData.payment_terms.payment_schedule && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Schedule:</span>
                  <span className="font-medium">{contractData.payment_terms.payment_schedule}</span>
                </div>
              )}
              {contractData.payment_terms.due_dates && contractData.payment_terms.due_dates.length > 0 && (
                <div>
                  <span className="text-gray-600">Due Dates:</span>
                  <div className="mt-1">
                    {contractData.payment_terms.due_dates.slice(0, 3).map((date: string, index: number) => (
                      <span key={index} className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded mr-1 mb-1">
                        {date}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Account Information */}
        {contractData.account_info && (
          <div className="card">
            <div className="flex items-center mb-4">
              <Phone className="w-5 h-5 text-gray-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Account Information</h3>
              <span className={`ml-auto text-sm font-medium ${getConfidenceColor(contractData.confidence_scores?.contact_information || 0)}`}>
                {contractData.confidence_scores?.contact_information || 0}% confidence
              </span>
            </div>
            <div className="space-y-2">
              {contractData.account_info.account_number && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Account #:</span>
                  <span className="font-medium">{contractData.account_info.account_number}</span>
                </div>
              )}
              {contractData.account_info.contact_email && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Email:</span>
                  <span className="font-medium">{contractData.account_info.contact_email}</span>
                </div>
              )}
              {contractData.account_info.contact_phone && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Phone:</span>
                  <span className="font-medium">{contractData.account_info.contact_phone}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Contract Dates and Type */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Contract Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {contractData.contract_start_date && (
            <div>
              <p className="text-sm text-gray-600">Start Date</p>
              <p className="font-medium">{contractData.contract_start_date}</p>
            </div>
          )}
          {contractData.contract_end_date && (
            <div>
              <p className="text-sm text-gray-600">End Date</p>
              <p className="font-medium">{contractData.contract_end_date}</p>
            </div>
          )}
          {contractData.contract_type && (
            <div>
              <p className="text-sm text-gray-600">Contract Type</p>
              <p className="font-medium">{contractData.contract_type}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
