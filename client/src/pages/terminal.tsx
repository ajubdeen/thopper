import { useEffect, useRef, useState, useCallback } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebLinksAddon } from "@xterm/addon-web-links";
import "@xterm/xterm/css/xterm.css";
import heroImage from "@assets/ana-wide_1766620482851.png";

type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error" | "ended";

export default function TerminalPage() {
  const terminalRef = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const mountedRef = useRef(true);
  const initializingRef = useRef(false);
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [isFullscreen, setIsFullscreen] = useState(false);

  const connectWebSocket = useCallback((term: Terminal) => {
    if (!mountedRef.current) return null;
    
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/terminal`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      if (!mountedRef.current) {
        ws.close(1000);
        return;
      }
      setStatus("connected");
      ws.send(JSON.stringify({ type: "resize", cols: term.cols, rows: term.rows }));
      term.focus();
    };

    ws.onmessage = (e) => {
      if (mountedRef.current) {
        term.write(e.data);
      }
    };

    ws.onclose = (e) => {
      if (!mountedRef.current) return;
      if (e.code === 1000) {
        setStatus("ended");
      } else {
        setStatus("disconnected");
      }
    };

    ws.onerror = () => {
      if (mountedRef.current) {
        setStatus("error");
      }
    };

    return ws;
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    
    if (!terminalRef.current || initializingRef.current) return;
    initializingRef.current = true;

    const term = new Terminal({
      cursorBlink: true,
      cursorStyle: "block",
      fontFamily: "'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', monospace",
      fontSize: 15,
      lineHeight: 1.2,
      theme: {
        background: "#0a0a0a",
        foreground: "#e0e0e0",
        cursor: "#00ff00",
        cursorAccent: "#0a0a0a",
        black: "#000000",
        red: "#ff5555",
        green: "#50fa7b",
        yellow: "#f1fa8c",
        blue: "#6272a4",
        magenta: "#ff79c6",
        cyan: "#8be9fd",
        white: "#f8f8f2",
        brightBlack: "#6272a4",
        brightRed: "#ff6e6e",
        brightGreen: "#69ff94",
        brightYellow: "#ffffa5",
        brightBlue: "#d6acff",
        brightMagenta: "#ff92df",
        brightCyan: "#a4ffff",
        brightWhite: "#ffffff",
        selectionBackground: "#44475a",
        selectionForeground: "#f8f8f2",
      },
      scrollback: 5000,
      convertEol: true,
    });

    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();
    
    term.loadAddon(fitAddon);
    term.loadAddon(webLinksAddon);
    term.open(terminalRef.current);
    
    requestAnimationFrame(() => {
      if (mountedRef.current) {
        fitAddon.fit();
        term.focus();
      }
    });

    termRef.current = term;
    fitAddonRef.current = fitAddon;

    const ws = connectWebSocket(term);
    if (ws) {
      wsRef.current = ws;
    }

    term.onData((data) => {
      const currentWs = wsRef.current;
      if (currentWs && currentWs.readyState === WebSocket.OPEN) {
        currentWs.send(JSON.stringify({ type: "input", data }));
      }
    });

    term.onResize(({ cols, rows }) => {
      const currentWs = wsRef.current;
      if (currentWs && currentWs.readyState === WebSocket.OPEN) {
        currentWs.send(JSON.stringify({ type: "resize", cols, rows }));
      }
    });

    const handleResize = () => {
      if (fitAddonRef.current && mountedRef.current) {
        fitAddonRef.current.fit();
      }
    };
    window.addEventListener("resize", handleResize);

    const containerEl = terminalRef.current;
    const handleClick = () => {
      if (termRef.current) {
        termRef.current.focus();
      }
    };
    containerEl?.addEventListener("click", handleClick);

    return () => {
      mountedRef.current = false;
      initializingRef.current = false;
      window.removeEventListener("resize", handleResize);
      containerEl?.removeEventListener("click", handleClick);
      
      const currentWs = wsRef.current;
      if (currentWs) {
        if (currentWs.readyState === WebSocket.OPEN || currentWs.readyState === WebSocket.CONNECTING) {
          currentWs.close(1000);
        }
        wsRef.current = null;
      }
      
      if (termRef.current) {
        termRef.current.dispose();
        termRef.current = null;
      }
    };
  }, [connectWebSocket]);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
      setTimeout(() => {
        fitAddonRef.current?.fit();
        termRef.current?.focus();
      }, 100);
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  const restartGame = () => {
    window.location.reload();
  };

  const getStatusColor = () => {
    switch (status) {
      case "connected": return "bg-green-500";
      case "connecting": return "bg-yellow-500 animate-pulse";
      case "disconnected": return "bg-red-500";
      case "error": return "bg-red-600";
      case "ended": return "bg-gray-500";
      default: return "bg-gray-500";
    }
  };

  const getStatusText = () => {
    switch (status) {
      case "connected": return "Connected";
      case "connecting": return "Connecting...";
      case "disconnected": return "Disconnected";
      case "error": return "Connection Error";
      case "ended": return "Game Ended";
      default: return "Unknown";
    }
  };

  return (
    <div className="h-screen w-screen bg-[#0a0a0a] flex flex-col overflow-hidden">
      <div className="relative w-full h-[200px] sm:h-[240px] md:h-[280px] flex-shrink-0">
        <img 
          src={heroImage} 
          alt="Anachron - Time Travel Adventure" 
          className="w-full h-full object-cover object-bottom"
          data-testid="img-hero"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#0a0a0a]" />
        
        <div className="absolute top-3 right-3 flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-black/60 backdrop-blur-sm rounded-md">
            <span className={`w-2 h-2 rounded-full ${getStatusColor()}`} data-testid="status-indicator" />
            <span className="text-xs text-gray-300" data-testid="text-status">{getStatusText()}</span>
          </div>
          {(status === "ended" || status === "disconnected" || status === "error") && (
            <button
              onClick={restartGame}
              className="px-3 py-1.5 text-xs font-medium text-cyan-400 bg-black/60 backdrop-blur-sm border border-cyan-500/30 rounded-md hover:bg-cyan-500/20 transition-colors"
              data-testid="button-restart"
            >
              New Game
            </button>
          )}
          <button
            onClick={toggleFullscreen}
            className="p-2 text-gray-300 bg-black/60 backdrop-blur-sm hover:bg-black/80 transition-colors rounded-md"
            data-testid="button-fullscreen"
            title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
          >
            {isFullscreen ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M8 3v3a2 2 0 0 1-2 2H3" />
                <path d="M21 8h-3a2 2 0 0 1-2-2V3" />
                <path d="M3 16h3a2 2 0 0 1 2 2v3" />
                <path d="M16 21v-3a2 2 0 0 1 2-2h3" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M8 3H5a2 2 0 0 0-2 2v3" />
                <path d="M21 8V5a2 2 0 0 0-2-2h-3" />
                <path d="M3 16v3a2 2 0 0 0 2 2h3" />
                <path d="M16 21h3a2 2 0 0 0 2-2v-3" />
              </svg>
            )}
          </button>
        </div>
      </div>
      
      {status === "connecting" && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0a]/90 z-50">
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-cyan-400 font-mono text-sm" data-testid="text-loading">Connecting to Time Machine...</p>
          </div>
        </div>
      )}

      <div 
        ref={terminalRef}
        className="flex-1 overflow-hidden cursor-text"
        style={{ padding: "8px" }}
        data-testid="terminal-container"
        onClick={() => termRef.current?.focus()}
      />
    </div>
  );
}
