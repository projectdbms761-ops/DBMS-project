/**
 * js/admin.js - Warden Management Logic
 */
// admin.js - Warden Management Logic
document.addEventListener('DOMContentLoaded', () => {
    loadPendingLeaves();
});

/**
 * Loads pending leave requests into the admin table
 */
function loadPendingLeaves() {
    const leaves = [
        { name: 'Arjun Mehta', date: '2026-03-05', reason: 'Family Function' },
        { name: 'Rahul S.', date: '2026-03-02', reason: 'Medical' },
        { name: 'Sneha Rao', date: '2026-03-08', reason: 'Holiday' }
    ];

    const tableBody = document.getElementById('adminLeaveTable');
    if (!tableBody) return;
    tableBody.innerHTML = leaves.map(l => `
        <tr>
            <td>${l.name}</td>
            <td>${l.date}</td>
            <td>${l.reason}</td>
            <td>
                <button class="status-tag approved" style="border:none; cursor:pointer;">Approve</button>
                <button class="status-tag pending" style="border:none; cursor:pointer; background:rgba(248,113,113,0.1); color:#f87171;">Reject</button>
            </td>
        </tr>
    `).join('');
}