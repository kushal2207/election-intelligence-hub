import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export default function Accordion({ title, children }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="glass-card overflow-hidden !hover:translate-y-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 font-heading font-semibold text-sm text-textMain hover:bg-white/[0.02] transition-colors duration-200"
      >
        <span>{title}</span>
        <ChevronDown
          size={18}
          className={`text-textMuted transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>
      <div
        className={`grid transition-all duration-300 ease-in-out ${
          isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        }`}
      >
        <div className="overflow-hidden">
          <div className="p-4 pt-0 text-textSecondary text-sm border-t border-borderSoft">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
