import React, { useRef } from 'react';
import { motion } from 'motion/react';
import { Upload, FileText, X } from 'lucide-react';

interface FileInputProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

export function FileInput({ onFileSelect, selectedFile }: FileInputProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    onFileSelect(file);
  };

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFileSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
        className="hidden"
      />
      
      <motion.div
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        onClick={handleClick}
        className="w-full p-4 border-2 border-dashed border-[#cbd5e1]/60 rounded-xl bg-white/40 cursor-pointer hover:bg-white/50 hover:border-[#3b82f6]/40 transition-all duration-200"
      >
        {selectedFile ? (
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <div className="p-2 bg-[#3b82f6]/10 rounded-lg">
                <FileText className="w-5 h-5 text-[#3b82f6]" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-[#334155] truncate">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-[#94a3b8]">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={clearFile}
              className="p-1 hover:bg-[#ef4444]/10 rounded-full transition-colors"
            >
              <X className="w-4 h-4 text-[#ef4444]" />
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-3 text-[#64748b]">
            <Upload className="w-5 h-5" />
            <span className="text-sm font-medium">
              Nhấn để chọn tệp (PDF, DOCX, TXT)
            </span>
          </div>
        )}
      </motion.div>
    </div>
  );
}
