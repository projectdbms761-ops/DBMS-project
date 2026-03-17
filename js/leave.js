/**
 * js/leave.js - Specific logic for Leave entity
 */
document.addEventListener('DOMContentLoaded', () => {
    loadLeaveHistory();

    const form = document.getElementById('leaveRequestForm');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Capturing attributes from your DBMS requirements
        const leaveData = {
            studentId: localStorage.getItem('currentUserId'),
            leaveDate: document.getElementById('leaveDate').value,
            returnDate: document.getElementById('returnDate').value,
            reason: document.getElementById('reason').value,
            status: 'Pending Approval' // Default status
        };

        console.log("Saving Leave Record to DB:", leaveData);
        alert("Leave Request Submitted! Leave_ID generated.");
        toggleLeaveForm();
    });
});

function toggleLeaveForm() {
    const section = document.getElementById('leaveFormSection');
    section.style.display = section.style.display === 'none' ? 'block' : 'none';
}

function loadLeaveHistory() {
    const history = [
        { id: 'LV405', start: '2026-01-10', end: '2026-01-15', status: 'Completed' },
        { id: 'LV490', start: '2026-02-20', end: '2026-02-22', status: 'Approved' }
    ];

    const tableBody = document.getElementById('leaveHistoryBody');
    tableBody.innerHTML = history.map(item => `
        <tr>
            <td>${item.id}</td>
            <td>${item.start}</td>
            <td>${item.end}</td>
            <td><span class="status-tag ${item.status.toLowerCase()}">${item.status}</span></td>
        </tr>
    `).join('');
}