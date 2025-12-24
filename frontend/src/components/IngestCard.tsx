import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardHeader } from './Card';
import { Label } from './Label';
import { Input } from './Input';
import { FileInput } from './FileInput';
import { Button } from './Button';
import { CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';

interface Status {
  type: 'success' | 'error';
  message: string;
}

export function IngestCard() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [collection, setCollection] = useState('my_docs');
  const [modelDir, setModelDir] = useState('./all-MiniLM-L6-v2');
  const [chunkSize, setChunkSize] = useState('800');
  const [overlap, setOverlap] = useState('150');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<Status | null>(null);

  const handleIngest = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setStatus(null);

    // Simulate ingestion process
    setTimeout(() => {
      setStatus({ 
        type: 'success', 
        message: `Ingest thành công: ${selectedFile.name}` 
      });
      setLoading(false);
    }, 2500);
  };

  const isDisabled = !selectedFile || !collection || !modelDir || !chunkSize || !overlap;

  return (
    <Card delay={0.1}>
      <CardHeader title="Ingest" />
      
      <div className="space-y-6">
        <div>
          <Label>File (PDF/DOCX/TXT)</Label>
          <FileInput 
            selectedFile={selectedFile}
            onFileSelect={setSelectedFile}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label>Collection</Label>
            <Input
              value={collection}
              onChange={(e) => setCollection(e.target.value)}
              placeholder="my_docs"
            />
          </div>
          <div>
            <Label>Model dir</Label>
            <Input
              value={modelDir}
              onChange={(e) => setModelDir(e.target.value)}
              placeholder="./all-MiniLM-L6-v2"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label>Chunk size</Label>
            <Input
              type="number"
              value={chunkSize}
              onChange={(e) => setChunkSize(e.target.value)}
              placeholder="800"
            />
          </div>
          <div>
            <Label>Overlap</Label>
            <Input
              type="number"
              value={overlap}
              onChange={(e) => setOverlap(e.target.value)}
              placeholder="150"
            />
          </div>
        </div>

        <Button
          onClick={handleIngest}
          loading={loading}
          loadingText="Đang ingest..."
          disabled={isDisabled}
        >
          <Sparkles className="w-4 h-4" />
          Ingest Document
        </Button>

        <AnimatePresence>
          {status && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`p-4 rounded-xl border ${
                status.type === 'success'
                  ? 'bg-[#f0fdf4]/80 border-[#22c55e]/20'
                  : 'bg-[#fef2f2]/80 border-[#ef4444]/20'
              }`}
            >
              <div className="flex items-start gap-3">
                {status.type === 'success' ? (
                  <CheckCircle2 className="w-5 h-5 text-[#22c55e] flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-[#ef4444] flex-shrink-0 mt-0.5" />
                )}
                <p className={`text-sm font-medium ${
                  status.type === 'success' ? 'text-[#166534]' : 'text-[#991b1b]'
                }`}>
                  {status.message}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </Card>
  );
}
