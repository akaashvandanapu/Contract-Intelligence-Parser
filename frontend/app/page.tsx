"use client";

import axios from "axios";
import {
  Brain,
  CheckCircle,
  Clock,
  Eye,
  FileText,
  Shield,
  Upload,
  XCircle,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import ContractDetail from "./components/ContractDetail";
import ContractList from "./components/ContractList";
import ContractUpload from "./components/ContractUpload";

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
}

export default function Home() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"upload" | "list" | "detail">(
    "upload"
  );

  useEffect(() => {
    fetchContracts();
  }, []);

  const fetchContracts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/contracts`);
      setContracts(response.data.contracts);
    } catch (error) {
      console.error("Error fetching contracts:", error);
      toast.error("Failed to fetch contracts");
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (contractId: string) => {
    toast.success("Contract uploaded successfully!");
    fetchContracts();
    setActiveTab("list");
  };

  const handleContractSelect = (contract: Contract) => {
    setSelectedContract(contract);
    setActiveTab("detail");
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "processing":
        return <Clock className="w-5 h-5 text-blue-500" />;
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

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Contract Intelligence
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-200 to-purple-200">
                Parser
              </span>
            </h1>
            <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
              Advanced AI-powered contract analysis with Direct Gemini AI
              integration, and intelligent scoring
            </p>

            {/* Feature Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
              <div className="glass-effect rounded-2xl p-6 text-center">
                <Brain className="w-12 h-12 text-blue-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">
                  Direct Gemini AI
                </h3>
                <p className="text-blue-100 text-sm">
                  Direct AI analysis for maximum contract extraction accuracy
                </p>
              </div>
              <div className="glass-effect rounded-2xl p-6 text-center">
                <Zap className="w-12 h-12 text-yellow-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">
                  90%+ Accuracy
                </h3>
                <p className="text-blue-100 text-sm">
                  High-confidence data extraction with intelligent scoring
                </p>
              </div>
              <div className="glass-effect rounded-2xl p-6 text-center">
                <Shield className="w-12 h-12 text-green-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">
                  Enterprise Ready
                </h3>
                <p className="text-blue-100 text-sm">
                  MongoDB Atlas, Docker containerized, production-ready
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab("upload")}
              className={`py-4 px-1 border-b-2 font-semibold text-sm transition-all duration-300 ${
                activeTab === "upload"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <Upload className="w-5 h-5 inline mr-2" />
              Upload Contract
            </button>
            <button
              onClick={() => setActiveTab("list")}
              className={`py-4 px-1 border-b-2 font-semibold text-sm transition-all duration-300 ${
                activeTab === "list"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              <FileText className="w-5 h-5 inline mr-2" />
              Contract List
              {contracts.length > 0 && (
                <span className="ml-2 bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
                  {contracts.length}
                </span>
              )}
            </button>
            {selectedContract && (
              <button
                onClick={() => setActiveTab("detail")}
                className={`py-4 px-1 border-b-2 font-semibold text-sm transition-all duration-300 ${
                  activeTab === "detail"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <Eye className="w-5 h-5 inline mr-2" />
                Contract Details
              </button>
            )}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "upload" && (
          <ContractUpload onUploadSuccess={handleUploadSuccess} />
        )}

        {activeTab === "list" && (
          <ContractList
            contracts={contracts}
            loading={loading}
            onContractSelect={handleContractSelect}
            onRefresh={fetchContracts}
          />
        )}

        {activeTab === "detail" && selectedContract && (
          <ContractDetail
            contract={selectedContract}
            onBack={() => setActiveTab("list")}
          />
        )}
      </div>
    </div>
  );
}
