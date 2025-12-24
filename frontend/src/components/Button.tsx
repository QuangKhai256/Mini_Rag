import React from 'react';
import { motion } from 'motion/react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  loadingText?: string;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

export function Button({ 
  loading = false, 
  loadingText, 
  children, 
  disabled,
  variant = 'primary',
  className = '',
  ...props 
}: ButtonProps) {
  const isDisabled = disabled || loading;

  const baseStyles = "w-full py-3.5 px-6 rounded-xl font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2";
  
  const variantStyles = variant === 'primary' 
    ? "bg-gradient-to-r from-[#60a5fa] to-[#3b82f6] text-white shadow-lg shadow-[#3b82f6]/20 hover:shadow-xl hover:shadow-[#3b82f6]/25"
    : "bg-white/70 text-[#3b82f6] border border-[#3b82f6]/20 hover:bg-white/90";
  
  const disabledStyles = isDisabled 
    ? "opacity-60 cursor-not-allowed" 
    : "hover:scale-[1.02] active:scale-[0.98]";

  return (
    <motion.button
      whileHover={!isDisabled ? { scale: 1.02 } : {}}
      whileTap={!isDisabled ? { scale: 0.98 } : {}}
      className={`${baseStyles} ${variantStyles} ${disabledStyles} ${className}`}
      disabled={isDisabled}
      {...props}
    >
      {loading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          {loadingText && <span>{loadingText}</span>}
        </>
      ) : (
        children
      )}
    </motion.button>
  );
}
