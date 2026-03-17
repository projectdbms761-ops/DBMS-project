/**
 * js/fees.js - Handling Fee Entity
 */
document.addEventListener('DOMContentLoaded', () => {
    loadFeeHistory();
});

function loadFeeHistory() {
    const transactions = [
        { id: 'TXN_9901', date: '2026-01-05', amount: '45,000', status: 'Paid' },
        { id: 'TXN_9952', date: '2026-02-01', amount: '40,000', status: 'Paid' },
        { id: 'TXN_1002', date: '2026-02-28', amount: '12,500', status: 'Pending' }
    ];

    const tableBody = document.getElementById('feeTableBody');
    tableBody.innerHTML = transactions.map(t => `
        <tr>
            <td>#${t.id}</td>
            <td>${t.date}</td>
            <td>₹${t.amount}</td>
            <td><span class="status-tag ${t.status.toLowerCase()}">${t.status}</span></td>
        </tr>
    `).join('');
}