// ==========================================
// HMS TOUCHSCREEN KEYBOARD
// ==========================================

(function () {

    let activeInput = null;

    const keyboard = document.createElement("div");
    keyboard.id = "hmsKeyboard";

    keyboard.innerHTML = `
        <div class="keyboard-header">
            <span>Keyboard</span>
            <button id="keyboardClose">✕</button>
        </div>

        <div class="keyboard-keys" id="keyboardKeys"></div>
    `;

    document.body.appendChild(keyboard);

    const keys = [
        ["1","2","3","4","5","6","7","8","9","0"],
        ["Q","W","E","R","T","Y","U","I","O","P"],
        ["A","S","D","F","G","H","J","K","L"],
        ["Z","X","C","V","B","N","M"],
        ["SPACE","⌫","ENTER"]
    ];

    const keysContainer =
        document.getElementById("keyboardKeys");

    function createKeyboard() {

        keysContainer.innerHTML = "";

        keys.forEach(row => {

            const rowDiv =
                document.createElement("div");

            rowDiv.className = "keyboard-row";

            row.forEach(key => {

                const button =
                    document.createElement("button");

                button.className = "keyboard-key";

                button.textContent = key;

                if (key === "SPACE") {
                    button.classList.add("space-key");
                }

                if (key === "⌫") {
                    button.classList.add("special-key");
                }

                if (key === "ENTER") {
                    button.classList.add("special-key");
                }

                button.addEventListener("click", function () {

                    if (!activeInput) return;

                    if (key === "⌫") {

                        activeInput.value =
                            activeInput.value.slice(0, -1);

                    }

                    else if (key === "SPACE") {

                        activeInput.value += " ";

                    }

                    else if (key === "ENTER") {

                        activeInput.blur();

                    }

                    else {

                        activeInput.value += key;

                    }

                    activeInput.dispatchEvent(
                        new Event("input", {
                            bubbles: true
                        })
                    );

                });

                rowDiv.appendChild(button);

            });

            keysContainer.appendChild(rowDiv);

        });

    }

    createKeyboard();


    // ==========================================
    // SHOW KEYBOARD
    // ==========================================

    function showKeyboard(input) {

        activeInput = input;

        keyboard.classList.add("keyboard-visible");

    }


    // ==========================================
    // HIDE KEYBOARD
    // ==========================================

    function hideKeyboard() {

        keyboard.classList.remove("keyboard-visible");

        activeInput = null;

    }


    // ==========================================
    // AUTOMATIC INPUT DETECTION
    // ==========================================

    document.addEventListener("focusin", function (event) {

        const element = event.target;

        if (
            element.tagName === "INPUT" ||
            element.tagName === "TEXTAREA"
        ) {

            showKeyboard(element);

        }

    });


    // ==========================================
    // CLOSE BUTTON
    // ==========================================

    document
        .getElementById("keyboardClose")
        .addEventListener("click", function () {

            hideKeyboard();

        });


    // ==========================================
    // OPTIONAL KEYBOARD BUTTON
    // ==========================================

    const toggleButton =
        document.createElement("button");

    toggleButton.id = "keyboardToggle";

    toggleButton.innerHTML = "⌨";

    toggleButton.title = "Show / Hide Keyboard";

    toggleButton.addEventListener("click", function () {

        if (
            keyboard.classList.contains("keyboard-visible")
        ) {

            hideKeyboard();

        } else {

            if (activeInput) {

                showKeyboard(activeInput);

            }

        }

    });

    document.body.appendChild(toggleButton);

})();
