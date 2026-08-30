import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import './Chat.css';

const SUGGESTIONS = [
  "I want to become a data scientist",
  "Compare React.js and Angular",
  "What should I learn after Python basics?",
  "Analyze my skill gaps",
  "How long to become a full stack developer?",
  "What courses cover deep learning?",
  "How am I doing with my learning?",
  "Recommend a project to practice",
];

/* ---- Streaming Text Effect ---- */
function StreamingText({ text, speed = 15, onComplete }) {
  const [displayed, setDisplayed] = useState('');
  const indexRef = useRef(0);

  useEffect(() => {
    indexRef.current = 0;
    setDisplayed('');
    const timer = setInterval(() => {
      indexRef.current += 1;
      if (indexRef.current >= text.length) {
        setDisplayed(text);
        clearInterval(timer);
        if (onComplete) onComplete();
      } else {
        setDisplayed(text.slice(0, indexRef.current));
      }
    }, speed);
    return () => clearInterval(timer);
  }, [text, speed]);

  return <>{renderContent(displayed)}</>;
}

function renderContent(content) {
  return content.split('\n').map((line, i) => {
    // Bold
    line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Bullet points
    if (line.startsWith('- ')) {
      return <li key={i} dangerouslySetInnerHTML={{ __html: line.slice(2) }} />;
    }
    if (/^\d+\.\s/.test(line)) {
      return <li key={i} dangerouslySetInnerHTML={{ __html: line.replace(/^\d+\.\s/, '') }} />;
    }
    if (!line.trim()) return <br key={i} />;
    return <p key={i} dangerouslySetInnerHTML={{ __html: line }} />;
  });
}

export default function Chat({ user }) {
  const navigate = useNavigate();
  const [isListening, setIsListening] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hi${user?.name ? ' ' + user.name : ''}! 👋 I'm your AI learning assistant. I can help you with:\n\n- **Course recommendations** based on your goals\n- **Learning path suggestions** for any career\n- **Skill gap analysis** to find what you're missing\n- **Course comparisons** to help you choose\n- **Progress tracking** and motivation\n\nWhat would you like to explore?`,
      isStreaming: false,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Web Speech API
  const handleVoiceRecord = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice recognition is not supported in this browser. Please use Chrome.");
      return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
    };
    recognition.onerror = (e) => console.error(e);
    recognition.onend = () => setIsListening(false);
    
    recognition.start();
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage(text) {
    if (!text.trim() || loading) return;

    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.sendMessage({
        user_id: user?.id,
        message: text,
      });

      let assistantContent = response.response || "I'm not sure how to answer that. Could you rephrase?";

      // Add recommendations if available
      if (response.recommendations?.length > 0) {
        assistantContent += '\n\n**Recommended courses:**';
        response.recommendations.slice(0, 5).forEach((rec, i) => {
          assistantContent += `\n${i + 1}. **${rec.course}** (${rec.domain}) - ${Math.round(rec.score * 100)}% match`;
        });
      }

      const assistantMsg = {
        role: 'assistant',
        content: assistantContent,
        isStreaming: true,
        recommendations: response.recommendations || [],
        type: response.type,
        gap_analysis: response.gap_analysis,
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm having trouble connecting. Please make sure the backend server is running on port 8000.",
        isStreaming: false,
      }]);
    }
    setLoading(false);
  }

  function handleStreamComplete(idx) {
    setMessages(prev => prev.map((msg, i) =>
      i === idx ? { ...msg, isStreaming: false } : msg
    ));
  }

  // Dynamic suggestions based on user context
  const contextSuggestions = user?.goals
    ? [
        `What skills do I need for ${user.goals}?`,
        "Analyze my skill gaps",
        ...SUGGESTIONS.slice(0, 4),
      ]
    : SUGGESTIONS;

  return (
    <div className="chat-page animate-fade-in">
      <div className="page-header">
        <h2>AI Learning Assistant</h2>
        <p>Ask me anything about courses, career paths, skill gaps, or learning strategies.</p>
      </div>

      <div className="chat-container premium-3d-card">
        <div className="chat-header-3d">
          <div className="ai-core-orb">
            <div className="orb-ring" />
            <div className="orb-core">AI</div>
          </div>
          <div className="chat-header-info">
            <h3>PathFinder Neural Assistant</h3>
            <span className="online-status">● Online — powered by TF-IDF + Course Knowledge Graph</span>
          </div>
        </div>

        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-message ${msg.role}`} style={{ animationDelay: `${i * 0.05}s` }}>
              <div className="chat-avatar">
                {msg.role === 'assistant' ? '🤖' : user?.name?.charAt(0) || 'U'}
              </div>
              <div className="chat-bubble">
                <div className="chat-content">
                  {msg.isStreaming ? (
                    <StreamingText
                      text={msg.content}
                      speed={12}
                      onComplete={() => handleStreamComplete(i)}
                    />
                  ) : (
                    renderContent(msg.content)
                  )}
                </div>

                {/* Rich course cards for recommendations */}
                {!msg.isStreaming && msg.recommendations?.length > 0 && (
                  <div className="chat-rec-cards">
                    {msg.recommendations.slice(0, 3).map((rec, j) => (
                      <div key={j} className="chat-rec-card">
                        <div className="chat-rec-card-header">
                          <h5>{rec.course}</h5>
                          <span className={`badge badge-${rec.difficulty?.toLowerCase()}`}>
                            {rec.difficulty}
                          </span>
                        </div>
                        <div className="chat-rec-card-meta">
                          <span className="tag">{rec.domain}</span>
                          <span className="chat-rec-score">{Math.round(rec.score * 100)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Skill Gap visualization in chat */}
                {!msg.isStreaming && msg.gap_analysis && (
                  <div className="chat-gap-card">
                    <div className="chat-gap-readiness">
                      <span className="chat-gap-percent">{msg.gap_analysis.overall_readiness?.toFixed(0)}%</span>
                      <span className="chat-gap-label">Readiness</span>
                    </div>
                    <div className="chat-gap-weaknesses">
                      {msg.gap_analysis.weaknesses?.slice(0, 3).map(w => (
                        <div key={w.domain} className="chat-gap-item">
                          <span>{w.domain}</span>
                          <span className="gap-badge">-{w.gap}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action buttons */}
                {!msg.isStreaming && msg.type === 'recommendation' && (
                  <button
                    className="btn btn-sm btn-primary chat-action-btn"
                    onClick={() => navigate('/learning-path')}
                  >
                    🗺️ Generate Learning Path
                  </button>
                )}
                {!msg.isStreaming && msg.type === 'skill_gap' && (
                  <button
                    className="btn btn-sm btn-primary chat-action-btn"
                    onClick={() => navigate('/dashboard')}
                  >
                    📊 View Full Analysis
                  </button>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="chat-message assistant">
              <div className="chat-avatar">🤖</div>
              <div className="chat-bubble">
                <div className="typing-indicator">
                  <span /><span /><span />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggestions */}
        <div className="chat-suggestions persistent-suggestions">
          {contextSuggestions.slice(0, 6).map(s => (
            <button key={s} className="suggestion-chip" onClick={() => sendMessage(s)}>
              {s}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="chat-input-container">
          <button 
            className={`btn btn-icon ${isListening ? 'listening' : ''}`}
            onClick={handleVoiceRecord}
            disabled={loading}
            title="Use Voice Input"
            style={{ 
              background: isListening ? '#ef4444' : 'var(--bg-glass)',
              border: isListening ? '1px solid #ef4444' : '1px solid rgba(255,255,255,0.1)',
              animation: isListening ? 'pulse 1.5s infinite' : 'none'
            }}
          >
            🎤
          </button>
          <input
            className="input chat-input"
            type="text"
            placeholder="Ask about courses, career paths, or skill gaps..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage(input)}
            disabled={loading}
          />
          <button
            className="btn btn-primary chat-send"
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
