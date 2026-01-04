import type { Express, Request, Response } from "express";
import { db } from "./db";
import { users } from "@shared/models/auth";
import { gameSaves, gameHistories, leaderboardEntries, aoaEntries } from "@shared/models/game";
import { eq, desc } from "drizzle-orm";

export function registerAdminRoutes(app: Express): void {
  app.get("/api/nexus/users", async (_req: Request, res: Response) => {
    try {
      const allUsers = await db.select().from(users).orderBy(desc(users.createdAt));
      res.json(allUsers.map(u => ({
        id: u.id,
        email: u.email,
        firstName: u.firstName,
        lastName: u.lastName,
        createdAt: u.createdAt?.toISOString(),
      })));
    } catch (error) {
      console.error("Admin list users error:", error);
      res.status(500).json({ error: "Failed to list users" });
    }
  });

  app.get("/api/nexus/user/:userId/saves", async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const saves = await db
        .select()
        .from(gameSaves)
        .where(eq(gameSaves.userId, userId))
        .orderBy(desc(gameSaves.savedAt));
      res.json(saves.map(s => ({
        id: s.id,
        gameId: s.gameId,
        playerName: s.playerName,
        currentEra: s.currentEra,
        phase: s.phase,
        state: s.state,
        savedAt: s.savedAt?.toISOString(),
        startedAt: s.startedAt?.toISOString(),
      })));
    } catch (error) {
      console.error("Admin get user saves error:", error);
      res.status(500).json({ error: "Failed to get user saves" });
    }
  });

  app.get("/api/nexus/user/:userId/histories", async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const histories = await db
        .select()
        .from(gameHistories)
        .where(eq(gameHistories.userId, userId))
        .orderBy(desc(gameHistories.endedAt));
      res.json(histories.map(h => ({
        id: h.id,
        gameId: h.gameId,
        playerName: h.playerName,
        startedAt: h.startedAt?.toISOString(),
        endedAt: h.endedAt?.toISOString(),
        eras: h.eras,
        finalScore: h.finalScore,
        endingType: h.endingType,
        blurb: h.blurb,
      })));
    } catch (error) {
      console.error("Admin get user histories error:", error);
      res.status(500).json({ error: "Failed to get user histories" });
    }
  });

  app.get("/api/nexus/user/:userId/leaderboard", async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const entries = await db
        .select()
        .from(leaderboardEntries)
        .where(eq(leaderboardEntries.userId, userId))
        .orderBy(desc(leaderboardEntries.createdAt));
      res.json(entries.map(e => ({
        id: e.id,
        gameId: e.gameId,
        playerName: e.playerName,
        turnsSurvived: e.turnsSurvived,
        erasVisited: e.erasVisited,
        belongingScore: e.belongingScore,
        legacyScore: e.legacyScore,
        freedomScore: e.freedomScore,
        totalScore: e.totalScore,
        endingType: e.endingType,
        finalEra: e.finalEra,
        blurb: e.blurb,
        endingNarrative: e.endingNarrative,
        createdAt: e.createdAt?.toISOString(),
      })));
    } catch (error) {
      console.error("Admin get user leaderboard error:", error);
      res.status(500).json({ error: "Failed to get user leaderboard entries" });
    }
  });

  app.get("/api/nexus/user/:userId/aoa", async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const entries = await db
        .select()
        .from(aoaEntries)
        .where(eq(aoaEntries.userId, userId))
        .orderBy(desc(aoaEntries.createdAt));
      res.json(entries.map(e => ({
        id: e.id,
        entryId: e.entryId,
        gameId: e.gameId,
        playerName: e.playerName,
        characterName: e.characterName,
        finalEra: e.finalEra,
        finalEraYear: e.finalEraYear,
        erasVisited: e.erasVisited,
        turnsSurvived: e.turnsSurvived,
        endingType: e.endingType,
        belongingScore: e.belongingScore,
        legacyScore: e.legacyScore,
        freedomScore: e.freedomScore,
        totalScore: e.totalScore,
        keyNpcs: e.keyNpcs,
        definingMoments: e.definingMoments,
        wisdomMoments: e.wisdomMoments,
        itemsUsed: e.itemsUsed,
        playerNarrative: e.playerNarrative,
        historianNarrative: e.historianNarrative,
        createdAt: e.createdAt?.toISOString(),
      })));
    } catch (error) {
      console.error("Admin get user AoA error:", error);
      res.status(500).json({ error: "Failed to get user AoA entries" });
    }
  });
}
