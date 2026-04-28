import { useJurisdiction } from '../contexts/JurisdictionContext';
import { MapPin } from 'lucide-react';

export default function JurisdictionSelector() {
  const {
    selectedState, setSelectedState,
    selectedDistrict, setSelectedDistrict,
    selectedType, setSelectedType,
    autoDetectLocation, isLocating
  } = useJurisdiction();

  return (
    <div className="flex flex-wrap items-center gap-2">
      <button 
        onClick={autoDetectLocation} 
        disabled={isLocating}
        className="btn-ghost flex items-center gap-2 text-textMuted hover:text-accentCyan disabled:opacity-50 border border-borderSoft px-3 py-1.5 rounded-lg text-sm transition-all"
        title="Detect My Location"
      >
        <MapPin size={16} className={isLocating ? 'animate-pulse text-accentCyan' : ''} />
        <span className="hidden md:inline">{isLocating ? 'Locating...' : 'Auto-detect'}</span>
      </button>

      <input
        type="text"
        value={selectedState}
        onChange={e => setSelectedState(e.target.value)}
        placeholder="State (e.g. Maharashtra)"
        className="input-field max-w-[140px] text-sm py-1.5"
      />

      <input
        type="text"
        value={selectedDistrict}
        onChange={e => setSelectedDistrict(e.target.value)}
        placeholder="City/District"
        className="input-field max-w-[140px] text-sm py-1.5"
      />

      <select
        value={selectedType}
        onChange={e => setSelectedType(e.target.value)}
        className="select-field max-w-[120px] text-sm py-1.5"
      >
        <option value="Municipal">Municipal</option>
        <option value="Assembly">Assembly</option>
        <option value="Lok Sabha">Lok Sabha</option>
      </select>
    </div>
  );
}
