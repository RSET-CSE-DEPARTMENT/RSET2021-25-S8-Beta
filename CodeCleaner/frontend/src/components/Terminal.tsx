import React, { useState, useRef, useEffect } from 'react';
import { Terminal as TerminalIcon, ChevronUp, ChevronDown, GripHorizontal } from 'lucide-react';
import { TerminalProps } from '../types';

export const Terminal: React.FC<TerminalProps> = ({ messages, theme }) => {
  const [height, setHeight] = useState(200); // Default height in pixels
  const isDragging = useRef(false);
  const startY = useRef(0);
  const startHeight = useRef(0);

  const handleMouseDown = (e: React.MouseEvent) => {
    isDragging.current = true;
    startY.current = e.clientY;
    startHeight.current = height;
    document.body.style.cursor = 'row-resize';
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current) return;
      
      const delta = startY.current - e.clientY;
      const newHeight = Math.min(Math.max(100, startHeight.current + delta), window.innerHeight * 0.8);
      setHeight(newHeight);
    };

    const handleMouseUp = () => {
      isDragging.current = false;
      document.body.style.cursor = '';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const isComparisonResult = (message: string) => {
    return message.startsWith('SAME_FUNCTIONALITY') || message.startsWith('DIFFERENT_FUNCTIONALITY');
  };

  const isCleanCodeSuccess = (message: string) => {
    return message.includes('Code processing completed successfully') || 
           message.includes('Clean code applied successfully');
  };

  const getMessageClass = (message: string) => {
    if (isComparisonResult(message)) {
      if (message.startsWith('SAME_FUNCTIONALITY')) {
        return theme === 'dark' 
          ? 'bg-green-900/30 border-green-500/50 text-green-400' 
          : 'bg-green-100 border-green-500/30 text-green-700';
      }
      if (message.startsWith('DIFFERENT_FUNCTIONALITY')) {
        return theme === 'dark'
          ? 'bg-red-900/30 border-red-500/50 text-red-400'
          : 'bg-red-100 border-red-500/30 text-red-700';
      }
    }
    
    if (isCleanCodeSuccess(message)) {
      return theme === 'dark'
        ? 'bg-blue-900/20 border-blue-500/30 text-blue-400'
        : 'bg-blue-50 border-blue-300/30 text-blue-700';
    }
    
    return '';
  };

  return (
    <div style={{ height: `${height}px` }} className="relative flex flex-col">
      {/* Drag handle */}
      <div 
        className={`absolute top-0 left-0 right-0 h-2 cursor-row-resize flex items-center justify-center -translate-y-full
          ${theme === 'dark' ? 'bg-gray-800/50' : 'bg-slate-200/50'} 
          hover:bg-opacity-100 transition-colors`}
        onMouseDown={handleMouseDown}
      >
        <GripHorizontal className="w-4 h-4 opacity-50" />
      </div>

      <div className={`flex-1 flex flex-col ${
        theme === 'dark' ? 'bg-gray-950' : 'bg-white'
      }`}>
        <div className={`px-4 py-2 ${
          theme === 'dark' ? 'bg-gray-800 text-gray-200' : 'bg-slate-100 text-slate-700'
        } border-b ${
          theme === 'dark' ? 'border-gray-700' : 'border-slate-200'
        } flex items-center`}>
          <TerminalIcon className="w-4 h-4 mr-2" />
          <span className="font-medium">Terminal</span>
        </div>

        <div className={`flex-1 p-4 font-mono text-sm overflow-y-auto ${
          theme === 'dark' ? 'text-gray-300 bg-gray-950' : 'text-slate-700 bg-white'
        } custom-scrollbar`}
        style={{
          maxHeight: 'calc(100vh - 200px)'
        }}>
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`mb-2 terminal-message ${
                isComparisonResult(message) 
                  ? 'comparison-result p-3 rounded-md border'
                  : isCleanCodeSuccess(message)
                    ? 'success-message p-2 rounded-md border'
                    : ''
              } ${getMessageClass(message)}`}
              style={{ 
                animationDelay: `${index * 100}ms`,
              }}
            >
              {!isComparisonResult(message) && !isCleanCodeSuccess(message) && (
                <span className={theme === 'dark' ? 'text-blue-500' : 'text-blue-600'}>$</span>
              )} {message}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};