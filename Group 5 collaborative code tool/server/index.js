import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { PythonShell } from 'python-shell';
import { WebSocketServer } from 'ws';
import * as Y from 'yjs';
import { writeFileSync, mkdirSync, existsSync, readdirSync, statSync } from 'fs';
import { join, dirname } from 'path';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "http://localhost:5173",
    methods: ["GET", "POST"]
  }
});

app.use(cors());
app.use(express.json());

// Workspace management
const workspaces = new Map();

// Create workspace directory
const createWorkspaceDir = (roomId) => {
  const workspaceDir = join(process.cwd(), 'workspaces', roomId);
  if (!existsSync(workspaceDir)) {
    mkdirSync(workspaceDir, { recursive: true });
  }
  return workspaceDir;
};

// Get directory structure
const getDirectoryStructure = (dir) => {
  const files = readdirSync(dir);
  const structure = [];

  for (const file of files) {
    const fullPath = join(dir, file);
    const stats = statSync(fullPath);
    
    if (stats.isDirectory()) {
      structure.push({
        name: file,
        type: 'directory',
        children: getDirectoryStructure(fullPath)
      });
    } else {
      structure.push({
        name: file,
        type: 'file'
      });
    }
  }

  return structure;
};

// WebSocket server for Yjs
const wss = new WebSocketServer({ 
  server: httpServer,
  path: "/collaboration"
});

const docs = new Map();

wss.on('connection', (ws, req) => {
  console.log('New WebSocket connection');
  
  const url = new URL(req.url, `http://${req.headers.host}`);
  const roomId = url.searchParams.get('room');
  const filePath = url.searchParams.get('file') || 'main.py';
  
  if (!roomId) {
    console.log('No room ID provided');
    ws.close();
    return;
  }

  // Get or create Yjs document for this file in this room
  const docKey = `${roomId}:${filePath}`;
  if (!docs.has(docKey)) {
    docs.set(docKey, new Y.Doc());
  }
  const doc = docs.get(docKey);

  // Set up awareness
  const awareness = new Y.Awareness(doc);

  ws.on('message', (message) => {
    try {
      Y.applyUpdate(doc, new Uint8Array(message));
      
      wss.clients.forEach((client) => {
        if (client !== ws && client.readyState === WebSocket.OPEN) {
          client.send(message);
        }
      });
    } catch (err) {
      console.error('Error processing message:', err);
    }
  });

  const initialUpdate = Y.encodeStateAsUpdate(doc);
  ws.send(initialUpdate);

  ws.on('close', () => {
    console.log('Client disconnected');
    awareness.destroy();
  });
});

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  socket.on('create-room', (roomId) => {
    if (!workspaces.has(roomId)) {
      const workspaceDir = createWorkspaceDir(roomId);
      workspaces.set(roomId, {
        dir: workspaceDir,
        users: new Set([socket.id])
      });
      socket.join(roomId);
      socket.emit('room-created', roomId);
      
      // Create initial main.py file
      const mainPyPath = join(workspaceDir, 'main.py');
      if (!existsSync(mainPyPath)) {
        writeFileSync(mainPyPath, '# Write your Python code here\n');
      }
    } else {
      socket.emit('error', 'Room already exists');
    }
  });

  socket.on('join-room', (roomId) => {
    if (workspaces.has(roomId)) {
      socket.join(roomId);
      workspaces.get(roomId).users.add(socket.id);
      
      // Send file structure to client
      const structure = getDirectoryStructure(workspaces.get(roomId).dir);
      socket.emit('file-structure', structure);
      socket.emit('room-joined', roomId);
    } else {
      socket.emit('error', 'Room not found');
    }
  });

  socket.on('create-file', ({ roomId, path, type }) => {
    if (!workspaces.has(roomId)) {
      socket.emit('error', 'Room not found');
      return;
    }

    const fullPath = join(workspaces.get(roomId).dir, path);
    try {
      if (type === 'directory') {
        mkdirSync(fullPath, { recursive: true });
      } else {
        mkdirSync(dirname(fullPath), { recursive: true });
        writeFileSync(fullPath, '');
      }
      
      const structure = getDirectoryStructure(workspaces.get(roomId).dir);
      io.to(roomId).emit('file-structure', structure);
    } catch (error) {
      socket.emit('error', `Failed to create ${type}: ${error.message}`);
    }
  });

  socket.on('execute-code', async ({ roomId, filePath, code }) => {
    try {
      if (!workspaces.has(roomId)) {
        throw new Error('Room not found');
      }

      const workspaceDir = workspaces.get(roomId).dir;
      const fullPath = join(workspaceDir, filePath);
      
      // Write the code to the file
      writeFileSync(fullPath, code);

      let output = '';
      const options = {
        mode: 'text',
        pythonOptions: ['-u'],
        scriptPath: workspaceDir,
        scriptFile: filePath
      };

      const pyshell = new PythonShell(filePath, options);
      
      pyshell.on('message', (message) => {
        output += message + '\n';
      });

      pyshell.end((err) => {
        if (err) {
          socket.emit('code-output', { error: err.message });
        } else {
          socket.emit('code-output', { output: output.trim() });
        }
      });
    } catch (error) {
      socket.emit('code-output', { error: error.message });
    }
  });

  socket.on('disconnect', () => {
    workspaces.forEach((workspace, roomId) => {
      if (workspace.users.has(socket.id)) {
        workspace.users.delete(socket.id);
        if (workspace.users.size === 0) {
          workspaces.delete(roomId);
        }
      }
    });
  });
});

const PORT = process.env.PORT || 3000;
httpServer.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});