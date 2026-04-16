document.addEventListener('DOMContentLoaded', () => {
    const loginLink = document.getElementById('login-link');
    const signupLink = document.getElementById('signup-link');
    const logoutLink = document.getElementById('logout-link');
    const adminLink = document.getElementById('admin-link');

    const accessToken = localStorage.getItem('accessToken');

    const updateAuthLinks = async () => {
        if (accessToken) {
            loginLink.classList.add('hidden');
            signupLink.classList.add('hidden');
            logoutLink.classList.remove('hidden');

            if (adminLink) {
                try {
                    const response = await fetch('/api/v1/me', {
                        headers: { 'Authorization': `Bearer ${accessToken}` }
                    });
                    if (response.ok) {
                        const user = await response.json();
                        if (user.is_admin) {
                            adminLink.classList.remove('hidden');
                        } else {
                            adminLink.classList.add('hidden');
                        }
                    } else {
                        adminLink.classList.add('hidden');
                    }
                } catch {
                    if (adminLink) adminLink.classList.add('hidden');
                }
            }
        } else {
            loginLink.classList.remove('hidden');
            signupLink.classList.remove('hidden');
            logoutLink.classList.add('hidden');
            if (adminLink) adminLink.classList.add('hidden');
        }
    };

    updateAuthLinks();

    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('accessToken');
        window.location.href = '/login.html';
    });

    const dashboardContent = document.getElementById('dashboard-content');
    const dashboard = document.getElementById('dashboard');
    const categoryFilter = document.getElementById('category-filter');
    const severityFilter = document.getElementById('severity-filter');
    const startDateFilter = document.getElementById('start-date-filter');
    const endDateFilter = document.getElementById('end-date-filter');
    const filterBtn = document.getElementById('filter-btn');
    const clearFilterBtn = document.getElementById('clear-filter-btn');
    const contributeBtn = document.getElementById('contribute-btn');
    const contributeModal = document.getElementById('contribute-modal');
    const contributeClose = document.getElementById('contribute-close');
    const contribTitle = document.getElementById('contrib-title');
    const contribCategory = document.getElementById('contrib-category');
    const contribSeverity = document.getElementById('contrib-severity');
    const contribDescription = document.getElementById('contrib-description');
    const contribResources = document.getElementById('contrib-resources');
    const contribSubmit = document.getElementById('contrib-submit');

    // Function to fetch and display incidents
    const loadIncidents = async () => {
        const params = new URLSearchParams();
        if (categoryFilter.value) params.append('category', categoryFilter.value);
        if (severityFilter.value) params.append('severity', severityFilter.value);
        if (startDateFilter.value) params.append('start_date', new Date(startDateFilter.value).toISOString());
        if (endDateFilter.value) params.append('end_date', new Date(endDateFilter.value).toISOString());

        try {
            const response = await fetch(`/api/v1/incidents/?${params.toString()}`);
            const incidents = await response.json();
            
            dashboardContent.innerHTML = ''; // Clear existing content
            if (incidents.length === 0) {
                dashboardContent.innerHTML = '<p>No incidents match the current filters.</p>';
                return;
            }

            const groupedIncidents = incidents.reduce((acc, incident) => {
                const date = new Date(incident.date).toDateString();
                if (!acc[date]) {
                    acc[date] = [];
                }
                acc[date].push(incident);
                return acc;
            }, {});

            const today = new Date().toDateString();
            const yesterday = new Date(Date.now() - 86400000).toDateString();

            for (const dateStr in groupedIncidents) {
                const dateGroup = document.createElement('div');
                const heading = document.createElement('h3');
                heading.className = 'date-heading';
                let dateLabel = dateStr;
                if (dateStr === today) {
                    dateLabel = 'Today';
                } else if (dateStr === yesterday) {
                    dateLabel = 'Yesterday';
                } else {
                    const date = new Date(dateStr);
                    dateLabel = `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getFullYear()}`;
                }
                heading.textContent = dateLabel;
                dateGroup.appendChild(heading);

                const incidentsContainer = document.createElement('div');
                incidentsContainer.className = 'card-container';

                groupedIncidents[dateStr].forEach(incident => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    const incidentDate = new Date(incident.date);
                    const formattedDate = `${incidentDate.getDate().toString().padStart(2, '0')}/${(incidentDate.getMonth() + 1).toString().padStart(2, '0')}/${incidentDate.getFullYear()}`;
                    card.innerHTML = `
                        <div class="card-header">
                            <h3>${incident.title}</h3>
                            <span class="severity-${incident.severity.toLowerCase()}">${incident.severity}</span>
                        </div>
                        <p>${incident.description}</p>
                        <div class="card-footer">
                            <span>${formattedDate}</span>
                            <a href="${incident.source}" target="_blank">Source</a>
                        </div>
                    `;
                    incidentsContainer.appendChild(card);
                });
                dateGroup.appendChild(incidentsContainer);
                dashboardContent.appendChild(dateGroup);
            }
        } catch (error) {
            console.error('Failed to load incidents:', error);
            dashboard.innerHTML += '<p>Could not load threat data.</p>';
        }
    };

    const toggleButton = document.createElement('button');
    toggleButton.className = 'theme-toggle';

    const updateThemeIcon = () => {
        const isLight = document.body.classList.contains('light-mode');
        toggleButton.textContent = isLight ? '🌙' : '☀';
    };

    updateThemeIcon();
    document.body.appendChild(toggleButton);

    toggleButton.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
        updateThemeIcon();
    });

    filterBtn.addEventListener('click', loadIncidents);

    clearFilterBtn.addEventListener('click', () => {
        categoryFilter.value = '';
        severityFilter.value = '';
        startDateFilter.value = '';
        endDateFilter.value = '';
        loadIncidents();
    });

    loadIncidents();

    if (contributeBtn && contributeModal && contributeClose && contribTitle && contribCategory && contribSeverity && contribDescription && contribSubmit) {
        contributeBtn.addEventListener('click', () => {
            if (!accessToken) {
                alert('Please log in to contribute an incident.');
                window.location.href = '/login.html';
                return;
            }
            contribTitle.value = '';
            contribCategory.value = '';
            contribSeverity.value = 'Medium';
            contribDescription.value = '';
            if (contribResources) contribResources.value = '';
            contributeModal.classList.add('open');
        });

        contributeClose.addEventListener('click', () => {
            contributeModal.classList.remove('open');
        });

        contribSubmit.addEventListener('click', async () => {
            const title = contribTitle.value.trim();
            const category = contribCategory.value.trim();
            const severity = contribSeverity.value;
            const description = contribDescription.value.trim();
            const resources = contribResources ? contribResources.value.trim() : '';

            if (!title || !category || !description) {
                alert('Please fill in title, category, and description.');
                return;
            }

            try {
                const response = await fetch('/api/v1/incidents/contributions/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${accessToken}`
                    },
                    body: JSON.stringify({
                        title,
                        description,
                        category,
                        severity,
                        resources: resources || null
                    })
                });

                if (response.status === 401) {
                    alert('Session expired or invalid. Please log in again.');
                    localStorage.removeItem('accessToken');
                    window.location.href = '/login.html';
                    return;
                }

                if (response.ok) {
                    alert('Thank you! Your contribution has been submitted for review by an admin.');
                    contributeModal.classList.remove('open');
                } else {
                    alert('Failed to submit contribution.');
                }
            } catch {
                alert('Failed to submit contribution.');
            }
        });
    }
});
