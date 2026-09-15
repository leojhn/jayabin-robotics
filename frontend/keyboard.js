// ==========================================
// HMS MOBILE TOUCHSCREEN KEYBOARD
// Modern Mobile Model (iOS / Android Style)
// ==========================================

(function () {
    "use strict";

    if (window.HMSTouchKeyboardLoaded) return;
    window.HMSTouchKeyboardLoaded = true;

    let activeInput = null;
    let lastInput = null;

    // Mobile layout states: 'abc', '123', 'sym'
    let layoutMode = "abc";
    let shiftOn = false;
    let capsLock = false;

    // Secret exit password tracking ("jayabin")
    let exitBuffer = "";
    const EXIT_PASSWORD = "jayabin";

    function checkExitPassword(char) {
        if (!char || char.length !== 1) return;
        exitBuffer += char.toLowerCase();
        if (exitBuffer.length > 20) {
            exitBuffer = exitBuffer.slice(-20);
        }
        if (exitBuffer.endsWith(EXIT_PASSWORD)) {
            exitBuffer = "";
            executeKioskExit();
        }
    }

    function executeKioskExit() {
        if (activeInput && activeInput.value) {
            const val = activeInput.value;
            const idx = val.toLowerCase().lastIndexOf(EXIT_PASSWORD);
            if (idx !== -1) {
                activeInput.value = val.slice(0, idx) + val.slice(idx + EXIT_PASSWORD.length);
                activeInput.dispatchEvent(new Event("input", { bubbles: true }));
            }
        }

        hideKeyboard();

        if (document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement) {
            if (document.exitFullscreen) {
                document.exitFullscreen().catch(function () {});
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }

        try {
            window.close();
        } catch (e) {}

        let overlay = document.getElementById("kioskExitOverlay");
        if (!overlay) {
            overlay = document.createElement("div");
            overlay.id = "kioskExitOverlay";
            overlay.className = "kiosk-exit-overlay";
            overlay.innerHTML = `
                <div class="kiosk-exit-card">
                    <div class="kiosk-exit-icon">🔒</div>
                    <h2>Kiosk Exit Command Triggered</h2>
                    <p>Secret password <strong>"jayabin"</strong> verified. Kiosk mode and fullscreen terminated (Alt+F4 action performed).</p>
                    <div class="kiosk-exit-actions">
                        <button type="button" class="btn-exit-close" id="kioskExitCloseBtn">Close Window</button>
                        <button type="button" class="btn-exit-reopen" id="kioskExitResumeBtn">Resume Kiosk</button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);

            document.getElementById("kioskExitCloseBtn").addEventListener("click", function () {
                window.close();
                window.location.href = "about:blank";
            });

            document.getElementById("kioskExitResumeBtn").addEventListener("click", function () {
                overlay.style.display = "none";
            });
        } else {
            overlay.style.display = "flex";
        }
    }

    // CREATE KEYBOARD CONTAINER
    const keyboard = document.createElement("div");
    keyboard.id = "hmsKeyboard";
    keyboard.className = "mobile-keyboard";
    keyboard.setAttribute("aria-hidden", "true");

    keyboard.innerHTML = `
        <div class="keyboard-header">
            <span class="keyboard-title">📱 Touch Keyboard</span>
            <button id="keyboardClose" type="button" aria-label="Hide keyboard">✕</button>
        </div>
        <div class="keyboard-body" id="keyboardMain"></div>
    `;

    document.body.appendChild(keyboard);

    const main = keyboard.querySelector("#keyboardMain");
    const closeButton = keyboard.querySelector("#keyboardClose");

    // LAYOUT DEFINITIONS (MOBILE MODEL)
    const abcLayout = [
        [
            { key: "q" }, { key: "w" }, { key: "e" }, { key: "r" }, { key: "t" },
            { key: "y" }, { key: "u" }, { key: "i" }, { key: "o" }, { key: "p" }
        ],
        [
            { key: "a" }, { key: "s" }, { key: "d" }, { key: "f" }, { key: "g" },
            { key: "h" }, { key: "j" }, { key: "k" }, { key: "l" }
        ],
        [
            { key: "Shift", label: "⇧", cls: "key-action key-shift" },
            { key: "z" }, { key: "x" }, { key: "c" }, { key: "v" },
            { key: "b" }, { key: "n" }, { key: "m" },
            { key: "Backspace", label: "⌫", cls: "key-action key-delete" }
        ],
        [
            { key: "Mode123", label: "?123", cls: "key-action key-mode" },
            { key: "@", cls: "key-symbol" },
            { key: " ", label: "space", cls: "key-space" },
            { key: ".", cls: "key-symbol" },
            { key: "Enter", label: "return", cls: "key-enter" }
        ]
    ];

    const numLayout = [
        [
            { key: "1" }, { key: "2" }, { key: "3" }, { key: "4" }, { key: "5" },
            { key: "6" }, { key: "7" }, { key: "8" }, { key: "9" }, { key: "0" }
        ],
        [
            { key: "-" }, { key: "/" }, { key: ":" }, { key: ";" }, { key: "(" },
            { key: ")" }, { key: "$" }, { key: "&" }, { key: "@" }, { key: '"' }
        ],
        [
            { key: "ModeSym", label: "=#\\", cls: "key-action key-mode" },
            { key: "." }, { key: "," }, { key: "?" }, { key: "!" }, { key: "'" },
            { key: "Backspace", label: "⌫", cls: "key-action key-delete" }
        ],
        [
            { key: "ModeABC", label: "ABC", cls: "key-action key-mode" },
            { key: "-", cls: "key-symbol" },
            { key: " ", label: "space", cls: "key-space" },
            { key: ".", cls: "key-symbol" },
            { key: "Enter", label: "return", cls: "key-enter" }
        ]
    ];

    const symLayout = [
        [
            { key: "[" }, { key: "]" }, { key: "{" }, { key: "}" }, { key: "#" },
            { key: "%" }, { key: "^" }, { key: "*" }, { key: "+" }, { key: "=" }
        ],
        [
            { key: "_" }, { key: "\\" }, { key: "|" }, { key: "~" }, { key: "<" },
            { key: ">" }, { key: "€" }, { key: "£" }, { key: "¥" }, { key: "•" }
        ],
        [
            { key: "Mode123", label: "123", cls: "key-action key-mode" },
            { key: "." }, { key: "," }, { key: "?" }, { key: "!" }, { key: "'" },
            { key: "Backspace", label: "⌫", cls: "key-action key-delete" }
        ],
        [
            { key: "ModeABC", label: "ABC", cls: "key-action key-mode" },
            { key: "-", cls: "key-symbol" },
            { key: " ", label: "space", cls: "key-space" },
            { key: ".", cls: "key-symbol" },
            { key: "Enter", label: "return", cls: "key-enter" }
        ]
    ];

    function getCurrentRows() {
        if (layoutMode === "123") return numLayout;
        if (layoutMode === "sym") return symLayout;
        return abcLayout;
    }

    function createKey(definition) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "keyboard-key " + (definition.cls || "");
        button.dataset.key = definition.key;

        let displayLabel = definition.label || definition.key;

        if (layoutMode === "abc" && /^[a-z]$/i.test(definition.key)) {
            displayLabel = (shiftOn || capsLock) ? definition.key.toUpperCase() : definition.key.toLowerCase();
        }

        button.innerHTML = `<span class="key-main">${escapeHtml(displayLabel)}</span>`;

        if (definition.key === "Shift" && (shiftOn || capsLock)) {
            button.classList.add("key-active");
        }

        button.addEventListener("pointerdown", function (event) {
            event.preventDefault();
        });

        button.addEventListener("click", function () {
            handleKey(definition.key);
        });

        return button;
    }

    function buildKeyboard() {
        main.innerHTML = "";
        const rows = getCurrentRows();

        rows.forEach(function (row) {
            const rowElement = document.createElement("div");
            rowElement.className = "keyboard-row";

            row.forEach(function (definition) {
                rowElement.appendChild(createKey(definition));
            });

            main.appendChild(rowElement);
        });
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function showKeyboard(input) {
        if (!input) return;
        activeInput = input;
        lastInput = input;

        keyboard.classList.add("keyboard-visible");
        keyboard.setAttribute("aria-hidden", "false");
        toggleButton.classList.add("keyboard-open");
    }

    function hideKeyboard() {
        keyboard.classList.remove("keyboard-visible");
        keyboard.setAttribute("aria-hidden", "true");
        toggleButton.classList.remove("keyboard-open");
        activeInput = null;
    }

    function insertText(text) {
        if (!activeInput || !document.contains(activeInput)) return;
        const input = activeInput;
        const start = typeof input.selectionStart === "number" ? input.selectionStart : input.value.length;
        const end = typeof input.selectionEnd === "number" ? input.selectionEnd : input.value.length;

        input.focus();
        input.value = input.value.slice(0, start) + text + input.value.slice(end);
        const cursor = start + text.length;

        try {
            input.setSelectionRange(cursor, cursor);
        } catch (_) {}

        input.dispatchEvent(new Event("input", { bubbles: true }));
    }

    function deleteCharacter() {
        if (!activeInput || !document.contains(activeInput)) return;
        const input = activeInput;
        const start = input.selectionStart ?? input.value.length;
        const end = input.selectionEnd ?? input.value.length;

        input.focus();
        if (start !== end) {
            input.value = input.value.slice(0, start) + input.value.slice(end);
            input.setSelectionRange(start, start);
        } else if (start > 0) {
            input.value = input.value.slice(0, start - 1) + input.value.slice(end);
            input.setSelectionRange(start - 1, start - 1);
        }

        input.dispatchEvent(new Event("input", { bubbles: true }));
    }

    function handleKey(key) {
        if (key === "Mode123") {
            layoutMode = "123";
            buildKeyboard();
            return;
        }

        if (key === "ModeABC") {
            layoutMode = "abc";
            buildKeyboard();
            return;
        }

        if (key === "ModeSym") {
            layoutMode = "sym";
            buildKeyboard();
            return;
        }

        if (key === "Shift") {
            if (!shiftOn && !capsLock) {
                shiftOn = true;
            } else if (shiftOn && !capsLock) {
                shiftOn = false;
                capsLock = true;
            } else {
                shiftOn = false;
                capsLock = false;
            }
            buildKeyboard();
            return;
        }

        if (key === "Backspace") {
            deleteCharacter();
            return;
        }

        if (key === "Enter") {
            if (activeInput) {
                activeInput.dispatchEvent(
                    new KeyboardEvent("keydown", {
                        key: "Enter",
                        code: "Enter",
                        bubbles: true
                    })
                );
            }
            hideKeyboard();
            return;
        }

        if (key === " ") {
            insertText(" ");
            return;
        }

        // Letter or Symbol Key
        let character = key;
        if (layoutMode === "abc" && /^[a-z]$/i.test(key)) {
            character = (shiftOn || capsLock) ? key.toUpperCase() : key.toLowerCase();
        }

        insertText(character);
        checkExitPassword(character);

        // Reset single-tap shift
        if (shiftOn && !capsLock) {
            shiftOn = false;
            buildKeyboard();
        }
    }

    // Focus listener
    document.addEventListener("focusin", function (event) {
        const element = event.target;
        if (element.tagName === "INPUT" || element.tagName === "TEXTAREA") {
            showKeyboard(element);
        }
    });

    closeButton.addEventListener("click", hideKeyboard);

    const toggleButton = document.createElement("button");
    toggleButton.id = "keyboardToggle";
    toggleButton.type = "button";
    toggleButton.innerHTML = "⌨";
    toggleButton.title = "Show / Hide keyboard";
    toggleButton.setAttribute("aria-label", "Show or hide keyboard");

    toggleButton.addEventListener("pointerdown", function (event) {
        event.preventDefault();
    });

    toggleButton.addEventListener("click", function () {
        if (keyboard.classList.contains("keyboard-visible")) {
            hideKeyboard();
            return;
        }

        const candidate =
            (activeInput && document.contains(activeInput)) ? activeInput :
            (lastInput && document.contains(lastInput)) ? lastInput :
            document.querySelector("input:not([disabled]), textarea:not([disabled])");

        if (candidate) {
            showKeyboard(candidate);
            candidate.focus();
        }
    });

    document.body.appendChild(toggleButton);

    // Global listener for physical keyboard
    document.addEventListener("keydown", function (event) {
        if (event.key && event.key.length === 1) {
            checkExitPassword(event.key);
        }
    });

    buildKeyboard();
})();
