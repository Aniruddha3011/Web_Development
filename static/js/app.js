// Main page JavaScript - handles comment input and analysis

const API_BASE = ''; // Use relative paths for Vercel stability

document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 App.js Loaded Successfully!");

    // --- DOM Elements ---
    const elements = {
        analyzeBtn: document.getElementById('analyzeBtn'),
        analyzeUrlBtn: document.getElementById('analyzeUrlBtn'),
        demoBtn: document.getElementById('demoBtn'),
        uploadBtn: document.getElementById('uploadBtn'),
        csvFile: document.getElementById('csvFile'),
        commentsTextarea: document.getElementById('comments'),
        titleInput: document.getElementById('title'),
        urlInput: document.getElementById('urlInput'),
        loading: document.getElementById('loading'),
        errorDiv: document.getElementById('error'),
        singleModeBtn: document.getElementById('singleModeBtn'),
        creatorModeBtn: document.getElementById('creatorModeBtn'),
        singleModeSection: document.getElementById('singleModeSection'),
        creatorModeSection: document.getElementById('creatorModeSection'),
        addUrlBtn: document.getElementById('addUrlBtn'),
        addManualBtn: document.getElementById('analyzeManualBtn') || document.getElementById('addManualBtn'), // Handle possible ID mismatch
        analyzeCreatorBtn: document.getElementById('analyzeCreatorBtn'),
        creatorName: document.getElementById('creatorName'),
        urlList: document.getElementById('urlList')
    };

    // Verify critical elements
    for (const [key, el] of Object.entries(elements)) {
        if (!el && key !== 'addManualBtn') { // Optional buttons
            console.warn(`Element not found: ${key}`);
        }
    }

    // --- Mode Switching ---
    if (elements.singleModeBtn && elements.creatorModeBtn) {
        elements.singleModeBtn.addEventListener('click', () => {
            elements.singleModeSection.style.display = 'block';
            // Assuming singleModeSection is inside a card, we might need to show parent
            // But based on HTML, the structure is simpler now.
            // If checking parent is needed: elements.singleModeSection.parentElement.style.display = 'block';
            elements.creatorModeSection.style.display = 'none';

            elements.singleModeBtn.classList.add('btn-primary');
            elements.singleModeBtn.classList.remove('btn-secondary');
            elements.creatorModeBtn.classList.add('btn-secondary');
            elements.creatorModeBtn.classList.remove('btn-primary');
        });

        elements.creatorModeBtn.addEventListener('click', () => {
            elements.singleModeSection.style.display = 'none';
            elements.creatorModeSection.style.display = 'block';

            elements.creatorModeBtn.classList.add('btn-primary');
            elements.creatorModeBtn.classList.remove('btn-secondary');
            elements.singleModeBtn.classList.add('btn-secondary');
            elements.singleModeBtn.classList.remove('btn-primary');
        });
    }

    // --- CREATOR MODE HANDLERS ---

    // 1. Add URL Button
    if (elements.addUrlBtn) {
        elements.addUrlBtn.addEventListener('click', () => {
            const div = document.createElement('div');
            div.className = 'url-input-group';
            div.innerHTML = `
                <input type="text" class="creator-url-input" placeholder="Paste another URL..." />
                <button class="btn-remove" onclick="this.parentElement.remove()" style="margin-left:5px;">×</button>
            `;
            elements.urlList.appendChild(div);
        });
    }

    // 2. Add Manual Button
    if (elements.addManualBtn) {
        elements.addManualBtn.addEventListener('click', () => {
            const div = document.createElement('div');
            div.className = 'manual-input-group';
            div.style.marginTop = '1rem';
            div.style.padding = '1rem';
            div.style.border = '1px dashed var(--border-color)';
            div.style.borderRadius = '0.5rem';
            div.innerHTML = `
                 <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                     <select class="manual-platform-select" style="padding:0.3rem;">
                         <option value="instagram">Instagram</option>
                         <option value="tiktok">TikTok</option>
                         <option value="twitter">Twitter/X</option>
                         <option value="other">Other</option>
                     </select>
                     <button class="btn-remove" onclick="this.parentElement.parentElement.remove()" style="cursor:pointer; color:red;">Remove</button>
                 </div>
                 <textarea class="manual-text-input" rows="3" placeholder="Paste comments here..." style="width:100%;"></textarea>
             `;
            elements.urlList.appendChild(div);
        });
    }

    // 3. Analyze Creator Button
    if (elements.analyzeCreatorBtn) {
        elements.analyzeCreatorBtn.addEventListener('click', async () => {
            console.log("Clicked Analyze Creator");
            const name = elements.creatorName.value.trim();

            // Gather URLs
            const urlInputs = document.querySelectorAll('.creator-url-input');
            const urls = Array.from(urlInputs).map(i => i.value.trim()).filter(u => u);

            // Gather Manual Data
            const manualGroups = document.querySelectorAll('.manual-input-group');
            const manualData = Array.from(manualGroups).map(group => {
                return {
                    platform: group.querySelector('.manual-platform-select').value,
                    text: group.querySelector('.manual-text-input').value,
                    title: 'Manual Entry'
                };
            }).filter(d => d.text.trim());

            if (!name) return showError('Please enter a creator name (@handle).');
            if (urls.length === 0 && manualData.length === 0) return showError('Please add at least one URL or Manual Source.');

            showLoading();
            hideError();

            try {
                const res = await fetch(`${API_BASE}/api/creator/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, urls, manual_data: manualData })
                });

                const data = await res.json();
                if (res.ok) {
                    localStorage.setItem('sessionId', data.session_id);
                    localStorage.setItem('sessionType', 'creator');
                    window.location.href = '/dashboard';
                } else {
                    showError(data.error || 'Creator analysis failed.');
                }
            } catch (err) {
                showError('Network Error: ' + err.message);
            } finally {
                hideLoading();
            }
        });
    }

    // --- SINGLE MODE HANDLERS ---

    // 1. Analyze URL (YouTube/Reddit)
    if (elements.analyzeUrlBtn) {
        elements.analyzeUrlBtn.addEventListener('click', async () => {
            console.log("Clicked Analyze URL");
            const url = elements.urlInput.value.trim();
            if (!url) return showError('Please enter a valid URL.');

            showLoading();
            hideError();

            try {
                const res = await fetch(`${API_BASE}/api/analyze-url`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });

                const data = await res.json();
                if (res.ok) {
                    localStorage.setItem('sessionId', data.session_id);
                    // Reset session type to default/single
                    localStorage.removeItem('sessionType');
                    window.location.href = '/dashboard';
                } else {
                    showError(data.error || 'URL analysis failed.');
                }
            } catch (err) {
                showError('Network Error: ' + err.message);
            } finally {
                hideLoading();
            }
        });
    }

    // 2. Analyze Text (Manual Paste)
    if (elements.analyzeBtn) {
        elements.analyzeBtn.addEventListener('click', async () => {
            console.log("Clicked Analyze Text");
            const text = elements.commentsTextarea.value.trim();
            const title = elements.titleInput.value.trim() || 'Untitled Analysis';

            if (!text) return showError('Please paste some comments.');

            const commentsList = text.split('\n').map(c => c.trim()).filter(c => c);
            if (commentsList.length === 0) return showError('No valid comments found.');

            await performSingleAnalysis(commentsList, title);
        });
    }

    // 3. Demo Button
    if (elements.demoBtn) {
        elements.demoBtn.addEventListener('click', async () => {
            console.log("Clicked Demo");
            showLoading();
            hideError();
            try {
                const res = await fetch(`${API_BASE}/api/demo`);
                const data = await res.json();
                if (res.ok) {
                    localStorage.setItem('sessionId', data.session_id);
                    localStorage.removeItem('sessionType');
                    window.location.href = '/dashboard';
                } else {
                    showError(data.error || 'Demo failed.');
                }
            } catch (err) {
                showError(err.message);
            } finally {
                hideLoading();
            }
        });
    }

    // 4. Upload CSV
    if (elements.uploadBtn && elements.csvFile) {
        elements.uploadBtn.addEventListener('click', () => {
            elements.csvFile.click();
        });

        elements.csvFile.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = async (ev) => {
                const content = ev.target.result;
                const lines = content.split('\n').map(l => l.trim()).filter(l => l);
                // Simple CSV parsing: assume no commas/quotes complexity for now for demo
                // Or just treat lines as comments
                // Skip header if 'comment' is in first line
                const comments = (lines[0] && lines[0].toLowerCase().includes('comment')) ? lines.slice(1) : lines;

                if (comments.length === 0) return showError('No comments found in CSV.');

                await performSingleAnalysis(comments, file.name.replace('.csv', ''));
            };
            reader.readAsText(file);
        });
    }

    // --- HELPERS ---

    async function performSingleAnalysis(comments, title) {
        showLoading();
        hideError();
        try {
            const res = await fetch(`${API_BASE}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ comments, title })
            });
            const data = await res.json();
            if (res.ok) {
                // For Vercel, we bypass backend sessions and use localStorage
                const sessionId = 'v-' + Date.now();
                localStorage.setItem('sessionId', sessionId);
                localStorage.setItem('analysisResults', JSON.stringify(data.results));
                localStorage.removeItem('sessionType');
                window.location.href = '/dashboard';
            } else {
                showError(data.error || 'Analysis failed.');
            }
        } catch (err) {
            showError('Network Error: ' + err.message);
        } finally {
            hideLoading();
        }
    }

    function showLoading() {
        if (elements.loading) {
            elements.loading.style.display = 'block';
            // Also append to body for overlay effect if needed, but existing CSS handles it
        }
    }

    function hideLoading() {
        if (elements.loading) elements.loading.style.display = 'none';
    }

    function showError(msg) {
        console.error(msg);
        if (elements.errorDiv) {
            elements.errorDiv.textContent = msg;
            elements.errorDiv.style.display = 'block';
        } else {
            alert(msg);
        }
    }

    function hideError() {
        if (elements.errorDiv) elements.errorDiv.style.display = 'none';
    }

});
