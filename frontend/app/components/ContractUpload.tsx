"use client";

import axios from "axios";
import {
  AlertCircle,
  Brain,
  CheckCircle,
  FileText,
  Shield,
  Upload,
  Zap,
} from "lucide-react";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface ContractUploadProps {
  onUploadSuccess: (contractId: string) => void;
}

export default function ContractUpload({
  onUploadSuccess,
}: ContractUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      // Validate file type
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        toast.error("Please upload a PDF file");
        return;
      }

      // Validate file size (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        toast.error("File size must be less than 50MB");
        return;
      }

      setUploading(true);
      setUploadProgress(0);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await axios.post(
          `${API_BASE_URL}/contracts/upload`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
            onUploadProgress: (progressEvent) => {
              if (progressEvent.total) {
                const progress = Math.round(
                  (progressEvent.loaded * 100) / progressEvent.total
                );
                setUploadProgress(progress);
              }
            },
          }
        );

        onUploadSuccess(response.data.contract_id);
      } catch (error: any) {
        console.error("Upload error:", error);
        toast.error(
          error.response?.data?.detail || "Failed to upload contract"
        );
      } finally {
        setUploading(false);
        setUploadProgress(0);
      }
    },
    [onUploadSuccess]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
    },
    multiple: false,
    disabled: uploading,
  });

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold gradient-text mb-4">
          Upload Your Contract
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload a PDF contract and let our advanced AI extract all the critical
          information with 90%+ accuracy
        </p>
      </div>

      {/* Upload Area */}
      <div className="card-gradient">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
            isDragActive
              ? "border-blue-400 bg-blue-50/50 scale-105"
              : "border-gray-300 hover:border-blue-400 hover:bg-blue-50/30"
          } ${uploading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          <input {...getInputProps()} />

          {uploading ? (
            <div className="space-y-6">
              <div className="w-20 h-20 mx-auto bg-gradient-to-r from-blue-100 to-indigo-100 rounded-full flex items-center justify-center animate-pulse-slow">
                <Upload className="w-10 h-10 text-blue-600" />
              </div>
              <div>
                <p className="text-xl font-semibold text-gray-900 mb-2">
                  Uploading Contract...
                </p>
                <div className="w-full bg-gray-200 rounded-full h-3 mt-4">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {uploadProgress}% complete
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="w-20 h-20 mx-auto bg-gradient-to-r from-blue-100 to-indigo-100 rounded-full flex items-center justify-center animate-float">
                <FileText className="w-10 h-10 text-blue-600" />
              </div>
              <div>
                <p className="text-xl font-semibold text-gray-900 mb-2">
                  {isDragActive
                    ? "Drop your PDF here"
                    : "Drag & drop your PDF contract here"}
                </p>
                <p className="text-gray-600 mb-4">
                  or click to browse and select a file
                </p>
                <div className="btn-primary inline-flex items-center">
                  <Upload className="w-5 h-5 mr-2" />
                  Choose File
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="text-center p-4 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50">
            <Brain className="w-8 h-8 text-blue-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">
              Direct Gemini AI
            </h3>
            <p className="text-sm text-gray-600">
              Direct AI analysis for maximum extraction accuracy
            </p>
          </div>
          <div className="text-center p-4 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50">
            <Zap className="w-8 h-8 text-green-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">90%+ Accuracy</h3>
            <p className="text-sm text-gray-600">
              High-confidence data extraction and intelligent scoring
            </p>
          </div>
          <div className="text-center p-4 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50">
            <Shield className="w-8 h-8 text-purple-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">
              Secure Processing
            </h3>
            <p className="text-sm text-gray-600">
              Enterprise-grade security with MongoDB Atlas
            </p>
          </div>
        </div>

        {/* Requirements */}
        <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
          <div className="flex items-start">
            <AlertCircle className="w-6 h-6 text-blue-600 mt-0.5 mr-4 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-3">
                Upload Requirements
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span className="text-sm text-blue-800">PDF files only</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span className="text-sm text-blue-800">
                    Maximum 50MB file size
                  </span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span className="text-sm text-blue-800">
                    Processing takes 1-2 minutes
                  </span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span className="text-sm text-blue-800">
                    Real-time progress tracking
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
