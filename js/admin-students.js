/**
 * js/admin-students.js - Warden Student Management
 */
document.addEventListener('DOMContentLoaded', () => {
    renderStudents();

    document.getElementById('regForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            course: document.getElementById('course').value,
            phone: document.getElementById('phone').value
        };
        try {
            const res = await fetch('/api/students', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw await res.json();
            const data = await res.json();
            toggleAddStudentForm();
            renderStudents();
            alert('Student created: ' + data.id);
        } catch (err) {
            console.error(err);
            alert('Failed to create student: ' + (err.message || JSON.stringify(err)));
        }
    });
});

function toggleAddStudentForm() {
    const section = document.getElementById('addStudentSection');
    section.style.display = section.style.display === 'none' ? 'block' : 'none';
}

function renderStudents() {
    // Fetch students from server API
    fetch('/api/students')
        .then(r => r.json())
        .then(data => {
            const students = data.students || [];
            const body = document.getElementById('adminStudentTableBody');
            body.innerHTML = students.map(s => `
                <tr>
                    <td><strong>${s.id}</strong></td>
                    <td>${s.name}</td>
                    <td>${s.course || ''}</td>
                    <td>${s.email || ''}</td>
                    <td>
                        <button class="action-link" onclick="editStudent('${s.id}')">Edit</button>
                        <button class="action-link delete" onclick="deleteStudent('${s.id}')">Delete</button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(err => {
            console.error('Failed to load students', err);
            const body = document.getElementById('adminStudentTableBody');
            body.innerHTML = '<tr><td colspan="5">Failed to load students.</td></tr>';
        });
}

function searchStudents() {
    let filter = document.getElementById('studentSearch').value.toUpperCase();
    let rows = document.getElementById('adminStudentTableBody').getElementsByTagName('tr');
    for (let row of rows) {
        row.style.display = row.innerText.toUpperCase().includes(filter) ? "" : "none";
    }
}

function deleteStudent(id) {
    if(confirm(`Are you sure you want to delete ${id}? This will trigger a CASCADE delete in related tables.`)) {
        fetch(`/api/students/${encodeURIComponent(id)}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(res => {
                if (res.ok) {
                    alert('Deleted ' + id);
                    renderStudents();
                } else {
                    alert('Delete failed: ' + (res.error || JSON.stringify(res)));
                }
            })
            .catch(e => {
                console.error(e);
                alert('Delete failed');
            });
    }
}