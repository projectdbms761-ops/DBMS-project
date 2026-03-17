/**
 * js/laundry.js - Specific logic for Laundry entity
 */
const RATE_PER_CLOTH = 10;

document.addEventListener('DOMContentLoaded', () => {
    loadLaundryHistory();

    const form = document.getElementById('laundryForm');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const laundryEntry = {
            id: 'L' + Math.floor(Math.random() * 1000),
            studentId: localStorage.getItem('currentUserId'),
            count: document.getElementById('clothesCount').value,
            date: document.getElementById('dropDate').value,
            charges: document.getElementById('clothesCount').value * RATE_PER_CLOTH,
            status: 'Pending'
        };

        alert(`Request Logged! Total Charges: ₹${laundryEntry.charges}`);
        location.reload(); // Refresh to show new data in history
    });
});

function calculateCharges() {
    const count = document.getElementById('clothesCount').value;
    document.getElementById('totalCharges').innerText = `₹${count * RATE_PER_CLOTH}.00`;
}

function loadLaundryHistory() {
    const history = [
        { id: 'LN102', count: 15, charges: 150, status: 'Completed', return: '2026-02-24' },
        { id: 'LN105', count: 8, charges: 80, status: 'Pending', return: '2026-03-02' }
    ];

    const tableBody = document.getElementById('laundryTableBody');
    tableBody.innerHTML = history.map(item => `
        <tr>
            <td>${item.id}</td>
            <td>${item.count}</td>
            <td>₹${item.charges}</td>
            <td><span class="status-tag ${item.status.toLowerCase()}">${item.status}</span></td>
            <td>${item.return}</td>
        </tr>
    `).join('');
}