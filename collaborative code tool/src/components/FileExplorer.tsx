import React from 'react';
import { Folder, File, Plus, FolderPlus } from 'lucide-react';

interface FileNode {
  name: string;
  type: 'file' | 'directory';
  children?: FileNode[];
}

interface FileExplorerProps {
  files: FileNode[];
  onFileSelect: (path: string) => void;
  onCreateFile: (path: string, type: 'file' | 'directory') => void;
  currentFile: string;
}

const FileExplorer: React.FC<FileExplorerProps> = ({
  files,
  onFileSelect,
  onCreateFile,
  currentFile
}) => {
  const renderTree = (nodes: FileNode[], parentPath: string = '') => {
    return nodes.map((node) => {
      const path = `${parentPath}${parentPath ? '/' : ''}${node.name}`;
      
      if (node.type === 'directory') {
        return (
          <div key={path} className="ml-4">
            <div className="flex items-center group">
              <Folder className="w-4 h-4 text-yellow-500 mr-2" />
              <span className="text-gray-700">{node.name}</span>
              <div className="hidden group-hover:flex ml-2 space-x-1">
                <button
                  onClick={() => onCreateFile(`${path}/new-file.py`, 'file')}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <Plus className="w-3 h-3 text-gray-500" />
                </button>
                <button
                  onClick={() => onCreateFile(`${path}/new-folder`, 'directory')}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <FolderPlus className="w-3 h-3 text-gray-500" />
                </button>
              </div>
            </div>
            {node.children && renderTree(node.children, path)}
          </div>
        );
      }

      return (
        <div
          key={path}
          className={`ml-4 flex items-center cursor-pointer ${
            currentFile === path ? 'bg-blue-100' : 'hover:bg-gray-100'
          } rounded px-2 py-1`}
          onClick={() => onFileSelect(path)}
        >
          <File className="w-4 h-4 text-gray-500 mr-2" />
          <span className="text-gray-700">{node.name}</span>
        </div>
      );
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 h-full overflow-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Files</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => onCreateFile('new-file.py', 'file')}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <Plus className="w-4 h-4 text-gray-500" />
          </button>
          <button
            onClick={() => onCreateFile('new-folder', 'directory')}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <FolderPlus className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      </div>
      {renderTree(files)}
    </div>
  );
};

export default FileExplorer;