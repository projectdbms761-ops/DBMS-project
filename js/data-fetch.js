/**
 * data-fetch.js - Mocking Database Queries
 */
const mockDatabase = {
    students: [
        { id: 'STU101', name: 'Arjun Mehta', room: '201', feesPending: 12500 },
        { id: 'STU102', name: 'Sneha Rao', room: '305', feesPending: 0 }
    ],
    laundry: [
        { id: 'L1', studentId: 'STU101', count: 12, status: 'In Progress' },
        { id: 'L2', studentId: 'STU101', count: 10, status: 'Returned' }
    ]
};

// Function to "Query" student data
function getStudentData(id) {
    return mockDatabase.students.find(s => s.id === id);
}