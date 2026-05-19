document.addEventListener('DOMContentLoaded', () => {
    const screens = document.querySelectorAll('.screen');
    const homeBtn = document.getElementById('home-btn');
    const backBtn = document.getElementById('back-btn');
    let history = ['screen-welcome'];

    // Navigation Function
    window.showScreen = function(screenId, addToHistory = true) {
        screens.forEach(s => s.classList.remove('active'));
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.add('active');
            if (addToHistory && history[history.length - 1] !== screenId) {
                history.push(screenId);
            }
        }

        // Toggle Nav Buttons visibility
        if (screenId === 'screen-welcome') {
            homeBtn.classList.add('hidden');
            backBtn.classList.add('hidden');
            history = ['screen-welcome'];
        } else {
            homeBtn.classList.remove('hidden');
            backBtn.classList.remove('hidden');
        }

        // Reset some specific screen states
        if (screenId === 'screen-emergency') {
            document.getElementById('emergency-status').classList.add('hidden');
        }
        if (screenId === 'screen-checkin-signature') {
            initSignaturePad();
        }
    }

    // Global click listener for data-target attributes
    document.addEventListener('click', (e) => {
        const target = e.target.closest('[data-target]');
        if (target) {
            const screenId = target.getAttribute('data-target');
            showScreen(screenId);
        }
    });

    homeBtn.addEventListener('click', () => showScreen('screen-welcome'));

    backBtn.addEventListener('click', () => {
        if (history.length > 1) {
            history.pop();
            const prevScreen = history[history.length - 1];
            showScreen(prevScreen, false);
        }
    });

    // --- Specific Flow Logics ---

    // Wayfinding Search
    const wayfindingInput = document.getElementById('wayfinding-search');
    const resultsContainer = document.getElementById('search-results');

    const wayfindingData = {
        'Cardiology': 'Cabin C-201',
        'Orthopedics': 'Cabin B-104',
        'Lab': 'Ground Floor',
        'Pharmacy': 'Ground Floor',
        'John Heart': 'Cabin C-201',
        'Sarah Pulse': 'Cabin C-202',
        'Bone Kumar': 'Cabin B-104',
        'Brain Das': 'Cabin A-305',
        'Skin Mary': 'Cabin D-102'
    };

    window.searchWayfinding = (term) => {
        wayfindingInput.value = term;
        performSearch(term);
    };

    wayfindingInput.addEventListener('input', (e) => {
        performSearch(e.target.value);
    });

    function performSearch(term) {
        if (!term) {
            resultsContainer.innerHTML = '';
            return;
        }
        const filtered = Object.keys(wayfindingData).filter(k =>
            k.toLowerCase().includes(term.toLowerCase())
        );

        resultsContainer.innerHTML = filtered.map(k => `
            <div class="result-card">
                <span><strong>${k}</strong></span>
                <span style="color: var(--primary-color)">${wayfindingData[k]}</span>
            </div>
        `).join('');
    }

    // Appointment Scheduling
    const doctors = {
        'Cardiology': ['Dr. John Heart', 'Dr. Sarah Pulse'],
        'Orthopedics': ['Dr. Bone Kumar'],
        'Neurology': ['Dr. Brain Das'],
        'Dermatology': ['Dr. Skin Mary']
    };

    let selectedDoctor = '';

    window.selectDept = (dept) => {
        const doctorList = document.getElementById('doctor-list');
        document.getElementById('dept-title').innerText = `Select Doctor - ${dept}`;

        doctorList.innerHTML = doctors[dept].map(doc => `
            <div class="doctor-item">
                <span style="font-size: 1.3rem; font-weight: 600;">${doc}</span>
                <button class="btn-primary" onclick="selectDoctor('${doc}')">Select</button>
            </div>
        `).join('');

        showScreen('screen-scheduling-doctor');
    };

    window.selectDoctor = (doc) => {
        selectedDoctor = doc;
        document.getElementById('confirm-doctor-name').innerText = doc;
        showScreen('screen-scheduling-calendar');
    };

    // Emergency Request
    window.sendHelpRequest = (type) => {
        const alertBox = document.getElementById('emergency-status');
        alertBox.innerText = `Help request for ${type} sent successfully.`;
        alertBox.classList.remove('hidden');

        // Auto-hide after 3 seconds
        setTimeout(() => {
            alertBox.classList.add('hidden');
        }, 3000);
    };

    // Signature Pad logic
    let canvas, ctx, drawing = false;

    function initSignaturePad() {
        canvas = document.getElementById('signature-pad');
        if (!canvas) return;
        ctx = canvas.getContext('2d');

        // Match canvas size to display size
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;

        ctx.strokeStyle = '#2c3e50';
        ctx.lineWidth = 3;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';

        const getPos = (e) => {
            const rect = canvas.getBoundingClientRect();
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            return {
                x: clientX - rect.left,
                y: clientY - rect.top
            };
        };

        const start = (e) => {
            drawing = true;
            const pos = getPos(e);
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
            e.preventDefault();
        };

        const move = (e) => {
            if (!drawing) return;
            const pos = getPos(e);
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
            e.preventDefault();
        };

        const stop = () => {
            drawing = false;
        };

        canvas.addEventListener('mousedown', start);
        canvas.addEventListener('mousemove', move);
        canvas.addEventListener('mouseup', stop);
        canvas.addEventListener('touchstart', start);
        canvas.addEventListener('touchmove', move);
        canvas.addEventListener('touchend', stop);
    }

    document.getElementById('clear-signature')?.addEventListener('click', () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });

    // Initialize
    showScreen('screen-welcome');
});

