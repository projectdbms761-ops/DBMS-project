/**
 * js/admin-maintenance.js - Maintenance Entity Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    renderMaintenanceLogs();
});

function renderMaintenanceLogs() {
    const logs = [
        { mid: 'MNT_501', cid: 'CMP8821', type: 'Electrical', cost: '1,200', status: 'Completed' },
        { mid: 'MNT_502', cid: 'CMP8701', type: 'Plumbing', cost: '3,500', status: 'In Progress' },
        { mid: 'MNT_503', cid: 'CMP8910', type: 'Carpentry', cost: '0', status: 'Pending' }
    ];

    const body = document.getElementById('maintenanceTableBody');
    body.innerHTML = logs.map(l => `
        <tr>
            <td><strong>${l.mid}</strong></td>
            <td>${l.cid}</td>
            <td>${l.type}</td>
            <td>₹${l.cost}</td>
            <td><span class="status-tag ${l.status.replace(/\s+/g, '-').toLowerCase()}">${l.status}</span></td>
            <td>
                <button class="action-link" onclick="updateCost('${l.mid}')">Update Cost</button>
            </td>
        </tr>
    `).join('');
}

function updateCost(id) {
    const newCost = prompt("Enter Maintenance Cost for " + id);
    if(newCost) {
        alert(`SQL: UPDATE Maintenance SET Cost = ${newCost}, Status = 'Completed' WHERE Maintenance_ID = '${id}'`);
    }
}