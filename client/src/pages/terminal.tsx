import { useEffect, useRef, useState } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebLinksAddon } from "@xterm/addon-web-links";
import "@xterm/xterm/css/xterm.css";

type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

export default function TerminalPage() {
  const terminalRef = useRef<HTMLDivElement>(null);
  const terminalInstance = useRef<Terminal | null>(null);
  const fitAddon = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (!terminalRef.current || terminalInstance.current) return;

    const term = new Terminal({
      cursorBlink: true,
      cursorStyle: "block",
      fontFamily: "'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', monospace",
      fontSize: 15,
      lineHeight: 1.2,
      letterSpacing: 0,
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
      scrollback: 1000,
      convertEol: true,
      allowProposedApi: true,
    });

    const fit = new FitAddon();
    const webLinks = new WebLinksAddon();

    term.loadAddon(fit);
    term.loadAddon(webLinks);
    term.open(terminalRef.current);

    setTimeout(() => {
      fit.fit();
    }, 0);

    terminalInstance.current = term;
    fitAddon.current = fit;

    const connectWebSocket = () => {
      setStatus("connecting");

      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/terminal`);

      ws.onopen = () => {
        setStatus("connected");
        const dims = { cols: term.cols, rows: term.rows };
        ws.send(JSON.stringify({ type: "resize", ...dims }));
      };

      ws.onmessage = (event) => {
        term.write(event.data);
      };

      ws.onclose = () => {
        setStatus("disconnected");
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = () => {
        setStatus("error");
      };

      wsRef.current = ws;
    };

    term.onData((data) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "input", data }));
      }
    });

    term.onResize(({ cols, rows }) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "resize", cols, rows }));
      }
    });

    connectWebSocket();

    const handleResize = () => {
      if (fitAddon.current) {
        fitAddon.current.fit();
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (terminalInstance.current) {
        terminalInstance.current.dispose();
        terminalInstance.current = null;
      }
    };
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
      setTimeout(() => {
        if (fitAddon.current) {
          fitAddon.current.fit();
        }
      }, 100);
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    };
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case "connected":
        return "bg-green-500";
      case "connecting":
        return "bg-yellow-500 animate-pulse";
      case "disconnected":
        return "bg-red-500";
      case "error":
        return "bg-red-600";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusText = () => {
    switch (status) {
      case "connected":
        return "Connected";
      case "connecting":
        return "Connecting...";
      case "disconnected":
        return "Reconnecting...";
      case "error":
        return "Connection Error";
      default:
        return "Unknown";
    }
  };

  return (
    <div className="h-screen w-screen bg-[#0a0a0a] flex flex-col overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-[#1a1a1a] border-b border-[#2a2a2a]">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-semibold text-gray-200 font-mono tracking-wide" data-testid="text-title">
            TIME HOPPER
          </h1>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span className={`w-2 h-2 rounded-full ${getStatusColor()}`} data-testid="status-indicator" />
            <span data-testid="text-status">{getStatusText()}</span>
          </div>
        </div>
        <button
          onClick={toggleFullscreen}
          className="p-2 text-gray-400 hover:text-gray-200 transition-colors rounded-md hover:bg-[#2a2a2a]"
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
      
      {status === "connecting" && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0a]/90 z-50">
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-cyan-400 font-mono text-sm" data-testid="text-loading">Connecting to Time Machine...</p>
          </div>
        </div>
      )}

      {status === "error" && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0a]/90 z-50">
          <div className="flex flex-col items-center gap-4 p-6 bg-[#1a1a1a] border border-red-500/30 rounded-lg max-w-md text-center">
            <div className="w-12 h-12 flex items-center justify-center rounded-full bg-red-500/20">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-400">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <p className="text-red-400 font-mono text-sm" data-testid="text-error">
              Connection failed. Retrying...
            </p>
          </div>
        </div>
      )}

      <div className="flex-1 p-2 md:p-4 overflow-hidden">
        <div className="h-full max-w-5xl mx-auto">
          <div
            ref={terminalRef}
            className="h-full w-full rounded-md border border-[#2a2a2a] overflow-hidden shadow-lg shadow-black/50"
            data-testid="terminal-container"
          />
        </div>
      </div>
    </div>
  );
}
