export type TimelineStatus = "thriving" | "struggling" | "surviving" | "just_started";

export interface TimelineSave {
  id: string;
  game_id: string;
  playerName: string;
  era: string;
  year: string;
  turn: number;
  status: TimelineStatus;
  location?: string;
  savedAt?: string;
}

// Map era IDs to their thumbnail image paths
// Uses EXACT original filenames
export const ERA_THUMBNAILS: Record<string, string> = {
  // Era ID -> image path
  "classical_athens": "/assets/eras/greece.png",
  "viking_age": "/assets/eras/viking.png",
  "medieval_europe": "/assets/eras/medival.png",
  "colonial_america": "/assets/eras/AmericanRevolution.png",
  "industrial_britain": "/assets/eras/industrial.png",
  "american_civil_war": "/assets/eras/American_civil_war.png",
  "ww2_europe": "/assets/eras/ww2Europe.png",
  "ww2_homefront": "/assets/eras/WW2Homefront.png",
  "cold_war": "/assets/eras/coldwar.png",
  
  // Also map by display name for flexibility
  "Classical Athens": "/assets/eras/greece.png",
  "Viking Age Scandinavia": "/assets/eras/viking.png",
  "Medieval Europe (Black Death)": "/assets/eras/medival.png",
  "Colonial America - Revolution": "/assets/eras/AmericanRevolution.png",
  "Industrial Britain": "/assets/eras/industrial.png",
  "American Civil War": "/assets/eras/American_civil_war.png",
  "WWII - Occupied Europe": "/assets/eras/ww2Europe.png",
  "WWII - American Home Front": "/assets/eras/WW2Homefront.png",
  "Cold War East Germany": "/assets/eras/coldwar.png",
};

// Get thumbnail for an era (by ID or display name)
export function getEraThumbnail(era: string): string | null {
  return ERA_THUMBNAILS[era] || null;
}

export interface LeaderboardEntry {
  rank: number;
  playerName: string;
  finalEra: string;
  endingType: string;
  score: number;
  timestamp: string;
}
