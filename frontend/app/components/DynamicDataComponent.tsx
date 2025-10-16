"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Info, AlertCircle } from "lucide-react";

interface DynamicDataItem {
  key: string;
  value: any;
  confidence?: number;
  type: "text" | "number" | "date" | "boolean" | "array" | "object";
  description?: string;
}

interface DynamicDataComponentProps {
  title: string;
  data: DynamicDataItem[];
  icon?: React.ReactNode;
  color?: string;
}

export default function DynamicDataComponent({ 
  title, 
  data, 
  icon, 
  color = "blue" 
}: DynamicDataComponentProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const colorClasses = {
    blue: "bg-blue-50 border-blue-200 text-blue-900",
    green: "bg-green-50 border-green-200 text-green-900",
    purple: "bg-purple-50 border-purple-200 text-purple-900",
    orange: "bg-orange-50 border-orange-200 text-orange-900",
    red: "bg-red-50 border-red-200 text-red-900",
    indigo: "bg-indigo-50 border-indigo-200 text-indigo-900"
  };

  const renderValue = (item: DynamicDataItem) => {
    switch (item.type) {
      case "array":
        return (
          <div className="space-y-1">
            {Array.isArray(item.value) ? item.value.map((val, index) => (
              <div key={index} className="text-sm bg-white rounded px-2 py-1 border">
                {typeof val === "object" ? JSON.stringify(val, null, 2) : String(val)}
              </div>
            )) : "No items"}
          </div>
        );
      case "object":
        return (
          <div className="text-sm bg-white rounded p-2 border">
            <pre className="whitespace-pre-wrap text-xs">
              {JSON.stringify(item.value, null, 2)}
            </pre>
          </div>
        );
      case "boolean":
        return (
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            item.value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
          }`}>
            {item.value ? "Yes" : "No"}
          </span>
        );
      case "date":
        return (
          <span className="text-sm">
            {new Date(item.value).toLocaleDateString()}
          </span>
        );
      case "number":
        return (
          <span className="text-sm font-mono">
            {typeof item.value === "number" ? item.value.toLocaleString() : item.value}
          </span>
        );
      default:
        return (
          <span className="text-sm">
            {String(item.value || "Not available")}
          </span>
        );
    }
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return "text-gray-500";
    if (confidence >= 80) return "text-green-600";
    if (confidence >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className={`rounded-lg border ${colorClasses[color as keyof typeof colorClasses] || colorClasses.blue}`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-opacity-80 transition-colors"
      >
        <div className="flex items-center">
          {icon && <div className="mr-3">{icon}</div>}
          <div>
            <h4 className="font-semibold">{title}</h4>
            <p className="text-sm opacity-75">
              {data.length} {data.length === 1 ? "item" : "items"} extracted
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {data.some(item => item.confidence) && (
            <div className="text-xs">
              Avg: {Math.round(
                data.filter(item => item.confidence).reduce((sum, item) => sum + (item.confidence || 0), 0) /
                data.filter(item => item.confidence).length || 0
              )}%
            </div>
          )}
          {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </div>
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-opacity-20">
          <div className="space-y-3 mt-3">
            {data.map((item, index) => (
              <div key={index} className="bg-white rounded p-3 border">
                <div className="flex items-center justify-between mb-2">
                  <h5 className="font-medium text-gray-900 capitalize">
                    {item.key.replace(/_/g, " ")}
                  </h5>
                  {item.confidence && (
                    <span className={`text-xs font-medium ${getConfidenceColor(item.confidence)}`}>
                      {Math.round(item.confidence)}% confidence
                    </span>
                  )}
                </div>
                {item.description && (
                  <p className="text-xs text-gray-600 mb-2 flex items-center">
                    <Info className="w-3 h-3 mr-1" />
                    {item.description}
                  </p>
                )}
                <div className="text-gray-800">
                  {renderValue(item)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
