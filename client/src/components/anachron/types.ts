// Import era thumbnail images
import greeceImg from "@assets/eras/greece.png";
import vikingImg from "@assets/eras/viking.png";
import medievalImg from "@assets/eras/medival.png";
import revolutionImg from "@assets/eras/AmericanRevolution.png";
import industrialImg from "@assets/eras/industrial.png";
import civilWarImg from "@assets/eras/American_civil_war.png";
import ww2EuropeImg from "@assets/eras/ww2Europe.png";
import ww2HomefrontImg from "@assets/eras/WW2Homefront.png";
import coldWarImg from "@assets/eras/coldwar.png";

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
export const ERA_THUMBNAILS: Record<string, string> = {
  // Era ID -> image path
  "classical_athens": greeceImg,
  "viking_age": vikingImg,
  "medieval_europe": medievalImg,
  "colonial_america": revolutionImg,
  "industrial_britain": industrialImg,
  "american_civil_war": civilWarImg,
  "ww2_europe": ww2EuropeImg,
  "ww2_homefront": ww2HomefrontImg,
  "cold_war": coldWarImg,
  
  // Also map by display name for flexibility
  "Classical Athens": greeceImg,
  "Viking Age Scandinavia": vikingImg,
  "Medieval Europe (Black Death)": medievalImg,
  "Colonial America - Revolution": revolutionImg,
  "Industrial Britain": industrialImg,
  "American Civil War": civilWarImg,
  "WWII - Occupied Europe": ww2EuropeImg,
  "WWII - American Home Front": ww2HomefrontImg,
  "Cold War East Germany": coldWarImg,
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
