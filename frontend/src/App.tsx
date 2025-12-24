import React from 'react';
import { motion } from 'motion/react';
import { IngestCard } from './components/IngestCard';
import { QueryCard } from './components/QueryCard';
import { Sparkles, Database, Cpu } from 'lucide-react';

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0f9ff] via-[#e0f2fe] to-[#dbeafe] relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.2, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute -top-40 -right-40 w-96 h-96 bg-gradient-to-br from-[#60a5fa] to-[#3b82f6] rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.1, 1, 1.1],
            opacity: [0.2, 0.3, 0.2],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-br from-[#a5b4fc] to-[#60a5fa] rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            y: [-20, 20, -20],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-1/2 left-1/2 w-80 h-80 bg-gradient-to-br from-[#93c5fd] to-[#dbeafe] rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"
        />
      </div>

      <div className="relative z-10">
        <div className="max-w-7xl mx-auto px-6 py-14">
          {/* Header */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12 text-center"
          >
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white/70 backdrop-blur-sm rounded-full border border-white/40 shadow-lg"
            >
              <Database className="w-4 h-4 text-[#3b82f6]" />
              <p className="text-xs font-semibold uppercase tracking-wide bg-gradient-to-r from-[#1e3a8a] to-[#3b82f6] bg-clip-text text-transparent">
                Mini-RAG • ChromaDB + SentenceTransformers
              </p>
              <Cpu className="w-4 h-4 text-[#3b82f6]" />
            </motion.div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-5xl md:text-6xl font-bold mt-6 mb-4 bg-gradient-to-r from-[#1e3a8a] to-[#3b82f6] bg-clip-text text-transparent"
            >
              Demo UI
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-[#475569] text-lg flex items-center justify-center gap-2"
            >
              <Sparkles className="w-5 h-5 text-[#3b82f6]" />
              Ingest tài liệu và truy vấn semantic search với AI
              <Sparkles className="w-5 h-5 text-[#3b82f6]" />
            </motion.p>
          </motion.div>

          {/* Main Content */}
          <div className="grid md:grid-cols-2 gap-10 max-w-5xl mx-auto">
            <IngestCard />
            <QueryCard />
          </div>

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-12 text-center"
          >
            <p className="text-xs text-[#94a3b8]">
              Powered by ChromaDB, SentenceTransformers & React
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
