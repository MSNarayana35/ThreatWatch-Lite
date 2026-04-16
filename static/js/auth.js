document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('accessToken');
    const logoutLink = document.getElementById('logout-link');

    if (logoutLink) {
        if (token) {
            logoutLink.classList.remove('hidden');
        } else {
            logoutLink.classList.add('hidden');
        }

        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('accessToken');
            window.location.href = '/login.html';
        });
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            try {
                const response = await fetch('/api/v1/login', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('accessToken', data.access_token);
                    window.location.href = '/';
                } else {
                    const errorData = await response.json();
                    alert(`Login failed: ${errorData.detail}`);
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('An error occurred during login.');
            }
        });
    }

    const adminLoginForm = document.getElementById('admin-login-form');
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('admin-email').value;
            const password = document.getElementById('admin-password').value;

            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            try {
                const response = await fetch('/api/v1/login', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    alert(`Admin login failed: ${errorData.detail}`);
                    return;
                }

                const data = await response.json();
                localStorage.setItem('accessToken', data.access_token);

                const meResponse = await fetch('/api/v1/me', {
                    headers: {
                        Authorization: `Bearer ${data.access_token}`
                    }
                });

                if (!meResponse.ok) {
                    alert('Unable to verify admin status.');
                    localStorage.removeItem('accessToken');
                    return;
                }

                const me = await meResponse.json();
                if (!me.is_admin) {
                    alert('You are not an admin user.');
                    localStorage.removeItem('accessToken');
                    return;
                }

                window.location.href = '/admin.html';
            } catch (error) {
                console.error('Admin login error:', error);
                alert('An error occurred during admin login.');
            }
        });
    }

    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/v1/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, email, password })
                });

                if (response.ok) {
                    alert('Signup successful! Please log in.');
                    window.location.href = '/login.html';
                } else {
                    const errorData = await response.json();
                    alert(`Signup failed: ${errorData.detail}`);
                }
            } catch (error) {
                console.error('Signup error:', error);
                alert('An error occurred during signup.');
            }
        });
    }
});
