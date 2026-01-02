import { 
  type User, 
  type InsertUser,
  type GameSave,
  type InsertGameSave,
  type LeaderboardEntry,
  type InsertLeaderboardEntry,
  type GameHistory,
  type InsertGameHistory,
  type AoaEntry,
  type InsertAoaEntry,
  gameSaves,
  leaderboardEntries,
  gameHistories,
  aoaEntries
} from "@shared/schema";
import { db } from "./db";
import { eq, and, desc, gt, sql } from "drizzle-orm";

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  saveGame(save: InsertGameSave): Promise<GameSave>;
  loadGame(userId: string, gameId: string): Promise<GameSave | undefined>;
  deleteGame(userId: string, gameId: string): Promise<boolean>;
  listUserGames(userId: string): Promise<GameSave[]>;
  
  addLeaderboardEntry(entry: InsertLeaderboardEntry): Promise<LeaderboardEntry>;
  getTopScores(limit?: number): Promise<LeaderboardEntry[]>;
  getUserScores(userId: string, limit?: number): Promise<LeaderboardEntry[]>;
  getRank(totalScore: number): Promise<number>;
  
  saveGameHistory(history: InsertGameHistory): Promise<GameHistory>;
  getGameHistory(gameId: string): Promise<GameHistory | undefined>;
  getUserHistories(userId: string): Promise<GameHistory[]>;
  
  saveAoaEntry(entry: InsertAoaEntry): Promise<AoaEntry>;
  getAoaEntry(entryId: string): Promise<AoaEntry | undefined>;
  getUserAoaEntries(userId: string, limit: number, offset: number): Promise<AoaEntry[]>;
  getRecentAoaEntries(limit: number, offset: number): Promise<AoaEntry[]>;
  countUserAoaEntries(userId: string): Promise<number>;
  countAllAoaEntries(): Promise<number>;
}

export class DatabaseStorage implements IStorage {
  async getUser(id: string): Promise<User | undefined> {
    return undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return undefined;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    throw new Error("Not implemented - use Replit Auth");
  }

  async saveGame(save: InsertGameSave): Promise<GameSave> {
    const existing = await db
      .select()
      .from(gameSaves)
      .where(and(eq(gameSaves.userId, save.userId), eq(gameSaves.gameId, save.gameId)))
      .limit(1);
    
    if (existing.length > 0) {
      const [updated] = await db
        .update(gameSaves)
        .set({ 
          state: save.state, 
          savedAt: new Date(),
          playerName: save.playerName,
          currentEra: save.currentEra,
          phase: save.phase
        })
        .where(and(eq(gameSaves.userId, save.userId), eq(gameSaves.gameId, save.gameId)))
        .returning();
      return updated;
    }
    
    const [result] = await db.insert(gameSaves).values(save).returning();
    return result;
  }

  async loadGame(userId: string, gameId: string): Promise<GameSave | undefined> {
    const [result] = await db
      .select()
      .from(gameSaves)
      .where(and(eq(gameSaves.userId, userId), eq(gameSaves.gameId, gameId)))
      .limit(1);
    return result;
  }

  async deleteGame(userId: string, gameId: string): Promise<boolean> {
    const result = await db
      .delete(gameSaves)
      .where(and(eq(gameSaves.userId, userId), eq(gameSaves.gameId, gameId)));
    return true;
  }

  async listUserGames(userId: string): Promise<GameSave[]> {
    return db
      .select()
      .from(gameSaves)
      .where(eq(gameSaves.userId, userId))
      .orderBy(desc(gameSaves.savedAt));
  }

  async addLeaderboardEntry(entry: InsertLeaderboardEntry): Promise<LeaderboardEntry> {
    const [result] = await db.insert(leaderboardEntries).values(entry).returning();
    return result;
  }

  async getTopScores(limit: number = 10): Promise<LeaderboardEntry[]> {
    return db
      .select()
      .from(leaderboardEntries)
      .orderBy(desc(leaderboardEntries.totalScore))
      .limit(limit);
  }

  async getUserScores(userId: string, limit: number = 10): Promise<LeaderboardEntry[]> {
    return db
      .select()
      .from(leaderboardEntries)
      .where(eq(leaderboardEntries.userId, userId))
      .orderBy(desc(leaderboardEntries.totalScore))
      .limit(limit);
  }

  async getRank(totalScore: number): Promise<number> {
    const result = await db
      .select({ count: sql<number>`count(*)` })
      .from(leaderboardEntries)
      .where(gt(leaderboardEntries.totalScore, totalScore));
    return (result[0]?.count ?? 0) + 1;
  }

  async saveGameHistory(history: InsertGameHistory): Promise<GameHistory> {
    const existing = await db
      .select()
      .from(gameHistories)
      .where(eq(gameHistories.gameId, history.gameId))
      .limit(1);
    
    if (existing.length > 0) {
      const [updated] = await db
        .update(gameHistories)
        .set(history)
        .where(eq(gameHistories.gameId, history.gameId))
        .returning();
      return updated;
    }
    
    const [result] = await db.insert(gameHistories).values(history).returning();
    return result;
  }

  async getGameHistory(gameId: string): Promise<GameHistory | undefined> {
    const [result] = await db
      .select()
      .from(gameHistories)
      .where(eq(gameHistories.gameId, gameId))
      .limit(1);
    return result;
  }

  async getUserHistories(userId: string): Promise<GameHistory[]> {
    return db
      .select()
      .from(gameHistories)
      .where(eq(gameHistories.userId, userId))
      .orderBy(desc(gameHistories.endedAt));
  }

  async saveAoaEntry(entry: InsertAoaEntry): Promise<AoaEntry> {
    const [result] = await db.insert(aoaEntries).values(entry).returning();
    return result;
  }

  async getAoaEntry(entryId: string): Promise<AoaEntry | undefined> {
    const [result] = await db
      .select()
      .from(aoaEntries)
      .where(eq(aoaEntries.entryId, entryId))
      .limit(1);
    return result;
  }

  async getUserAoaEntries(userId: string, limit: number = 20, offset: number = 0): Promise<AoaEntry[]> {
    return db
      .select()
      .from(aoaEntries)
      .where(eq(aoaEntries.userId, userId))
      .orderBy(desc(aoaEntries.createdAt))
      .limit(limit)
      .offset(offset);
  }

  async getRecentAoaEntries(limit: number = 20, offset: number = 0): Promise<AoaEntry[]> {
    return db
      .select()
      .from(aoaEntries)
      .orderBy(desc(aoaEntries.createdAt))
      .limit(limit)
      .offset(offset);
  }

  async countUserAoaEntries(userId: string): Promise<number> {
    const result = await db
      .select({ count: sql<number>`count(*)` })
      .from(aoaEntries)
      .where(eq(aoaEntries.userId, userId));
    return result[0]?.count ?? 0;
  }

  async countAllAoaEntries(): Promise<number> {
    const result = await db
      .select({ count: sql<number>`count(*)` })
      .from(aoaEntries);
    return result[0]?.count ?? 0;
  }
}

export const storage = new DatabaseStorage();
