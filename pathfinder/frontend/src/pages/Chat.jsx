import { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import './Chat.css';

const SUGGESTIONS = [
  "I want to become a data scientist",
  "Compare React.js and Angular",
  "What should I learn after Python basics?",
  "Explain the machine learning path",
  "What courses cover deep learning?",
  "How long to become a full stack developer?",
];

export default function Chat({ user }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hi${user?.name ? ' ' + user.name : ''}! I'm your AI learning assistant. I can help you with:\n\n- **Course recommendations** based on your goals\n- **Learning path suggestions** for any career\n- **Course comparisons** to help you choose\n- **Study tips** and guidance\n\nWhat would you like to explore?`,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

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

      setMessages(prev => [...prev, { role: 'assistant', content: assistantContent }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm having trouble connecting. Please make sure the backend server is running on port 8000.",
      }]);
    }
    setLoading(false);
  }

  function renderContent(content) {
    // Simple markdown rendering
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

  return (
    <div className="chat-page animate-fade-in">
      <div className="page-header">
        <h2>AI Learning Assistant</h2>
        <p>Ask me anything about courses, career paths, or learning strategies.</p>
      </div>

      <div className="chat-container premium-3d-card">
        <div className="chat-header-3d">
          <img src="/ai_core.jpg" alt="AI Core" className="ai-core-avatar float-anim" />
          <div className="chat-header-info">
            <h3>Neural Core Assistant</h3>
            <span className="online-status">● Online</span>
          </div>
        </div>
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-message ${msg.role}`} style={{ animationDelay: `${i * 0.05}s` }}>
              <div className="chat-avatar">
                {msg.role === 'assistant' ? 'AI' : user?.name?.charAt(0) || 'U'}
              </div>
              <div className="chat-bubble">
                <div className="chat-content">{renderContent(msg.content)}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="chat-message assistant">
              <div className="chat-avatar">AI</div>
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
        {messages.length <= 1 && (
          <div className="chat-suggestions">
            {SUGGESTIONS.map(s => (
              <button key={s} className="suggestion-chip" onClick={() => sendMessage(s)}>
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="chat-input-container">
          <input
            className="input chat-input"
            type="text"
            placeholder="Type your question..."
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
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
