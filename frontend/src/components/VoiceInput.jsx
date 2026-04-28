import { useState, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';

export default function VoiceInput({ onResult }) {
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef(null);

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support the Web Speech API.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onResult(transcript);
      setIsRecording(false);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
  };

  return (
    <button
      onClick={toggleRecording}
      className={`p-2.5 rounded-xl border transition-all duration-200 ${
        isRecording
          ? 'bg-danger/15 border-danger/40 text-danger shadow-[0_0_15px_rgba(239,68,68,0.2)] animate-pulse'
          : 'bg-bgElevated border-borderSoft text-textMuted hover:text-textMain hover:border-borderMed'
      }`}
      title="Voice Input"
    >
      {isRecording ? <MicOff size={16} /> : <Mic size={16} />}
    </button>
  );
}
