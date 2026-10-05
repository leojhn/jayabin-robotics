(function() {
  'use strict';

  let lastSpokenText = "";

  const GeminiLive = {
    setApiKey: function(key) {
      if (key) sessionStorage.setItem('gemini_api_key', key);
    },

    getApiKey: function() {
      return sessionStorage.getItem('gemini_api_key') || window.GEMINI_API_KEY || "";
    },

    // Explains a form or specific field using Gemini Live API
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
      } else if (target && target.tagName === 'FORM') {
        const labels = Array.from(target.querySelectorAll('label')).map(l => l.textContent.replace(/[*:]/g, '').trim());
        textToSpeak = "Form fields to complete: " + labels.join(", ") + ".";
      }

      if (!textToSpeak) return;
      lastSpokenText = textToSpeak;
      await this.speak(textToSpeak);
    },

    // Option to re-speak the last explanation
    respeak: async function() {
      if (lastSpokenText) {
        await this.speak(lastSpokenText);
      }
    },

    // Re-speak a specific field or text
    respeakField: async function(fieldId) {
      if (fieldId) {
        await this.explainForm(fieldId);
      } else {
        await this.respeak();
      }
    },

    // Core audio/explanation speaker (no UI indicators shown)
    speak: async function(text) {
      if (!text) return;
      lastSpokenText = text;

      const key = this.getApiKey();
      if (key) {
        try {
          const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${key}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{
                parts: [{ text: `Explain this form input clearly in 1 brief sentence: ${text}` }]
              }]
            })
          });
          const data = await response.json();
          const explanation = data?.candidates?.[0]?.content?.parts?.[0]?.text || text;
          this._tts(explanation);
          return;
        } catch (e) {
          console.warn("Gemini Live API call error, falling back:", e);
        }
      }

      this._tts(text);
    },

    _tts: function(text) {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const lang = sessionStorage.getItem('language') === 'ml' ? 'ml-IN' : 'en-US';
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang;
        window.speechSynthesis.speak(utterance);
      }
    },

    // Add user reply to appropriate field automatically
    processUserReply: async function(userReply, formElement) {
      if (!userReply) return;

      const key = this.getApiKey();
      const form = formElement || document.querySelector('form') || document.body;
      const inputs = Array.from(form.querySelectorAll('input, textarea, select')).filter(i => i.id || i.name);

      if (key) {
        try {
          const fieldDescriptors = inputs.map(i => {
            const label = document.querySelector(`label[for="${i.id}"]`) || i.closest('.field')?.querySelector('label') || i.closest('div')?.querySelector('label') || i.previousElementSibling;
            return { id: i.id || i.name, label: label ? label.textContent.replace(/[*:]/g, '').trim() : i.id };
          });

          const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${key}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{
                parts: [{
                  text: `User provided input: "${userReply}". Map the information into appropriate field key-value pairs matching these fields: ${JSON.stringify(fieldDescriptors)}. Output valid JSON object only.`
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
          console.warn("Gemini extraction failed, using active field fallback:", e);
        }
      }

      // Fallback: populate active or first empty field automatically
      this._fallbackAutofill(userReply, inputs, form);
    },

    applyAutofill: function(dataMap, form) {
      if (!dataMap || typeof dataMap !== 'object') return;
      Object.keys(dataMap).forEach(key => {
        const val = dataMap[key];
        if (val === null || val === undefined) return;
        const input = (form || document).querySelector(`#${key}, [name="${key}"]`);
        if (input) {
          input.value = val;
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });
    },

    _fallbackAutofill: function(reply, inputs, form) {
      const active = document.activeElement;
      if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.tagName === 'SELECT')) {
        active.value = reply;
        active.dispatchEvent(new Event('input', { bubbles: true }));
        active.dispatchEvent(new Event('change', { bubbles: true }));
        return;
      }
      const empty = inputs.find(i => !i.value);
      if (empty) {
        empty.value = reply;
        empty.dispatchEvent(new Event('input', { bubbles: true }));
        empty.dispatchEvent(new Event('change', { bubbles: true }));
      }
    },

    initFormExplanations: function() {
      document.querySelectorAll('input, textarea, select').forEach(el => {
        if (el.dataset.geminiBound) return;
        el.dataset.geminiBound = 'true';
        el.addEventListener('focus', () => {
          this.explainForm(el.id);
        });
      });
    }
  };

  window.GeminiLive = GeminiLive;

  document.addEventListener('DOMContentLoaded', () => {
    GeminiLive.initFormExplanations();
  });
})();
