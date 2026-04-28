import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, Search, Calendar, MapPin, TrendingUp, Users, Zap, ChevronRight } from 'lucide-react';
import { useJurisdiction } from '../contexts/JurisdictionContext';
import { useAuth } from '../contexts/AuthContext';
import VoiceInput from './VoiceInput';
import axios from 'axios';
import './ElectionHub.css';

/* ─────────────────────────────────────────────
   ELECTION DATA — upcoming / live / concluded
   ───────────────────────────────────────────── */
const ELECTION_DATA = [
  {
    id: 'delhi-2025',
    state: 'Delhi',
    type: 'Assembly',
    seats: 70,
    date: 'Feb 5, 2025',
    status: 'concluded',
    result: 'AAP secures majority',
    turnout: '58.7%',
  },
  {
    id: 'bihar-2025',
    state: 'Bihar',
    type: 'Assembly',
    seats: 243,
    date: 'Oct–Nov 2025',
    status: 'concluded',
    result: 'JDU+BJP alliance retains power',
    turnout: '64.2%',
  },
  {
    id: 'assam-2026',
    state: 'Assam',
    type: 'Assembly',
    seats: 126,
    date: 'Apr 9, 2026',
    status: 'live',
    phase: 'Single phase polling',
    turnout: '72% (estimated)',
  },
  {
    id: 'kerala-2026',
    state: 'Kerala',
    type: 'Assembly',
    seats: 140,
    date: 'Apr 9, 2026',
    status: 'live',
    phase: 'Single phase polling',
    turnout: '74% (estimated)',
  },
  {
    id: 'puducherry-2026',
    state: 'Puducherry',
    type: 'Assembly',
    seats: 30,
    date: 'Apr 9, 2026',
    status: 'live',
    phase: 'Single phase polling',
    turnout: '81% (estimated)',
  },
  {
    id: 'tn-2026',
    state: 'Tamil Nadu',
    type: 'Assembly',
    seats: 234,
    date: 'Apr 23, 2026',
    status: 'upcoming',
    phase: 'Single phase',
  },
  {
    id: 'wb-2026',
    state: 'West Bengal',
    type: 'Assembly',
    seats: 294,
    date: 'Apr 23 & 29, 2026',
    status: 'upcoming',
    phase: 'Phase 1 & 2',
  },
  {
    id: 'counting-2026',
    state: 'All States',
    type: 'Counting Day',
    seats: null,
    date: 'May 4, 2026',
    status: 'milestone',
    phase: 'Results from 8 AM',
  },
];

const statusConfig = {
  concluded: { label: 'Concluded', cls: 'eh-badge-done', dotCls: 'done' },
  live:      { label: 'Live',       cls: 'eh-badge-live', dotCls: 'live' },
  upcoming:  { label: 'Upcoming',   cls: 'eh-badge-next', dotCls: 'next' },
  milestone: { label: 'Milestone',  cls: 'eh-badge-future', dotCls: 'future' },
};

function getDaysUntil(dateStr) {
  const parts = dateStr.match(/(\w+ \d+), (\d{4})/);
  if (!parts) return null;
  const target = new Date(`${parts[1]}, ${parts[2]}`);
  const now = new Date();
  const diff = Math.ceil((target - now) / (1000 * 60 * 60 * 24));
  return diff > 0 ? diff : null;
}


/* ─────────────────────────────────────────────
   SIDEBAR — Election Hub Panel
   ───────────────────────────────────────────── */
function buildElectionPrompt(el) {
  if (el.status === 'live') {
    return `Give me a complete, detailed breakdown of the ${el.state} ${el.type} Election ${el.date}. It is currently LIVE. Cover:\n\n1. **Overview** — Total seats (${el.seats}), voting phase (${el.phase || 'N/A'}), estimated turnout so far (${el.turnout || 'N/A'})\n2. **Key Candidates & Parties** — Major contenders, alliances, and prominent candidates\n3. **Key Issues** — Top election issues and voter concerns in ${el.state}\n4. **Polling Updates** — Any notable developments, incidents, or trends during voting\n5. **Historical Context** — What happened in the last ${el.state} election and how this one compares\n6. **Expected Outcomes** — Exit poll trends or pre-poll predictions if available\n\nProvide everything in a clean, well-formatted manner.`;
  }
  if (el.status === 'concluded') {
    return `Give me a complete, detailed breakdown of the ${el.state} ${el.type} Election held on ${el.date}. This election has CONCLUDED. Cover:\n\n1. **Final Result** — ${el.result || 'Winner and seat tally'}\n2. **Party-wise Seat Breakdown** — Seats won by each major party/alliance\n3. **Vote Share** — Percentage vote share of major parties\n4. **Voter Turnout** — Final turnout was ${el.turnout || 'N/A'}, compare with previous elections\n5. **Key Winners & Losers** — Notable candidates who won or lost their seats\n6. **Swing Analysis** — Which constituencies changed hands and why\n7. **Impact & Significance** — What this result means for national politics\n\nProvide everything in a clean, well-formatted manner.`;
  }
  if (el.status === 'upcoming' || el.status === 'milestone') {
    return `Give me a complete, detailed preview of the ${el.state} ${el.type} ${el.status === 'milestone' ? 'event' : 'Election'} scheduled for ${el.date}. Cover:\n\n1. **Overview** — ${el.seats ? `Total seats: ${el.seats},` : ''} voting schedule (${el.phase || 'TBD'})\n2. **Key Candidates & Parties** — Major contenders, alliances, and prominent candidates expected to contest\n3. **Pre-election Scenario** — Current political landscape in ${el.state}\n4. **Key Issues** — Major campaign issues and voter sentiments\n5. **Predictions & Surveys** — Any opinion polls or expert predictions\n6. **Important Dates** — Registration deadlines, nomination dates, and counting schedule\n7. **What to Watch For** — Key battleground constituencies and factors that could decide the outcome\n\nProvide everything in a clean, well-formatted manner.`;
  }
  return `Tell me everything about the ${el.state} ${el.type} Election (${el.date}) in detail.`;
}

function ElectionHubSidebar({ onElectionClick }) {
  const liveElections = ELECTION_DATA.filter(e => e.status === 'live');
  const upcomingElections = ELECTION_DATA.filter(e => e.status === 'upcoming' || e.status === 'milestone');
  const concludedElections = ELECTION_DATA.filter(e => e.status === 'concluded');

  const totalLiveSeats = liveElections.reduce((a, e) => a + (e.seats || 0), 0);
  const totalUpcomingSeats = upcomingElections.reduce((a, e) => a + (e.seats || 0), 0);

  return (
    <div className="eh-sidebar">
      {/* Header */}
      <div className="eh-sidebar-header">
        <div className="eh-live-dot"></div>
        <span className="eh-sidebar-title">Election Hub 2026</span>
      </div>

      {/* Quick Stats */}
      <div className="eh-quick-stats">
        <div className="eh-qs-item">
          <Zap size={14} className="eh-qs-icon text-[var(--eh-peach)]" />
          <div>
            <div className="eh-qs-value">{liveElections.length}</div>
            <div className="eh-qs-label">Live</div>
          </div>
        </div>
        <div className="eh-qs-item">
          <Calendar size={14} className="eh-qs-icon text-[var(--eh-lavender)]" />
          <div>
            <div className="eh-qs-value">{upcomingElections.length}</div>
            <div className="eh-qs-label">Upcoming</div>
          </div>
        </div>
        <div className="eh-qs-item">
          <Users size={14} className="eh-qs-icon text-[var(--eh-mint)]" />
          <div>
            <div className="eh-qs-value">{totalLiveSeats + totalUpcomingSeats}</div>
            <div className="eh-qs-label">Seats</div>
          </div>
        </div>
      </div>

      {/* Live Elections */}
      {liveElections.length > 0 && (
        <div className="eh-section">
          <div className="eh-section-title">
            <span className="eh-pulse-ring"></span> Live Now
          </div>
          {liveElections.map(el => (
            <div key={el.id} className="eh-election-card eh-election-live eh-clickable" onClick={() => onElectionClick && onElectionClick(buildElectionPrompt(el))} title={`Ask AI about ${el.state} election`}>
              <div className="eh-ec-top">
                <span className="eh-ec-state">{el.state}</span>
                <span className={`eh-badge ${statusConfig[el.status].cls}`}>{statusConfig[el.status].label}</span>
              </div>
              <div className="eh-ec-meta">{el.type} · {el.seats} seats · {el.date}</div>
              <div className="eh-ec-detail">{el.phase}</div>
              {el.turnout && <div className="eh-ec-turnout"><TrendingUp size={12}/> Turnout: {el.turnout}</div>}
              <div className="eh-ec-ask-hint"><ChevronRight size={12}/> Click to ask AI</div>
            </div>
          ))}
        </div>
      )}

      {/* Upcoming */}
      {upcomingElections.length > 0 && (
        <div className="eh-section">
          <div className="eh-section-title">Upcoming</div>
          {upcomingElections.map(el => {
            const days = getDaysUntil(el.date);
            return (
              <div key={el.id} className="eh-election-card eh-clickable" onClick={() => onElectionClick && onElectionClick(buildElectionPrompt(el))} title={`Ask AI about ${el.state} election`}>
                <div className="eh-ec-top">
                  <span className="eh-ec-state">{el.state}</span>
                  <span className={`eh-badge ${statusConfig[el.status].cls}`}>{statusConfig[el.status].label}</span>
                </div>
                <div className="eh-ec-meta">{el.type}{el.seats ? ` · ${el.seats} seats` : ''} · {el.date}</div>
                {el.phase && <div className="eh-ec-detail">{el.phase}</div>}
                {days && <div className="eh-ec-countdown">{days} days away</div>}
                <div className="eh-ec-ask-hint"><ChevronRight size={12}/> Click to ask AI</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Concluded */}
      {concludedElections.length > 0 && (
        <div className="eh-section">
          <div className="eh-section-title eh-section-muted">Concluded</div>
          {concludedElections.map(el => (
            <div key={el.id} className="eh-election-card eh-election-concluded eh-clickable" onClick={() => onElectionClick && onElectionClick(buildElectionPrompt(el))} title={`Ask AI about ${el.state} election results`}>
              <div className="eh-ec-top">
                <span className="eh-ec-state">{el.state}</span>
                <span className={`eh-badge ${statusConfig[el.status].cls}`}>{statusConfig[el.status].label}</span>
              </div>
              <div className="eh-ec-meta">{el.type} · {el.seats} seats · {el.date}</div>
              {el.result && <div className="eh-ec-result">{el.result}</div>}
              {el.turnout && <div className="eh-ec-turnout"><TrendingUp size={12}/> Turnout: {el.turnout}</div>}
              <div className="eh-ec-ask-hint"><ChevronRight size={12}/> Click to ask AI</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


/* ─────────────────────────────────────────────
   MAIN COMPONENT — AI Chat + Sidebar
   ───────────────────────────────────────────── */
export default function ElectionHub() {
  const { selectedState, selectedDistrict, selectedType, year } = useJurisdiction();
  const { logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (text = input) => {
    if (!text.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInput('');
    setIsLoading(true);

    try {
      const apiBase = `http://${window.location.hostname}:8000`;
      const authToken = localStorage.getItem('token');
      const { data } = await axios.post(`${apiBase}/api/v1/query`, {
        query_text: text,
        user_location: { jurisdiction_id: selectedState, constituency_id: selectedDistrict },
        user_language: 'en'
      }, {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      });

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.final_answer,
        confidence: data.confidence,
        citations: data.source_citations,
        conflict: data.conflict_detected
      }]);
    } catch (error) {
      console.error('API call failed:', error?.response?.status, error?.message);
      if (error.response && error.response.status === 401) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Your session has expired. Please log out and log back in to continue.',
          confidence: 'low',
          citations: [],
        }]);
        setTimeout(() => logout(), 3000);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Error communicating with the knowledge graph. Please ensure the backend server is running.',
          confidence: 'low',
          citations: [],
        }]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const suggestions = [
    'Am I eligible to vote?',
    'How to register as a voter?',
    'Polling booth near me?',
    'Next election dates?',
    'Who are the candidates in my area?',
    'What documents do I need to vote?',
  ];

  return (
    <div className="eh-layout">
      {/* Sidebar Toggle (mobile) */}
      <button
        className="eh-sidebar-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        title="Toggle Election Hub"
      >
        <Zap size={16} />
      </button>

      {/* Left: Election Hub Sidebar */}
      <div className={`eh-sidebar-wrapper ${sidebarOpen ? 'open' : 'closed'}`}>
        <ElectionHubSidebar onElectionClick={(prompt) => handleSend(prompt)} />
      </div>

      {/* Right: AI Chat */}
      <div className="eh-chat-panel">
        {/* Empty State */}
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center p-6 md:p-8 text-center animate-slideUp">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent/20 to-accentLavender/20 flex items-center justify-center mb-5 shadow-glow">
              <Sparkles size={32} className="text-accentCyan" />
            </div>
            <h2 className="text-2xl md:text-3xl font-heading font-extrabold text-white mb-3">
              Ask <span className="text-gradient">Anything</span>
            </h2>
            <p className="text-textSecondary max-w-md text-sm mb-6">
              Get AI-powered answers about elections, voter eligibility, candidates, polling locations, or any question you have{selectedDistrict ? ` for ${selectedDistrict}` : ''}.
            </p>
            <div className="flex flex-wrap justify-center gap-2 max-w-lg">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(s)}
                  className="px-3 py-1.5 rounded-lg bg-bgElevated border border-borderSoft text-xs text-textMuted hover:text-accentCyan hover:border-accentCyan/30 transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.length > 0 && (
          <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth">
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} animate-fadeIn`}>
                <div className={`p-4 max-w-[90%] md:max-w-[80%] rounded-2xl text-[14px] leading-relaxed shadow-lg ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-accentLavender to-accentCyan text-black font-medium rounded-br-sm'
                    : 'bg-bgElevated border border-borderSoft text-textMain rounded-bl-sm'
                }`}>
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-2 mb-2 border-b border-borderSoft/50 pb-2">
                      <Sparkles size={14} className="text-accentCyan" />
                      <span className="text-[10px] font-bold uppercase tracking-widest text-textMuted">AI Review & Analysis</span>
                    </div>
                  )}
                  <div style={{ whiteSpace: 'pre-line' }}>{msg.content}</div>

                  {msg.role === 'assistant' && msg.citations?.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1.5 pt-2 border-t border-borderSoft/30">
                      {msg.citations.map((cit, idx) => (
                        <span key={idx} className="badge bg-[#111111] text-textSecondary border border-borderSoft text-[10px]" title={cit.source_detail}>
                          {cit.authority_name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-start animate-fadeIn">
                <div className="p-4 bg-bgElevated border border-borderSoft rounded-2xl rounded-bl-sm flex items-center gap-3">
                  <Search size={16} className="text-accentCyan animate-pulse" />
                  <span className="text-textMuted text-xs font-medium">Reviewing sources...</span>
                  <div className="flex gap-1.5 ml-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-accentCyan animate-pulseDot" />
                    <span className="w-1.5 h-1.5 rounded-full bg-accentCyan animate-pulseDot" style={{ animationDelay: '0.2s' }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-accentCyan animate-pulseDot" style={{ animationDelay: '0.4s' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} className="h-4" />
          </div>
        )}

        {/* Input Area */}
        <div className="p-3 md:p-4 bg-bgCardSolid/80 backdrop-blur-xl border-t border-borderSoft">
          <div className="max-w-3xl mx-auto flex gap-2 relative">
            <input
              type="text"
              className="w-full bg-[#111111] border border-borderSoft text-textMain rounded-xl pl-4 pr-20 py-3 focus:outline-none focus:border-accentCyan/50 focus:ring-1 focus:ring-accentCyan/50 transition-all text-sm"
              placeholder={`Ask anything about elections${selectedDistrict ? ` in ${selectedDistrict}` : ''}...`}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
            />
            <div className="absolute right-1.5 top-1.5 flex gap-1.5">
              <VoiceInput onResult={(text) => { setInput(text); handleSend(text); }} />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="p-2 rounded-lg bg-gradient-to-br from-accent to-accentLavender text-black font-bold transition-all duration-200 hover:shadow-glow hover:scale-105 active:scale-95 disabled:opacity-40"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
          <div className="text-center mt-2 text-[10px] text-textMuted">
            AI can make mistakes. Verify critical information.
          </div>
        </div>
      </div>
    </div>
  );
}
