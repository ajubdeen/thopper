import { useEffect, useRef, useState } from "react";

export default function TerminalPage() {
  const terminalRef = useRef<HTMLDivElement>(null);
  const [logs, setLogs] = useState<string[]>(["Page loaded"]);
  const [wsStatus, setWsStatus] = useState("Not connected");

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
  };

  useEffect(() => {
    addLog("useEffect running");
    
    // Dynamically import xterm to check for errors
    import("@xterm/xterm").then(({ Terminal }) => {
      addLog("xterm loaded successfully");
      
      if (!terminalRef.current) {
        addLog("ERROR: terminalRef is null");
        return;
      }

      const term = new Terminal({
        cursorBlink: true,
        fontFamily: "monospace",
        fontSize: 14,
        theme: { background: "#1a1a1a", foreground: "#ffffff" },
      });

      import("@xterm/addon-fit").then(({ FitAddon }) => {
        addLog("FitAddon loaded");
        const fitAddon = new FitAddon();
        term.loadAddon(fitAddon);
        term.open(terminalRef.current!);
        fitAddon.fit();
        addLog("Terminal opened");

        term.writeln("Terminal ready. Connecting to server...");

        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws/terminal`;
        addLog(`Connecting to: ${wsUrl}`);

        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          addLog("WebSocket opened");
          setWsStatus("Connected");
          ws.send(JSON.stringify({ type: "resize", cols: term.cols, rows: term.rows }));
        };

        ws.onmessage = (e) => {
          term.write(e.data);
        };

        ws.onclose = (e) => {
          addLog(`WebSocket closed: code=${e.code}, reason=${e.reason}`);
          setWsStatus(`Closed (${e.code})`);
        };

        ws.onerror = (e) => {
          addLog(`WebSocket error: ${e}`);
          setWsStatus("Error");
        };

        term.onData((data) => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "input", data }));
          }
        });
      }).catch(err => {
        addLog(`FitAddon error: ${err.message}`);
      });
    }).catch(err => {
      addLog(`xterm error: ${err.message}`);
    });
  }, []);

  return (
    <div style={{ width: "100vw", height: "100vh", background: "#0a0a0a", display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "8px 16px", background: "#1a1a1a", color: "#fff", borderBottom: "1px solid #333", display: "flex", gap: "16px", alignItems: "center" }}>
        <strong>TIME HOPPER</strong>
        <span style={{ fontSize: "12px", color: "#888" }}>WebSocket: {wsStatus}</span>
      </div>
      
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <div 
          ref={terminalRef} 
          style={{ flex: 1, padding: "8px" }}
          data-testid="terminal-container"
        />
        
        <div style={{ width: "300px", background: "#111", borderLeft: "1px solid #333", padding: "8px", overflow: "auto", fontSize: "11px", fontFamily: "monospace", color: "#888" }}>
          <div style={{ fontWeight: "bold", marginBottom: "8px", color: "#fff" }}>Debug Log:</div>
          {logs.map((log, i) => (
            <div key={i} style={{ marginBottom: "4px" }}>{log}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
