import { spawn, ChildProcess } from "child_process";
import type { Server } from "http";
import { Server as SocketIOServer } from "socket.io";
import { io as SocketIOClient, Socket as ClientSocket } from "socket.io-client";
import path from "path";

let pythonServer: ChildProcess | null = null;
const clientSockets = new Map<string, ClientSocket>();

export function setupPtyWebSocket(httpServer: Server): void {
  const gameDir = path.join(process.cwd(), "game");
  const serverPath = path.join(gameDir, "server.py");

  console.log("Starting Python game server...");
  
  pythonServer = spawn("python", [serverPath], {
    cwd: gameDir,
    env: {
      ...process.env,
      GAME_SERVER_PORT: "5001",
      PYTHONUNBUFFERED: "1",
    },
    stdio: ["pipe", "pipe", "pipe"],
  });

  pythonServer.stdout?.on("data", (data) => {
    console.log(`[Python] ${data.toString().trim()}`);
  });

  pythonServer.stderr?.on("data", (data) => {
    const msg = data.toString().trim();
    if (!msg.includes('DEBUG') && !msg.includes('INFO')) {
      console.error(`[Python Error] ${msg}`);
    }
  });

  pythonServer.on("error", (err) => {
    console.error("Failed to start Python game server:", err);
  });

  pythonServer.on("exit", (code, signal) => {
    console.log(`Python game server exited with code ${code}, signal ${signal}`);
    pythonServer = null;
  });

  const io = new SocketIOServer(httpServer, {
    path: "/socket.io/",
    cors: {
      origin: "*",
      methods: ["GET", "POST"],
    },
    pingTimeout: 60000,
    pingInterval: 25000,
  });

  io.on("connection", (browserSocket) => {
    console.log(`Browser connected: ${browserSocket.id}`);

    const pythonSocket = SocketIOClient("http://127.0.0.1:5001", {
      transports: ["websocket"],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    clientSockets.set(browserSocket.id, pythonSocket);

    pythonSocket.on("connect", () => {
      console.log(`Proxy connected to Python server for ${browserSocket.id}`);
    });

    pythonSocket.on("message", (data: any) => {
      browserSocket.emit("message", data);
    });

    pythonSocket.on("disconnect", (reason) => {
      console.log(`Proxy disconnected from Python: ${reason}`);
    });

    pythonSocket.on("connect_error", (error) => {
      console.error(`Proxy connection error: ${error.message}`);
      browserSocket.emit("message", { type: "error", data: { message: "Failed to connect to game server" } });
    });

    browserSocket.on("set_name", (data: { name: string }) => {
      pythonSocket.emit("set_name", data);
    });

    browserSocket.on("set_region", (data: { region: string }) => {
      pythonSocket.emit("set_region", data);
    });

    browserSocket.on("enter_first_era", () => {
      pythonSocket.emit("enter_first_era");
    });

    browserSocket.on("choose", (data: { choice: string }) => {
      pythonSocket.emit("choose", data);
    });

    browserSocket.on("continue_to_next_era", () => {
      pythonSocket.emit("continue_to_next_era");
    });

    browserSocket.on("get_state", () => {
      pythonSocket.emit("get_state");
    });

    browserSocket.on("restart", () => {
      pythonSocket.emit("restart");
    });

    browserSocket.on("disconnect", () => {
      console.log(`Browser disconnected: ${browserSocket.id}`);
      pythonSocket.disconnect();
      clientSockets.delete(browserSocket.id);
    });
  });

  process.on("exit", () => {
    if (pythonServer) {
      pythonServer.kill();
    }
  });

  process.on("SIGTERM", () => {
    if (pythonServer) {
      pythonServer.kill();
    }
    process.exit(0);
  });

  process.on("SIGINT", () => {
    if (pythonServer) {
      pythonServer.kill();
    }
    process.exit(0);
  });

  console.log("Socket.IO proxy ready, Python game server spawned on port 5001");
}
