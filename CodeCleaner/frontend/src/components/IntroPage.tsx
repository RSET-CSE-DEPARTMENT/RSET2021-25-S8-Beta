import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Code2, Sparkles, Zap } from 'lucide-react';
import { Theme } from '../types';

interface IntroPageProps {
  theme: Theme;
  onComplete: () => void;
}

export const IntroPage: React.FC<IntroPageProps> = ({ theme, onComplete }) => {
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    const handleInteraction = () => {
      if (isAnimating) {
        setIsAnimating(false);
        setTimeout(onComplete, 1500); // Increased time for exit animation
      }
    };

    window.addEventListener('click', handleInteraction);
    window.addEventListener('keydown', handleInteraction);

    return () => {
      window.removeEventListener('click', handleInteraction);
      window.removeEventListener('keydown', handleInteraction);
    };
  }, [isAnimating, onComplete]);

  return (
    <motion.div
      className={`fixed inset-0 flex items-center justify-center ${
        theme === 'dark' ? 'bg-gray-900' : 'bg-slate-50'
      } z-50`}
      initial={{ opacity: 1 }}
      exit={{ 
        opacity: 0,
        transition: {
          duration: 0.8,
          ease: "easeInOut",
          when: "beforeChildren"
        }
      }}
    >
      <motion.div 
        className="text-center"
        exit={{ 
          scale: 1.2,
          y: -30,
          opacity: 0,
          transition: {
            duration: 0.8,
            ease: "easeInOut"
          }
        }}
      >
        <motion.div
          className="relative inline-block mb-6"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ 
            type: "spring",
            stiffness: 260,
            damping: 20,
            delay: 0.2
          }}
          exit={{
            scale: 0,
            transition: {
              duration: 0.4,
              ease: "easeInOut"
            }
          }}
        >
          <div className={`w-24 h-24 rounded-xl flex items-center justify-center ${
            theme === 'dark' ? 'bg-blue-600' : 'bg-blue-500'
          }`}>
            <Code2 className="w-12 h-12 text-white" />
          </div>
          <motion.div
            className="absolute -top-1 -right-1"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1 }}
          >
            <Sparkles className={`w-6 h-6 ${
              theme === 'dark' ? 'text-blue-400' : 'text-blue-600'
            }`} />
          </motion.div>
          <motion.div
            className="absolute -bottom-1 -left-1"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.2 }}
          >
            <Zap className={`w-6 h-6 ${
              theme === 'dark' ? 'text-blue-400' : 'text-blue-600'
            }`} />
          </motion.div>
        </motion.div>

        <motion.h1
          className={`text-4xl font-bold mb-2 ${
            theme === 'dark' ? 'text-white' : 'text-slate-900'
          }`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          exit={{
            y: -20,
            opacity: 0,
            transition: {
              duration: 0.4,
              ease: "easeInOut"
            }
          }}
        >
          CodeCleaner
        </motion.h1>

        <motion.p
          className={`text-lg ${
            theme === 'dark' ? 'text-gray-400' : 'text-slate-600'
          }`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          exit={{
            y: -20,
            opacity: 0,
            transition: {
              duration: 0.3,
              ease: "easeInOut"
            }
          }}
        >
          The New Way of Coding
        </motion.p>

        <motion.div
          className="mt-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          exit={{
            opacity: 0,
            transition: {
              duration: 0.2
            }
          }}
        >
          <p className={`text-sm ${
            theme === 'dark' ? 'text-gray-500' : 'text-slate-400'
          }`}>
            Click anywhere to continue
          </p>
        </motion.div>

        <motion.div
          className="absolute bottom-0 left-0 right-0 h-1 bg-blue-500"
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 2, ease: "easeInOut" }}
          exit={{
            scaleX: 0,
            transition: {
              duration: 0.4,
              ease: "easeInOut"
            }
          }}
        />
      </motion.div>
    </motion.div>
  );
}; 