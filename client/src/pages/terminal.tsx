import { useEffect, useRef, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import heroImage from "@assets/ChatGPT_Image_Dec_24,_2025,_03_00_08_PM_1766617226950.png";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";

type GamePhase = 
  | "title" 
  | "setup_name" 
  | "setup_region" 
  | "intro" 
  | "gameplay" 
  | "loading" 
  | "ended";

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
}

export default function GamePage() {
  const socketRef = useRef<Socket | null>(null);
  const narrativeEndRef = useRef<HTMLDivElement>(null);
  const [connected, setConnected] = useState(false);
  const [phase, setPhase] = useState<GamePhase>("setup_name");
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
  const [waitingAction, setWaitingAction] = useState<string | null>(null);

  const scrollToBottom = useCallback(() => {
    narrativeEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [narrative, choices, scrollToBottom]);

  const handleMessage = useCallback((msg: GameMessage) => {
    switch (msg.type) {
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
        setWaitingAction(msg.data.action);
        setIsLoading(false);
        break;
        
      case "era_arrival":
        setCurrentEra({
          name: msg.data.era_name,
          year: msg.data.year,
          year_display: msg.data.year_display,
          location: msg.data.location
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
        break;
        
      case "narrative_chunk":
        setNarrative(prev => prev + (msg.data.text || ""));
        setShowEraSummary(false);
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
      case "staying_forever":
        setNarrative("");
        break;
        
      case "final_score":
        setFinalScore(msg.data);
        setPhase("ended");
        setIsLoading(false);
        break;
        
      case "game_end":
        setPhase("ended");
        setIsLoading(false);
        break;
        
      case "error":
        console.error("Game error:", msg.data.message);
        setIsLoading(false);
        break;
    }
  }, []);

  useEffect(() => {
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
    });

    socket.on('message', handleMessage);

    socket.on('disconnect', (reason) => {
      console.log('Disconnected:', reason);
      setConnected(false);
    });

    socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setConnected(false);
    });

    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, [handleMessage]);

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
    setIsLoading(true);
    socketRef.current?.emit('choose', { choice: choiceId });
  };

  const continueToNextEra = () => {
    setIsLoading(true);
    socketRef.current?.emit('continue_to_next_era');
    setWaitingAction(null);
  };

  const restartGame = () => {
    setPhase("title");
    setNarrative("");
    setChoices([]);
    setFinalScore(null);
    setCurrentEra(null);
    socketRef.current?.emit('restart');
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
      </div>

      <div className="flex-1 flex flex-col px-4 pb-4 overflow-hidden">
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
                          <span className="text-amber-400">•</span>
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
                          <span className="text-red-400">•</span>
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
                  {isLoading ? "Traveling in time..." : "See where you've landed..."}
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
                  <h2 className="text-lg font-semibold text-amber-400">{currentEra.name}</h2>
                  <p className="text-sm text-gray-500">{currentEra.location} • {currentEra.year_display}</p>
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
                          <span className="text-gray-600">•</span>
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
                  <div className="flex items-center gap-2 text-gray-500 mt-4">
                    <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
                    <span>The story unfolds...</span>
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
                  {isLoading ? "Traveling in time..." : "Continue to next era..."}
                </Button>
              </div>
            )}
          </div>
        )}

        {phase === "ended" && (
          <ScrollArea className="flex-1">
            <div className="max-w-md mx-auto py-4 space-y-6">
              <h2 className="text-2xl font-bold text-amber-400 text-center">Journey Complete</h2>
              
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
              
              <Button 
                onClick={restartGame}
                className="w-full bg-amber-600 hover:bg-amber-700 text-white py-4"
                data-testid="button-play-again"
              >
                Play Again
              </Button>
            </div>
          </ScrollArea>
        )}
      </div>
    </div>
  );
}
