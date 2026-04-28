import { useJurisdiction } from '../contexts/JurisdictionContext';
import { useAuth } from '../contexts/AuthContext';
import JurisdictionSelector from '../components/JurisdictionSelector';
import ElectionHub from '../components/ElectionHub';
import { LogOut, Sparkles } from 'lucide-react';

export default function Dashboard() {
  const { selectedState, selectedDistrict, selectedType, year } = useJurisdiction();
  const { user, logout } = useAuth();

  return (
    <div className="flex-1 flex flex-col p-4 md:p-6 lg:p-8 max-w-7xl mx-auto w-full h-[100dvh] animate-fadeIn">
      {/* Header */}
      <header className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-6 flex-shrink-0">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={18} className="text-accentCyan" />
            <span className="text-textMuted text-xs font-bold uppercase tracking-widest">Knowledge Graph</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-heading font-extrabold text-white">
            Welcome, <span className="text-gradient">{user?.name || 'Citizen'}</span>
          </h1>
          <div className="flex flex-wrap items-center gap-2 mt-3">
            {selectedState && <span className="badge-info !bg-accentCyan/10 !text-accentCyan !border-accentCyan/20">{selectedState}</span>}
            {selectedDistrict && <span className="badge-info !bg-accentCyan/10 !text-accentCyan !border-accentCyan/20">{selectedDistrict}</span>}
            <span className="badge-info !bg-accentCyan/10 !text-accentCyan !border-accentCyan/20">{selectedType}</span>
            <span className="badge border-borderSoft bg-[#111111]">{year}</span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4 bg-bgCard p-3 rounded-xl border border-borderSoft">
          <JurisdictionSelector />
          <div className="w-px h-8 bg-borderSoft hidden md:block"></div>
          <button onClick={logout} className="btn-ghost flex items-center gap-2 text-textMuted hover:text-danger p-2">
            <LogOut size={16} />
            <span className="hidden md:inline text-sm font-medium">Logout</span>
          </button>
        </div>
      </header>

      {/* Main Hub */}
      <main className="flex-1 flex min-h-0">
        <ElectionHub />
      </main>
    </div>
  );
}
