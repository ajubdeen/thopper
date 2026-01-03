import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";
import TerminalPage from "@/pages/terminal";
import HomeV2Page from "@/pages/home-v2";

function Router() {
  return (
    <Switch>
      <Route path="/" component={TerminalPage} />
      <Route path="/v2" component={HomeV2Page} />
      <Route path="/game" component={TerminalPage} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
