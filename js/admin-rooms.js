/**
 * js/admin-rooms.js - Room & Hostel Entity Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    renderRooms();
});

function renderRooms() {
    fetch('/api/rooms')
        .then(r => r.json())
        .then(data => {
            const rooms = data.rooms || [];
            const container = document.getElementById('roomContainer');
            container.innerHTML = rooms.map(r => {
                const isFull = r.occupied >= r.capacity;
                const percent = Math.round((r.occupied / (r.capacity || 1)) * 100);
                return `
                    <div class="card glass-card room-card ${isFull ? 'full' : ''}">
                        <div class="room-header">
                            <h3>Room ${r.number}</h3>
                            <span class="floor-tag">${r.hostel_id || ''}</span>
                        </div>
                        <p class="room-type">${r.type || ''}</p>
                        <div class="occupancy-stats">
                            <span>${r.occupied} / ${r.capacity} Beds</span>
                            <div class="progress-bar">
                                <div style="width: ${percent}%; background: ${isFull ? '#f87171' : 'var(--accent-blue)'}"></div>
                            </div>
                        </div>
                        <button class="action-btn-small" onclick="viewRoomDetails('${r.id}')">Manage Allotment</button>
                    </div>
                `;
            }).join('');
        })
        .catch(err => {
            console.error('Failed to load rooms', err);
            document.getElementById('roomContainer').innerHTML = '<div class="card">Failed to load rooms.</div>';
        });
}

function viewRoomDetails(roomNo) {
    // Show current allocations and allow assigning a student
    fetch(`/api/allocations?room=${encodeURIComponent(roomNo)}`)
        .then(r => r.json())
        .then(data => {
            const allocs = data.allocations || [];
            let msg = `Allocations for room ${roomNo}:\n`;
            if (allocs.length === 0) msg += '(none)\n';
            allocs.forEach(a => msg += `${a.id}: ${a.student_id} (on ${a.date})\n`);
            msg += '\nEnter a Student ID to assign (or blank to cancel):';
            const sid = prompt(msg);
            if (sid) {
                fetch('/api/allocations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ student_id: sid, room_id: roomNo })
                }).then(res => res.json()).then(resp => {
                    if (resp.ok) {
                        alert('Assigned ' + sid + ' to ' + roomNo);
                        renderRooms();
                    } else {
                        alert('Failed: ' + (resp.error || JSON.stringify(resp)));
                    }
                }).catch(e => { console.error(e); alert('Assign failed') });
            }
        })
        .catch(e => { console.error(e); alert('Failed to load allocations') });
}   