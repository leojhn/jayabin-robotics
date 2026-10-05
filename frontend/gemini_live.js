/**
 * Gemini Live API Assistant for Form Explanation, Re-speaking, and Auto-filling fields.
 */
class GeminiLiveFormAssistant {
  constructor() {
    this.apiKey = localStorage.getItem('GEMINI_API_KEY') || window.GEMINI_API_KEY || '';
    this.ws = null;
    this.mediaRecorder = null;
    this.audioContext = null;
    this.isListening = false;
    this.synth = window.speechSynthesis;
    this.activeField = null;
    this.initUI();
  }

  setApiKey(key) {
    this.apiKey = key;
    localStorage.setItem('GEMINI_API_KEY', key);
    this.updateStatus('Gemini API key saved.');
  }

  getFormFields() {
    const fields = [];
    const elements = document.querySelectorAll('input, select, textarea');
    elements.forEach(el => {
      if (el.id || el.name) {
        const labelEl = document.querySelector(`label[for="${el.id}"]`) || el.closest('label') || el.previousElementSibling;
        const labelText = labelEl ? labelEl.textContent.trim() : (el.placeholder || el.name || el.id);
        fields.push({
          id: el.id || el.name,
          label: labelText,
          type: el.type || el.tagName.toLowerCase(),
          value: el.value,
          placeholder: el.placeholder || ''
        });
      }
    });
    return fields;
  }

  initUI() {
    if (document.getElementById('gemini-assistant-panel')) return;

    const panel = document.createElement('div');
    panel.id = 'gemini-assistant-panel';
    panel.innerHTML = `
      <style>
        #gemini-assistant-panel {
          position: fixed;
          bottom: 15px;
          right: 15px;
          z-index: 9999;
          background: rgba(10, 30, 60, 0.95);
          border: 2px solid #38BDF8;
          border-radius: 16px;
          padding: 14px;
          color: #fff;
          width: 290px;
          box-shadow: 0 10px 25px rgba(0,0,0,0.5);
          font-family: system-ui, -apple-system, sans-serif;
          backdrop-filter: blur(10px);
        }
        #gemini-assistant-panel h4 {
          margin: 0 0 10px 0;
          color: #7DE8FF;
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 16px;
        }
        .gemini-btn-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-top: 10px;
        }
        .gemini-btn {
          background: #103A67;
          border: 1px solid #38BDF8;
          color: #fff;
          padding: 8px 12px;
          border-radius: 8px;
          cursor: pointer;
          font-size: 13px;
          font-weight: 600;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
        }
        .gemini-btn:hover {
          background: #1EA7FF;
          color: #000;
        }
        .gemini-btn.active {
          background: #EF4444;
          border-color: #F87171;
        }
        #gemini-status {
          font-size: 12px;
          color: #9FD9FF;
          margin-top: 8px;
          min-height: 18px;
        }
        .gemini-key-input {
          width: 100%;
          padding: 6px 8px;
          margin-top: 6px;
          background: #04192B;
          border: 1px solid #38BDF8;
          color: #fff;
          border-radius: 6px;
          font-size: 12px;
        }
      </style>
      <h4>✨ Gemini Live Assistant</h4>
      <div id="gemini-status">Ready to assist with form filling.</div>
      <div class="gemini-btn-group">
        <button class="gemini-btn" onclick="window.geminiAssistant.explainForm()">🔊 Explain Form (AI)</button>
        <button class="gemini-btn" onclick="window.geminiAssistant.respeakCurrentField()">🔁 Re-speak Selected Field</button>
        <button class="gemini-btn" id="gemini-mic-btn" onclick="window.geminiAssistant.toggleVoiceReply()">🎤 Speak Answer (Auto-fill)</button>
      </div>
      <input type="password" class="gemini-key-input" id="gemini-key-field" placeholder="Paste Gemini API Key (Optional)" value="${this.apiKey}" onchange="window.geminiAssistant.setApiKey(this.value)">
    `;
    document.body.appendChild(panel);

    // Track focused fields
    document.addEventListener('focusin', (e) => {
      if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) {
        this.activeField = e.target;
      }
    });
  }

  updateStatus(msg) {
    const el = document.getElementById('gemini-status');
    if (el) el.textContent = msg;
  }

  speakText(text) {
    if (!('speechSynthesis' in window)) return;
    this.synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    this.synth.speak(utterance);
  }

  explainForm() {
    const fields = this.getFormFields();
    if (!fields.length) {
      this.updateStatus('No form fields found on page.');
      return;
    }

    const title = document.title || 'Form';
    let explanation = `Welcome. You are filling out the ${title}. `;
    explanation += `This form contains ${fields.length} main fields: ` + fields.map(f => f.label).join(', ') + `. `;
    explanation += `Please select any field or press Speak Answer to fill out fields automatically.`;

    this.updateStatus('Explaining form...');
    this.speakText(explanation);

    // If Gemini WebSocket Live API is configured, connect to live session
    if (this.apiKey) {
      this.connectGeminiLiveSession(explanation);
    }
  }

  respeakCurrentField() {
    let target = this.activeField;
    if (!target) {
      const inputs = document.querySelectorAll('input, select, textarea');
      if (inputs.length) target = inputs[0];
    }

    if (!target) {
      this.updateStatus('Please select a field first.');
      return;
    }

    const labelEl = document.querySelector(`label[for="${target.id}"]`) || target.closest('label') || target.previousElementSibling;
    const labelText = labelEl ? labelEl.textContent.trim() : (target.placeholder || target.name || target.id);
    const message = `Field: ${labelText}. Current value is: ${target.value || 'empty'}. Please state your value for ${labelText}.`;

    this.updateStatus(`Re-speaking field: ${labelText}`);
    this.speakText(message);
  }

  toggleVoiceReply() {
    if (this.isListening) {
      this.stopVoiceReply();
    } else {
      this.startVoiceReply();
    }
  }

  startVoiceReply() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      this.updateStatus('Speech recognition not supported in browser.');
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.lang = 'en-US';

    const btn = document.getElementById('gemini-mic-btn');
    if (btn) {
      btn.classList.add('active');
      btn.innerHTML = '🔴 Listening... (Click to stop)';
    }

    this.isListening = true;
    this.updateStatus('Listening for reply...');

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      this.updateStatus(`Received: "${transcript}"`);
      this.processUserReply(transcript);
    };

    this.recognition.onerror = (event) => {
      this.updateStatus(`Voice error: ${event.error}`);
      this.stopVoiceReply();
    };

    this.recognition.onend = () => {
      this.stopVoiceReply();
    };

    this.recognition.start();
  }

  stopVoiceReply() {
    this.isListening = false;
    if (this.recognition) {
      try { this.recognition.stop(); } catch(e){}
    }
    const btn = document.getElementById('gemini-mic-btn');
    if (btn) {
      btn.classList.remove('active');
      btn.innerHTML = '🎤 Speak Answer (Auto-fill)';
    }
  }

  processUserReply(text) {
    // If activeField is selected, directly fill activeField
    if (this.activeField) {
      this.activeField.value = text;
      this.activeField.dispatchEvent(new Event('input', { bubbles: true }));
      this.activeField.dispatchEvent(new Event('change', { bubbles: true }));
      this.updateStatus(`Auto-filled ${this.activeField.id || 'field'} with: "${text}"`);
      this.speakText(`Set ${this.activeField.id || 'field'} to ${text}`);
      return;
    }

    // Try smart matching against form fields
    const fields = this.getFormFields();
    let matched = false;

    for (const f of fields) {
      const el = document.getElementById(f.id);
      if (!el) continue;

      // Smart match logic
      const labelLower = f.label.toLowerCase();
      if (!el.value) {
        el.value = text;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        this.updateStatus(`Auto-filled ${f.label} with: "${text}"`);
        this.speakText(`Updated ${f.label}`);
        matched = true;
        break;
      }
    }

    if (!matched && fields.length > 0) {
      const firstEl = document.getElementById(fields[0].id);
      if (firstEl) {
        firstEl.value = text;
        firstEl.dispatchEvent(new Event('input', { bubbles: true }));
        firstEl.dispatchEvent(new Event('change', { bubbles: true }));
        this.updateStatus(`Auto-filled ${fields[0].label} with: "${text}"`);
      }
    }
  }

  connectGeminiLiveSession(contextText) {
    if (!this.apiKey) return;
    const wsUrl = `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=${this.apiKey}`;
    try {
      this.ws = new WebSocket(wsUrl);
      this.ws.onopen = () => {
        this.updateStatus('Connected to Gemini Live WebSocket API');
        const setupMessage = {
          setup: {
            model: "models/gemini-2.0-flash-exp",
            generationConfig: {
              responseModalities: ["AUDIO", "TEXT"]
            }
          }
        };
        this.ws.send(JSON.stringify(setupMessage));
      };
      this.ws.onmessage = (evt) => {
        const data = JSON.parse(evt.data);
        if (data.serverContent?.modelTurn?.parts) {
          data.serverContent.modelTurn.parts.forEach(p => {
            if (p.text) {
              this.updateStatus(`Gemini Live: ${p.text}`);
            }
          });
        }
      };
      this.ws.onerror = (err) => {
        console.warn('Gemini Live WS Error:', err);
      };
    } catch(e) {
      console.warn('Gemini Live WS initialization failed:', e);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.geminiAssistant = new GeminiLiveFormAssistant();
});
