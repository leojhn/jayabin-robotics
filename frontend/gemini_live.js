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
  let noResponseTimer = null;
  const NO_RESPONSE_TIMEOUT_MS = 10000;

  function getApiKey() {
    return GEMINI_API_KEY || sessionStorage.getItem('gemini_api_key') || window.GEMINI_API_KEY || "";
  }

  function getLang() {
    return sessionStorage.getItem('language') === 'ml' ? 'ml-IN' : 'en-US';
  }

  function getLabel(el) {
    if (!el) return "";
    const id = el.id || el.name;
    if (id) {
      const labelEl = document.querySelector(`label[for="${id}"]`);
      if (labelEl) return labelEl.textContent.replace(/[*:]/g, '').trim();
    }
    const closestField = el.closest('.field') || el.closest('div') || el.closest('td');
    if (closestField) {
      const label = closestField.querySelector('label');
      if (label) return label.textContent.replace(/[*:]/g, '').trim();
    }
    if (el.previousElementSibling && el.previousElementSibling.tagName === 'LABEL') {
      return el.previousElementSibling.textContent.replace(/[*:]/g, '').trim();
    }
    return el.placeholder || el.name || el.id || el.type || "";
  }

  // 1. DYNAMIC PAGE CONTEXT EXTRACTION
  function getPageContext() {
    const pageName = window.location.pathname.split('/').pop() || 'index.html';
    const language = sessionStorage.getItem('language') || 'en';

    const fields = Array.from(document.querySelectorAll('input:not([type=hidden]), select, textarea')).map(el => {
      const ctx = {
        id: el.id || el.name,
        tagName: el.tagName.toLowerCase(),
        type: el.type || el.tagName.toLowerCase(),
        label: getLabel(el),
        value: el.value || "",
        required: el.required || false,
        disabled: el.disabled || false
      };
      if (el.tagName === 'SELECT') {
        ctx.options = Array.from(el.options).map(o => ({
          value: o.value,
          text: o.text.trim()
        })).filter(o => o.text !== "" && o.value !== "");
      }
      return ctx;
    });

    const buttons = Array.from(document.querySelectorAll('button, a.button')).map(b => ({
      id: b.id || "",
      text: b.textContent.trim(),
      type: b.type || 'button'
    })).filter(b => b.text !== "");

    return {
      page: pageName,
      language: language,
      fields: fields,
      buttons: buttons
    };
  }

  // 2. ROBUST SELECT OPTION MATCHING
  function selectOption(selectElement, spokenValue) {
    if (!selectElement || selectElement.tagName !== 'SELECT' || !spokenValue) return false;
    const wanted = spokenValue.trim().toLowerCase();

    const options = Array.from(selectElement.options);

    // Exact text or value match
    let option = options.find(o =>
      o.text.trim().toLowerCase() === wanted ||
      o.value.trim().toLowerCase() === wanted
    );

    // Partial/Contains match
    if (!option) {
      option = options.find(o =>
        o.text.trim().toLowerCase().includes(wanted) ||
        wanted.includes(o.text.trim().toLowerCase()) ||
        o.value.trim().toLowerCase().includes(wanted)
      );
    }

    if (option) {
      selectElement.value = option.value;
      selectElement.dispatchEvent(new Event('change', { bubbles: true }));
      selectElement.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    }

    return false;
  }

  // 3. TOOL DECLARATIONS FOR GEMINI LIVE FUNCTION CALLING
  const toolDeclarations = [
    {
      name: "fill_field",
      description: "Fill a text, number, date, or textarea input field on the current page.",
      parameters: {
        type: "OBJECT",
        properties: {
          field_id: { type: "STRING", description: "The HTML id or name of the input field." },
          value: { type: "STRING", description: "The value to enter (e.g., patient name, phone number, date YYYY-MM-DD)." }
        },
        required: ["field_id", "value"]
      }
    },
    {
      name: "select_option",
      description: "Select an option from a dropdown/select element on the page.",
      parameters: {
        type: "OBJECT",
        properties: {
          field_id: { type: "STRING", description: "The HTML id or name of the select element." },
          option: { type: "STRING", description: "The name, text, or value of the option to select (e.g., 'Cardiology', 'English', 'Cash')." }
        },
        required: ["field_id", "option"]
      }
    },
    {
      name: "click_button",
      description: "Click a button or action on the page (e.g., 'Continue', 'Back', 'Confirm Appointment', 'Register').",
      parameters: {
        type: "OBJECT",
        properties: {
          button_id: { type: "STRING", description: "The ID of the button if available." },
          button_text: { type: "STRING", description: "The text on the button to click." }
        }
      }
    },
    {
      name: "read_page",
      description: "Read aloud the current page title and available form fields or options to the user.",
      parameters: {
        type: "OBJECT",
        properties: {}
      }
    }
  ];

  // 4. FUNCTION CALL EXECUTION ENGINE
  function executeToolCall(name, args) {
    console.log(`Executing Tool Call: ${name}`, args);
    if (name === "fill_field") {
      const field = document.getElementById(args.field_id) || document.querySelector(`[name="${args.field_id}"]`);
      if (field) {
        if (field.tagName === 'SELECT') {
          return selectOption(field, args.value);
        } else {
          field.value = args.value;
          field.dispatchEvent(new Event('input', { bubbles: true }));
          field.dispatchEvent(new Event('change', { bubbles: true }));
          return true;
        }
      }
    } else if (name === "select_option") {
      const field = document.getElementById(args.field_id) || document.querySelector(`[name="${args.field_id}"]`);
      if (field) {
        return selectOption(field, args.option);
      } else {
        // Fallback search across all select elements
        const selects = Array.from(document.querySelectorAll('select'));
        for (let sel of selects) {
          if (selectOption(sel, args.option)) return true;
        }
      }
    } else if (name === "click_button") {
      let btn = null;
      if (args.button_id) btn = document.getElementById(args.button_id);
      if (!btn && args.button_text) {
        const wanted = args.button_text.toLowerCase().trim();
        btn = Array.from(document.querySelectorAll('button, a.button')).find(b => b.textContent.toLowerCase().trim().includes(wanted));
      }
      if (btn) {
        btn.click();
        return true;
      }
    } else if (name === "read_page") {
      GeminiLive.explainCurrentPage();
      return true;
    }
    return false;
  }

  const GeminiLive = {
    setApiKey: function(key) {
      if (key) sessionStorage.setItem('gemini_api_key', key);
    },

    getApiKey: getApiKey,
    getPageContext: getPageContext,
    selectOption: selectOption,

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

    // Silent Audio Speaker (no UI assistant badges)
    speak: function(text) {
      return new Promise((resolve) => {
        if (!text) { resolve(); return; }
        lastSpokenText = text;

        if ('speechSynthesis' in window) {
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.lang = getLang();
          utterance.onend = () => { resolve(); };
          utterance.onerror = () => { resolve(); };
          window.speechSynthesis.speak(utterance);
        } else {
          resolve();
        }
      });
    },

    // Explain full current page context aloud
    explainCurrentPage: async function() {
      const ctx = getPageContext();
      const key = getApiKey();
      const ml = sessionStorage.getItem('language') === 'ml';

      const promptText = `Current Kiosk Page Context: ${JSON.stringify(ctx)}. Generate a concise 1-2 sentence spoken announcement welcoming the patient and explaining what to do on this screen in ${ml ? 'Malayalam' : 'English'}.`;

      if (key) {
        try {
          const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${key}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{ parts: [{ text: promptText }] }]
            })
          });
          const data = await response.json();
          const speech = data?.candidates?.[0]?.content?.parts?.[0]?.text;
          if (speech) {
            await this.speak(speech);
            return;
          }
        } catch(e) {
          console.warn("Gemini Live page explanation fallback:", e);
        }
      }

      // Default page narration fallback
      const fallbacks = {
        'index.html': ml ? 'ജയാബിൻ ഹോസ്പിറ്റലിലേക്ക് സ്വാഗതം. ഇംഗ്ലീഷ് അല്ലെങ്കിൽ മലയാളം തിരഞ്ഞെടുക്കുക.' : 'Welcome to Jayabin Hospital. Please select your language.',
        'checkin.html': ml ? 'ചെക്ക്-ഇൻ സ്വാഗതം. പുതിയ രോഗി അല്ലെങ്കിൽ പഴയ രോഗി എന്നത് തിരഞ്ഞെടുക്കുക.' : 'Welcome to Check-in. Please select New Patient or Existing Patient.',
        'neo_nano_welcome.html': ml ? 'നിയോ നാനോ മെഡിക്കൽ ഇന്റലിജൻസിലേക്ക് സ്വാഗതം. തുടരുക.' : 'Welcome to Neo Nano Medical Intelligence. Please continue for symptom analysis.',
        'neo_nano_symptoms.html': ml ? 'നിങ്ങളെ ബുദ്ധിമുട്ടിക്കുന്ന ലക്ഷണങ്ങൾ നൽകുക.' : 'Please describe what symptoms you are experiencing.',
        'new_patient.html': ml ? 'പുതിയ രോഗി രജിസ്ട്രേഷനായി ഫോം പൂരിപ്പിക്കുക.' : 'Please enter your patient details for registration.',
        'appointments.html': ml ? 'കൺസൾട്ടേഷനായി വിഭാഗവും ഡോക്ടറും തിരഞ്ഞെടുക്കുക.' : 'Please select your department, doctor, date, and time for appointment.',
        'consultant_bill.html': ml ? 'പേയ്മെന്റ് രീതി തിരഞ്ഞെടുക്കുക.' : 'Please select your preferred payment method: UPI, Card, or Cash.'
      };

      const fallbackText = fallbacks[ctx.page] || (ml ? "ദയവായി ഫോം പൂരിപ്പിക്കുക." : "Please fill out the details on the screen.");
      await this.speak(fallbackText);
    },

    // Process user spoken input using Gemini Live Function Calling
    processUserReply: async function(userReply) {
      if (!userReply) return;
      this.clearNoResponseTimer();

      const key = getApiKey();
      const pageContext = getPageContext();

      if (key) {
        try {
          const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${key}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{
                role: "user",
                parts: [{
                  text: `Page Context: ${JSON.stringify(pageContext)}.\nUser Spoke: "${userReply}".\nCall the appropriate tool function (fill_field, select_option, click_button, or read_page) to update the website state based on what the user wants.`
                }]
              }],
              tools: [{ functionDeclarations: toolDeclarations }]
            })
          });

          const data = await response.json();
          const candidate = data?.candidates?.[0];
          const call = candidate?.content?.parts?.[0]?.functionCall;

          if (call) {
            executeToolCall(call.name, call.args);
            return;
          }
        } catch(e) {
          console.warn("Gemini Live Function Calling Error:", e);
        }
      }

      // Fallback matching when Gemini Live key is omitted or offline
      this.fallbackProcessUserReply(userReply, pageContext);
    },

    fallbackProcessUserReply: function(userReply, ctx) {
      const replyLower = userReply.toLowerCase().trim();

      // Check language selection on index
      if (ctx.page === 'index.html' || ctx.page === '') {
        if (replyLower.includes('english')) if (typeof selectLanguage === 'function') selectLanguage('en');
        if (replyLower.includes('malayalam') || replyLower.includes('മലയാളം')) if (typeof selectLanguage === 'function') selectLanguage('ml');
        return;
      }

      // Check select options
      const selects = Array.from(document.querySelectorAll('select'));
      for (let sel of selects) {
        if (selectOption(sel, replyLower)) return;
      }

      // Check buttons
      const buttons = Array.from(document.querySelectorAll('button, a.button'));
      for (let btn of buttons) {
        if (btn.textContent.toLowerCase().trim().includes(replyLower)) {
          btn.click();
          return;
        }
      }

      // Fallback fill active or empty field
      const active = document.activeElement;
      if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) {
        active.value = userReply;
        active.dispatchEvent(new Event('input', { bubbles: true }));
        active.dispatchEvent(new Event('change', { bubbles: true }));
        return;
      }

      const empty = ctx.fields.find(f => !f.value && f.tagName !== 'select');
      if (empty) {
        const field = document.getElementById(empty.id);
        if (field) {
          field.value = userReply;
          field.dispatchEvent(new Event('input', { bubbles: true }));
          field.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }
    },

    // Background Audio Listening Engine (Silent - no UI indicators)
    startListening: function() {
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
          const transcript = event.results[event.results.length - 1][0].transcript.trim();
          if (transcript) {
            await this.processUserReply(transcript);
          }
        };

        recognition.onerror = (e) => {
          console.warn("Background audio listening notice:", e.error);
        };

        recognition.onend = () => {
          recognitionActive = false;
          setTimeout(() => {
            if (!recognitionActive) {
              try { recognition.start(); } catch(e){}
            }
          }, 1000);
        };

        recognition.start();
      } catch(e) {
        console.warn("Speech recognition init notice:", e);
      }
    },

    resetNoResponseTimer: function(customPrompt) {
      if (noResponseTimer) clearTimeout(noResponseTimer);
      noResponseTimer = setTimeout(() => {
        const ml = sessionStorage.getItem('language') === 'ml';
        const prompt = customPrompt || (ml ? "എനിക്ക് മനസ്സിലായില്ല. ദയവായി വീണ്ടും പറയുക." : "Please reply or select your option on the screen.");
        this.speak(prompt);
      }, NO_RESPONSE_TIMEOUT_MS);
    },

    clearNoResponseTimer: function() {
      if (noResponseTimer) clearTimeout(noResponseTimer);
    },

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
          btn.onclick = (e) => { e.preventDefault(); e.stopPropagation(); GeminiLive.explainForm(el.id || el.name); };
          parent.appendChild(btn);
        }
      });
    },

    explainForm: function(target) {
      const el = typeof target === 'string' ? document.getElementById(target) : target;
      if (!el) return;
      const labelText = getLabel(el);
      const ml = sessionStorage.getItem('language') === 'ml';
      const text = ml ? `ദയവായി ${labelText} നൽകുക.` : `Please provide your ${labelText}.`;
      this.speak(text);
    },

    initPageNarration: async function() {
      await this.explainCurrentPage();
      this.startListening();
      this.addRespeakButtons();
    }
  };

  window.GeminiLive = GeminiLive;

  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
      GeminiLive.initPageNarration();
    }, 400);
  });
})();
