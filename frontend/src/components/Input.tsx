import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export function Input({ className = '', ...props }: InputProps) {
  return (
    <input
      className={`w-full px-4 py-3 bg-white/60 border border-white/30 rounded-xl 
      text-[#334155] placeholder:text-[#94a3b8]
      focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20 focus:border-[#3b82f6]/40
      transition-all duration-200 ${className}`}
      {...props}
    />
  );
}
