/**
 * auth.js - Handles Login and Session redirection
 */
/**
 * Handles Login and Session redirection
 */
function handleLogin(event) {
    event.preventDefault();

    const userId = document.getElementById('userId').value;
    const role = document.querySelector('.role-btn.active').innerText;

    // Simulate login (replace with DB check in production)
    console.log(`Logging in as ${role}: ${userId}`);

    // Store user info in LocalStorage
    localStorage.setItem('userRole', role);
    localStorage.setItem('currentUserId', userId);

    // Redirect based on role
    if (role.toLowerCase().includes('student')) {
        window.location.href = 'student-dashboard.html';
    } else {
        window.location.href = 'admin-dashboard.html';
    }
}

/**
 * Toggle between Student and Admin buttons on the login page
 */
function setRole(role, event) {
    document.querySelectorAll('.role-btn').forEach(btn => btn.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    }
    const idInput = document.getElementById('userId');
    idInput.placeholder = role === 'student' ? 'e.g. STU101' : 'e.g. WRD501';
}