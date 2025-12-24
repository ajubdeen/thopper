import * as pty from "node-pty";
import { WebSocket, WebSocketServer } from "ws";
import type { Server } from "http";
import path from "path";

interface TerminalSession {
  ptyProcess: pty.IPty;
  ws: WebSocket;
}

const sessions = new Map<WebSocket, TerminalSession>();

export function setupPtyWebSocket(server: Server): void {
  const wss = new WebSocketServer({
    server,
    path: "/ws/terminal",
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

    sessions.set(ws, { ptyProcess, ws });

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
