document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert('Please log in as an admin.');
        window.location.href = '/login.html';
        return;
    }

    const reportsContainer = document.getElementById('admin-ctf-reports');
    const contributionsContainer = document.getElementById('admin-contributions');
    const statsContainer = document.getElementById('admin-contrib-stats');

    const loadReports = async () => {
        try {
            const response = await fetch('/api/v1/admin/ctf/reports', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.status === 401 || response.status === 403) {
                alert('Admin access required. Please log in with an admin account.');
                window.location.href = '/login.html';
                return;
            }
            const data = await response.json();
            if (!Array.isArray(data) || data.length === 0) {
                reportsContainer.innerHTML = '<p>No CTF reports yet.</p>';
                return;
            }
            let html = '<table><tr><th>When</th><th>User</th><th>Challenge</th><th>Category</th><th>Description</th></tr>';
            data.forEach((r) => {
                const date = r.created_at ? new Date(r.created_at) : null;
                const dateStr = date
                    ? `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1)
                          .toString()
                          .padStart(2, '0')}/${date.getFullYear()}`
                    : '';
                html += `<tr>
                    <td>${dateStr}</td>
                    <td>${r.username || r.user_id}</td>
                    <td>${r.challenge_title || r.challenge_id || '-'}</td>
                    <td>${r.category}</td>
                    <td>${r.description}</td>
                </tr>`;
            });
            html += '</table>';
            reportsContainer.innerHTML = html;
        } catch {
            reportsContainer.innerHTML = '<p>Failed to load CTF reports.</p>';
        }
    };

    const loadPendingContributions = async () => {
        try {
            const response = await fetch('/api/v1/admin/contributions/pending', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.status === 401 || response.status === 403) {
                contributionsContainer.innerHTML = '<p>Admin access required.</p>';
                return;
            }
            const data = await response.json();
            if (!Array.isArray(data) || data.length === 0) {
                contributionsContainer.innerHTML = '<p>No pending contributions.</p>';
                return;
            }

            let html = '<table><tr><th>Title</th><th>User</th><th>Category</th><th>Severity</th><th>Submitted</th><th>Actions</th></tr>';
            data.forEach((c) => {
                const date = c.created_at ? new Date(c.created_at) : null;
                const dateStr = date
                    ? `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1)
                          .toString()
                          .padStart(2, '0')}/${date.getFullYear()}`
                    : '';
                html += `<tr data-id="${c.id}">
                    <td>${c.title}</td>
                    <td>${c.username || c.user_id}</td>
                    <td>${c.category}</td>
                    <td>${c.severity}</td>
                    <td>${dateStr}</td>
                    <td>
                        <button class="btn-approve" data-id="${c.id}">Approve</button>
                        <button class="btn-reject" data-id="${c.id}">Reject</button>
                    </td>
                </tr>
                <tr>
                    <td colspan="6"><strong>Description:</strong> ${c.description}<br><strong>Resources:</strong> ${c.resources || '-'}</td>
                </tr>`;
            });
            html += '</table>';
            contributionsContainer.innerHTML = html;

            contributionsContainer.querySelectorAll('.btn-approve').forEach((btn) => {
                btn.addEventListener('click', async () => {
                    const id = btn.getAttribute('data-id');
                    if (!confirm('Approve this contribution and add it to incidents?')) return;
                    try {
                        const resp = await fetch(`/api/v1/admin/contributions/${id}/approve`, {
                            method: 'POST',
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        if (resp.ok) {
                            alert('Contribution approved.');
                            loadPendingContributions();
                            loadStats();
                        } else {
                            alert('Failed to approve contribution.');
                        }
                    } catch {
                        alert('Failed to approve contribution.');
                    }
                });
            });

            contributionsContainer.querySelectorAll('.btn-reject').forEach((btn) => {
                btn.addEventListener('click', async () => {
                    const id = btn.getAttribute('data-id');
                    if (!confirm('Reject this contribution?')) return;
                    try {
                        const resp = await fetch(`/api/v1/admin/contributions/${id}/reject`, {
                            method: 'POST',
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        if (resp.ok) {
                            alert('Contribution rejected.');
                            loadPendingContributions();
                        } else {
                            alert('Failed to reject contribution.');
                        }
                    } catch {
                        alert('Failed to reject contribution.');
                    }
                });
            });
        } catch {
            contributionsContainer.innerHTML = '<p>Failed to load pending contributions.</p>';
        }
    };

    const loadStats = async () => {
        try {
            const response = await fetch('/api/v1/admin/contributions/stats', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.status === 401 || response.status === 403) {
                statsContainer.innerHTML = '<p>Admin access required.</p>';
                return;
            }
            const data = await response.json();
            if (!Array.isArray(data) || data.length === 0) {
                statsContainer.innerHTML = '<p>No approved contributions yet.</p>';
                return;
            }
            let html = '<table><tr><th>User</th><th>Approved Contributions</th></tr>';
            data.forEach((row) => {
                html += `<tr><td>${row.username}</td><td>${row.count}</td></tr>`;
            });
            html += '</table>';
            statsContainer.innerHTML = html;
        } catch {
            statsContainer.innerHTML = '<p>Failed to load contribution stats.</p>';
        }
    };

    loadReports();
    loadPendingContributions();
    loadStats();
});

