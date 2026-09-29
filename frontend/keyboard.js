// ============================================================
// HMS MINIMAL TOUCHSCREEN KEYBOARD - CURSOR SAFE VERSION
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

    // Saved cursor/selection position.
    // This prevents characters from being inserted backwards
    // when a keyboard button receives focus.
    let savedSelectionStart = 0;
    let savedSelectionEnd = 0;

    const keyboard = document.createElement("div");
    keyboard.id = "hmsKeyboard";
    keyboard.setAttribute("aria-hidden", "true");

    keyboard.innerHTML = `
        <div class="keyboard-header">
            <span>Touch Keyboard</span>
            <button id="keyboardClose" type="button"
                    aria-label="Hide keyboard">✕</button>
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
            {key:"\`", shift:"~"},
            {key:"1", shift:"!"},
            {key:"2", shift:"@"},
            {key:"3", shift:"#"},
            {key:"4", shift:"$"},
            {key:"5", shift:"%"},
            {key:"6", shift:"^"},
            {key:"7", shift:"&"},
            {key:"8", shift:"*"},
            {key:"9", shift:"("},
            {key:"0", shift:")"},
            {key:"-", shift:"_"},
            {key:"=", shift:"+"}
        ],

        [
            {key:"q"},
            {key:"w"},
            {key:"e"},
            {key:"r"},
            {key:"t"},
            {key:"y"},
            {key:"u"},
            {key:"i"},
            {key:"o"},
            {key:"p"},
            {key:"[", shift:"{"},
            {key:"]", shift:"}"}
        ],

        [
            {key:"a"},
            {key:"s"},
            {key:"d"},
            {key:"f"},
            {key:"g"},
            {key:"h"},
            {key:"j"},
            {key:"k"},
            {key:"l"},
            {key:";", shift:":"},
            {key:"'", shift:'"'}
        ],

        [
            {key:"\\", shift:"|"},
            {key:"z"},
            {key:"x"},
            {key:"c"},
            {key:"v"},
            {key:"b"},
            {key:"n"},
            {key:"m"},
            {key:",", shift:"<"},
            {key:".", shift:">"},
            {key:"/", shift:"?"}
        ]
    ];

    // --------------------------------------------------------
    // SAVE CURSOR POSITION
    // --------------------------------------------------------
    function saveSelection() {
        if (!activeInput) return;

        try {
            const start = activeInput.selectionStart;
            const end = activeInput.selectionEnd;

            if (typeof start === "number") {
                savedSelectionStart = start;

                savedSelectionEnd =
                    typeof end === "number"
                        ? end
                        : start;
            } else {
                savedSelectionStart =
                    activeInput.value.length;

                savedSelectionEnd =
                    activeInput.value.length;
            }

        } catch (_) {

            savedSelectionStart =
                activeInput.value.length;

            savedSelectionEnd =
                activeInput.value.length;
        }
    }

    // --------------------------------------------------------
    // RESTORE CURSOR POSITION
    // --------------------------------------------------------
    function restoreSelection() {
        if (!activeInput) return;

        const length = activeInput.value.length;

        savedSelectionStart = Math.max(
            0,
            Math.min(savedSelectionStart, length)
        );

        savedSelectionEnd = Math.max(
            savedSelectionStart,
            Math.min(savedSelectionEnd, length)
        );

        try {
            activeInput.focus({
                preventScroll: true
            });
        } catch (_) {
            try {
                activeInput.focus();
            } catch (_) {}
        }

        try {
            activeInput.setSelectionRange(
                savedSelectionStart,
                savedSelectionEnd
            );
        } catch (_) {}
    }

    // --------------------------------------------------------
    // GET CURRENT CHARACTER
    // --------------------------------------------------------
    function currentChar(item) {

        let value =
            shiftOn && item.shift
                ? item.shift
                : item.key;

        if (/^[a-z]$/.test(value)) {

            value =
                (capsOn !== shiftOn)
                    ? value.toUpperCase()
                    : value.toLowerCase();
        }

        return value;
    }

    // --------------------------------------------------------
    // INSERT TEXT
    // --------------------------------------------------------
    function insertText(text) {

        if (!activeInput) return;

        // Restore the position before inserting.
        restoreSelection();

        const start = savedSelectionStart;
        const end = savedSelectionEnd;

        const value = activeInput.value;

        activeInput.value =
            value.slice(0, start) +
            text +
            value.slice(end);

        // Move cursor AFTER inserted text.
        const pos = start + text.length;

        savedSelectionStart = pos;
        savedSelectionEnd = pos;

        try {
            activeInput.setSelectionRange(
                pos,
                pos
            );
        } catch (_) {}

        activeInput.dispatchEvent(
            new Event("input", {
                bubbles: true
            })
        );

        activeInput.dispatchEvent(
            new Event("change", {
                bubbles: true
            })
        );
    }

    // --------------------------------------------------------
    // BACKSPACE
    // --------------------------------------------------------
    function backspace() {

        if (!activeInput) return;

        restoreSelection();

        let start = savedSelectionStart;
        let end = savedSelectionEnd;

        const value = activeInput.value;

        // Delete selected text.
        if (start !== end) {

            activeInput.value =
                value.slice(0, start) +
                value.slice(end);

            savedSelectionEnd = start;

        }

        // Delete previous character.
        else if (start > 0) {

            activeInput.value =
                value.slice(0, start - 1) +
                value.slice(start);

            start--;

            savedSelectionStart = start;
            savedSelectionEnd = start;
        }

        try {
            activeInput.setSelectionRange(
                savedSelectionStart,
                savedSelectionEnd
            );
        } catch (_) {}

        activeInput.dispatchEvent(
            new Event("input", {
                bubbles: true
            })
        );

        activeInput.dispatchEvent(
            new Event("change", {
                bubbles: true
            })
        );
    }

    // --------------------------------------------------------
    // ENTER
    // --------------------------------------------------------
    function pressEnter() {

        if (!activeInput) return;

        restoreSelection();

        activeInput.dispatchEvent(
            new KeyboardEvent("keydown", {
                key: "Enter",
                code: "Enter",
                keyCode: 13,
                which: 13,
                bubbles: true
            })
        );
    }

    // --------------------------------------------------------
    // RENDER KEYBOARD
    // --------------------------------------------------------
    function render() {

        main.innerHTML = "";

        rows.forEach((row) => {

            const rowDiv =
                document.createElement("div");

            rowDiv.className =
                "keyboard-row";

            row.forEach((item) => {

                const btn =
                    document.createElement("button");

                btn.type = "button";

                btn.className =
                    "keyboard-key";

                btn.innerHTML =
                    item.shift
                        ? `<span class="key-shift">${item.shift}</span>
                           <span class="key-main">${item.key}</span>`
                        : `<span class="key-main">${item.key}</span>`;

                // Prevent keyboard button from stealing
                // the input cursor.
                btn.addEventListener(
                    "mousedown",
                    (event) => {
                        event.preventDefault();
                    }
                );

                btn.addEventListener(
                    "touchstart",
                    (event) => {
                        event.preventDefault();
                    },
                    { passive: false }
                );

                btn.addEventListener(
                    "click",
                    (event) => {

                        event.preventDefault();

                        insertText(
                            currentChar(item)
                        );

                        if (shiftOn) {

                            shiftOn = false;

                            render();
                        }
                    }
                );

                rowDiv.appendChild(btn);
            });

            main.appendChild(rowDiv);
        });

        // ----------------------------------------------------
        // CONTROL ROW
        // ----------------------------------------------------

        const controls =
            document.createElement("div");

        controls.className =
            "keyboard-row minimal-controls";

        // ----------------------------------------------------
        // SHIFT
        // ----------------------------------------------------

        const shift =
            document.createElement("button");

        shift.type = "button";

        shift.className =
            "keyboard-key key-wide";

        shift.textContent =
            shiftOn
                ? "SHIFT ✓"
                : "SHIFT";

        shift.addEventListener(
            "mousedown",
            (event) => {
                event.preventDefault();
            }
        );

        shift.addEventListener(
            "touchstart",
            (event) => {
                event.preventDefault();
            },
            { passive: false }
        );

        shift.addEventListener(
            "click",
            (event) => {

                event.preventDefault();

                shiftOn = !shiftOn;

                render();
            }
        );

        controls.appendChild(shift);

        // ----------------------------------------------------
        // CAPS LOCK
        // ----------------------------------------------------

        const caps =
            document.createElement("button");

        caps.type = "button";

        caps.className =
            "keyboard-key key-wide";

        caps.textContent =
            capsOn
                ? "CAPS ✓"
                : "CAPS";

        caps.addEventListener(
            "mousedown",
            (event) => {
                event.preventDefault();
            }
        );

        caps.addEventListener(
            "touchstart",
            (event) => {
                event.preventDefault();
            },
            { passive: false }
        );

        caps.addEventListener(
            "click",
            (event) => {

                event.preventDefault();

                capsOn = !capsOn;

                render();
            }
        );

        controls.appendChild(caps);

        // ----------------------------------------------------
        // SPACE
        // ----------------------------------------------------

        const space =
            document.createElement("button");

        space.type = "button";

        space.className =
            "keyboard-key key-space";

        space.textContent =
            "SPACE";

        space.addEventListener(
            "mousedown",
            (event) => {
                event.preventDefault();
            }
        );

        space.addEventListener(
            "touchstart",
            (event) => {
                event.preventDefault();
            },
            { passive: false }
        );

        space.addEventListener(
            "click",
            (event) => {

                event.preventDefault();

                insertText(" ");
            }
        );

        controls.appendChild(space);

        // ----------------------------------------------------
        // BACKSPACE
        // ----------------------------------------------------

        const back =
            document.createElement("button");

        back.type = "button";

        back.className =
            "keyboard-key key-wide";

        back.textContent =
            "⌫";

        back.addEventListener(
            "mousedown",
            (event) => {
                event.preventDefault();
            }
        );

        back.addEventListener(
            "touchstart",
            (event) => {
                event.preventDefault();
            },
            { passive: false }
        );

        back.addEventListener(
            "click",
            (event) => {

                event.preventDefault();

                backspace();
            }
        );

        controls.appendChild(back);

        // ----------------------------------------------------
        // ENTER
        // ----------------------------------------------------

        const enter =
            document.createElement("button");

        enter.type = "button";

        enter.className =
            "keyboard-key key-wide";

        enter.textContent =
            "ENTER";

        enter.addEventListener(
            "mousedown",
            (event) => {
                event.preventDefault();
            }
        );

        enter.addEventListener(
            "touchstart",
            (event) => {
                event.preventDefault();
            },
            { passive: false }
        );

        enter.addEventListener(
            "click",
            (event) => {

                event.preventDefault();

                pressEnter();
            }
        );

        controls.appendChild(enter);

        main.appendChild(controls);
    }

    // --------------------------------------------------------
    // SHOW KEYBOARD
    // --------------------------------------------------------
    function showKeyboard(input) {

        activeInput = input;

        // Force normal left-to-right typing.
        try {

            input.style.direction = "ltr";

            input.style.textAlign = "left";

            input.setAttribute(
                "dir",
                "ltr"
            );

        } catch (_) {}

        saveSelection();

        keyboard.classList.add(
            "keyboard-visible"
        );

        keyboard.setAttribute(
            "aria-hidden",
            "false"
        );
    }

    // --------------------------------------------------------
    // HIDE KEYBOARD
    // --------------------------------------------------------
    function hideKeyboard() {

        keyboard.classList.remove(
            "keyboard-visible"
        );

        keyboard.setAttribute(
            "aria-hidden",
            "true"
        );

        activeInput = null;

        savedSelectionStart = 0;
        savedSelectionEnd = 0;
    }

    // Initial keyboard rendering.
    render();

    // --------------------------------------------------------
    // INPUT FOCUS
    // --------------------------------------------------------

    document.addEventListener(
        "focusin",
        (event) => {

            const el =
                event.target;

            if (
                el &&
                (
                    el.tagName === "INPUT" ||
                    el.tagName === "TEXTAREA"
                )
            ) {

                // Prevent Chromium/Squeekboard.
                try {

                    el.setAttribute(
                        "inputmode",
                        "none"
                    );

                    // Force LTR.
                    el.setAttribute(
                        "dir",
                        "ltr"
                    );

                    el.style.direction =
                        "ltr";

                    el.style.textAlign =
                        "left";

                } catch (_) {}

                activeInput = el;

                saveSelection();

                showKeyboard(el);
            }
        }
    );

    // --------------------------------------------------------
    // TRACK CURSOR
    // --------------------------------------------------------

    document.addEventListener(
        "selectionchange",
        () => {

            if (!activeInput) return;

            if (
                document.activeElement ===
                activeInput
            ) {
                saveSelection();
            }
        }
    );

    // --------------------------------------------------------
    // CLOSE BUTTON
    // --------------------------------------------------------

    closeButton.addEventListener(
        "mousedown",
        (event) => {
            event.preventDefault();
        }
    );

    closeButton.addEventListener(
        "click",
        (event) => {

            event.preventDefault();

            hideKeyboard();
        }
    );

    // --------------------------------------------------------
    // KEYBOARD TOGGLE
    // --------------------------------------------------------

    const toggle =
        document.createElement("button");

    toggle.id =
        "keyboardToggle";

    toggle.type =
        "button";

    toggle.innerHTML =
        "⌨";

    toggle.title =
        "Show / Hide Touch Keyboard";

    toggle.addEventListener(
        "mousedown",
        (event) => {
            event.preventDefault();
        }
    );

    toggle.addEventListener(
        "click",
        (event) => {

            event.preventDefault();

            if (
                keyboard.classList.contains(
                    "keyboard-visible"
                )
            ) {

                hideKeyboard();

            } else if (activeInput) {

                showKeyboard(activeInput);
            }
        }
    );

    document.body.appendChild(toggle);

})();
