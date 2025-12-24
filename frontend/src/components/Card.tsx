import React from 'react';
import { motion } from 'motion/react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export function Card({ children, className = '', delay = 0 }: CardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={`bg-white/80 backdrop-blur-xl rounded-2xl border border-white/20 p-7 ${className}`}
      style={{ 
        boxShadow: '0 20px 60px rgba(59, 130, 246, 0.12), 0 0 1px rgba(0, 0, 0, 0.05)' 
      }}
    >
      {children}
    </motion.div>
  );
}

interface CardHeaderProps {
  title: string;
}

export function CardHeader({ title }: CardHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-6">
      <h2 className="text-xl font-semibold bg-gradient-to-r from-[#1e3a8a] to-[#3b82f6] bg-clip-text text-transparent">
        {title}
      </h2>
    </div>
  );
}
