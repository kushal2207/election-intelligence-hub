import { useState, useEffect } from 'react';

export default function GlossaryPopup() {
  const [popup, setPopup] = useState(null);

  useEffect(() => {
    const handleMouseUp = (e) => {
      if (e.target.classList.contains('glossary-term')) {
        const rect = e.target.getBoundingClientRect();
        setPopup({
          x: rect.left,
          y: rect.bottom + window.scrollY,
          term: e.target.innerText,
          definition: getMockDefinition(e.target.innerText)
        });
      } else if (!e.target.closest('.glossary-popup')) {
        setPopup(null);
      }
    };

    document.addEventListener('mouseup', handleMouseUp);
    return () => document.removeEventListener('mouseup', handleMouseUp);
  }, []);

  if (!popup) return null;

  return (
    <div
      className="glossary-popup absolute z-[60] glass-card p-4 max-w-xs animate-fadeIn"
      style={{ left: popup.x, top: popup.y + 10 }}
    >
      {/* Top accent line */}
      <div className="absolute top-0 left-4 right-4 h-px bg-gradient-to-r from-transparent via-accent/50 to-transparent" />
      <h4 className="font-heading font-bold text-accent text-sm mb-2">{popup.term}</h4>
      <p className="text-textSecondary text-sm leading-relaxed">{popup.definition}</p>
    </div>
  );
}

function getMockDefinition(term) {
  const dict = {
    'EPIC Card': "Electors Photo Identity Card. The official voter ID card issued by the Election Commission of India.",
    'Form 6': "The application form for inclusion of name in the electoral roll for a first-time voter."
  };
  return dict[term] || "Legal definition currently unavailable.";
}
