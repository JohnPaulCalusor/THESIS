document.addEventListener("DOMContentLoaded", function() {
    // Ensure the close button exists before attaching the listener
    var closeButton = document.getElementById("close-button");
    
    if (closeButton) {
        closeButton.addEventListener("click", function() {
            document.getElementById("attendance_record").style.display = "none";
        });
    }
});

    function openAttendance(eventId) {
        document.getElementById("attendance_record").style.display = "block";
        const tableBody = document.getElementById('attendees-body');
        fetch(`get-attendance/${eventId}/`)
        .then(response => response.json())
        .then(data => {
            const attendees = data.attendees;
            tableBody.innerHTML = '';
            attendees.forEach(attendee => {
                const tableRow = document.createElement('tr');
                tableRow.innerHTML = `
                    <td>${attendee.first_name} ${attendee.last_name}</td>   
                    <td>${attendee.status ? 'Present' : 'Absent'}</td>

                `;
                tableBody.appendChild(tableRow);
        });
    });
    }

    // Function to close the attendance modal
    document.getElementById("close-button").addEventListener("click", function() {
        document.getElementById("attendance_record").style.display = "none";
        
    });

    // Optional: close modal when clicking outside of it
    window.onclick = function(event) {
        var modal = document.getElementById("attendance_record");
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }