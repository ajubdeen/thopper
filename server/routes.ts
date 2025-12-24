import type { Express } from "express";
import { type Server } from "http";
import { setupPtyWebSocket } from "./pty";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  // Setup PTY WebSocket for terminal
  setupPtyWebSocket(httpServer);

  // Health check endpoint
  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  return httpServer;
}
