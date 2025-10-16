"use client";

import axios from "axios";
import { format } from "date-fns";
import {
  AlertCircle,
  BarChart3,
  Calendar,
  CheckCircle,
  Clock,
  DollarSign,
  Download,
  Eye,
  FileText,
  RefreshCw,
  Search,
  Star,
  Trash2,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface Contract {
  id: string;
  filename: string;
  status: "pending" | "processing" | "completed" | "failed";
  uploaded_at: string;
  file_size: number;
  score: number;
  progress: number;
  extracted_data?: any;
}

interface ContractListProps {
  contracts: Contract[];
  loading: boolean;
  onContractSelect: (contract: Contract) => void;
  onRefresh: () => void;
}

export default function ContractList({
  contracts,
  loading,
  onContractSelect,
  onRefresh,
}: ContractListProps) {
  const [processingContracts, setProcessingContracts] = useState<Set<string>>(
    new Set()
  );
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("uploaded_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    // Check for processing contracts and poll their status
    const processingIds = contracts
      .filter((c) => c.status === "processing" || c.status === "pending")
      .map((c) => c.id);

    if (processingIds.length > 0) {
      setProcessingContracts(new Set(processingIds));
      const interval = setInterval(() => {
        onRefresh();
      }, 3000); // Poll every 3 seconds

      return () => clearInterval(interval);
    } else {
      setProcessingContracts(new Set());
    }
  }, [contracts, onRefresh]);

  const handleDownload = async (contractId: string, filename: string) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/contracts/${contractId}/download`,
        {
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success("Contract downloaded successfully");
    } catch (error) {
      console.error("Download error:", error);
      toast.error("Failed to download contract");
    }
  };

  const handleDelete = async (contractId: string, filename: string) => {
    if (
      !confirm(
        `Are you sure you want to delete "${filename}"? This action cannot be undone.`
      )
    ) {
      return;
    }

    try {
      await axios.delete(`${API_BASE_URL}/contracts/${contractId}`);
      toast.success("Contract deleted successfully");
      onRefresh(); // Refresh the list
    } catch (error) {
      console.error("Delete error:", error);
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 404) {
          toast.error("Contract not found");
        } else if (error.response?.status === 500) {
          toast.error("Server error while deleting contract");
        } else {
          toast.error("Failed to delete contract");
        }
      } else {
        toast.error("Failed to delete contract");
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "processing":
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600 bg-green-100";
      case "failed":
        return "text-red-600 bg-red-100";
      case "processing":
        return "text-blue-600 bg-blue-100";
      default:
        return "text-yellow-600 bg-yellow-100";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  // Filter and sort contracts
  const filteredContracts = contracts
    .filter((contract) => {
      const matchesSearch = contract.filename
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesStatus =
        statusFilter === "all" || contract.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      let aValue, bValue;

      switch (sortBy) {
        case "filename":
          aValue = a.filename.toLowerCase();
          bValue = b.filename.toLowerCase();
          break;
        case "score":
          aValue = a.score || 0;
          bValue = b.score || 0;
          break;
        case "uploaded_at":
        default:
          aValue = new Date(a.uploaded_at).getTime();
          bValue = new Date(b.uploaded_at).getTime();
          break;
      }

      if (sortOrder === "asc") {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <RefreshCw className="w-8 h-8 text-primary-600 animate-spin" />
        <span className="ml-2 text-gray-600">Loading contracts...</span>
      </div>
    );
  }

  if (contracts.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No contracts found
        </h3>
        <p className="text-gray-500">
          Upload your first contract to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Enhanced Header */}
      <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl p-6 border border-indigo-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <FileText className="w-8 h-8 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Contract Intelligence Dashboard
              </h2>
              <p className="text-gray-600 mt-1">
                Manage and analyze your contract portfolio
              </p>
            </div>
          </div>
          <button
            onClick={onRefresh}
            className="flex items-center px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">
                  Total Contracts
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {contracts.length}
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Completed</p>
                <p className="text-2xl font-bold text-green-600">
                  {contracts.filter((c) => c.status === "completed").length}
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
                  {contracts.filter((c) => c.status === "processing").length}
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
                  {contracts.filter((c) => c.status === "failed").length}
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
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Contract Portfolio
              </h3>
              <p className="text-sm text-gray-500">
                Click on any contract to view detailed analysis
              </p>
            </div>

            {/* Search and Filter Controls */}
            <div className="flex flex-col sm:flex-row gap-3">
              {/* Search */}
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search contracts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="processing">Processing</option>
                <option value="pending">Pending</option>
                <option value="failed">Failed</option>
              </select>

              {/* Sort Controls */}
              <div className="flex gap-2">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="uploaded_at">Date</option>
                  <option value="filename">Name</option>
                  <option value="score">Score</option>
                </select>
                <button
                  onClick={() =>
                    setSortOrder(sortOrder === "asc" ? "desc" : "asc")
                  }
                  className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {sortOrder === "asc" ? "↑" : "↓"}
                </button>
              </div>
            </div>
          </div>
        </div>
        <div className="divide-y divide-gray-200">
          {filteredContracts.map((contract, index) => (
            <div
              key={contract.id}
              className="px-6 py-6 hover:bg-gray-50 transition-colors cursor-pointer"
              onClick={() => onContractSelect(contract)}
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
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          contract.status
                        )}`}
                      >
                        {contract.status}
                      </span>
                      {contract.score && (
                        <div className="flex items-center space-x-1">
                          <Star className="w-4 h-4 text-yellow-500" />
                          <span className="text-sm font-medium text-gray-900">
                            {contract.score}%
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {format(new Date(contract.uploaded_at), "MMM dd, yyyy")}
                      </div>
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {format(new Date(contract.uploaded_at), "HH:mm")}
                      </div>
                      {contract.extracted_data?.financial_details
                        ?.total_contract_value && (
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-1" />$
                          {contract.extracted_data.financial_details.total_contract_value.toLocaleString()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onContractSelect(contract);
                    }}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Eye className="w-5 h-5" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(contract.id, contract.filename);
                    }}
                    className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(contract.id, contract.filename);
                    }}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete contract"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
