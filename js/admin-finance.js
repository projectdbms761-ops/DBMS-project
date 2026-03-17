/**
 * js/admin-finance.js - Finance & Fees Entity Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    renderFinanceTable();
});

function renderFinanceTable() {
    const feeRecords = [
        { id: 'STU101', name: 'Arjun Mehta', date: '2026-02-01', paid: '85,000', pending: '12,500' },
        { id: 'STU102', name: 'Sneha Rao', date: '2026-02-15', paid: '97,500', pending: '0' },
        { id: 'STU105', name: 'Rahul S.', date: '2026-01-10', paid: '40,000', pending: '57,500' },
        { id: 'STU110', name: 'John Doe', date: '2026-02-20', paid: '97,500', pending: '0' }
    ];

    const body = document.getElementById('adminFeeTableBody');
    body.innerHTML = feeRecords.map(f => `
        <tr class="${parseInt(f.pending.replace(',','')) > 0 ? 'defaulter-row' : ''}">
            <td><strong>${f.id}</strong></td>
            <td>${f.name}</td>
            <td>${f.date}</td>
            <td>₹${f.paid}</td>
            <td style="color: ${parseInt(f.pending.replace(',','')) > 0 ? '#f87171' : '#4ade80'}">
                ₹${f.pending}
            </td>
            <td>
                <button class="action-link" onclick="sendReminder('${f.id}')">Send Reminder</button>
            </td>
        </tr>
    `).join('');
}

function filterDefaulters() {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        if (!row.classList.contains('defaulter-row')) {
            row.style.display = row.style.display === 'none' ? '' : 'none';
        }
    });
}

function sendReminder(id) {
    alert(`Notification: A fee reminder email has been sent to Student ${id}.`);
}