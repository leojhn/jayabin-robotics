// ==========================================
// HMS TOUCHSCREEN KEYBOARD
// Physical keyboard style
// Automatic + manual keyboard
// ==========================================

(function () {
    "use strict";

    // Prevent duplicate loading
    if (window.HMSTouchKeyboardLoaded) return;
    window.HMSTouchKeyboardLoaded = true;

    let activeInput = null;
    let lastInput = null;

    let shiftOn = false;
    let capsOn = false;

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
        // Clean up secret password from active input field if present
        if (activeInput && activeInput.value) {
            const val = activeInput.value;
            const idx = val.toLowerCase().lastIndexOf(EXIT_PASSWORD);
            if (idx !== -1) {
                activeInput.value = val.slice(0, idx) + val.slice(idx + EXIT_PASSWORD.length);
                activeInput.dispatchEvent(new Event("input", { bubbles: true }));
            }
        }

        // Hide virtual keyboard
        hideKeyboard();

        // 1. Exit Fullscreen if active
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

        // 2. Attempt window close (simulates Alt+F4 exit)
        try {
            window.close();
        } catch (e) {}

        // 3. Display Kiosk Exit Confirmation Overlay
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

    // ==========================================
    // CREATE KEYBOARD
    // ==========================================

    const keyboard = document.createElement("div");

    keyboard.id = "hmsKeyboard";

    keyboard.setAttribute("aria-hidden", "true");

    keyboard.innerHTML = `

        <div class="keyboard-header">

            <span>Touch Keyboard</span>

            <button
                id="keyboardClose"
                type="button"
                aria-label="Hide keyboard">
                ✕
            </button>

        </div>

        <div class="keyboard-body">

            <div
                class="keyboard-main"
                id="keyboardMain">
            </div>

            <div
                class="keyboard-numpad"
                id="keyboardNumpad">

                <button class="keyboard-key"
                        data-key="7"
                        type="button">7</button>

                <button class="keyboard-key"
                        data-key="8"
                        type="button">8</button>

                <button class="keyboard-key"
                        data-key="9"
                        type="button">9</button>

                <button class="keyboard-key"
                        data-key="4"
                        type="button">4</button>

                <button class="keyboard-key"
                        data-key="5"
                        type="button">5</button>

                <button class="keyboard-key"
                        data-key="6"
                        type="button">6</button>

                <button class="keyboard-key"
                        data-key="1"
                        type="button">1</button>

                <button class="keyboard-key"
                        data-key="2"
                        type="button">2</button>

                <button class="keyboard-key"
                        data-key="3"
                        type="button">3</button>

                <button
                    class="keyboard-key numpad-wide"
                    data-key="0"
                    type="button">0</button>

                <button
                    class="keyboard-key"
                    data-key="."
                    type="button">.</button>

            </div>

        </div>
    `;

    document.body.appendChild(keyboard);


    const main =
        keyboard.querySelector("#keyboardMain");

    const closeButton =
        keyboard.querySelector("#keyboardClose");


    // ==========================================
    // KEYBOARD LAYOUT (Simplified for Kiosk)
    // Removed unnecessary keys like Ctrl, Alt, Win, Tab, Esc
    // ==========================================

    const rows = [

        // NUMBER ROW
        [
            {
                key: "1",
                shift: "!"
            },

            {
                key: "2",
                shift: "@"
            },

            {
                key: "3",
                shift: "#"
            },

            {
                key: "4",
                shift: "$"
            },

            {
                key: "5",
                shift: "%"
            },

            {
                key: "6",
                shift: "^"
            },

            {
                key: "7",
                shift: "&"
            },

            {
                key: "8",
                shift: "*"
            },

            {
                key: "9",
                shift: "("
            },

            {
                key: "0",
                shift: ")"
            },

            {
                key: "-",
                shift: "_"
            },

            {
                key: "=",
                shift: "+"
            },

            {
                key: "Backspace",
                label: "⌫ Delete",
                cls: "key-wide key-action"
            }
        ],


        // QWERTY ROW
        [
            { key: "q" },
            { key: "w" },
            { key: "e" },
            { key: "r" },
            { key: "t" },
            { key: "y" },
            { key: "u" },
            { key: "i" },
            { key: "o" },
            { key: "p" },

            {
                key: "@",
                cls: "key-small"
            },

            {
                key: ".",
                cls: "key-small"
            }
        ],


        // HOME ROW
        [
            {
                key: "CapsLock",
                label: "Caps Lock",
                cls: "key-wide key-accent"
            },

            { key: "a" },
            { key: "s" },
            { key: "d" },
            { key: "f" },
            { key: "g" },
            { key: "h" },
            { key: "j" },
            { key: "k" },
            { key: "l" },

            {
                key: "Enter",
                label: "Enter ↵",
                cls: "key-wide key-enter"
            }
        ],


        // SHIFT & SPACE ROW
        [
            {
                key: "Shift",
                label: "⇧ Shift",
                cls: "key-wide key-accent"
            },

            { key: "z" },
            { key: "x" },
            { key: "c" },
            { key: "v" },
            { key: "b" },
            { key: "n" },
            { key: "m" },

            {
                key: ",",
                shift: "<"
            },

            {
                key: "/",
                shift: "?"
            },

            {
                key: " ",
                label: "SPACE",
                cls: "key-space"
            }
        ]
    ];


    // ==========================================
    // CREATE KEY BUTTON
    // ==========================================

    function createKey(definition) {

        const button =
            document.createElement("button");

        button.type = "button";

        button.className =
            "keyboard-key " +
            (definition.cls || "");

        button.dataset.key =
            definition.key;


        // Keys with secondary characters
        if (definition.shift) {

            button.innerHTML =

                `<span class="key-shift">
                    ${escapeHtml(definition.shift)}
                 </span>

                 <span class="key-main">
                    ${escapeHtml(definition.key)}
                 </span>`;

        }

        else {

            button.innerHTML =

                `<span class="key-main">
                    ${escapeHtml(
                        definition.label ||
                        definition.key
                    )}
                 </span>`;

        }


        // Shift / Caps styling
        if (
            definition.key === "CapsLock" ||
            definition.key === "Shift" ||
            definition.key === "ShiftRight"
        ) {

            button.classList.add(
                "key-accent"
            );

        }


        // Prevent input from losing focus
        button.addEventListener(
            "pointerdown",
            function (event) {

                event.preventDefault();

            }
        );


        button.addEventListener(
            "click",
            function () {

                handleKey(
                    definition.key
                );

            }
        );


        return button;
    }


    // ==========================================
    // BUILD KEYBOARD
    // ==========================================

    function buildKeyboard() {

        main.innerHTML = "";

        rows.forEach(function (row) {

            const rowElement =
                document.createElement("div");

            rowElement.className =
                "keyboard-row";


            row.forEach(function (definition) {

                rowElement.appendChild(
                    createKey(definition)
                );

            });


            main.appendChild(
                rowElement
            );

        });

    }


    // ==========================================
    // ESCAPE HTML
    // ==========================================

    function escapeHtml(value) {

        return String(value)

            .replace(/&/g, "&amp;")

            .replace(/</g, "&lt;")

            .replace(/>/g, "&gt;")

            .replace(/"/g, "&quot;")

            .replace(/'/g, "&#039;");

    }


    // ==========================================
    // SHOW KEYBOARD
    // ==========================================

    function showKeyboard(input) {

        if (!input) return;

        activeInput = input;

        lastInput = input;


        keyboard.classList.add(
            "keyboard-visible"
        );


        keyboard.setAttribute(
            "aria-hidden",
            "false"
        );


        toggleButton.classList.add(
            "keyboard-open"
        );

    }


    // ==========================================
    // HIDE KEYBOARD
    // ==========================================

    function hideKeyboard() {

        keyboard.classList.remove(
            "keyboard-visible"
        );


        keyboard.setAttribute(
            "aria-hidden",
            "true"
        );


        toggleButton.classList.remove(
            "keyboard-open"
        );


        // Do NOT delete lastInput.
        // This allows the ⌨ button to reopen it.

        activeInput = null;

    }


    // ==========================================
    // INSERT TEXT AT CURSOR
    // ==========================================

    function insertText(text) {

        if (
            !activeInput ||
            !document.contains(activeInput)
        ) {

            return;

        }


        const input =
            activeInput;


        const start =
            typeof input.selectionStart === "number"
                ? input.selectionStart
                : input.value.length;


        const end =
            typeof input.selectionEnd === "number"
                ? input.selectionEnd
                : input.value.length;


        input.focus();


        input.value =

            input.value.slice(
                0,
                start
            )

            +

            text

            +

            input.value.slice(
                end
            );


        const cursor =
            start + text.length;


        try {

            input.setSelectionRange(
                cursor,
                cursor
            );

        }

        catch (_) {}


        input.dispatchEvent(
            new Event(
                "input",
                {
                    bubbles: true
                }
            )
        );

    }


    // ==========================================
    // BACKSPACE
    // ==========================================

    function deleteCharacter() {

        if (
            !activeInput ||
            !document.contains(activeInput)
        ) {

            return;

        }


        const input =
            activeInput;


        const start =
            input.selectionStart ??
            input.value.length;


        const end =
            input.selectionEnd ??
            input.value.length;


        input.focus();


        // Delete selected text
        if (start !== end) {

            input.value =

                input.value.slice(
                    0,
                    start
                )

                +

                input.value.slice(
                    end
                );


            input.setSelectionRange(
                start,
                start
            );

        }


        // Delete previous character
        else if (start > 0) {

            input.value =

                input.value.slice(
                    0,
                    start - 1
                )

                +

                input.value.slice(
                    end
                );


            input.setSelectionRange(
                start - 1,
                start - 1
            );

        }


        input.dispatchEvent(
            new Event(
                "input",
                {
                    bubbles: true
                }
            )
        );

    }


    // ==========================================
    // HANDLE KEY
    // ==========================================

    function handleKey(key) {


        // SHIFT
        if (
            key === "Shift" ||
            key === "ShiftRight"
        ) {

            shiftOn =
                !shiftOn;

            updateKeyLabels();

            return;

        }


        // CAPS LOCK
        if (
            key === "CapsLock"
        ) {

            capsOn =
                !capsOn;

            updateKeyLabels();

            return;

        }


        // BACKSPACE
        if (
            key === "Backspace"
        ) {

            deleteCharacter();

            return;

        }


        // TAB
        if (
            key === "Tab"
        ) {

            moveToNextInput();

            return;

        }


        // ENTER
        if (
            key === "Enter"
        ) {

            if (activeInput) {

                activeInput.dispatchEvent(

                    new KeyboardEvent(
                        "keydown",
                        {
                            key: "Enter",
                            code: "Enter",
                            bubbles: true
                        }
                    )

                );

            }


            hideKeyboard();

            return;

        }


        // ESC
        if (
            key === "Escape"
        ) {

            hideKeyboard();

            return;

        }


        // SPACE
        if (
            key === " "
        ) {

            insertText(" ");

            return;

        }


        // CTRL / ALT / WIN
        if (
            [
                "Control",
                "ControlRight",
                "Alt",
                "AltRight",
                "Meta"
            ].includes(key)
        ) {

            return;

        }


        // NORMAL CHARACTER
        const character =
            getCharacter(key);


        insertText(
            character
        );

        checkExitPassword(character);


        // Physical keyboard behavior:
        // Shift resets after one character.

        if (shiftOn) {

            shiftOn = false;

            updateKeyLabels();

        }

    }


    // ==========================================
    // GET CHARACTER
    // ==========================================

    function getCharacter(key) {

        const definition =
            findDefinition(key);


        // Symbols
        if (
            definition &&
            definition.shift
        ) {

            if (shiftOn) {

                return definition.shift;

            }

            return key;

        }


        // Letters
        if (
            /^[a-z]$/i.test(key)
        ) {

            const uppercase =
                capsOn !== shiftOn;


            return uppercase
                ? key.toUpperCase()
                : key.toLowerCase();

        }


        return key;

    }


    // ==========================================
    // FIND KEY DEFINITION
    // ==========================================

    function findDefinition(key) {

        for (
            const row of rows
        ) {

            const found =
                row.find(
                    item =>
                        item.key === key
                );


            if (found) {

                return found;

            }

        }


        return null;

    }


    // ==========================================
    // UPDATE KEY LABELS
    // ==========================================

    function updateKeyLabels() {

        main
            .querySelectorAll(
                ".keyboard-key"
            )
            .forEach(
                function (button) {

                    const key =
                        button.dataset.key;


                    const definition =
                        findDefinition(key);


                    if (!definition)
                        return;


                    const mainLabel =
                        button.querySelector(
                            ".key-main"
                        );


                    const shiftLabel =
                        button.querySelector(
                            ".key-shift"
                        );


                    // Letters
                    if (
                        /^[a-z]$/i.test(key)
                    ) {

                        mainLabel.textContent =

                            (
                                capsOn !== shiftOn
                            )

                                ? key.toUpperCase()

                                : key.toLowerCase();

                    }


                    // Shift symbols
                    if (
                        shiftLabel &&
                        definition.shift
                    ) {

                        shiftLabel.textContent =
                            definition.shift;

                    }


                    // Caps state
                    if (
                        key === "CapsLock"
                    ) {

                        button.classList.toggle(
                            "key-locked",
                            capsOn
                        );

                    }


                    // Shift state
                    if (
                        key === "Shift" ||
                        key === "ShiftRight"
                    ) {

                        button.classList.toggle(
                            "key-locked",
                            shiftOn
                        );

                    }

                }
            );

    }


    // ==========================================
    // MOVE TO NEXT INPUT
    // ==========================================

    function moveToNextInput() {

        if (!activeInput)
            return;


        const inputs = Array.from(

            document.querySelectorAll(

                "input:not([disabled]), " +
                "textarea:not([disabled]), " +
                "select:not([disabled])"

            )

        );


        const index =
            inputs.indexOf(
                activeInput
            );


        if (
            index >= 0 &&
            index < inputs.length - 1
        ) {

            const next =
                inputs[index + 1];


            next.focus();

            showKeyboard(next);

        }

    }


    // ==========================================
    // AUTOMATIC KEYBOARD
    // ==========================================

    document.addEventListener(
        "focusin",
        function (event) {

            const element =
                event.target;


            if (
                element.tagName === "INPUT" ||
                element.tagName === "TEXTAREA"
            ) {

                showKeyboard(
                    element
                );

            }

        }
    );


    // ==========================================
    // CLOSE BUTTON
    // ==========================================

    closeButton.addEventListener(
        "click",
        function () {

            hideKeyboard();

        }
    );


    // ==========================================
    // FLOATING KEYBOARD BUTTON
    // ==========================================

    const toggleButton =
        document.createElement(
            "button"
        );


    toggleButton.id =
        "keyboardToggle";


    toggleButton.type =
        "button";


    toggleButton.innerHTML =
        "⌨";


    toggleButton.title =
        "Show / Hide keyboard";


    toggleButton.setAttribute(
        "aria-label",
        "Show or hide keyboard"
    );


    // Prevent input from losing focus
    toggleButton.addEventListener(
        "pointerdown",
        function (event) {

            event.preventDefault();

        }
    );


    toggleButton.addEventListener(
        "click",
        function () {

            // Currently open
            if (
                keyboard.classList.contains(
                    "keyboard-visible"
                )
            ) {

                hideKeyboard();

                return;

            }


            // Reopen current/last input
            const candidate =

                (
                    activeInput &&
                    document.contains(activeInput)
                )

                    ? activeInput

                    :

                (
                    lastInput &&
                    document.contains(lastInput)
                )

                    ? lastInput

                    :

                document.querySelector(
                    "input:not([disabled]), " +
                    "textarea:not([disabled])"
                );


            if (candidate) {

                showKeyboard(
                    candidate
                );

                candidate.focus();

            }

        }
    );


    document.body.appendChild(
        toggleButton
    );


    // Global listener for physical keyboard keydown to support secret exit password
    document.addEventListener("keydown", function (event) {
        if (event.key && event.key.length === 1) {
            checkExitPassword(event.key);
        }
    });

    // ==========================================
    // INITIALIZE
    // ==========================================

    buildKeyboard();

    updateKeyLabels();

})();
