import { TimelineSave, getEraThumbnail, TimelineStatus } from "./types";
import { Hourglass, Trash2 } from "lucide-react";

interface SavedTimelineCardProps {
  save: TimelineSave;
  onResume: (save: TimelineSave) => void;
  onDelete?: (save: TimelineSave) => void;
}

const STATUS_STYLES: Record<TimelineStatus, { bg: string; text: string; label: string }> = {
  thriving: {
    bg: "bg-emerald-600/90",
    text: "text-emerald-100",
    label: "Thriving"
  },
  surviving: {
    bg: "bg-amber-600/90", 
    text: "text-amber-100",
    label: "Surviving"
  },
  struggling: {
    bg: "bg-red-600/90",
    text: "text-red-100", 
    label: "Struggling"
  },
  just_started: {
    bg: "bg-blue-600/90",
    text: "text-blue-100",
    label: "Just Started"
  }
};

export function SavedTimelineCard({ save, onResume, onDelete }: SavedTimelineCardProps) {
  const statusStyle = STATUS_STYLES[save.status] || STATUS_STYLES.surviving;
  const thumbnailSrc = getEraThumbnail(save.era);
  
  return (
    <div className="anachron-saved-card group relative">
      {/* Background with subtle glow effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-amber-900/20 via-transparent to-amber-900/20 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative flex items-center gap-4 p-4 bg-black/60 backdrop-blur-sm border border-amber-900/40 rounded-lg hover:border-amber-600/60 transition-all duration-300">
        {/* Era Thumbnail (only if image exists) */}
        {thumbnailSrc && (
          <div className="relative flex-shrink-0">
            <div className="w-16 h-16 rounded-lg overflow-hidden border-2 border-amber-800/60 shadow-lg shadow-black/50">
              <img 
                src={thumbnailSrc} 
                alt={save.era}
                className="w-full h-full object-cover"
              />
            </div>
            {/* Decorative corner accents */}
            <div className="absolute -top-1 -left-1 w-2 h-2 border-t-2 border-l-2 border-amber-500/60" />
            <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b-2 border-r-2 border-amber-500/60" />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Player Name */}
          <h3 className="text-lg font-semibold text-amber-100 truncate font-serif">
            {save.playerName}
          </h3>
          
          {/* Era and Time Info */}
          <p className="text-sm text-gray-300 truncate">
            <span className="text-amber-400">{save.era}</span>
            <span className="mx-2">·</span>
            <span>Year {save.year}</span>
            <span className="mx-2">·</span>
            <span>Turn {save.turn}</span>
            {save.location && (
              <>
                <span className="mx-2">·</span>
                <span className="text-gray-400">{save.location}</span>
              </>
            )}
          </p>

          {/* Status Badge and Player Name Tag */}
          <div className="flex items-center gap-2 mt-2">
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusStyle.bg} ${statusStyle.text}`}>
              {statusStyle.label}
            </span>
            <span className="text-xs text-gray-500 uppercase tracking-wider">
              {save.playerName}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(save);
              }}
              className="p-2 text-gray-500 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
              title="Delete Timeline"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
          
          <button
            onClick={() => onResume(save)}
            className="flex items-center gap-2 px-3 py-2 text-sm text-amber-200 hover:text-amber-100 transition-colors"
          >
            <span className="hidden sm:inline">Resume Timeline</span>
            <Hourglass className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default SavedTimelineCard;
