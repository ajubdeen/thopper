import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useSearch } from "wouter";
import heroImage from "@assets/banner3_1767202989616.png";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useAuth } from "@/hooks/use-auth";
import { LogOut, Trophy, Play, RotateCcw, User, Compass } from "lucide-react";

type GamePhase = 
  | "connecting"
  | "menu"
  | "title" 
  | "setup_name" 
  | "setup_region" 
  | "intro" 
  | "gameplay" 
  | "loading" 
  | "ended"
  | "leaderboard";

interface Choice {
  id: string;
  text: string;
}

interface GameMessage {
  type: string;
  data: any;
  timestamp?: string;
}

interface DeviceStatus {
  status: string;
  description: string;
  window_active?: boolean;
  window_turns_remaining?: number;
}

interface EraInfo {
  name: string;
  year: number;
  year_display: string;
  location: string;
  time_in_era?: string;
  era_number?: number;
  turn_in_era?: number;
}

function getOrdinal(n: number): string {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

function getEraOrdinal(n: number): string {
  const words = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"];
  if (n >= 1 && n <= 10) return words[n - 1];
  return getOrdinal(n);
}

function getProgressDescription(turnInEra: number, timeInEra: string): string {
  if (turnInEra === 1) return "you just landed";
  return timeInEra + " in";
}

interface SavedGame {
  game_id: string;
  player_name: string;
  phase: string;
  current_era: string | null;
  total_turns: number;
  saved_at: string;
}

interface LeaderboardEntry {
  user_id: string;
  player_name?: string;
  total: number;
  ending_type: string;
  final_era: string;
  timestamp: string;
  ending_narrative?: string;
  belonging_score?: number;
  legacy_score?: number;
  freedom_score?: number;
  blurb?: string;
}

export default function GamePage() {
  const { user, isLoading: authLoading, isAuthenticated, logout } = useAuth();
  const searchString = useSearch();
  const socketRef = useRef<Socket | null>(null);
  const narrativeEndRef = useRef<HTMLDivElement>(null);
  const [connected, setConnected] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [phase, setPhase] = useState<GamePhase>("connecting");
  const [urlActionProcessed, setUrlActionProcessed] = useState(false);
  const [playerName, setPlayerName] = useState("");
  const [narrative, setNarrative] = useState("");
  const [choices, setChoices] = useState<Choice[]>([]);
  const [canQuit, setCanQuit] = useState(true);
  const [windowOpen, setWindowOpen] = useState(false);
  const [canStayForever, setCanStayForever] = useState(false);
  const [deviceStatus, setDeviceStatus] = useState<DeviceStatus | null>(null);
  const [currentEra, setCurrentEra] = useState<EraInfo | null>(null);
  const [eraSummary, setEraSummary] = useState<string[]>([]);
  const [showEraSummary, setShowEraSummary] = useState(false);
  const [introItems, setIntroItems] = useState<any[]>([]);
  const [introDevice, setIntroDevice] = useState<any>(null);
  const [introStory, setIntroStory] = useState<string[]>([]);
  const [regionOptions, setRegionOptions] = useState<any[]>([]);
  const [finalScore, setFinalScore] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("The story unfolds...");
  const [waitingAction, setWaitingAction] = useState<string | null>(null);
  const [savedGames, setSavedGames] = useState<SavedGame[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [showGlobalLeaderboard, setShowGlobalLeaderboard] = useState(true);
  const [storyModalEntry, setStoryModalEntry] = useState<LeaderboardEntry | null>(null);

  const scrollToBottom = useCallback(() => {
    narrativeEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [narrative, choices, scrollToBottom]);

  const handleMessage = useCallback((msg: GameMessage) => {
    switch (msg.type) {
      case "ready":
        setInitialized(true);
        socketRef.current?.emit('list_saves');
        break;
        
      case "user_games":
        setSavedGames(msg.data.games || []);
        setPhase("menu");
        break;
        
      case "game_loaded":
        socketRef.current?.emit('resume');
        break;
        
      case "game_resumed":
        if (msg.data.era) {
          setCurrentEra({
            name: msg.data.era.name,
            year: msg.data.era.year,
            year_display: msg.data.era.year_display,
            location: msg.data.era.location,
            era_number: msg.data.era.era_number,
            turn_in_era: msg.data.era.turns_in_era,
            time_in_era: msg.data.era.time_in_era
          });
        } else {
          setCurrentEra(null);
        }
        setPhase("gameplay");
        break;
        
      case "leaderboard":
        setLeaderboard(msg.data.scores || []);
        setPhase("leaderboard");
        break;
        
      case "title":
        setPhase("title");
        break;
        
      case "setup_name":
        setPhase("setup_name");
        break;
        
      case "setup_region":
        if (msg.data.auto_select) {
          setIsLoading(true);
          socketRef.current?.emit('set_region', { region: msg.data.auto_select });
        } else {
          setPhase("setup_region");
          setRegionOptions(msg.data.options || []);
        }
        break;
        
      case "intro_story":
        setIntroStory(msg.data.paragraphs || []);
        setPhase("intro");
        break;
        
      case "intro_items":
        setIntroItems(msg.data.items || []);
        break;
        
      case "intro_device":
        setIntroDevice(msg.data);
        break;
        
      case "waiting_input":
        // Backend may send 'action' or 'prompt' field depending on version
        const waitAction = msg.data.action || msg.data.prompt;
        // Map 'continue' to the appropriate action based on game state
        if (waitAction === "continue") {
          // Could be continue_to_score or continue_to_next_era
          // Check the message hint or default to score for endings
          if (msg.data.message?.includes("score")) {
            setWaitingAction("continue_to_score");
          } else if (msg.data.message?.includes("land")) {
            setWaitingAction("continue_to_next_era");
          } else {
            setWaitingAction("continue_to_score");
          }
        } else {
          setWaitingAction(waitAction);
        }
        setIsLoading(false);
        break;
        
      case "era_arrival":
        setCurrentEra({
          name: msg.data.era_name,
          year: msg.data.year,
          year_display: msg.data.year_display,
          location: msg.data.location,
          era_number: msg.data.era_number,
          turn_in_era: msg.data.turn_in_era,
          time_in_era: msg.data.time_in_era
        });
        setNarrative("");
        setShowEraSummary(true);
        setPhase("gameplay");
        break;
        
      case "era_summary":
        setEraSummary(msg.data.key_events || []);
        break;
        
      case "loading":
        setIsLoading(true);
        setLoadingMessage(msg.data.message || "The story unfolds...");
        break;
        
      case "narrative":
      case "narrative_chunk":
        setNarrative(prev => prev + (msg.data.text || ""));
        setIsLoading(false);
        break;
        
      case "choices":
        setChoices(msg.data.choices || []);
        setCanQuit(msg.data.can_quit !== false);
        setWindowOpen(msg.data.window_open || false);
        setCanStayForever(msg.data.can_stay_forever || false);
        setIsLoading(false);
        break;
        
      case "device_status":
        setDeviceStatus(msg.data);
        if (msg.data.era_number !== undefined) {
          setCurrentEra(prev => prev ? {
            ...prev,
            era_number: msg.data.era_number,
            turn_in_era: msg.data.turn_in_era,
            time_in_era: msg.data.time_in_era
          } : prev);
        }
        break;
        
      case "window_open":
        setWindowOpen(true);
        setCanStayForever(msg.data.can_stay_meaningfully || false);
        break;
        
      case "window_closing":
      case "window_closed":
        setWindowOpen(false);
        break;
        
      case "departure":
        setNarrative("");
        break;
        
      case "staying_forever":
        // Clear choices so the continue button can render
        // Clear narrative to show fresh ending story
        setChoices([]);
        setWindowOpen(false);
        setNarrative("");
        break;
        
      case "ending_narrative":
        // Handle the ending narrative (from stay_forever or quit)
        setNarrative(msg.data.text || "");
        setIsLoading(false);
        break;
        
      case "final_score":
        setFinalScore(msg.data);
        setPhase("ended");
        setIsLoading(false);
        break;
        
      case "game_end":
        // Don't change phase yet - wait for final_score
        // This allows the loading indicator to show during narrative generation
        setIsLoading(false);
        break;
        
      case "error":
        console.error("Game error:", msg.data.message);
        setIsLoading(false);
        break;
    }
  }, []);

  useEffect(() => {
    if (authLoading || !isAuthenticated) return;
    
    const socket = io({
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      timeout: 20000,
    });
    
    socket.on('connect', () => {
      console.log('Connected to game server');
      setConnected(true);
      socket.emit('init', { user_id: user?.id || 'anonymous' });
    });

    socket.on('message', handleMessage);

    socket.on('disconnect', (reason) => {
      console.log('Disconnected:', reason);
      setConnected(false);
      setInitialized(false);
    });

    socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setConnected(false);
    });

    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, [handleMessage, authLoading, isAuthenticated, user?.id]);

  // Handle URL action parameters (from /v2 home page)
  useEffect(() => {
    if (!initialized || urlActionProcessed || !socketRef.current) return;
    
    const params = new URLSearchParams(searchString);
    const action = params.get('action');
    const gameId = params.get('game_id');
    
    if (action) {
      setUrlActionProcessed(true);
      
      if (action === 'new') {
        socketRef.current.emit('new_game');
      } else if (action === 'load' && gameId) {
        socketRef.current.emit('load', { game_id: gameId });
      } else if (action === 'leaderboard') {
        setShowGlobalLeaderboard(true);
        socketRef.current.emit('leaderboard', { global: true });
      }
      
      // Clean up URL without reloading
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [initialized, urlActionProcessed, searchString]);

  const startNewGame = () => {
    socketRef.current?.emit('new_game');
  };

  const loadGame = (gameId: string) => {
    socketRef.current?.emit('load', { game_id: gameId });
  };

  const showLeaderboard = (global: boolean = true) => {
    setShowGlobalLeaderboard(global);
    socketRef.current?.emit('leaderboard', { global });
  };

  const backToMenu = () => {
    socketRef.current?.emit('list_saves');
  };

  const submitName = () => {
    socketRef.current?.emit('set_name', { name: playerName || 'Traveler' });
  };

  const selectRegion = (regionId: string) => {
    socketRef.current?.emit('set_region', { region: regionId });
  };

  const startAdventure = () => {
    setIsLoading(true);
    socketRef.current?.emit('enter_first_era');
  };

  const makeChoice = (choiceId: string) => {
    setNarrative("");
    setChoices([]);
    setShowEraSummary(false);
    setIsLoading(true);
    setLoadingMessage(choiceId === 'Q' ? "Preparing your debrief..." : "The story unfolds...");
    socketRef.current?.emit('choose', { choice: choiceId });
  };

  const continueToNextEra = () => {
    setIsLoading(true);
    socketRef.current?.emit('continue_to_next_era');
    setWaitingAction(null);
  };

  const continueToScore = () => {
    setIsLoading(true);
    socketRef.current?.emit('continue_to_score');
    setWaitingAction(null);
  };

  const restartGame = () => {
    setPhase("menu");
    setNarrative("");
    setChoices([]);
    setFinalScore(null);
    setCurrentEra(null);
    socketRef.current?.emit('list_saves');
  };

  const getDeviceStatusColor = () => {
    if (!deviceStatus) return "bg-gray-600";
    switch (deviceStatus.status) {
      case "window_open": return "bg-amber-500 animate-pulse";
      case "steady_glow": return "bg-cyan-500";
      case "faint_pulse": return "bg-cyan-700";
      default: return "bg-gray-600";
    }
  };

  // Show loading while auth is loading
  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center">
        <div className="flex items-center gap-3 text-amber-400/80">
          <Compass className="w-6 h-6 animate-spin" style={{ animationDuration: '3s' }} />
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] text-gray-100 flex flex-col">
        <div className="relative w-full h-[200px] sm:h-[280px]">
          <img 
            src={heroImage} 
            alt="Anachron" 
            className="w-full h-full object-cover object-top"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/40 to-[#0d0d0d]" />
        </div>
        
        <div className="flex-1 flex flex-col items-center justify-center gap-6 px-4 -mt-16">
          <div className="flex flex-col gap-3 w-full max-w-xs">
            <Button 
              onClick={() => window.location.href = "/api/login"}
              className="bg-amber-600 hover:bg-amber-700 text-white py-6 text-lg"
              data-testid="button-login"
            >
              Sign In to Play
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0d0d0d] text-gray-100 flex flex-col overscroll-none touch-pan-y">
      <div className="relative w-full h-[140px] sm:h-[180px] flex-shrink-0">
        <img 
          src={heroImage} 
          alt="Anachron" 
          className="w-full h-full object-cover object-top"
          data-testid="img-hero"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/40 to-[#0d0d0d]" />
        
        <div className="absolute top-3 left-3 flex items-center gap-2 px-2 py-1 bg-black/60 backdrop-blur-sm rounded-md">
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-xs text-gray-300">{connected ? 'Connected' : 'Disconnected'}</span>
        </div>

        {deviceStatus && phase === "gameplay" && (
          <div className="absolute top-3 right-3 flex items-center gap-2 px-2 py-1 bg-black/60 backdrop-blur-sm rounded-md">
            <span className={`w-2 h-2 rounded-full ${getDeviceStatusColor()}`} />
            <span className="text-xs text-gray-300 capitalize">{deviceStatus.status.replace('_', ' ')}</span>
          </div>
        )}
        
        {(phase === "menu" || phase === "leaderboard") && (
          <div className="absolute top-3 right-3 flex items-center gap-2">
            <div className="flex items-center gap-2 px-2 py-1 bg-black/60 backdrop-blur-sm rounded-md">
              <User className="w-3 h-3 text-gray-300" />
              <span className="text-xs text-gray-300">{user?.firstName || user?.email || 'Player'}</span>
            </div>
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => logout()}
              className="h-7 w-7 bg-black/60 backdrop-blur-sm hover:bg-black/80"
              data-testid="button-logout"
            >
              <LogOut className="w-3 h-3 text-gray-300" />
            </Button>
          </div>
        )}
      </div>

      <div className="flex-1 flex flex-col px-4 pb-4 overflow-hidden">
        {phase === "connecting" && (
          <div className="flex-1 flex flex-col items-center justify-center gap-4">
            <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400">Connecting to game server...</p>
          </div>
        )}

        {phase === "menu" && (
          <div className="flex-1 flex flex-col items-center justify-center gap-8 max-w-sm mx-auto w-full px-2">
            <p className="text-gray-300 text-center text-lg">
              How will <em className="text-amber-400 not-italic font-medium">you</em> fare in another era?
            </p>
            
            <div className="flex flex-col gap-4 w-full">
              <Button 
                onClick={startNewGame}
                className="bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white py-7 text-lg font-semibold gap-3 shadow-lg shadow-amber-900/30 border border-amber-500/30"
                data-testid="button-new-game"
              >
                <Play className="w-5 h-5" />
                New Game
              </Button>
              
              {savedGames.length > 0 && (
                <div className="space-y-3 mt-2">
                  <div className="text-sm text-gray-500 text-center uppercase tracking-wide">Saved Games</div>
                  {savedGames.slice(0, 3).map((game) => (
                    <button 
                      key={game.game_id}
                      className="w-full bg-gray-900/80 border border-gray-700/50 rounded-lg p-4 flex items-center justify-between hover:bg-gray-800/80 hover:border-amber-600/40 transition-all duration-200 group"
                      onClick={() => loadGame(game.game_id)}
                      data-testid={`button-continue-${game.game_id}`}
                    >
                      <div className="text-left">
                        <div className="text-amber-400 font-semibold group-hover:text-amber-300 transition-colors">{game.player_name}</div>
                        <div className="text-xs text-gray-500 mt-0.5">
                          {game.current_era || 'Starting'} &middot; Turn {game.total_turns}
                        </div>
                      </div>
                      <RotateCcw className="w-4 h-4 text-gray-600 group-hover:text-amber-500 transition-colors" />
                    </button>
                  ))}
                </div>
              )}
              
              <div className="pt-4 border-t border-gray-800/50 mt-2">
                <Button 
                  onClick={() => showLeaderboard(true)}
                  variant="ghost"
                  className="w-full text-gray-400 hover:text-amber-400 gap-2 py-5"
                  data-testid="button-leaderboard"
                >
                  <Trophy className="w-4 h-4" />
                  View Leaderboard
                </Button>
              </div>
            </div>
          </div>
        )}

        {phase === "leaderboard" && (
          <div className="flex-1 flex flex-col max-w-md mx-auto w-full py-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-amber-400">Leaderboard</h2>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={backToMenu}
                className="text-gray-400"
                data-testid="button-back-menu"
              >
                Back
              </Button>
            </div>
            
            <div className="flex gap-2 mb-4">
              <Button
                variant={showGlobalLeaderboard ? "default" : "outline"}
                size="sm"
                onClick={() => showLeaderboard(true)}
                className={showGlobalLeaderboard ? "bg-amber-600" : "border-gray-700"}
                data-testid="button-global-leaderboard"
              >
                Global
              </Button>
              <Button
                variant={!showGlobalLeaderboard ? "default" : "outline"}
                size="sm"
                onClick={() => showLeaderboard(false)}
                className={!showGlobalLeaderboard ? "bg-amber-600" : "border-gray-700"}
                data-testid="button-my-scores"
              >
                My Scores
              </Button>
            </div>
            
            <ScrollArea className="flex-1">
              <div className="space-y-2">
                {leaderboard.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No scores yet: Play your first game!</p>
                ) : (
                  leaderboard.map((entry, i) => (
                    <Card key={i} className="bg-gray-900 border-gray-700">
                      <CardContent className="p-3 flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center text-amber-400 font-bold">
                          {i + 1}
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between items-center gap-2">
                            <span className="text-gray-100 font-medium">{entry.player_name || 'Anonymous'}</span>
                            <span className="text-amber-400 font-bold">{entry.total}</span>
                          </div>
                          <div className="text-xs text-gray-500 flex items-center gap-1 flex-wrap">
                            <span className="capitalize">{entry.ending_type}</span>
                            <span>&middot;</span>
                            <span>{entry.final_era}</span>
                            {entry.ending_narrative && (
                              <>
                                <span>&middot;</span>
                                <button
                                  onClick={() => setStoryModalEntry(entry)}
                                  className="text-amber-500 hover:text-amber-400 underline"
                                  data-testid={`button-story-${i}`}
                                >
                                  The Story
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </ScrollArea>
            
            <Dialog open={!!storyModalEntry} onOpenChange={(open) => !open && setStoryModalEntry(null)}>
              <DialogContent className="bg-gray-900 border-gray-700 max-w-2xl max-h-[80vh] flex flex-col">
                <DialogHeader>
                  <DialogTitle className="text-amber-400">
                    {storyModalEntry?.player_name || 'Anonymous'} chose to stay in {storyModalEntry?.final_era}
                  </DialogTitle>
                </DialogHeader>
                
                <div className="space-y-4 pb-2">
                  <div className="text-gray-300">
                    <span className="text-amber-400 font-bold text-lg">{storyModalEntry?.total} pts</span>
                    <span className="text-gray-500 mx-2">-</span>
                    <span className="text-gray-400">{storyModalEntry?.blurb || `${storyModalEntry?.ending_type} ending`}</span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="text-gray-400 text-sm w-20">Belonging</span>
                      <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-amber-500 rounded-full transition-all"
                          style={{ width: `${storyModalEntry?.belonging_score || 0}%` }}
                        />
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-gray-400 text-sm w-20">Legacy</span>
                      <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-amber-500 rounded-full transition-all"
                          style={{ width: `${storyModalEntry?.legacy_score || 0}%` }}
                        />
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-gray-400 text-sm w-20">Freedom</span>
                      <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-amber-500 rounded-full transition-all"
                          style={{ width: `${storyModalEntry?.freedom_score || 0}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="border-t border-gray-700 pt-4 flex-1 overflow-hidden">
                  <ScrollArea className="h-[40vh]">
                    <div className="text-gray-300 whitespace-pre-wrap leading-relaxed pr-4">
                      {storyModalEntry?.ending_narrative}
                    </div>
                  </ScrollArea>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        )}

        {phase === "title" && (
          <div className="flex-1 flex flex-col items-center justify-center gap-6">
            <h1 className="text-3xl sm:text-4xl font-bold text-amber-400 tracking-wider">ANACHRON</h1>
            <p className="text-gray-400 text-center">How will you fare in another era?</p>
            <Button 
              onClick={() => setPhase("setup_name")}
              className="bg-amber-600 hover:bg-amber-700 text-white px-8 py-6 text-lg"
              data-testid="button-start"
            >
              Begin Your Journey
            </Button>
          </div>
        )}

        {phase === "setup_name" && (
          <div className="flex-1 flex flex-col items-center justify-center gap-6 max-w-md mx-auto w-full">
            <h2 className="text-xl font-semibold text-amber-400">Who are you?</h2>
            <Input
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="Enter your name"
              className="bg-gray-900 border-gray-700 text-white text-center text-lg"
              data-testid="input-name"
              onKeyDown={(e) => e.key === 'Enter' && submitName()}
            />
            <Button 
              onClick={submitName}
              className="bg-amber-600 hover:bg-amber-700 text-white px-8"
              data-testid="button-submit-name"
            >
              Continue
            </Button>
          </div>
        )}

        {phase === "setup_region" && (
          <div className="flex-1 flex flex-col gap-4 max-w-md mx-auto w-full py-4">
            <h2 className="text-xl font-semibold text-amber-400 text-center">Where in history?</h2>
            <div className="flex flex-col gap-3">
              {regionOptions.map((option) => (
                <Card 
                  key={option.id}
                  className="bg-gray-900 border-gray-700 cursor-pointer hover:border-amber-500 transition-colors"
                  onClick={() => selectRegion(option.id)}
                  data-testid={`button-region-${option.id}`}
                >
                  <CardContent className="p-4">
                    <h3 className="text-lg font-medium text-amber-400">{option.name}</h3>
                    <p className="text-sm text-gray-400 mt-1">{option.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {phase === "intro" && (
          <ScrollArea className="flex-1">
            <div className="max-w-xl mx-auto py-4 space-y-6">
              {introStory.length > 0 && (
                <div className="space-y-3">
                  {introStory.map((para, i) => (
                    <p key={i} className="text-gray-300 leading-relaxed">{para}</p>
                  ))}
                </div>
              )}
              
              {introItems.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-amber-400 font-medium">Your Items:</h3>
                  {introItems.map((item) => (
                    <Card key={item.id} className="bg-gray-900 border-gray-700">
                      <CardContent className="p-3">
                        <div className="font-medium text-cyan-400">{item.name}</div>
                        <div className="text-sm text-gray-400">{item.description}</div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
              
              {introDevice && (
                <div className="space-y-3">
                  <h3 className="text-amber-400 font-medium">{introDevice.title}</h3>
                  <p className="text-gray-300">{introDevice.description}</p>
                  
                  <div className="space-y-2">
                    <h4 className="text-cyan-400 text-sm font-medium">How it works:</h4>
                    <ul className="text-sm text-gray-400 space-y-1">
                      {introDevice.mechanics?.map((m: string, i: number) => (
                        <li key={i} className="flex gap-2">
                          <span className="text-amber-400">-</span>
                          <span>{m}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="text-cyan-400 text-sm font-medium">The catch:</h4>
                    <ul className="text-sm text-gray-400 space-y-1">
                      {introDevice.catch?.map((c: string, i: number) => (
                        <li key={i} className="flex gap-2">
                          <span className="text-red-400">-</span>
                          <span>{c}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <p className="text-gray-300 italic">{introDevice.goal}</p>
                </div>
              )}
              
              {waitingAction === "continue_to_era" && (
                <Button 
                  onClick={startAdventure}
                  className="w-full bg-amber-600 hover:bg-amber-700 text-white py-6 text-lg"
                  disabled={isLoading}
                  data-testid="button-start-adventure"
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <Compass className="w-5 h-5 animate-spin" style={{ animationDuration: '3s' }} />
                      Traveling in time...
                    </span>
                  ) : "See where you've landed..."}
                </Button>
              )}
            </div>
          </ScrollArea>
        )}

        {phase === "gameplay" && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {currentEra && (
              <div className="flex-shrink-0 py-2 border-b border-gray-800">
                <div className="text-center">
                  <h2 className="text-lg font-semibold text-amber-400" data-testid="text-era-name">{currentEra.name}</h2>
                  <p className="text-sm text-gray-500" data-testid="text-era-location">{currentEra.location} - {currentEra.year_display}</p>
                  {currentEra.era_number !== undefined && (
                    <p className="text-sm text-gray-500" data-testid="text-era-progress">
                      Your {getEraOrdinal(currentEra.era_number)} era. {getOrdinal(currentEra.turn_in_era ?? 1)} turn - {getProgressDescription(currentEra.turn_in_era ?? 1, currentEra.time_in_era ?? "just arrived")}
                    </p>
                  )}
                </div>
              </div>
            )}
            
            {windowOpen && (
              <div className="flex-shrink-0 py-2 px-3 bg-amber-900/30 border border-amber-600/50 rounded-md my-2">
                <p className="text-amber-400 text-center font-medium">
                  The time machine window is open!
                </p>
                {canStayForever && (
                  <p className="text-amber-300 text-center text-sm">
                    You've built something here. You could stay forever...
                  </p>
                )}
              </div>
            )}
            
            <ScrollArea className="flex-1 my-2">
              <div className="prose prose-invert prose-sm max-w-none">
                {eraSummary.length > 0 && showEraSummary && (
                  <div className="mb-4 p-3 bg-gray-900/50 rounded-md">
                    <h4 className="text-cyan-400 text-sm font-medium mb-2">About this era:</h4>
                    <ul className="text-sm text-gray-400 space-y-1 list-none p-0 m-0">
                      {eraSummary.map((event, i) => (
                        <li key={i} className="flex gap-2">
                          <span className="text-gray-600">-</span>
                          <span>{event}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {narrative.replace(/\n\s*\[[^\]]+\][^\n]*/g, '')}
                </div>
                
                {isLoading && (
                  <div className="flex items-center gap-3 text-amber-400/80 mt-4">
                    <Compass className="w-5 h-5 animate-spin" style={{ animationDuration: '3s' }} />
                    <span>{loadingMessage}</span>
                  </div>
                )}
                
                <div ref={narrativeEndRef} />
              </div>
            </ScrollArea>
            
            {choices.length > 0 && !isLoading && (
              <div className="flex-shrink-0 space-y-2 pt-2 border-t border-gray-800">
                {choices.map((choice) => (
                  <Button
                    key={choice.id}
                    onClick={() => makeChoice(choice.id)}
                    variant="outline"
                    className="w-full justify-start text-left h-auto py-3 px-4 border-gray-700 bg-gray-900/50 hover:bg-gray-800 hover:border-amber-600 whitespace-normal"
                    data-testid={`button-choice-${choice.id}`}
                  >
                    <span className="text-amber-400 font-bold mr-3 flex-shrink-0">[{choice.id}]</span>
                    <span className="text-gray-300">{choice.text}</span>
                  </Button>
                ))}
                
                {canQuit && (
                  <Button
                    onClick={() => makeChoice('Q')}
                    variant="ghost"
                    className="w-full text-gray-500 hover:text-gray-400"
                    data-testid="button-quit"
                  >
                    [Q] Quit game
                  </Button>
                )}
              </div>
            )}
            
            {waitingAction === "continue_to_next_era" && (
              <div className="flex-shrink-0 pt-2 border-t border-gray-800">
                <Button 
                  onClick={continueToNextEra}
                  className="w-full bg-amber-600 hover:bg-amber-700 text-white py-4"
                  disabled={isLoading}
                  data-testid="button-continue-era"
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <Compass className="w-5 h-5 animate-spin" style={{ animationDuration: '3s' }} />
                      Traveling in time...
                    </span>
                  ) : "Continue to next era..."}
                </Button>
              </div>
            )}
            
            {waitingAction === "continue_to_score" && (
              <div className="flex-shrink-0 pt-2 border-t border-gray-800">
                <Button 
                  onClick={continueToScore}
                  className="w-full bg-amber-600 hover:bg-amber-700 text-white py-4"
                  disabled={isLoading}
                  data-testid="button-continue-score"
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <Compass className="w-5 h-5 animate-spin" style={{ animationDuration: '3s' }} />
                      Calculating...
                    </span>
                  ) : "Continue to see your score..."}
                </Button>
              </div>
            )}
          </div>
        )}

        {phase === "ended" && (
          <ScrollArea className="flex-1">
            <div className="max-w-md mx-auto py-4 space-y-6">
              <h2 className="text-2xl font-bold text-amber-400 text-center">Journey Complete</h2>
              
              {finalScore?.ending_narrative && (
                <div className="prose prose-invert prose-sm max-w-none">
                  <div className="text-gray-300 leading-relaxed whitespace-pre-wrap" data-testid="text-ending-narrative">
                    {finalScore.ending_narrative}
                  </div>
                </div>
              )}
              
              <Button 
                onClick={restartGame}
                className="w-full bg-amber-600 hover:bg-amber-700 text-white py-4"
                data-testid="button-play-again"
              >
                Play Again
              </Button>
              
              {finalScore && (
                <Card className="bg-gray-900 border-gray-700">
                  <CardContent className="p-4 space-y-4">
                    <div className="text-center">
                      <div className="text-4xl font-bold text-amber-400">{finalScore.total}</div>
                      <div className="text-gray-500">Total Score</div>
                      {finalScore.rank && (
                        <div className="text-cyan-400 mt-1">Rank #{finalScore.rank}</div>
                      )}
                    </div>
                    
                    <div className="border-t border-gray-700 pt-4 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Turns Survived</span>
                        <span className="text-gray-200">{finalScore.breakdown?.survival?.turns}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Eras Visited</span>
                        <span className="text-gray-200">{finalScore.breakdown?.exploration?.eras}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Belonging</span>
                        <span className="text-cyan-400">{finalScore.breakdown?.fulfillment?.belonging}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Legacy</span>
                        <span className="text-amber-400">{finalScore.breakdown?.fulfillment?.legacy}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Freedom</span>
                        <span className="text-green-400">{finalScore.breakdown?.fulfillment?.freedom}</span>
                      </div>
                      <div className="flex justify-between border-t border-gray-700 pt-2">
                        <span className="text-gray-400">Ending</span>
                        <span className="text-gray-200 capitalize">{finalScore.breakdown?.ending?.type}</span>
                      </div>
                    </div>
                    
                    {finalScore.summary && (
                      <p className="text-gray-400 text-sm italic border-t border-gray-700 pt-4">
                        {finalScore.summary}
                      </p>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </ScrollArea>
        )}
      </div>
    </div>
  );
}
