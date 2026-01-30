let currentPlan = null;
let currentMode = 'oneshot';

function goToStep(stepId) {
    document.querySelectorAll('.page-step').forEach(s => s.classList.remove('active'));
    document.getElementById(`step-${stepId}`).classList.add('active');
}

function initMode(mode) {
    currentMode = mode;
    goToStep('input');
}

async function processStep1() {
    const idea = document.getElementById('user-idea').value;
    const segments = document.getElementById('duration-select').value;
    
    // Si One-Shot, on va direct au chargement, sinon au studio
    if (currentMode === 'oneshot') {
        goToStep('loading');
        const plan = await fetchAPI('/api/script', { idea, segments });
        currentPlan = plan;
        startProduction();
    } else {
        const plan = await fetchAPI('/api/script', { idea, segments });
        currentPlan = plan;
        renderScriptEditor();
        goToStep('studio');
    }
}

async function startProduction() {
    // Création de la grille de progression visuelle
    const grid = document.getElementById('segment-progress-grid');
    grid.innerHTML = currentPlan.segments.map(s => `<div id="status-node-${s.segment_id}" class="node-loading">○</div>`).join('');
    
    const result = await fetchAPI('/api/generate', currentPlan);
    document.getElementById('final-video').src = result.video_url;
    goToStep('result');
}

// Helpers pour Fetch
async function fetchAPI(url, data) {
    const r = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    return await r.json();
}