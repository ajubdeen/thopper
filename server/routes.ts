import type { Express, Request, Response } from "express";
import { type Server } from "http";
import { setupPtyWebSocket } from "./pty";
import { setupAuth, registerAuthRoutes } from "./replit_integrations/auth";
import { storage } from "./storage";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  await setupAuth(app);
  registerAuthRoutes(app);

  setupPtyWebSocket(httpServer);

  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  app.post("/api/saves", async (req: Request, res: Response) => {
    try {
      const { userId, gameId, playerName, currentEra, phase, state } = req.body;
      if (!userId || !gameId || !state) {
        return res.status(400).json({ error: "Missing required fields" });
      }
      const result = await storage.saveGame({
        userId,
        gameId,
        playerName,
        currentEra,
        phase,
        state,
        startedAt: state.started_at ? new Date(state.started_at) : undefined,
      });
      res.json({ success: true, id: result.id });
    } catch (error) {
      console.error("Save game error:", error);
      res.status(500).json({ error: "Failed to save game" });
    }
  });

  app.get("/api/saves/:userId/:gameId", async (req: Request, res: Response) => {
    try {
      const { userId, gameId } = req.params;
      const result = await storage.loadGame(userId, gameId);
      if (!result) {
        return res.status(404).json({ error: "Game not found" });
      }
      res.json(result);
    } catch (error) {
      console.error("Load game error:", error);
      res.status(500).json({ error: "Failed to load game" });
    }
  });

  app.delete("/api/saves/:userId/:gameId", async (req: Request, res: Response) => {
    try {
      const { userId, gameId } = req.params;
      await storage.deleteGame(userId, gameId);
      res.json({ success: true });
    } catch (error) {
      console.error("Delete game error:", error);
      res.status(500).json({ error: "Failed to delete game" });
    }
  });

  app.get("/api/saves/:userId", async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const games = await storage.listUserGames(userId);
      res.json(games.map(g => ({
        game_id: g.gameId,
        player_name: g.playerName,
        current_era: g.currentEra,
        phase: g.phase,
        saved_at: g.savedAt?.toISOString(),
        started_at: g.startedAt?.toISOString(),
      })));
    } catch (error) {
      console.error("List games error:", error);
      res.status(500).json({ error: "Failed to list games" });
    }
  });

  app.post("/api/leaderboard", async (req: Request, res: Response) => {
    try {
      const entry = req.body;
      if (!entry.userId || !entry.playerName) {
        return res.status(400).json({ error: "Missing required fields" });
      }
      const result = await storage.addLeaderboardEntry(entry);
      
      const rank = await storage.getRank(result.totalScore ?? 0);
      
      res.json({ success: true, id: result.id, rank });
    } catch (error) {
      console.error("Add leaderboard error:", error);
      res.status(500).json({ error: "Failed to add leaderboard entry" });
    }
  });

  app.get("/api/leaderboard", async (req: Request, res: Response) => {
    try {
      const limit = parseInt(req.query.limit as string) || 10;
      const scores = await storage.getTopScores(limit);
      res.json(scores.map(s => ({
        user_id: s.userId,
        game_id: s.gameId,
        player_name: s.playerName,
        turns_survived: s.turnsSurvived,
        eras_visited: s.erasVisited,
        belonging: s.belongingScore,
        legacy: s.legacyScore,
        freedom: s.freedomScore,
        total: s.totalScore,
        ending_type: s.endingType,
        final_era: s.finalEra,
        blurb: s.blurb,
        ending_narrative: s.endingNarrative,
        timestamp: s.createdAt?.toISOString(),
      })));
    } catch (error) {
      console.error("Get leaderboard error:", error);
      res.status(500).json({ error: "Failed to get leaderboard" });
    }
  });

  app.get("/api/leaderboard/:userId", async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const limit = parseInt(req.query.limit as string) || 10;
      const scores = await storage.getUserScores(userId, limit);
      res.json(scores.map(s => ({
        user_id: s.userId,
        game_id: s.gameId,
        player_name: s.playerName,
        turns_survived: s.turnsSurvived,
        eras_visited: s.erasVisited,
        belonging: s.belongingScore,
        legacy: s.legacyScore,
        freedom: s.freedomScore,
        total: s.totalScore,
        ending_type: s.endingType,
        final_era: s.finalEra,
        blurb: s.blurb,
        ending_narrative: s.endingNarrative,
        timestamp: s.createdAt?.toISOString(),
      })));
    } catch (error) {
      console.error("Get user scores error:", error);
      res.status(500).json({ error: "Failed to get user scores" });
    }
  });

  app.post("/api/history", async (req: Request, res: Response) => {
    try {
      const history = req.body;
      if (!history.gameId || !history.userId) {
        return res.status(400).json({ error: "Missing required fields" });
      }
      const result = await storage.saveGameHistory({
        ...history,
        startedAt: history.startedAt ? new Date(history.startedAt) : undefined,
        endedAt: history.endedAt ? new Date(history.endedAt) : undefined,
      });
      res.json({ success: true, id: result.id });
    } catch (error) {
      console.error("Save history error:", error);
      res.status(500).json({ error: "Failed to save history" });
    }
  });

  app.get("/api/history/:gameId", async (req: Request, res: Response) => {
    try {
      const { gameId } = req.params;
      const result = await storage.getGameHistory(gameId);
      if (!result) {
        return res.status(404).json({ error: "History not found" });
      }
      res.json(result);
    } catch (error) {
      console.error("Get history error:", error);
      res.status(500).json({ error: "Failed to get history" });
    }
  });

  app.get("/api/histories/:userId", async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const histories = await storage.getUserHistories(userId);
      res.json(histories);
    } catch (error) {
      console.error("Get user histories error:", error);
      res.status(500).json({ error: "Failed to get user histories" });
    }
  });

  return httpServer;
}
