import * as pty from "node-pty";
import { WebSocket, WebSocketServer } from "ws";
import type { Server } from "http";
import path from "path";

interface TerminalSession {
  ptyProcess: pty.IPty;
  ws: WebSocket;
  isAlive: boolean;
}

const sessions = new Map<WebSocket, TerminalSession>();

export function setupPtyWebSocket(server: Server): void {
  const wss = new WebSocketServer({
    server,
    path: "/ws/terminal",
  });

  // Ping/pong to keep connections alive - check every 15 seconds
  const interval = setInterval(() => {
    const now = new Date().toISOString();
    wss.clients.forEach((ws) => {
      const session = sessions.get(ws);
      if (session) {
        if (!session.isAlive) {
          console.log(`[${now}] Terminating inactive WebSocket - no pong received in 15s`);
          ws.terminate();
          return;
        }
        session.isAlive = false;
        console.log(`[${now}] Sending server ping, marking isAlive=false`);
        ws.ping();
      }
    });
  }, 15000);

  wss.on("close", () => {
    clearInterval(interval);
  });

  wss.on("connection", (ws: WebSocket) => {
    console.log("Terminal WebSocket connected");

    const gamePath = path.join(process.cwd(), "game", "game.py");
    
    const ptyProcess = pty.spawn("python", [gamePath], {
      name: "xterm-256color",
      cols: 80,
      rows: 24,
      cwd: path.join(process.cwd(), "game"),
      env: {
        ...process.env,
        TERM: "xterm-256color",
        COLORTERM: "truecolor",
        PYTHONUNBUFFERED: "1",
      },
    });

    sessions.set(ws, { ptyProcess, ws, isAlive: true });

    // Handle pong to mark connection as alive
    ws.on("pong", () => {
      const now = new Date().toISOString();
      console.log(`[${now}] Received pong from browser, marking isAlive=true`);
      const session = sessions.get(ws);
      if (session) {
        session.isAlive = true;
      }
    });

    ptyProcess.onData((data: string) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    });

    ptyProcess.onExit(({ exitCode }) => {
      console.log(`Game process exited with code ${exitCode}`);
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("\r\n\x1b[33mGame session ended. Refresh to start a new game.\x1b[0m\r\n");
      }
    });

    ws.on("message", (message: Buffer | string) => {
      try {
        const msg = JSON.parse(message.toString());
        
        if (msg.type === "input") {
          ptyProcess.write(msg.data);
        } else if (msg.type === "resize") {
          ptyProcess.resize(msg.cols || 80, msg.rows || 24);
        } else if (msg.type === "ping") {
          // Client heartbeat - mark connection as alive
          const now = new Date().toISOString();
          console.log(`[${now}] Received client ping message, marking isAlive=true`);
          const session = sessions.get(ws);
          if (session) {
            session.isAlive = true;
          }
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    });

    ws.on("close", () => {
      console.log("Terminal WebSocket disconnected");
      const session = sessions.get(ws);
      if (session) {
        session.ptyProcess.kill();
        sessions.delete(ws);
      }
    });

    ws.on("error", (error) => {
      console.error("WebSocket error:", error);
      const session = sessions.get(ws);
      if (session) {
        session.ptyProcess.kill();
        sessions.delete(ws);
      }
    });
  });

  console.log("PTY WebSocket server ready on /ws/terminal");
}
