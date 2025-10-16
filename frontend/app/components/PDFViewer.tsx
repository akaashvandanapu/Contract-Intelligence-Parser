"use client";

import { useState, useEffect, useCallback } from "react";
import { Download, X, FileText, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

interface PDFViewerProps {
  contractId: string;
  filename: string;
  filePath?: string;
  onClose: () => void;
}

export default function PDFViewer({ contractId, filename, filePath, onClose }: PDFViewerProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPDF = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // First try to get from cache (sessionStorage)
      const cachedUrl = sessionStorage.getItem(`pdf_${contractId}`);
      if (cachedUrl) {
        setPdfUrl(cachedUrl);
        setLoading(false);
        return;
      }

      // If not in cache, download from server
      const response = await fetch(`http://localhost:8000/contracts/${contractId}/download`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to download PDF: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      // Cache the URL in sessionStorage
      sessionStorage.setItem(`pdf_${contractId}`, url);
      
      setPdfUrl(url);
    } catch (err) {
      console.error('Error loading PDF:', err);
      setError(err instanceof Error ? err.message : 'Failed to load PDF');
      toast.error('Failed to load PDF');
    } finally {
      setLoading(false);
    }
  }, [contractId]);

  useEffect(() => {
    loadPDF();
  }, [loadPDF]);

  const handleDownload = async () => {
    try {
      const response = await fetch(`http://localhost:8000/contracts/${contractId}/download`);
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success('PDF downloaded successfully');
    } catch (err) {
      console.error('Download error:', err);
      toast.error('Failed to download PDF');
    }
  };

  const cleanup = useCallback(() => {
    if (pdfUrl) {
      URL.revokeObjectURL(pdfUrl);
    }
    sessionStorage.removeItem(`pdf_${contractId}`);
  }, [pdfUrl, contractId]);

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full h-full max-w-7xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center">
            <FileText className="w-5 h-5 mr-2 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">{filename}</h3>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleDownload}
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </button>
            <button
              onClick={onClose}
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              <X className="w-4 h-4 mr-2" />
              Close
            </button>
          </div>
        </div>

        {/* PDF Content */}
        <div className="flex-1 p-4">
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
                <p className="text-gray-600">Loading PDF...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 mb-2">Failed to load PDF</p>
                <p className="text-sm text-gray-500">{error}</p>
                <button
                  onClick={loadPDF}
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

          {pdfUrl && !loading && !error && (
            <iframe
              src={pdfUrl}
              className="w-full h-full border-0 rounded-lg"
              title={`PDF Viewer - ${filename}`}
            />
          )}
        </div>
      </div>
    </div>
  );
}
