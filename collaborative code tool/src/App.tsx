import React, { useState, useEffect } from 'react';
import { Socket, io } from 'socket.io-client';
import Editor from '@monaco-editor/react';
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import { MonacoBinding } from 'y-monaco';
import { Toaster, toast } from 'sonner';
import { Code2, Users, Play } from 'lucide-react';
import FileExplorer from './components/FileExplorer';

interface FileNode {
  name: string;
  type: 'file' | 'directory';
  children?: FileNode[];
}

const SERVER_URL = 'http://localhost:3000';

function App() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [roomId, setRoomId] = useState('');
  const [username, setUsername] = useState('');
  const [isJoined, setIsJoined] = useState(false);
  const [editorContent, setEditorContent] = useState('# Write your Python code here\n');
  const [output, setOutput] = useState('');
  const [files, setFiles] = useState<FileNode[]>([]);
  const [currentFile, setCurrentFile] = useState('main.py');

  useEffect(() => {
    const newSocket = io(SERVER_URL);
    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  useEffect(() => {
    if (!socket) return;

    socket.on('room-created', (id) => {
      toast.success(`Room created: ${id}`);
      setIsJoined(true);
    });

    socket.on('room-joined', () => {
      toast.success(`Joined room: ${roomId}`);
      setIsJoined(true);
    });

    socket.on('error', (message) => {
      toast.error(message);
    });

    socket.on('code-output', (data) => {
      if (data.error) {
        setOutput(`Error: ${data.error}`);
        toast.error('Execution failed');
      } else {
        setOutput(data.output);
        toast.success('Code executed successfully');
      }
    });

    socket.on('file-structure', (structure) => {
      setFiles(structure);
    });

    return () => {
      socket.off('room-created');
      socket.off('room-joined');
      socket.off('error');
      socket.off('code-output');
      socket.off('file-structure');
    };
  }, [socket, roomId]);

  const generateRoomId = () => {
    const id = Math.random().toString(36).substring(2, 8);
    setRoomId(id);
  };

  const handleJoinRoom = () => {
    if (!socket?.connected) {
      toast.error('Server connection failed. Please try again later.');
      return;
    }
    if (!roomId || !username) {
      toast.error('Please enter both Room ID and Username');
      return;
    }
    socket?.emit('join-room', roomId);
  };

  const handleCreateRoom = () => {
    if (!socket?.connected) {
      toast.error('Server connection failed. Please try again later.');
      return;
    }
    if (!roomId || !username) {
      toast.error('Please enter both Room ID and Username');
      return;
    }
    socket?.emit('create-room', roomId);
  };

  const handleEditorDidMount = (editor: any, monaco: any) => {
    try {
      const doc = new Y.Doc();
      const provider = new WebsocketProvider(
        `${SERVER_URL.replace('http', 'ws')}/collaboration`,
        `${roomId}?file=${currentFile}`,
        doc
      );
      const type = doc.getText('monaco');
      const binding = new MonacoBinding(
        type,
        editor.getModel(),
        new Set([editor]),
        provider.awareness
      );

      provider.on('status', ({ status }: { status: string }) => {
        if (status === 'connected') {
          toast.success('Collaboration connected');
        } else if (status === 'disconnected') {
          toast.error('Collaboration disconnected');
        }
      });
    } catch (error) {
      console.error('Collaboration setup failed:', error);
      toast.error('Failed to setup collaboration');
    }
  };

  const handleFileSelect = (path: string) => {
    setCurrentFile(path);
    // Reset editor content and reconnect WebSocket for the new file
    setEditorContent('');
  };

  const handleCreateFile = (path: string, type: 'file' | 'directory') => {
    socket?.emit('create-file', { roomId, path, type });
  };

  const executeCode = () => {
    if (!socket?.connected) {
      toast.error('Server connection failed. Please try again later.');
      return;
    }
    socket?.emit('execute-code', { roomId, filePath: currentFile, code: editorContent });
  };

  if (!isJoined) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <div className="flex items-center justify-center mb-8">
            <Code2 className="w-12 h-12 text-indigo-600" />
          </div>
          <h1 className="text-2xl font-bold text-center mb-6">Collaborative Python Editor</h1>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Enter username"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Room ID
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={roomId}
                  onChange={(e) => setRoomId(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter room ID"
                />
                <button
                  onClick={generateRoomId}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Generate
                </button>
              </div>
            </div>
            <div className="flex gap-4">
              <button
                onClick={handleCreateRoom}
                className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                Create Room
              </button>
              <button
                onClick={handleJoinRoom}
                className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Join Room
              </button>
            </div>
          </div>
        </div>
        <Toaster />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Code2 className="w-8 h-8 text-indigo-600" />
              <h1 className="text-xl font-semibold text-gray-900">Python Collaborative Editor</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Users className="w-5 h-5 text-gray-500" />
              <span className="text-sm text-gray-600">{username} • Room: {roomId}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex flex-col md:flex-row gap-4 p-4 max-w-7xl mx-auto w-full">
        <div className="w-64">
          <FileExplorer
            files={files}
            onFileSelect={handleFileSelect}
            onCreateFile={handleCreateFile}
            currentFile={currentFile}
          />
        </div>
        
        <div className="flex-1">
          <div className="bg-white rounded-lg shadow-sm h-full">
            <Editor
              height="70vh"
              defaultLanguage="python"
              value={editorContent}
              onChange={(value) => setEditorContent(value || '')}
              onMount={handleEditorDidMount}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                wordWrap: 'on',
              }}
            />
          </div>
        </div>

        <div className="w-full md:w-96">
          <div className="bg-white rounded-lg shadow-sm p-4 h-full">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Output</h2>
              <button
                onClick={executeCode}
                className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <Play className="w-4 h-4" />
                <span>Run</span>
              </button>
            </div>
            <pre className="bg-gray-50 p-4 rounded-md h-[calc(70vh-8rem)] overflow-auto">
              {output || 'Code output will appear here...'}
            </pre>
          </div>
        </div>
      </div>
      <Toaster />
    </div>
  );
}

export default App;