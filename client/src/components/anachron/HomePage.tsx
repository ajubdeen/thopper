import { useState } from "react";
import { TimelineSave } from "./types";
import { SteampunkButton } from "./SteampunkButton";
import { SavedTimelineCard } from "./SavedTimelineCard";
import { Trophy, ChevronLeft, ChevronRight } from "lucide-react";

interface HomePageProps {
  savedGames?: TimelineSave[];
  onNewGame?: () => void;
  onResumeGame?: (save: TimelineSave) => void;
  onDeleteGame?: (save: TimelineSave) => void;
  onViewAnnals?: () => void;
  isLoading?: boolean;
}

export function HomePage({
  savedGames = [],
  onNewGame,
  onResumeGame,
  onDeleteGame,
  onViewAnnals,
  isLoading = false
}: HomePageProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const savesPerPage = 3;
  const totalPages = Math.ceil(savedGames.length / savesPerPage);
  
  const currentSaves = savedGames.slice(
    currentPage * savesPerPage,
    (currentPage + 1) * savesPerPage
  );

  const hasSavedGames = savedGames.length > 0;

  return (
    <div className="anachron-container">
      <div 
        className={`anachron-background ${
          hasSavedGames ? 'anachron-background-full' : 'anachron-background-simple'
        }`}
      />
      <div className="anachron-vignette" />

      <div className="relative z-10 min-h-screen flex flex-col">
        <div className="flex-shrink-0 h-[28vh]" />

        <div className="flex-1 flex flex-col items-center px-4 pb-8">
          <p className="anachron-subtitle text-lg md:text-xl text-center mb-8 animate-fadeIn">
            {hasSavedGames 
              ? "You don't belong here. Survive anyway."
              : "How would you fare in another era?"
            }
          </p>

          <div className="animate-fadeIn-delay-1">
            <SteampunkButton
              variant="primary"
              size="lg"
              onClick={onNewGame}
              disabled={isLoading}
              className="min-w-[280px] md:min-w-[320px]"
              data-testid="button-new-game"
            >
              {hasSavedGames ? "Jump Into Time" : "Start Your Journey"}
            </SteampunkButton>
          </div>

          {hasSavedGames && (
            <p className="text-gray-500 text-sm mt-2 animate-fadeIn-delay-1">
              Initiates uncontrolled jump
            </p>
          )}

          {hasSavedGames && (
            <div className="w-full max-w-lg mt-12 animate-fadeIn-delay-2">
              <div className="flex items-center justify-center gap-4 mb-6">
                <div className="h-px w-12 bg-gradient-to-r from-transparent to-amber-800/60" />
                <h2 className="font-cinzel text-sm uppercase tracking-[0.2em] text-gray-400">
                  Saved Timelines
                </h2>
                <div className="h-px w-12 bg-gradient-to-l from-transparent to-amber-800/60" />
              </div>

              <div className="space-y-3">
                {currentSaves.map((save, index) => (
                  <div 
                    key={save.id || save.game_id}
                    className="animate-fadeIn"
                    style={{ animationDelay: `${0.3 + index * 0.1}s` }}
                  >
                    <SavedTimelineCard
                      save={save}
                      onResume={onResumeGame || (() => {})}
                      onDelete={onDeleteGame}
                    />
                  </div>
                ))}
              </div>

              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-4 mt-6">
                  <button
                    onClick={() => setCurrentPage(p => Math.max(0, p - 1))}
                    disabled={currentPage === 0}
                    className="p-2 text-gray-500 hover:text-amber-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    data-testid="button-prev-page"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  
                  <div className="anachron-page-dots">
                    {Array.from({ length: totalPages }).map((_, i) => (
                      <button
                        key={i}
                        onClick={() => setCurrentPage(i)}
                        className={`anachron-page-dot ${currentPage === i ? 'active' : ''}`}
                        data-testid={`button-page-${i}`}
                      />
                    ))}
                  </div>
                  
                  <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages - 1, p + 1))}
                    disabled={currentPage === totalPages - 1}
                    className="p-2 text-gray-500 hover:text-amber-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    data-testid="button-next-page"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              )}
            </div>
          )}

          <div className="flex-1" />

          <button
            onClick={onViewAnnals}
            className="anachron-annals-link mt-8 animate-fadeIn-delay-3"
            data-testid="button-annals"
          >
            <span className="anachron-annals-title flex items-center gap-2">
              <Trophy className="w-4 h-4 opacity-60" />
              The Annals of Anachron
            </span>
            <span className="anachron-annals-subtitle">
              Where history remembers the few.
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
