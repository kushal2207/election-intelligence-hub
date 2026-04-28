import { AlertTriangle } from 'lucide-react';

export default function ConflictBanner({ message }) {
  return (
    <div className="glass-card !border-warning/30 bg-warningBg p-4 flex gap-4 items-start">
      <div className="p-2 rounded-lg bg-warning/15 border border-warning/20 shrink-0">
        <AlertTriangle size={18} className="text-warning" />
      </div>
      <div>
        <h3 className="font-heading font-bold text-warning text-sm">Conflict Detected</h3>
        <p className="text-sm mt-1 text-textSecondary leading-relaxed">{message}</p>
      </div>
    </div>
  );
}
