document.addEventListener('DOMContentLoaded', () => {
    const ctfList = document.getElementById('ctf-list');
    if (!ctfList) return;

    const difficultyFilter = document.getElementById('difficulty-filter');

    const token = localStorage.getItem('accessToken');
    if (!token) {
        window.location.href = '/login.html';
        return;
    }

    const leaderboardContent = document.getElementById('leaderboard-content');
    const leaderboardMeta = document.getElementById('leaderboard-meta');
    const modal = document.getElementById('ctf-modal');
    const modalClose = document.getElementById('ctf-modal-close');
    const modalTitle = document.getElementById('ctf-modal-title');
    const modalDesc = document.getElementById('ctf-modal-description');
    const modalPoints = document.getElementById('ctf-modal-points');
    const modalDifficulty = document.getElementById('ctf-modal-difficulty');
    const modalResources = document.getElementById('ctf-modal-resources');
    const modalHint = document.getElementById('ctf-modal-hint');
    const modalStart = document.getElementById('ctf-modal-start');
    const reportOpen = document.getElementById('ctf-report-open');
    const reportModal = document.getElementById('ctf-report-modal');
    const reportClose = document.getElementById('ctf-report-close');
    const reportType = document.getElementById('ctf-report-type');
    const reportChallenge = document.getElementById('ctf-report-challenge');
    const reportDescription = document.getElementById('ctf-report-description');
    const reportSubmit = document.getElementById('ctf-report-submit');

    let solvedSet = new Set();
    let currentUser = null;
    let activeChallengeId = null;
    let challengeStartTime = null;
    let timerInterval = null;

    const difficultyForPoints = (pts) => {
        if (pts <= 100) return { label: 'Easy', color: '#22c55e' };
        if (pts <= 150) return { label: 'Medium', color: '#f59e0b' };
        return { label: 'Hard', color: '#ef4444' };
    };

    const updateTimer = () => {
        if (!activeChallengeId || !challengeStartTime) {
            if (timerInterval) clearInterval(timerInterval);
            const timerEl = document.getElementById('active-timer');
            if (timerEl) timerEl.remove();
            return;
        }

        let timerEl = document.getElementById('active-timer');
        if (!timerEl) {
            timerEl = document.createElement('div');
            timerEl.id = 'active-timer';
            timerEl.style.position = 'fixed';
            timerEl.style.bottom = '20px';
            timerEl.style.right = '20px';
            timerEl.style.background = '#222';
            timerEl.style.color = '#00ff00';
            timerEl.style.padding = '10px 20px';
            timerEl.style.borderRadius = '5px';
            timerEl.style.border = '1px solid #00ff00';
            timerEl.style.zIndex = '1000';
            timerEl.style.fontFamily = 'monospace';
            timerEl.style.fontSize = '1.2rem';
            document.body.appendChild(timerEl);
        }

        const now = new Date();
        const start = new Date(challengeStartTime + 'Z'); // Ensure UTC
        const diff = Math.floor((now - start) / 1000);
        
        if (diff < 0) {
             timerEl.textContent = "Time: 00:00";
             return;
        }

        const minutes = Math.floor(diff / 60).toString().padStart(2, '0');
        const seconds = (diff % 60).toString().padStart(2, '0');
        timerEl.textContent = `Time: ${minutes}:${seconds}`;
    };

    const startTimer = () => {
        if (timerInterval) clearInterval(timerInterval);
        updateTimer();
        timerInterval = setInterval(updateTimer, 1000);
    };

    const stopTimer = () => {
        if (timerInterval) clearInterval(timerInterval);
        const timerEl = document.getElementById('active-timer');
        if (timerEl) timerEl.remove();
    };

    const openModal = (challenge) => {
        const d = difficultyForPoints(challenge.points);
        if (modalTitle) modalTitle.textContent = challenge.title;
        if (modalDesc) modalDesc.textContent = challenge.description;
        if (modalPoints) modalPoints.textContent = challenge.points;
        if (modalDifficulty) {
            modalDifficulty.textContent = d.label;
            modalDifficulty.style.borderColor = d.color;
            modalDifficulty.style.color = '#fff';
            modalDifficulty.style.background = d.color + '25';
        }
        const resources = (challenge.resources || '')
            .split(',')
            .map((r) => r.trim())
            .filter(Boolean);
        if (modalResources) {
            modalResources.innerHTML = '<h3>Resources</h3>';
            if (resources.length) {
                const list = document.createElement('ul');
                resources.forEach((url) => {
                    const li = document.createElement('li');
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    a.rel = 'noopener noreferrer';
                    
                    if (url.startsWith('/ctf/scenario/')) {
                        a.textContent = 'Open Challenge Interface';
                        a.className = 'btn-link'; 
                        a.style.color = '#00ff00';
                        a.style.fontWeight = 'bold';
                    } else if (url.startsWith('/static/challenges/')) {
                        const filename = url.split('/').pop();
                        a.textContent = 'Download ' + filename;
                        a.download = filename;
                    } else {
                        a.textContent = url;
                    }
                    
                    li.appendChild(a);
                    list.appendChild(li);
                });
                modalResources.appendChild(list);
            } else {
                modalResources.innerHTML += '<p>No resources provided.</p>';
            }
        }
        if (modalHint) modalHint.innerHTML = `<h3>Hint</h3><p>${challenge.hint || 'No hint provided.'}</p>`;
        if (modal) modal.classList.add('open');
        
        if (modalStart) {
            // Check if user can start this challenge
            if (activeChallengeId && activeChallengeId !== challenge.id) {
                modalStart.textContent = "Another Challenge Active";
                modalStart.disabled = true;
                modalStart.style.background = '#555';
                modalStart.onclick = null;
            } else if (activeChallengeId === challenge.id) {
                modalStart.textContent = "Continue Challenge";
                modalStart.disabled = false;
                modalStart.style.background = '#00ff00';
                modalStart.onclick = () => {
                     if (modal) modal.classList.remove('open');
                };
            } else {
                modalStart.textContent = "Start Challenge";
                modalStart.disabled = false;
                modalStart.style.background = '#00ff00';
                modalStart.onclick = async () => {
                    try {
                        const response = await fetch(`/ctf/challenges/${challenge.id}/start`, {
                            method: 'POST',
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        if (response.ok) {
                            const data = await response.json();
                            activeChallengeId = challenge.id;
                            challengeStartTime = data.start_time;
                            startTimer();
                            loadChallenges();
                            if (modal) modal.classList.remove('open');
                        } else if (response.status === 401) {
                            alert("Session expired or invalid. Please log in again.");
                            localStorage.removeItem('accessToken');
                            window.location.href = '/login.html';
                        } else {
                            const err = await response.json();
                            alert(err.detail || "Failed to start challenge");
                        }
                    } catch (e) {
                        alert("Error starting challenge");
                    }
                };
            }
        }
    };
    if (modalClose) {
        modalClose.addEventListener('click', () => {
            if (modal) modal.classList.remove('open');
        });
    }

    const render = (challenges) => {
        ctfList.innerHTML = '';

        let filtered = challenges;
        if (difficultyFilter && difficultyFilter.value) {
            const target = difficultyFilter.value.toLowerCase();
            filtered = challenges.filter((challenge) => {
                const d = difficultyForPoints(challenge.points);
                return d.label.toLowerCase() === target;
            });
        }

        const easyChallenges = [];
        const mediumChallenges = [];
        const hardChallenges = [];

        filtered.forEach((challenge) => {
            const d = difficultyForPoints(challenge.points);
            if (d.label === 'Easy') {
                easyChallenges.push(challenge);
            } else if (d.label === 'Medium') {
                mediumChallenges.push(challenge);
            } else {
                hardChallenges.push(challenge);
            }
        });

        const renderGroup = (title, list) => {
            if (!list.length) return;

            const group = document.createElement('section');
            group.className = 'ctf-group';

            const heading = document.createElement('h2');
            heading.textContent = title + ' Challenges';
            group.appendChild(heading);

            const container = document.createElement('div');
            container.className = 'card-container';

            list.forEach((challenge) => {
            const card = document.createElement('div');
            card.className = 'card';
            
            const isActive = activeChallengeId === challenge.id;
            const isLocked = activeChallengeId && !isActive;
            const isSolved = solvedSet.has(challenge.id);

            if (isLocked) {
                card.style.opacity = '0.5';
                card.style.pointerEvents = 'none'; // Disable interaction with locked cards
            }
            if (isActive) {
                card.style.border = '2px solid #00ff00';
                card.style.boxShadow = '0 0 10px #00ff00';
            }

            const resources = (challenge.resources || '')
                .split(',')
                .map((r) => r.trim())
                .filter(Boolean);

            const resourcesHtml = resources.length
                ? `<ul>${resources
                      .map(
                          (r) => {
                              let text = r;
                              let downloadAttr = '';
                              if (r.startsWith('/ctf/scenario/')) {
                                  text = 'Open Challenge Interface';
                              } else if (r.startsWith('/static/challenges/')) {
                                  const filename = r.split('/').pop();
                                  text = 'Download ' + filename;
                                  downloadAttr = ` download="${filename}"`;
                              }
                              return `<li><a href="${r}" target="_blank" rel="noopener noreferrer"${downloadAttr}>${text}</a></li>`;
                          }
                      )
                      .join('')}</ul>`
                : '<p>No resources provided.</p>';

            const d = difficultyForPoints(challenge.points);
            const solvedBadge = isSolved
                ? `<span class="pill" style="border-color:#22c55e;background:#22c55e25;color:#fff;">Completed ✓</span>`
                : '';

            let actionButtons = '';
            if (isActive) {
                 actionButtons = `
                    <button class="btn" style="background: #ef4444; margin-right: 10px;" data-ctf-end="${challenge.id}">End Challenge</button>
                    <button class="btn" data-ctf-submit="${challenge.id}">Submit Flag</button>
                 `;
            } else if (isLocked) {
                 actionButtons = `<button class="btn" disabled style="background: #555;">Locked</button>`;
            } else if (isSolved) {
                 actionButtons = `<button class="btn" data-ctf-view="${challenge.id}">View Details</button>`;
            } else {
                 actionButtons = `<button class="btn" data-ctf-view="${challenge.id}">View Details</button>`;
            }

            card.innerHTML = `
                <h3>${challenge.title}</h3>
                <p>${challenge.description}</p>
                <p><strong>Points:</strong> ${challenge.points} <span class="pill" style="border-color:${d.color};background:${d.color}25;color:#fff;">${d.label}</span> ${solvedBadge}</p>
                <div>
                    <h3>Resources</h3>
                    ${isActive || isSolved ? resourcesHtml : '<p>Start challenge to view resources.</p>'}
                </div>
                <div>
                    <h3>Hint</h3>
                    <p>${isActive || isSolved ? (challenge.hint || 'No hint provided.') : 'Start challenge to view hint.'}</p>
                </div>
                <div>
                    ${isActive ? `<input type="text" data-ctf-flag="${challenge.id}" placeholder="Enter the flag">` : ''}
                    ${actionButtons}
                </div>
            `;
            container.appendChild(card);
            });

            group.appendChild(container);
            ctfList.appendChild(group);
        };

        renderGroup('Easy', easyChallenges);
        renderGroup('Medium', mediumChallenges);
        renderGroup('Hard', hardChallenges);

        ctfList.querySelectorAll('button[data-ctf-view]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const challengeId = parseInt(btn.getAttribute('data-ctf-view'), 10);
                const challenge = window.__ctfChallenges.find((c) => c.id === challengeId);
                if (challenge) openModal(challenge);
            });
        });

        ctfList.querySelectorAll('button[data-ctf-end]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                if (!confirm("Are you sure you want to end this challenge?")) return;
                try {
                    const response = await fetch('/ctf/challenges/end', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (response.ok) {
                        activeChallengeId = null;
                        challengeStartTime = null;
                        stopTimer();
                        loadChallenges();
                    } else if (response.status === 401) {
                        alert("Session expired or invalid. Please log in again.");
                        localStorage.removeItem('accessToken');
                        window.location.href = '/login.html';
                    } else {
                        alert("Failed to end challenge.");
                    }
                } catch {
                    alert("Error ending challenge.");
                }
            });
        });

        ctfList.querySelectorAll('button[data-ctf-submit]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const challengeId = btn.getAttribute('data-ctf-submit');
                const input = ctfList.querySelector(`input[data-ctf-flag="${challengeId}"]`);
                const flag = input ? input.value.trim() : '';
                if (!flag) {
                    alert('Please enter a flag before submitting.');
                    if (input) input.focus();
                    return;
                }
                
                try {
                    const response = await fetch(`/ctf/challenges/${challengeId}/submit`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({ flag })
                    });
                    if (response.status === 401) {
                        alert("Session expired or invalid. Please log in again.");
                        localStorage.removeItem('accessToken');
                        window.location.href = '/login.html';
                        return;
                    }
                    const result = await response.json();
                    if (result.correct) {
                        const awarded = typeof result.points_awarded === 'number' ? result.points_awarded : 0;
                        const total = typeof result.total_points === 'number' ? result.total_points : null;
                        alert(`${result.message} Points awarded: ${awarded}.`);
                        solvedSet.add(parseInt(challengeId, 10));
                        activeChallengeId = null;
                        challengeStartTime = null;
                        stopTimer();
                        loadChallenges();
                        loadLeaderboard();
                    } else {
                        alert(result.message || 'Incorrect flag.');
                    }
                } catch {
                    alert('Failed to submit flag.');
                }
            });
        });
    };

    const loadChallenges = async () => {
        try {
            const response = await fetch('/ctf/challenges');
            const data = await response.json();
            window.__ctfChallenges = Array.isArray(data) ? data : [];

            if (reportChallenge && window.__ctfChallenges.length) {
                reportChallenge.innerHTML = '<option value="">General / Entire CTF Page</option>';
                window.__ctfChallenges.forEach((c) => {
                    const opt = document.createElement('option');
                    opt.value = String(c.id);
                    opt.textContent = c.title;
                    reportChallenge.appendChild(opt);
                });
            }

            render(window.__ctfChallenges);
        } catch {
            ctfList.innerHTML = '<p>Could not load CTF challenges.</p>';
        }
    };

    if (difficultyFilter) {
        difficultyFilter.addEventListener('change', () => {
            if (Array.isArray(window.__ctfChallenges)) {
                render(window.__ctfChallenges);
            }
        });
    }

    if (reportOpen && reportModal && reportClose && reportSubmit && reportDescription && reportType && reportChallenge) {
        reportOpen.addEventListener('click', () => {
            reportDescription.value = '';
            if (reportType) reportType.value = 'challenge';
            if (reportChallenge) reportChallenge.value = '';
            reportModal.classList.add('open');
        });

        reportClose.addEventListener('click', () => {
            reportModal.classList.remove('open');
        });

        reportSubmit.addEventListener('click', async () => {
            const description = reportDescription.value.trim();
            if (!description) {
                alert('Please describe the problem you faced.');
                reportDescription.focus();
                return;
            }

            const category = reportType.value || 'challenge';
            const challengeIdRaw = reportChallenge.value;
            const challenge_id = challengeIdRaw ? parseInt(challengeIdRaw, 10) : null;

            try {
                const response = await fetch('/ctf/report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        category,
                        challenge_id,
                        description
                    })
                });

                if (response.status === 401) {
                    alert('Session expired or invalid. Please log in again.');
                    localStorage.removeItem('accessToken');
                    window.location.href = '/login.html';
                    return;
                }

                if (response.ok) {
                    alert('Thanks! Your report has been submitted.');
                    reportModal.classList.remove('open');
                } else {
                    alert('Failed to submit report.');
                }
            } catch {
                alert('Failed to submit report.');
            }
        });
    }

    const loadLeaderboard = async () => {
        if (!leaderboardContent) return;
        try {
            const response = await fetch('/api/v1/leaderboard/');
            const data = await response.json();
            if (!Array.isArray(data) || data.length === 0) {
                leaderboardContent.innerHTML = '<p>No leaderboard data yet.</p>';
                return;
            }
            leaderboardContent.innerHTML = '<table><tr><th>Rank</th><th>User</th><th>Points</th></tr></table>';
            const table = leaderboardContent.querySelector('table');
            data.forEach((entry, index) => {
                const row = table.insertRow();
                row.innerHTML = `<td>${index + 1}</td><td>${entry.username}</td><td>${entry.points}</td>`;
            });
            if (leaderboardMeta && currentUser) {
                const idx = data.findIndex((e) => e.username === currentUser.username);
                if (idx >= 0) {
                    const next = data[idx - 1];
                    const gap = next ? (next.points - data[idx].points) : 0;
                    leaderboardMeta.innerHTML = `<p>You are #${idx + 1}${gap > 0 ? ` | Next rank: ${gap} points ahead` : ''}</p>`;
                } else {
                    leaderboardMeta.innerHTML = `<p>You are not ranked yet. Solve a challenge to appear here.</p>`;
                }
            }
        } catch {
            leaderboardContent.innerHTML = '<p>Could not load leaderboard.</p>';
        }
    };

    const loadSolved = async () => {
        try {
            const response = await fetch('/ctf/solves/me', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.status === 401) {
                localStorage.removeItem('accessToken');
                window.location.href = '/login.html';
                return;
            }
            const ids = await response.json();
            solvedSet = new Set(Array.isArray(ids) ? ids : []);
        } catch {
            solvedSet = new Set();
        }
    };

    const loadActiveChallenge = async () => {
        try {
            const response = await fetch('/ctf/status/active', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.status === 401) {
                localStorage.removeItem('accessToken');
                window.location.href = '/login.html';
                return;
            }
            if (response.ok) {
                const data = await response.json();
                activeChallengeId = data.active_challenge_id;
                challengeStartTime = data.start_time;
                if (activeChallengeId) {
                    startTimer();
                }
            }
        } catch {
            console.error("Failed to load active challenge status");
        }
    };

    const loadMe = async () => {
        try {
            const response = await fetch('/api/v1/me', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.status === 401) {
                localStorage.removeItem('accessToken');
                window.location.href = '/login.html';
                return;
            }
            currentUser = await response.json();
        } catch {
            currentUser = null;
        }
    };

    (async () => {
        await loadMe();
        await loadSolved();
        await loadActiveChallenge();
        await loadChallenges();
        await loadLeaderboard();
    })();
});
