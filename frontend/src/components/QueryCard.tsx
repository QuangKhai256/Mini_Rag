import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardHeader } from './Card';
import { Label } from './Label';
import { Input } from './Input';
import { Textarea } from './Textarea';
import { Button } from './Button';
import { Search, FileText, TrendingUp, MessageSquare } from 'lucide-react';
import { queryRag, QueryHit } from '../api';

interface QueryResult {
  title: string;
  snippet: string;
  score: number;
  filename: string;
}

export function QueryCard() {
  const [query, setQuery] = useState('');
  const [collection, setCollection] = useState('my_docs');
  const [modelDir, setModelDir] = useState('./all-MiniLM-L6-v2');
  const [topK, setTopK] = useState('5');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<QueryHit[]>([]);
  const [answer, setAnswer] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setSearched(false);
    setResults([]);
    setAnswer(null);
    setError(null);

    try {
      const response = await queryRag({
        question: query,
        collection,
        top_k: parseInt(topK),
        model_dir: modelDir,
        use_llm: true
      });
      
      setResults(response.results || []);
      setAnswer(response.answer || null);
      setSearched(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Lỗi không xác định');
    } finally {
      setLoading(false);
    }
  };

  const isDisabled = !query.trim() || !collection || !modelDir;

  return (
    <Card delay={0.2}>
      <CardHeader title="Query" />
      
      <div className="space-y-6">
        <div>
          <Label>Câu hỏi</Label>
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Nhập nội dung bạn muốn tìm kiếm..."
            rows={4}
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

        <div>
          <Label>Kết quả</Label>
          <Input
            type="number"
            value={topK}
            onChange={(e) => setTopK(e.target.value)}
            placeholder="5"
            min="1"
            max="10"
          />
        </div>

        <Button
          onClick={handleSearch}
          loading={loading}
          loadingText="Đang tìm..."
          disabled={isDisabled}
        >
          <Search className="w-4 h-4" />
          Tìm kiếm
        </Button>

        {/* Results */}
        <div className="min-h-[200px]">
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600"
            >
              {error}
            </motion.div>
          )}

          {/* Answer Section */}
          {answer && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200"
            >
              <div className="flex items-center gap-2 mb-3">
                <MessageSquare className="w-5 h-5 text-blue-600" />
                <h3 className="text-sm font-semibold text-blue-900">Câu trả lời</h3>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                {answer}
              </p>
            </motion.div>
          )}

          <AnimatePresence mode="wait">
            {results.length > 0 ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="space-y-4"
              >
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  Nguồn tham khảo ({results.length})
                </h3>
                {results.map((result, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-4 bg-white/50 rounded-xl border border-white/30 hover:bg-white/60 transition-all duration-200"
                  >
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <h3 className="text-sm font-semibold text-[#334155] flex-1">
                        {result.metadata?.source || 'Unknown'}
                        {result.metadata?.page && ` (Trang ${result.metadata.page})`}
                      </h3>
                      <div className="flex items-center gap-1 text-xs font-medium text-[#3b82f6] bg-[#3b82f6]/10 px-2 py-1 rounded-full">
                        <TrendingUp className="w-3 h-3" />
                        {(1 - result.distance).toFixed(2)}
                      </div>
                    </div>
                    <p className="text-xs text-[#64748b] leading-relaxed mb-3">
                      {result.text.length > 300 ? result.text.substring(0, 300) + '...' : result.text}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-[#94a3b8]">
                      <FileText className="w-3.5 h-3.5" />
                      <span>Rank: {result.rank} • Distance: {result.distance.toFixed(3)}</span>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            ) : searched && !loading && !error ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center h-[200px] text-center"
              >
                <Search className="w-12 h-12 text-[#cbd5e1] mb-3" />
                <p className="text-sm text-[#94a3b8]">
                  Không tìm thấy kết quả phù hợp
                </p>
              </motion.div>
            ) : !error ? (
              <motion.div
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center h-[200px] text-center"
              >
                <Search className="w-12 h-12 text-[#cbd5e1] mb-3" />
                <p className="text-sm text-[#94a3b8]">
                  Nhập câu hỏi và nhấn tìm kiếm
                </p>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      </div>
    </Card>
  );
}