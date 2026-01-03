import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useAuth } from "@/hooks/use-auth";
import { useLocation } from "wouter";
import { HomePage, TimelineSave, TimelineStatus } from "@/components/anachron";
import { Compass, LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";

import "@/styles/anachron.css";

interface SavedGame {
  game_id: string;
  player_name: string;
  phase: string;
  current_era: string | null;
  total_turns: number;
  saved_at: string;
  era_year?: number;
}

interface GameMessage {
  type: string;
  data: any;
  timestamp?: string;
}

function inferStatus(turns: number): TimelineStatus {
  if (turns <= 2) return "just_started";
  if (turns <= 10) return "surviving";
  if (turns <= 20) return "thriving";
  return "thriving";
}

function convertToTimelineSave(save: SavedGame): TimelineSave {
  return {
    id: save.game_id,
    game_id: save.game_id,
    playerName: save.player_name,
    era: save.current_era || "Starting",
    year: save.era_year ? String(save.era_year) : "",
    turn: save.total_turns,
    status: inferStatus(save.total_turns),
    savedAt: save.saved_at,
  };
}

export default function HomeV2Page() {
  const { user, isLoading: authLoading, isAuthenticated, logout } = useAuth();
  const [, navigate] = useLocation();
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [savedGames, setSavedGames] = useState<SavedGame[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleMessage = useCallback((msg: GameMessage) => {
    switch (msg.type) {
      case "ready":
        setInitialized(true);
        socketRef.current?.emit('list_saves');
        break;
        
      case "user_games":
        setSavedGames(msg.data.games || []);
        setIsLoading(false);
        break;
        
      case "game_loaded":
        navigate("/game");
        break;
        
      case "title":
      case "setup_name":
        navigate("/game");
        break;
    }
  }, [navigate]);

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

  const handleNewGame = () => {
    setIsLoading(true);
    navigate("/game?action=new");
  };

  const handleResumeGame = (save: TimelineSave) => {
    setIsLoading(true);
    navigate(`/game?action=load&game_id=${save.game_id}`);
  };

  const handleDeleteGame = (save: TimelineSave) => {
    socketRef.current?.emit('delete_game', { game_id: save.game_id });
    // Wait for server confirmation via list_saves refresh
    socketRef.current?.emit('list_saves');
  };

  const handleViewAnnals = () => {
    navigate("/game?action=leaderboard");
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0a0908] flex items-center justify-center">
        <div className="flex items-center gap-3 text-amber-400/80">
          <Compass className="w-6 h-6 animate-spin" style={{ animationDuration: '3s' }} />
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="anachron-container">
        <div className="anachron-background anachron-background-simple" />
        <div className="anachron-vignette" />
        
        <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4">
          <div className="flex-shrink-0 h-[20vh]" />
          
          <p className="anachron-subtitle text-lg md:text-xl text-center mb-8">
            How would you fare in another era?
          </p>
          
          <p className="text-gray-400 text-center max-w-md mb-8">
            A time-travel survival adventure. Sign in to save your progress and compete on the leaderboard.
          </p>
          
          <Button 
            onClick={() => window.location.href = "/api/login"}
            className="bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white py-6 px-8 text-lg"
            data-testid="button-login"
          >
            Sign In to Play
          </Button>
        </div>
      </div>
    );
  }

  if (!connected || !initialized) {
    return (
      <div className="min-h-screen bg-[#0a0908] flex items-center justify-center">
        <div className="flex items-center gap-3 text-amber-400/80">
          <Compass className="w-6 h-6 animate-spin" style={{ animationDuration: '3s' }} />
          <span>Connecting to game server...</span>
        </div>
      </div>
    );
  }

  const timelineSaves = savedGames.map(convertToTimelineSave);

  return (
    <div className="relative">
      <div className="absolute top-3 right-3 z-20 flex items-center gap-2">
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
      
      <div className="absolute top-3 left-3 z-20 flex items-center gap-2 px-2 py-1 bg-black/60 backdrop-blur-sm rounded-md">
        <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-xs text-gray-300">{connected ? 'Connected' : 'Disconnected'}</span>
      </div>
      
      <HomePage
        savedGames={timelineSaves}
        onNewGame={handleNewGame}
        onResumeGame={handleResumeGame}
        onDeleteGame={handleDeleteGame}
        onViewAnnals={handleViewAnnals}
        isLoading={isLoading}
      />
    </div>
  );
}
