(function() {
  'use strict';

  // =========================================================================
  // PASTE YOUR GEMINI API KEY HERE BELOW IF YOU WANT TO SET IT IN CODE:
  // =========================================================================
  const GEMINI_API_KEY = "";
  // =========================================================================

  let lastSpokenText = "";
  let recognition = null;
  let recognitionActive = false;
  let currentFieldIndex = 0;
  let formFields = [];
  let noResponseTimer = null;
  const NO_RESPONSE_TIMEOUT_MS = 9000;

  function getApiKey() {
    return GEMINI_API_KEY || sessionStorage.getItem('gemini_api_key') || window.GEMINI_API_KEY || "";
  }

  function getLang() {
    return sessionStorage.getItem('language') === 'ml' ? 'ml-IN' : 'en-US';
  }

  const GeminiLive = {
    setApiKey: function(key) {
      if (key) sessionStorage.setItem('gemini_api_key', key);
    },

    getApiKey: getApiKey,

    // Re-speak last prompt or specific field prompt
    respeak: async function() {
      if (lastSpokenText) {
        await this.speak(lastSpokenText);
      }
    },

    respeakField: async function(fieldId) {
      if (fieldId) {
        this.explainForm(fieldId);
      } else {
        this.respeak();
      }
    },

    // Core TTS Speaker (runs silently, no visual UI badges)
    speak: function(text) {
      return new Promise((resolve) => {
        if (!text) { resolve(); return; }
        lastSpokenText = text;

        const key = getApiKey();

        const doTTS = (spokenText) => {
          if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(spokenText);
            utterance.lang = getLang();
            utterance.onend = () => { resolve(); };
            utterance.onerror = () => { resolve(); };
            window.speechSynthesis.speak(utterance);
          } else {
            resolve();
          }
        };

        if (key) {
          fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${key}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{
                parts: [{ text: `Format this kiosk message for audio speech output in 1 clear sentence: "${text}"` }]
              }]
            })
          }).then(res => res.json()).then(data => {
            const explanation = data?.candidates?.[0]?.content?.parts?.[0]?.text || text;
            doTTS(explanation);
          }).catch(() => {
            doTTS(text);
          });
        } else {
          doTTS(text);
        }
      });
    },

    // Start background audio listening without any visual UI widgets
    startListening: function(onTranscriptCallback) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) return;

      if (recognitionActive && recognition) {
        try { recognition.stop(); } catch(e){}
      }

      try {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = getLang();

        recognition.onstart = () => {
          recognitionActive = true;
        };

        recognition.onresult = async (event) => {
          this.resetNoResponseTimer();
          const transcript = event.results[event.results.length - 1][0].transcript.trim();
          if (transcript) {
            if (onTranscriptCallback) {
              await onTranscriptCallback(transcript);
            } else {
              await this.handleGlobalTranscript(transcript);
            }
          }
        };

        recognition.onerror = (e) => {
          console.warn("Background STT warning:", e.error);
        };

        recognition.onend = () => {
          recognitionActive = false;
          // Auto-restart background listening silently
          setTimeout(() => {
            if (!recognitionActive) {
              try { recognition.start(); } catch(e){}
            }
          }, 1000);
        };

        recognition.start();
      } catch(e) {
        console.warn("Background recognition failed to start:", e);
      }
    },

    resetNoResponseTimer: function(customPrompt) {
      if (noResponseTimer) clearTimeout(noResponseTimer);
      noResponseTimer = setTimeout(() => {
        const prompt = customPrompt || (sessionStorage.getItem('language') === 'ml' ? "എനിക്ക് മനസ്സിലായില്ല. ദയവായി വീണ്ടും പറയുക." : "I didn't catch that. Please reply or select on screen.");
        this.speak(prompt);
      }, NO_RESPONSE_TIMEOUT_MS);
    },

    clearNoResponseTimer: function() {
      if (noResponseTimer) clearTimeout(noResponseTimer);
    },

    // Handle transcripts for navigation and general speech
    handleGlobalTranscript: async function(transcript) {
      const t = transcript.toLowerCase();
      const page = window.location.pathname.split('/').pop() || 'index.html';

      // 1. Language Selection Page
      if (page === 'index.html' || page === '') {
        if (t.includes('english') || t.includes('ഇംഗ്ലീഷ്')) {
          if (typeof selectLanguage === 'function') selectLanguage('en');
        } else if (t.includes('malayalam') || t.includes('മലയാളം')) {
          if (typeof selectLanguage === 'function') selectLanguage('ml');
        }
        return;
      }

      // 2. Check-in Page
      if (page === 'checkin.html') {
        if (t.includes('new') || t.includes('പുതിയ')) {
          sessionStorage.setItem('is_existing_user', 'false');
          sessionStorage.removeItem('patient');
          window.location.href = 'neo_nano_welcome.html';
        } else if (t.includes('existing') || t.includes('قديم') || t.includes('പഴയ') || t.includes('പഴയ രോഗി')) {
          window.location.href = 'existing_patient.html';
        }
        return;
      }

      // 3. Neo Nano Welcome
      if (page === 'neo_nano_welcome.html') {
        if (t.includes('continue') || t.includes('next') || t.includes('തുടരുക')) {
          window.location.href = 'neo_nano_symptoms.html';
        } else if (t.includes('skip') || t.includes('ഒഴിവാക്കുക')) {
          const isExisting = sessionStorage.getItem('is_existing_user') === 'true';
          window.location.href = isExisting ? 'appointments.html' : 'new_patient.html';
        }
        return;
      }

      // 4. Consultant Bill
      if (page === 'consultant_bill.html') {
        if (t.includes('upi')) {
          if (typeof select === 'function') select('UPI');
        } else if (t.includes('card')) {
          if (typeof select === 'function') select('Card');
        } else if (t.includes('cash')) {
          if (typeof select === 'function') select('Cash');
        } else if (t.includes('confirm') || t.includes('paid') || t.includes('complete')) {
          const btn = document.getElementById('manualConfirm');
          if (btn) btn.click();
        }
        return;
      }

      // 5. Active Form Processing
      const activeForm = document.querySelector('form') || document.body;
      await this.processUserReply(transcript, activeForm);
    },

    // Process user reply and map to form fields using Gemini API
    processUserReply: async function(userReply, formElement) {
      if (!userReply) return;

      const key = getApiKey();
      const form = formElement || document.querySelector('form') || document.body;
      const inputs = Array.from(form.querySelectorAll('input, textarea, select')).filter(i => (i.id || i.name) && i.type !== 'hidden');

      if (key) {
        try {
          const fieldDescriptors = inputs.map(i => {
            const label = document.querySelector(`label[for="${i.id}"]`) || i.closest('.field')?.querySelector('label') || i.closest('div')?.querySelector('label') || i.previousElementSibling;
            return { id: i.id || i.name, type: i.type, label: label ? label.textContent.replace(/[*:]/g, '').trim() : i.id };
          });

          const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${key}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{
                parts: [{
                  text: `User spoke: "${userReply}". Extract field values for: ${JSON.stringify(fieldDescriptors)}. For dates, format as YYYY-MM-DD. Return valid JSON object mapping field IDs to values.`
                }]
              }],
              generationConfig: { responseMimeType: "application/json" }
            })
          });
          const data = await response.json();
          const jsonText = data?.candidates?.[0]?.content?.parts?.[0]?.text;
          if (jsonText) {
            const parsed = JSON.parse(jsonText);
            this.applyAutofill(parsed, form);
            return;
          }
        } catch (e) {
          console.warn("Gemini Live parsing fallback:", e);
        }
      }

      // Fallback: fill active element or current field sequentially
      this.fallbackAutofill(userReply, inputs, form);
    },

    applyAutofill: function(dataMap, form) {
      if (!dataMap || typeof dataMap !== 'object') return;
      let filled = false;
      Object.keys(dataMap).forEach(key => {
        const val = dataMap[key];
        if (val === null || val === undefined || val === "") return;
        const input = (form || document).querySelector(`#${key}, [name="${key}"]`);
        if (input) {
          input.value = val;
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.dispatchEvent(new Event('change', { bubbles: true }));
          filled = true;
        }
      });
      if (filled) {
        this.advanceToNextField();
      }
    },

    fallbackAutofill: function(reply, inputs, form) {
      const active = document.activeElement;
      if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.tagName === 'SELECT')) {
        active.value = reply;
        active.dispatchEvent(new Event('input', { bubbles: true }));
        active.dispatchEvent(new Event('change', { bubbles: true }));
        this.advanceToNextField();
        return;
      }
      if (formFields.length > 0 && currentFieldIndex < formFields.length) {
        const input = formFields[currentFieldIndex];
        input.value = reply;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        this.advanceToNextField();
        return;
      }
      const empty = inputs.find(i => !i.value);
      if (empty) {
        empty.value = reply;
        empty.dispatchEvent(new Event('input', { bubbles: true }));
        empty.dispatchEvent(new Event('change', { bubbles: true }));
      }
    },

    // Sequential Form Narration & Sequence Handling

    addRespeakButtons: function() {
      document.querySelectorAll('input, textarea, select').forEach(el => {
        if (el.dataset.respeakBtnAdded) return;
        el.dataset.respeakBtnAdded = 'true';
        const parent = el.closest('.field') || el.closest('div');
        if (parent && !parent.querySelector('.respeak-btn')) {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'respeak-btn';
          btn.textContent = '🔊 Re-speak';
          btn.style.cssText = 'margin-top:4px;padding:4px 8px;font-size:12px;background:rgba(255,255,255,0.15);color:#fff;border:none;border-radius:6px;cursor:pointer;width:fit-content;';
          btn.onclick = (e) => { e.preventDefault(); e.stopPropagation(); this.explainForm(el.id || el.name); };
          parent.appendChild(btn);
        }
      });
    },

    initSequentialForm: function(formSelector) {
      const form = document.querySelector(formSelector || 'form') || document.body;
      formFields = Array.from(form.querySelectorAll('input:not([type=hidden]):not([readonly]), textarea, select'));
      currentFieldIndex = 0;

      if (formFields.length > 0) {
        this.promptField(currentFieldIndex);
      }
    },

    promptField: async function(index) {
      if (index >= formFields.length) {
        this.clearNoResponseTimer();
        const ml = sessionStorage.getItem('language') === 'ml';
        await this.speak(ml ? "എല്ലാ വിവരങ്ങളും പൂർത്തിയായി. ദയവായി തുടരുക." : "All fields are filled. You can now submit or continue.");
        return;
      }

      currentFieldIndex = index;
      const el = formFields[index];
      el.focus();

      const label = document.querySelector(`label[for="${el.id}"]`) || el.closest('.field')?.querySelector('label') || el.closest('div')?.querySelector('label') || el.previousElementSibling;
      const labelText = label ? label.textContent.replace(/[*:]/g, '').trim() : el.id;

      const ml = sessionStorage.getItem('language') === 'ml';
      const promptText = ml ? `ദയവായി നിങ്ങളുടെ ${labelText} പറയുക.` : `Please provide your ${labelText}.`;

      await this.speak(promptText);
      this.resetNoResponseTimer(promptText);
    },

    advanceToNextField: function() {
      if (formFields.length > 0 && currentFieldIndex < formFields.length - 1) {
        this.promptField(currentFieldIndex + 1);
      } else {
        this.clearNoResponseTimer();
      }
    },

    explainForm: async function(target) {
      let textToSpeak = "";
      if (typeof target === 'string') {
        const el = document.getElementById(target);
        if (el) {
          const label = document.querySelector(`label[for="${target}"]`) || el.closest('.field')?.querySelector('label') || el.closest('div')?.querySelector('label') || el.previousElementSibling;
          const labelText = label ? label.textContent.replace(/[*:]/g, '').trim() : target;
          textToSpeak = `Please fill out ${labelText}.`;
        } else {
          textToSpeak = target;
        }
      }
      if (textToSpeak) {
        await this.speak(textToSpeak);
      }
    },

    // Page Level Auto Narration
    initPageNarration: async function() {
      const page = window.location.pathname.split('/').pop() || 'index.html';
      const ml = sessionStorage.getItem('language') === 'ml';

      if (page === 'index.html' || page === '') {
        const msg = "Welcome to Jayabin Hospital. Please select English or Malayalam.";
        await this.speak(msg);
        this.startListening();
        this.resetNoResponseTimer(msg);
      } else if (page === 'checkin.html') {
        const msg = ml ? "ജയാബിൻ ഹോസ്പിറ്റൽ ചെക്ക്-ഇന്നിലേക്ക് സ്വാഗതം. പുതിയ രോഗി അല്ലെങ്കിൽ പഴയ രോഗി എന്നത് തിരഞ്ഞെടുക്കുക." : "Welcome to patient check-in. Please select New Patient or Existing Patient.";
        await this.speak(msg);
        this.startListening();
        this.resetNoResponseTimer(msg);
      } else if (page === 'neo_nano_welcome.html') {
        const msg = ml ? "നിയോ നാനോ മെഡിക്കൽ ഇന്റലിജൻസിലേക്ക് സ്വാഗതം. തുടരാൻ കണ്ടിന്യൂ എന്ന് പറയുക അല്ലെങ്കിൽ തുടരുക ബട്ടൺ അമർത്തുക." : "Welcome to Neo Nano Medical Intelligence. Say continue to start symptom analysis.";
        await this.speak(msg);
        this.startListening();
        this.resetNoResponseTimer(msg);
      } else if (page === 'new_patient.html') {
        const msg = ml ? "പുതിയ രോഗി രജിസ്ട്രേഷനിലേക്ക് സ്വാഗതം. നിങ്ങളുടെ വിവരങ്ങൾ നൽകുക." : "Welcome to New Patient Registration. We will guide you through each field.";
        await this.speak(msg);
        this.initSequentialForm('#patientForm');
        this.startListening();
      } else if (page === 'appointments.html') {
        const msg = ml ? "അപ്പോയിന്റ്മെന്റ് സ്ഥിരീകരിക്കാൻ ഡോക്ടറെയും തീയതിയും തിരഞ്ഞെടുക്കുക." : "Please choose your department, doctor, and date to confirm your appointment.";
        await this.speak(msg);
        this.startListening();
      } else if (page === 'consultant_bill.html') {
        const msg = ml ? "നിങ്ങളുടെ കൺസൾട്ടേഷൻ ബിൽ തുക. യു.പി.ഐ, കാർഡ് അല്ലെങ്കിൽ ക്യാഷ് പേയ്മെന്റ് രീതി തിരഞ്ഞെടുക്കുക." : "Please select your payment method: UPI, Card, or Cash.";
        await this.speak(msg);
        this.startListening();
      } else {
        this.startListening();
      }
    }
  };

  window.GeminiLive = GeminiLive;

  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
      GeminiLive.initPageNarration(); GeminiLive.addRespeakButtons();
    }, 400);
  });
})();
