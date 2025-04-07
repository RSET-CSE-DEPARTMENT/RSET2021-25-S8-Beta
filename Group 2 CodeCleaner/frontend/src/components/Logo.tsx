import React from 'react';

export const Logo: React.FC = () => {
  return (
    <div className="flex items-center space-x-3">
      <svg
        width="36"
        height="36"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="text-blue-500"
      >
        <path
          d="M16 2L3 9V23L16 30L29 23V9L16 2Z"
          stroke="currentColor"
          strokeWidth="2"
          fill="none"
        />
        <path
          d="M16 8L8 12V20L16 24L24 20V12L16 8Z"
          fill="currentColor"
        />
      </svg>
      <div className="flex flex-col">
        <h1 className="header-title text-2xl leading-none mb-0.5">CodeCleaner</h1>
        <span className="header-subtitle text-[0.65rem] text-blue-500 uppercase tracking-widest">Java Edition</span>
      </div>
    </div>
  );
};