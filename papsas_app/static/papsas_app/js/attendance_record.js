let pollingInterval;

function showAttendanceModal(url) {
    document.getElementById('attendance_record').style.display = 'block';
    
    fetchAttendanceData(url);
    
    pollingInterval = setInterval(() => {
        fetchAttendanceData(url);
    }, 5000);
}

function hideAttendanceModal() {
    document.getElementById('attendance_record').style.display = 'none';
    
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    document.getElementById('attendees-body').innerHTML = '';
}

function fetchAttendanceData(url) {
    htmx.ajax('GET', url, {target: '#attendees-body'});
}
