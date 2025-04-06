import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Code2, Wand2, Terminal as TerminalIcon, Check, Sparkles, GitCompare } from 'lucide-react';
import { CodeEditor } from './components/CodeEditor';
import { ThemeToggle } from './components/ThemeToggle';
import { Terminal } from './components/Terminal';
import { Logo } from './components/Logo';
import { IntroPage } from './components/IntroPage';
import { Theme } from './types';
import { AnimatePresence, motion } from 'framer-motion';

export default function App() {
  const [showIntro, setShowIntro] = useState(true);
  const [theme, setTheme] = useState<Theme>('dark');
  const [code, setCode] = useState(`public class HelloWorld {
  public static void main(String[] args) {
    System.out.println("Hello, World!");
  }
}`);
  const [cleanCode, setCleanCode] = useState('// Clean code will appear here...');
  const [terminalMessages, setTerminalMessages] = useState<string[]>([
    'CodeCleaner initialized',
    'Ready to analyze code...'
  ]);
  const [splitPosition, setSplitPosition] = useState(50);
  const [isCleaningCode, setIsCleaningCode] = useState(false);
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState<'same' | 'different' | null>(null);
  const isDragging = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Add state for checkboxes
  const [cleaningOptions, setCleaningOptions] = useState({
    refactoring: true,
    renaming: true,
    summarization: true
  });

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleCodeChange = (value: string) => {
    setCode(value);
  };

  useEffect(() => {
    fetch("http://127.0.0.1:8000/")
      .then(res => res.json())
      .then(data => {
        setTerminalMessages(prev => [...prev, `Connected to Backend: ${data.message}`]);
      })
      .catch(err => {
        console.error("FastAPI connection failed", err);
        setTerminalMessages(prev => [...prev, "Error: Cannot reach backend"]);
      });
  }, []);

  const handleCleanCode = async () => {
    setIsCleaningCode(true);
    setTerminalMessages(prev => [...prev, 'Processing code...']);

    try {
        const response = await fetch("http://127.0.0.1:8000/process_code/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                code: code,
                optimization: cleaningOptions.refactoring,
                renaming: cleaningOptions.renaming,
                summarization: cleaningOptions.summarization
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const stepsApplied = data.steps_applied.join(", ");
        setTerminalMessages(prev => [
            ...prev,
            `Applied steps: ${stepsApplied}`,
            'Code processing completed successfully ✨'
        ]);
        
        // Apply the cleaned code with animation
        await applyCleanCode(data.processed_code);
    } catch (error) {
        console.error("Error:", error);
        setTerminalMessages(prev => [...prev, 'Error: Failed to process code']);
    }

    setIsCleaningCode(false);
  };

  const applyCleanCode = async (cleanedCode: string) => {
    const lines = cleanedCode.split('\n');
    let currentLines = [];
    
    // First, create empty lines with proper indentation
    for (let i = 0; i < lines.length; i++) {
        const indentation = lines[i].match(/^\s*/) || [''];
        currentLines.push(indentation[0]);
    }
    
    // Then, type each line character by character
    for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
        const line = lines[lineIndex];
        const lineContent = line.trimLeft();
        
        // Type each character of the line
        for (let charIndex = 0; charIndex < lineContent.length; charIndex++) {
            currentLines[lineIndex] = currentLines[lineIndex] + lineContent[charIndex];
            setCleanCode(currentLines.join('\n'));
            await new Promise(resolve => setTimeout(resolve, 8));
        }
        
        // Small pause at the end of each line
        await new Promise(resolve => setTimeout(resolve, 100));
    }
  };

  const handleCompare = async () => {
    setIsComparing(true);
    setComparisonResult(null);
    setTerminalMessages(prev => [...prev, 'Comparing code sections...']);
    
    try {
      const response = await fetch("http://127.0.0.1:8000/compare_code/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          original_code: code,
          cleaned_code: cleanCode 
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      setComparisonResult(data.is_same_functionality ? 'same' : 'different');
      setTerminalMessages(prev => [
        ...prev,
        data.explanation
      ]);
    } catch (error) {
      console.error("Error:", error);
      setTerminalMessages(prev => [...prev, 'Error: Failed to compare code']);
      setComparisonResult(null);
    }
    
    setIsComparing(false);
  };

  // Reset comparison result when code changes
  useEffect(() => {
    setComparisonResult(null);
  }, [code, cleanCode]);

  // Add function to handle intro completion
  const handleIntroComplete = () => {
    setShowIntro(false);
  };

  return (
    <>
      <AnimatePresence mode="wait">
        {showIntro ? (
          <IntroPage theme={theme} onComplete={handleIntroComplete} />
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 0.8,
              ease: "easeOut",
            }}
            className={`min-h-screen 
              ${
              theme === 'dark' 
                ? 'bg-gray-900 text-gray-100' 
                : 'bg-slate-50 text-slate-900'
            }`}
            data-theme={theme}
          >
            <motion.header
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className={`${
                theme === 'dark' ? 'bg-gray-800/50 backdrop-blur-sm' : 'bg-white/50 backdrop-blur-sm shadow-sm'
              } border-b ${
                theme === 'dark' ? 'border-gray-700/50' : 'border-slate-200/50'
              } px-4 py-4 sticky top-0 z-10`}
            >
              <div className="flex items-center justify-between max-w-7xl mx-auto">
                <Logo />
                <div className="flex flex-col items-end space-y-2.5">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={handleCleanCode}
                      disabled={isCleaningCode || isComparing}
                      className={`px-6 py-2.5 rounded-lg flex items-center space-x-2 button-text transition-all duration-300 ${
                        isCleaningCode ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105 active:scale-95'
                      } ${
                        theme === 'dark'
                          ? 'bg-blue-600 hover:bg-blue-500 text-white'
                          : 'bg-slate-800 hover:bg-slate-700 text-white'
                      }`}
                    >
                      <Wand2 className="w-5 h-5" />
                      <span className="text-[15px]">Clean Code</span>
                      {isCleaningCode && (
                        <Sparkles className="w-5 h-5 animate-spin" />
                      )}
                    </button>
                    <ThemeToggle theme={theme} onToggle={toggleTheme} />
                  </div>
                  <div className={`flex items-center gap-5 ${
                    theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
                  }`}>
                    <label className="flex items-center gap-1.5 cursor-pointer hover:opacity-80 group">
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={cleaningOptions.refactoring}
                          onChange={(e) => setCleaningOptions(prev => ({ ...prev, refactoring: e.target.checked }))}
                          className={`h-3.5 w-3.5 rounded-full border-2 appearance-none ${
                            theme === 'dark' 
                              ? 'border-gray-600 bg-gray-800/50 checked:bg-blue-600/90' 
                              : 'border-gray-300 bg-white/50 checked:bg-blue-500/90'
                          } focus:ring-0 focus:ring-offset-0 transition-all duration-200 cursor-pointer
                          group-hover:border-opacity-80 checked:border-transparent`}
                        />
                        <div className={`absolute inset-0 rounded-full transition-transform duration-200 pointer-events-none
                          ${cleaningOptions.refactoring ? 'scale-75 bg-current opacity-10' : 'scale-0 opacity-0'}`} />
                      </div>
                      <span className="font-body text-[13px] font-medium tracking-wide">Code Refactoring</span>
                    </label>
                    <label className="flex items-center gap-1.5 cursor-pointer hover:opacity-80 group">
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={cleaningOptions.renaming}
                          onChange={(e) => setCleaningOptions(prev => ({ ...prev, renaming: e.target.checked }))}
                          className={`h-3.5 w-3.5 rounded-full border-2 appearance-none ${
                            theme === 'dark' 
                              ? 'border-gray-600 bg-gray-800/50 checked:bg-blue-600/90' 
                              : 'border-gray-300 bg-white/50 checked:bg-blue-500/90'
                          } focus:ring-0 focus:ring-offset-0 transition-all duration-200 cursor-pointer
                          group-hover:border-opacity-80 checked:border-transparent`}
                        />
                        <div className={`absolute inset-0 rounded-full transition-transform duration-200 pointer-events-none
                          ${cleaningOptions.renaming ? 'scale-75 bg-current opacity-10' : 'scale-0 opacity-0'}`} />
                      </div>
                      <span className="font-body text-[13px] font-medium tracking-wide">Variable Renaming</span>
                    </label>
                    <label className="flex items-center gap-1.5 cursor-pointer hover:opacity-80 group">
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={cleaningOptions.summarization}
                          onChange={(e) => setCleaningOptions(prev => ({ ...prev, summarization: e.target.checked }))}
                          className={`h-3.5 w-3.5 rounded-full border-2 appearance-none ${
                            theme === 'dark' 
                              ? 'border-gray-600 bg-gray-800/50 checked:bg-blue-600/90' 
                              : 'border-gray-300 bg-white/50 checked:bg-blue-500/90'
                          } focus:ring-0 focus:ring-offset-0 transition-all duration-200 cursor-pointer
                          group-hover:border-opacity-80 checked:border-transparent`}
                        />
                        <div className={`absolute inset-0 rounded-full transition-transform duration-200 pointer-events-none
                          ${cleaningOptions.summarization ? 'scale-75 bg-current opacity-10' : 'scale-0 opacity-0'}`} />
                      </div>
                      <span className="font-body text-[13px] font-medium tracking-wide">Code Summarization</span>
                    </label>
                  </div>
                </div>
              </div>
            </motion.header>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className={`px-4 py-1.5 ${
                theme === 'dark' ? 'bg-gray-800/20' : 'bg-slate-100/50'
              }`}
            >
              <div className="flex justify-end max-w-7xl mx-auto">
                <button
                  onClick={handleCompare}
                  disabled={isCleaningCode || isComparing}
                  className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 text-sm font-medium transition-all duration-300 ${
                    isComparing ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105 active:scale-95'
                  } ${
                    theme === 'dark'
                      ? 'bg-green-600/80 hover:bg-green-500 text-white'
                      : 'bg-green-700/80 hover:bg-green-600 text-white'
                  }`}
                >
                  <GitCompare className="w-3.5 h-3.5" />
                  <span>Compare Code</span>
                  {isComparing && (
                    <Sparkles className="w-3.5 h-3.5 animate-spin" />
                  )}
                </button>
              </div>
            </motion.div>

            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="flex flex-col h-[calc(100vh-57px-36px)]"
            >
              <div ref={containerRef} className="flex flex-1 relative overflow-hidden">
                <div style={{ width: `${splitPosition}%` }} className="h-full">
                  <CodeEditor code={code} onChange={handleCodeChange} theme={theme} language="java" />
                </div>

                <div className="w-1 cursor-col-resize bg-gray-700" />

                <div style={{ width: `${100 - splitPosition}%` }} className="h-full">
                  <div className={`h-full transition-colors duration-300 ${
                    comparisonResult === 'same' 
                      ? 'bg-green-500/10' 
                      : comparisonResult === 'different' 
                        ? 'bg-red-500/10' 
                        : ''
                  }`}>
                    <CodeEditor code={cleanCode} onChange={setCleanCode} theme={theme} language="java" />
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-700/50">
                <Terminal messages={terminalMessages} theme={theme} />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
