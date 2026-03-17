    /**
 * dashboard.js - Handles Student Dashboard interactions
 */
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    const userId = localStorage.getItem('currentUserId');
    if (!userId) {
        // Redirect to the Flask login route (absolute path) instead of a static file.
        window.location.href = '/login';
        return;
    }

    // Update the UI with the logged-in ID
    const idDisplay = document.querySelector('.u-id');
    if (idDisplay) idDisplay.innerText = userId;
});

function openComplaintForm() {
    // Logic to show a hidden modal or redirect to complaint page
    alert("Opening Complaint Form for " + localStorage.getItem('currentUserId'));
}

function submitLeaveRequest(event) {
    event.preventDefault();
    // In a real DBMS, this would be an 'INSERT INTO Leave...' query
    alert("Leave request submitted successfully!");
}