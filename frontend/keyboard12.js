// ============================================================
// HMS MINIMAL TOUCHSCREEN KEYBOARD
// Letters + numbers + common special characters only.
// No function keys, navigation keys, Ctrl/Alt/Windows keys,
// and no separate laptop-style numeric keypad.
// ============================================================
(function () {
    "use strict";

    if (window.HMSTouchKeyboardLoaded) return;
    window.HMSTouchKeyboardLoaded = true;

    let activeInput = null;
    let shiftOn = false;
    let capsOn = false;

    const keyboard = document.createElement("div");
    keyboard.id = "hmsKeyboard";
    keyboard.setAttribute("aria-hidden", "true");

    keyboard.innerHTML = `
        <div class="keyboard-header">
            <span>Touch Keyboard</span>
            <button id="keyboardClose" type="button" aria-label="Hide keyboard">✕</button>
        </div>
        <div class="keyboard-body minimal-keyboard-body">
            <div class="keyboard-main" id="keyboardMain"></div>
        </div>
    `;

    document.body.appendChild(keyboard);

    const main = keyboard.querySelector("#keyboardMain");
    const closeButton = keyboard.querySelector("#keyboardClose");

    const rows = [
        [
            {key:"`", shift:"~"}, {key:"1", shift:"!"}, {key:"2", shift:"@"},
            {key:"3", shift:"#"}, {key:"4", shift:"$"}, {key:"5", shift:"%"},
            {key:"6", shift:"^"}, {key:"7", shift:"&"}, {key:"8", shift:"*"},
            {key:"9", shift:"("}, {key:"0", shift:")"}, {key:"-", shift:"_"},
            {key:"=", shift:"+"}
        ],
        [
            {key:"q"},{key:"w"},{key:"e"},{key:"r"},{key:"t"},{key:"y"},
            {key:"u"},{key:"i"},{key:"o"},{key:"p"},{key:"[",shift:"{"},{key:"]",shift:"}"}
        ],
        [
            {key:"a"},{key:"s"},{key:"d"},{key:"f"},{key:"g"},{key:"h"},
            {key:"j"},{key:"k"},{key:"l"},{key:";",shift:":"},{key:"'",shift:'"'}
        ],
        [
            {key:"\\",shift:"|"},{key:"z"},{key:"x"},{key:"c"},{key:"v"},{key:"b"},
            {key:"n"},{key:"m"},{key:",",shift:"<"},{key:".",shift:">"},{key:"/",shift:"?"}
        ]
    ];

    function currentChar(item) {
        let value = shiftOn && item.shift ? item.shift : item.key;
        if (/^[a-z]$/.test(value)) {
            value = (capsOn !== shiftOn) ? value.toUpperCase() : value.toLowerCase();
        }
        return value;
    }

    function insertText(text) {
        if (!activeInput) return;
        const start = activeInput.selectionStart ?? activeInput.value.length;
        const end = activeInput.selectionEnd ?? activeInput.value.length;
        activeInput.value = activeInput.value.slice(0,start) + text + activeInput.value.slice(end);
        const pos = start + text.length;
        try { activeInput.setSelectionRange(pos, pos); } catch (_) {}
        activeInput.dispatchEvent(new Event("input", {bubbles:true}));
        activeInput.dispatchEvent(new Event("change", {bubbles:true}));
    }

    function backspace() {
        if (!activeInput) return;
        const start = activeInput.selectionStart ?? activeInput.value.length;
        const end = activeInput.selectionEnd ?? activeInput.value.length;
        if (start !== end) {
            activeInput.value = activeInput.value.slice(0,start) + activeInput.value.slice(end);
            try { activeInput.setSelectionRange(start,start); } catch (_) {}
        } else if (start > 0) {
            activeInput.value = activeInput.value.slice(0,start-1) + activeInput.value.slice(end);
            try { activeInput.setSelectionRange(start-1,start-1); } catch (_) {}
        }
        activeInput.dispatchEvent(new Event("input", {bubbles:true}));
        activeInput.dispatchEvent(new Event("change", {bubbles:true}));
    }

    function render() {
        main.innerHTML = "";
        rows.forEach((row) => {
            const rowDiv = document.createElement("div");
            rowDiv.className = "keyboard-row";
            row.forEach((item) => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "keyboard-key";
                btn.innerHTML = item.shift
                    ? `<span class="key-shift">${item.shift}</span><span class="key-main">${item.key}</span>`
                    : `<span class="key-main">${item.key}</span>`;
                btn.addEventListener("click", () => {
                    insertText(currentChar(item));
                    if (shiftOn) {
                        shiftOn = false;
                        render();
                    }
                });
                rowDiv.appendChild(btn);
            });
            main.appendChild(rowDiv);
        });

        const controls = document.createElement("div");
        controls.className = "keyboard-row minimal-controls";

        const shift = document.createElement("button");
        shift.type = "button";
        shift.className = "keyboard-key key-wide";
        shift.textContent = shiftOn ? "SHIFT ✓" : "SHIFT";
        shift.addEventListener("click", () => { shiftOn = !shiftOn; render(); });
        controls.appendChild(shift);

        const caps = document.createElement("button");
        caps.type = "button";
        caps.className = "keyboard-key key-wide";
        caps.textContent = capsOn ? "CAPS ✓" : "CAPS";
        caps.addEventListener("click", () => { capsOn = !capsOn; render(); });
        controls.appendChild(caps);

        const space = document.createElement("button");
        space.type = "button";
        space.className = "keyboard-key key-space";
        space.textContent = "SPACE";
        space.addEventListener("click", () => insertText(" "));
        controls.appendChild(space);

        const back = document.createElement("button");
        back.type = "button";
        back.className = "keyboard-key key-wide";
        back.textContent = "⌫";
        back.addEventListener("click", backspace);
        controls.appendChild(back);

        const enter = document.createElement("button");
        enter.type = "button";
        enter.className = "keyboard-key key-wide";
        enter.textContent = "ENTER";
        enter.addEventListener("click", () => {
            if (!activeInput) return;
            activeInput.dispatchEvent(new KeyboardEvent("keydown", {key:"Enter", bubbles:true}));
        });
        controls.appendChild(enter);
        main.appendChild(controls);
    }

    function showKeyboard(input) {
        activeInput = input;
        keyboard.classList.add("keyboard-visible");
        keyboard.setAttribute("aria-hidden", "false");
    }

    function hideKeyboard() {
        keyboard.classList.remove("keyboard-visible");
        keyboard.setAttribute("aria-hidden", "true");
        activeInput = null;
    }

    render();

    document.addEventListener("focusin", (event) => {
        const el = event.target;
        if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA")) {
            // Prevent Chromium from requesting the OS/Squeekboard keyboard.
            try { el.setAttribute("inputmode", "none"); } catch (_) {}
            showKeyboard(el);
        }
    });

    closeButton.addEventListener("click", hideKeyboard);

    const toggle = document.createElement("button");
    toggle.id = "keyboardToggle";
    toggle.type = "button";
    toggle.innerHTML = "⌨";
    toggle.title = "Show / Hide Touch Keyboard";
    toggle.addEventListener("click", () => {
        if (keyboard.classList.contains("keyboard-visible")) hideKeyboard();
        else if (activeInput) showKeyboard(activeInput);
    });
    document.body.appendChild(toggle);
})();
