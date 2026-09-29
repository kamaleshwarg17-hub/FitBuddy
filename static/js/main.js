// FitBuddy Client Enhancements

document.addEventListener('DOMContentLoaded', () => {
    initPresetFillers();
    initFormLoaders();
    initCopyActions();
    initAdminSearch();
});

// Quick fill realistic demo profiles with 1 click
function initPresetFillers() {
    const presets = {
        muscle: {
            username: 'Alex Miller',
            user_id: 'FIT-' + Math.floor(1000 + Math.random() * 9000),
            age: 26,
            weight: 78.5,
            goal: 'Muscle Gain & Hypertrophy',
            intensity: 'High'
        },
        fatloss: {
            username: 'Sarah Chen',
            user_id: 'FIT-' + Math.floor(1000 + Math.random() * 9000),
            age: 31,
            weight: 68.0,
            goal: 'Fat Loss & Conditioning',
            intensity: 'Medium'
        },
        wellness: {
            username: 'Jordan Taylor',
            user_id: 'FIT-' + Math.floor(1000 + Math.random() * 9000),
            age: 42,
            weight: 72.0,
            goal: 'Mobility & General Fitness',
            intensity: 'Low'
        }
    };

    document.querySelectorAll('.preset-chip').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const type = btn.getAttribute('data-preset');
            const data = presets[type];
            if (!data) return;

            const nameInput = document.getElementById('username');
            const idInput = document.getElementById('user_id');
            const ageInput = document.getElementById('age');
            const weightInput = document.getElementById('weight');
            const goalInput = document.getElementById('goal');

            if (nameInput) nameInput.value = data.username;
            if (idInput) idInput.value = data.user_id;
            if (ageInput) ageInput.value = data.age;
            if (weightInput) weightInput.value = data.weight;
            if (goalInput) goalInput.value = data.goal;

            const radio = document.querySelector(`input[name="intensity"][value="${data.intensity}"]`);
            if (radio) radio.checked = true;

            btn.style.transform = 'scale(0.95)';
            setTimeout(() => { btn.style.transform = ''; }, 150);
        });
    });

    // Auto generate user ID button if exists
    const genIdBtn = document.getElementById('btn-gen-id');
    if (genIdBtn) {
        genIdBtn.addEventListener('click', () => {
            const idInput = document.getElementById('user_id');
            if (idInput) {
                idInput.value = 'FIT-' + Math.floor(1000 + Math.random() * 9000);
            }
        });
    }
}

// Show loading animation when submitting form to AI
function initFormLoaders() {
    const workoutForm = document.getElementById('workout-plan-form');
    const feedbackForm = document.getElementById('feedback-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-status-text');

    if (workoutForm && loadingOverlay) {
        workoutForm.addEventListener('submit', () => {
            if (loadingText) {
                loadingText.innerText = 'Gemini 3.8 Flash is analyzing your profile and generating your 7-Day Blueprint...';
            }
            loadingOverlay.style.display = 'flex';
        });
    }

    if (feedbackForm && loadingOverlay) {
        feedbackForm.addEventListener('submit', () => {
            if (loadingText) {
                loadingText.innerText = 'Gemini 3.8 Flash is revising your workout schedule with your feedback...';
            }
            loadingOverlay.style.display = 'flex';
        });
    }
}

// Clipboard copying for workout plan
function initCopyActions() {
    const copyBtn = document.getElementById('btn-copy-plan');
    const planBlock = document.getElementById('plan-content-raw');

    if (copyBtn && planBlock) {
        copyBtn.addEventListener('click', () => {
            const text = planBlock.innerText;
            navigator.clipboard.writeText(text).then(() => {
                const originalHtml = copyBtn.innerHTML;
                copyBtn.innerHTML = '✓ Copied to Clipboard!';
                copyBtn.classList.add('btn-accent');
                setTimeout(() => {
                    copyBtn.innerHTML = originalHtml;
                    copyBtn.classList.remove('btn-accent');
                }, 2000);
            }).catch(err => {
                console.error('Clipboard copy failed:', err);
            });
        });
    }
}

// Live search in admin dashboard
function initAdminSearch() {
    const searchInput = document.getElementById('admin-search-input');
    const goalFilter = document.getElementById('admin-goal-filter');
    const tableRows = document.querySelectorAll('.user-table-row');

    if (!searchInput || !tableRows.length) return;

    function applyFilter() {
        const query = searchInput.value.toLowerCase().trim();
        const selectedGoal = goalFilter ? goalFilter.value.toLowerCase().trim() : '';

        tableRows.forEach(row => {
            const text = row.innerText.toLowerCase();
            const goal = (row.getAttribute('data-goal') || '').toLowerCase();

            const matchesQuery = !query || text.includes(query);
            const matchesGoal = !selectedGoal || goal.includes(selectedGoal);

            if (matchesQuery && matchesGoal) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    searchInput.addEventListener('input', applyFilter);
    if (goalFilter) {
        goalFilter.addEventListener('change', applyFilter);
    }
}
