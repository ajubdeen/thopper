import { useEffect, useRef, useState } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "@xterm/xterm/css/xterm.css";

export default function TerminalPage() {
  const terminalRef = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!terminalRef.current || termRef.current) return;

    const term = new Terminal({
      cursorBlink: true,
      fontFamily: "monospace",
      fontSize: 14,
      theme: {
        background: "#1a1a1a",
        foreground: "#ffffff",
      },
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalRef.current);
    fitAddon.fit();
    termRef.current = term;

    term.writeln("Connecting to game server...");

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/terminal`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      term.writeln("Connected!");
      ws.send(JSON.stringify({ type: "resize", cols: term.cols, rows: term.rows }));
    };

    ws.onmessage = (e) => {
      term.write(e.data);
    };

    ws.onclose = () => {
      setConnected(false);
      term.writeln("\r\n\x1b[33mConnection closed.\x1b[0m");
    };

    ws.onerror = () => {
      setError("WebSocket error");
    };

    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "input", data }));
      }
    });

    const handleResize = () => fitAddon.fit();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      ws.close();
      term.dispose();
      termRef.current = null;
    };
  }, []);

  return (
    <div style={{ width: "100vw", height: "100vh", background: "#1a1a1a", display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "10px", background: "#2a2a2a", color: "white", display: "flex", gap: "10px", alignItems: "center" }}>
        <span style={{ fontWeight: "bold" }}>TIME HOPPER</span>
        <span style={{ 
          width: "8px", 
          height: "8px", 
          borderRadius: "50%", 
          background: connected ? "#22c55e" : "#ef4444" 
        }} />
        <span style={{ fontSize: "12px", color: "#888" }}>
          {connected ? "Connected" : "Disconnected"}
        </span>
        {error && <span style={{ color: "red", fontSize: "12px" }}>{error}</span>}
      </div>
      <div 
        ref={terminalRef} 
        style={{ flex: 1, padding: "10px" }}
        data-testid="terminal-container"
      />
    </div>
  );
}
