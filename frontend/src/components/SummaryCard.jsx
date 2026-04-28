import { Zap } from 'lucide-react';

export default function SummaryCard({ topic }) {
  return (
    <div className="glass-card p-6 space-y-4 relative overflow-hidden">
      {/* Subtle gradient accent */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent/40 to-transparent" />

      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-accent/10 border border-accent/20">
          <Zap size={16} className="text-accent" />
        </div>
        <h3 className="font-heading font-bold text-base text-textMain">Quick Summary</h3>
      </div>

      <ul className="space-y-3">
        <li className="flex items-start gap-3 group">
          <span className="mt-2 w-1.5 h-1.5 rounded-full bg-accent shrink-0 group-hover:shadow-[0_0_12px_rgba(192,255,0,0.8)] transition-shadow" />
          <p className="text-white text-sm leading-relaxed font-medium">Must be an Indian citizen, 18+ years of age on Jan 1st of the election year.</p>
        </li>
        <li className="flex items-start gap-3 group">
          <span className="mt-2 w-1.5 h-1.5 rounded-full bg-accent shrink-0 group-hover:shadow-[0_0_12px_rgba(192,255,0,0.8)] transition-shadow" />
          <p className="text-white text-sm leading-relaxed font-medium">Registration requires Form 6 via NVSP portal or local Electoral Registration Officer.</p>
        </li>
        <li className="flex items-start gap-3 group">
          <span className="mt-2 w-1.5 h-1.5 rounded-full bg-accent shrink-0 group-hover:shadow-[0_0_12px_rgba(192,255,0,0.8)] transition-shadow" />
          <p className="text-white text-sm leading-relaxed font-medium">Voter ID (EPIC) is essential but other IDs like Aadhaar/Passport are accepted if name is on roll.</p>
        </li>
      </ul>
    </div>
  );
}
