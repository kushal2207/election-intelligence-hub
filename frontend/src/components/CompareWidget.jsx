import { useState } from 'react';
import { ArrowRightLeft } from 'lucide-react';

export default function CompareWidget() {
  const [targetState, setTargetState] = useState('');

  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-xl bg-[#111111] border border-borderSoft shadow-sm">
          <ArrowRightLeft size={18} className="text-accentCyan" />
        </div>
        <h3 className="font-heading font-bold text-base text-white">Compare Jurisdiction</h3>
      </div>
      <div className="flex gap-2">
        <select
          className="select-field flex-1"
          value={targetState}
          onChange={(e) => setTargetState(e.target.value)}
        >
          <option value="">Select State to Compare...</option>
          <option value="Karnataka">Karnataka</option>
          <option value="Delhi">Delhi</option>
        </select>
        <button
          className="btn-primary !px-4 !py-2 text-sm"
          disabled={!targetState}
        >
          Compare
        </button>
      </div>
      {targetState && (
        <div className="mt-2 p-4 rounded-xl border border-dashed border-borderMed bg-bgElevated/50 animate-fadeIn">
          <p className="text-textSecondary text-sm">Comparing with {targetState} rules...</p>
        </div>
      )}
    </div>
  );
}
