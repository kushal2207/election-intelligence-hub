import { useParams, useNavigate } from 'react-router-dom';
import { useJurisdiction } from '../contexts/JurisdictionContext';
import { ArrowLeft, BookOpen, Scale } from 'lucide-react';
import SummaryCard from '../components/SummaryCard';
import Accordion from '../components/Accordion';
import CompareWidget from '../components/CompareWidget';
import ConflictBanner from '../components/ConflictBanner';

export default function Detail() {
  const { topic } = useParams();
  const navigate = useNavigate();
  const { selectedState, selectedType } = useJurisdiction();

  const topicMap = {
    eligibility: 'Voter Eligibility & Requirements',
    procedure: 'Voting Procedure & Rules',
    mechanics: 'Election Mechanics',
    timeline: 'Schedules & Timelines'
  };

  const title = topicMap[topic] || 'Details';

  return (
    <div className="flex-1 flex flex-col p-4 md:p-8 max-w-7xl mx-auto w-full pb-32 animate-fadeIn">
      {/* Header */}
      <header className="flex items-center gap-6 mb-10">
        <button
          onClick={() => navigate(-1)}
          className="p-3 rounded-full bg-bgElevated border border-borderSoft text-textMain hover:text-accent hover:border-accent/30 transition-all duration-300 hover:shadow-glow"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <p className="text-accentCyan text-xs font-bold uppercase tracking-widest mb-2">{selectedState} · {selectedType}</p>
          <h1 className="text-3xl md:text-5xl font-heading font-extrabold text-white">{title}</h1>
        </div>
      </header>

      {/* Simulated conflict banner for demonstration */}
      {topic === 'eligibility' && (
        <div className="mb-6 animate-slideUp">
          <ConflictBanner message="There is a recent amendment in Maharashtra municipal voting age conflicting with federal records." />
        </div>
      )}

      <div className="mb-8 animate-slideUp" style={{ animationDelay: '100ms' }}>
        <SummaryCard topic={topic} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left column */}
        <section className="space-y-5 animate-slideUp" style={{ animationDelay: '200ms' }}>
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-bgElevated border border-borderSoft shadow-sm">
              <BookOpen size={20} className="text-accent" />
            </div>
            <h2 className="text-2xl font-heading font-bold text-white">Actionable Steps & Checklist</h2>
          </div>

          <Accordion title="Required Documents">
            <ul className="space-y-3">
              <li className="flex items-start gap-3">
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-success shrink-0" />
                <p><span className="glossary-term text-accent font-semibold cursor-pointer border-b border-dashed border-accent/40 hover:border-accent transition-colors">EPIC Card</span> (Voter ID)</p>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-success shrink-0" />
                <p>Aadhaar Card (Optional but recommended for KYC)</p>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-success shrink-0" />
                <p>Proof of Address (Utility bill, passport)</p>
              </li>
            </ul>
          </Accordion>

          <Accordion title="Registration Process">
            <p className="leading-relaxed">Apply online via the NVSP portal using Form 6 for new voters. Processing takes 30-45 days.</p>
          </Accordion>
        </section>

        {/* Right column */}
        <section className="space-y-5 animate-slideUp" style={{ animationDelay: '300ms' }}>
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-bgElevated border border-borderSoft shadow-sm">
              <Scale size={20} className="text-accentCyan" />
            </div>
            <h2 className="text-2xl font-heading font-bold text-white">Legal Context & History</h2>
          </div>

          <Accordion title="Representation of the People Act, 1950">
            <p className="leading-relaxed">Under Section 19, every person who is 18 years of age and is ordinarily resident in a constituency is entitled to be registered.</p>
          </Accordion>

          <Accordion title="State Municipal Corporation Act">
            <p className="leading-relaxed">Specific to {selectedState}, municipal elections mandate a separate electoral roll derived from the ECI rolls but managed by SEC.</p>
          </Accordion>

          <CompareWidget />
        </section>
      </div>
    </div>
  );
}
