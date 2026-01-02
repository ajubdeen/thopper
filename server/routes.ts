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

  app.post("/api/aoa", async (req: Request, res: Response) => {
    try {
      const entry = req.body;
      if (!entry.entryId || !entry.userId) {
        return res.status(400).json({ error: "Missing required fields" });
      }
      const result = await storage.saveAoaEntry({
        entryId: entry.entryId,
        userId: entry.userId,
        gameId: entry.gameId || null,
        playerName: entry.playerName || null,
        characterName: entry.characterName || null,
        finalEra: entry.finalEra || null,
        finalEraYear: entry.finalEraYear || null,
        erasVisited: entry.erasVisited || 0,
        turnsSurvived: entry.turnsSurvived || 0,
        endingType: entry.endingType || null,
        belongingScore: entry.belongingScore || 0,
        legacyScore: entry.legacyScore || 0,
        freedomScore: entry.freedomScore || 0,
        totalScore: entry.totalScore || 0,
        keyNpcs: entry.keyNpcs || [],
        definingMoments: entry.definingMoments || [],
        wisdomMoments: entry.wisdomMoments || [],
        itemsUsed: entry.itemsUsed || [],
        playerNarrative: entry.playerNarrative || null,
        historianNarrative: entry.historianNarrative || null,
      });
      res.json({ success: true, id: result.id });
    } catch (error) {
      console.error("Save AoA entry error:", error);
      res.status(500).json({ error: "Failed to save AoA entry" });
    }
  });

  app.get("/api/aoa/entry/:entryId", async (req: Request, res: Response) => {
    try {
      const { entryId } = req.params;
      const result = await storage.getAoaEntry(entryId);
      if (!result) {
        return res.status(404).json({ error: "Entry not found" });
      }
      res.json({
        entry_id: result.entryId,
        user_id: result.userId,
        game_id: result.gameId,
        player_name: result.playerName,
        character_name: result.characterName,
        final_era: result.finalEra,
        final_era_year: result.finalEraYear,
        eras_visited: result.erasVisited,
        turns_survived: result.turnsSurvived,
        ending_type: result.endingType,
        belonging_score: result.belongingScore,
        legacy_score: result.legacyScore,
        freedom_score: result.freedomScore,
        total_score: result.totalScore,
        key_npcs: result.keyNpcs,
        defining_moments: result.definingMoments,
        wisdom_moments: result.wisdomMoments,
        items_used: result.itemsUsed,
        player_narrative: result.playerNarrative,
        historian_narrative: result.historianNarrative,
        created_at: result.createdAt?.toISOString(),
      });
    } catch (error) {
      console.error("Get AoA entry error:", error);
      res.status(500).json({ error: "Failed to get AoA entry" });
    }
  });

  app.get("/api/aoa/user/:userId", async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const limit = parseInt(req.query.limit as string) || 20;
      const offset = parseInt(req.query.offset as string) || 0;
      
      const entries = await storage.getUserAoaEntries(userId, limit, offset);
      const total = await storage.countUserAoaEntries(userId);
      
      res.json({
        entries: entries.map(e => ({
          entry_id: e.entryId,
          user_id: e.userId,
          game_id: e.gameId,
          player_name: e.playerName,
          character_name: e.characterName,
          final_era: e.finalEra,
          final_era_year: e.finalEraYear,
          eras_visited: e.erasVisited,
          turns_survived: e.turnsSurvived,
          ending_type: e.endingType,
          belonging_score: e.belongingScore,
          legacy_score: e.legacyScore,
          freedom_score: e.freedomScore,
          total_score: e.totalScore,
          key_npcs: e.keyNpcs,
          defining_moments: e.definingMoments,
          wisdom_moments: e.wisdomMoments,
          items_used: e.itemsUsed,
          player_narrative: e.playerNarrative,
          historian_narrative: e.historianNarrative,
          created_at: e.createdAt?.toISOString(),
        })),
        total,
        limit,
        offset,
        has_more: offset + entries.length < total,
      });
    } catch (error) {
      console.error("Get user AoA entries error:", error);
      res.status(500).json({ error: "Failed to get user AoA entries" });
    }
  });

  app.get("/api/aoa/recent", async (req: Request, res: Response) => {
    try {
      const limit = parseInt(req.query.limit as string) || 20;
      const offset = parseInt(req.query.offset as string) || 0;
      
      const entries = await storage.getRecentAoaEntries(limit, offset);
      const total = await storage.countAllAoaEntries();
      
      res.json({
        entries: entries.map(e => ({
          entry_id: e.entryId,
          user_id: e.userId,
          game_id: e.gameId,
          player_name: e.playerName,
          character_name: e.characterName,
          final_era: e.finalEra,
          final_era_year: e.finalEraYear,
          eras_visited: e.erasVisited,
          turns_survived: e.turnsSurvived,
          ending_type: e.endingType,
          belonging_score: e.belongingScore,
          legacy_score: e.legacyScore,
          freedom_score: e.freedomScore,
          total_score: e.totalScore,
          key_npcs: e.keyNpcs,
          defining_moments: e.definingMoments,
          wisdom_moments: e.wisdomMoments,
          items_used: e.itemsUsed,
          player_narrative: e.playerNarrative,
          historian_narrative: e.historianNarrative,
          created_at: e.createdAt?.toISOString(),
        })),
        total,
        limit,
        offset,
        has_more: offset + entries.length < total,
      });
    } catch (error) {
      console.error("Get recent AoA entries error:", error);
      res.status(500).json({ error: "Failed to get recent AoA entries" });
    }
  });

  app.get("/api/aoa/count", async (req: Request, res: Response) => {
    try {
      const userId = req.query.userId as string;
      let count: number;
      if (userId) {
        count = await storage.countUserAoaEntries(userId);
      } else {
        count = await storage.countAllAoaEntries();
      }
      res.json({ count });
    } catch (error) {
      console.error("Count AoA entries error:", error);
      res.status(500).json({ error: "Failed to count AoA entries" });
    }
  });

  return httpServer;
}
