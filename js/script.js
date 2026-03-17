const pages = {
    home: `
        <div class="hero">
            <div class="badge">Hostel Management System</div>
            <h1>Full Database <span>Control</span></h1>
            <p>Manage residents, staff, and logistics from a single aesthetic dashboard.</p>
            <button class="primary-btn" onclick="showPage('students')">Enter Dashboard</button>
        </div>
    `,
    students: `
        <section class="page-section">
            <h2>Student Directory</h2>
            <div class="table-card">
                <table>
                    <tr><th>Student_ID</th><th>Name</th><th>Course</th><th>Contact</th></tr>
                    <tr><td>S101</td><td>Arjun Sharma</td><td>B.Tech</td><td>+91 9898...</td></tr>
                    <tr><td>S102</td><td>Priya Rai</td><td>M.B.A</td><td>+91 9797...</td></tr>
                </table>
            </div>
        </section>
    `,
    rooms: `
        <section class="page-section">
            <h2>Room Allotment</h2>
            <div class="grid">
                <div class="card"><h3>Room 201</h3><p>Hostel: Boys Alpha</p><p>Capacity: 3</p><span class="status">● Available</span></div>
                <div class="card"><h3>Room 305</h3><p>Hostel: Girls Beta</p><p>Capacity: 2</p><span class="status">● Full</span></div>
            </div>
        </section>
    `,
    fees: `
        <section class="page-section">
            <h2>Financial Records</h2>
            <div class="table-card">
                <table>
                    <tr><th>Txn_ID</th><th>Student_ID</th><th>Amount</th><th>Status</th></tr>
                    <tr><td>#T882</td><td>S101</td><td>₹45,000</td><td>Paid</td></tr>
                    <tr><td>#T883</td><td>S102</td><td>₹12,000</td><td style="color:#facc15">Pending</td></tr>
                </table>
            </div>
        </section>
    `,
    services: `
        <section class="page-section">
            <h2>Logistics & Services</h2>
            <div class="grid">
                <div class="card">
                    <h3>Laundry Service</h3>
                    <p>Track clothes count and return dates.</p>
                    <button class="primary-btn" style="margin-top:10px; font-size:0.8rem">Manage</button>
                </div>
                <div class="card">
                    <h3>Leave Management</h3>
                    <p>Register Entry/Exit times and reasons.</p>
                    <button class="primary-btn" style="margin-top:10px; font-size:0.8rem">View Logs</button>
                </div>
                <div class="card">
                    <h3>Complaints</h3>
                    <p>Maintenance and student grievances.</p>
                    <button class="primary-btn" style="margin-top:10px; font-size:0.8rem">Open Tickets</button>
                </div>
            </div>
        </section>

        // Add this under the 'students' property in your pages object

    add_student: ``
        <section class="page-section">
            <div class="table-card" style="max-width: 600px; margin: 0 auto;">
                <h2>Register New Student</h2>
                <form id="studentForm" style="display: flex; flex-direction: column; gap: 1.5rem; margin-top: 2rem;">
                    <input type="text" placeholder="Full Name" style="padding: 1rem; background: var(--glass-bg); border: 1px solid var(--glass-border); color: white; border-radius: 10px;">
                    <input type="email" placeholder="Email Address" style="padding: 1rem; background: var(--glass-bg); border: 1px solid var(--glass-border); color: white; border-radius: 10px;">
                    <select style="padding: 1rem; background: var(--bg-dark); border: 1px solid var(--glass-border); color: white; border-radius: 10px;">
                        <option>Select Course</option>
                        <option>B.Tech</option>
                        <option>M.B.A</option>
                    </select>
                    <button type="button" class="primary-btn">Save Student Record</button>
                    <button type="button" onclick="showPage('students')" style="background:transparent; color: var(--text-dim); border:none; cursor:pointer;">Cancel</button>
                </form>
            </div>
        </section>
`
    ``
};

function showPage(pageId) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = pages[pageId];
    window.scrollTo(0, 0);
}

// Initialize
showPage('home');