/**
 * js/complaints.js - Handling Complaint Entity
 */
document.addEventListener('DOMContentLoaded', () => {
    loadComplaints();

    const form = document.getElementById('complaintForm');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Data structure based on your PDF attributes
        const newComplaint = {
            complaintId: 'CMP' + Math.floor(Math.random() * 9000),
            studentId: localStorage.getItem('currentUserId'),
            type: document.getElementById('complaintType').value,
            desc: document.getElementById('description').value,
            date: new Date().toLocaleDateString(),
            status: 'Open'
        };

        alert(`Complaint Registered! ID: ${newComplaint.complaintId}`);
        // Logically this would be an INSERT query in SQL
        location.reload(); 
    });
});

function loadComplaints() {
    const complaints = [
        { id: 'CMP8821', type: 'Electrical', desc: 'Ceiling fan making noise', date: '2026-02-25', status: 'In Progress' },
        { id: 'CMP8701', type: 'Plumbing', desc: 'Tap leaking in washroom', date: '2026-02-10', status: 'Closed' }
    ];

    const container = document.getElementById('complaintList');
    container.innerHTML = complaints.map(c => `
        <div class="complaint-item glass-card">
            <div class="comp-header">
                <strong>${c.type} Issue (#${c.id})</strong>
                <span class="status-tag ${c.status.replace(/\s+/g, '-').toLowerCase()}">${c.status}</span>
            </div>
            <p class="comp-desc">${c.desc}</p>
            <div class="comp-footer">Filed on: ${c.date}</div>
        </div>
    `).join('');
}
