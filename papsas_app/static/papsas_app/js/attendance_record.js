document.addEventListener('DOMContentLoaded', function(){
    event_links = document.querySelectorAll('.event-links')

    event_links.forEach(function(link){
        link.addEventListener('click', function(event){
            event.preventDefault();
            id = link.getAttribute('data-event');
            show_attendance(id)
            });
    });
})

function show_attendance(eventId){
    const attendance_record = document.querySelector('#attendance_record')
    const attendance_table = document.querySelector('#table-container')
    attendance_record.style.display = 'block'
    const tableBody = document.getElementById('attendees-body');

    close_button = document.querySelector('#close-button')
    close_button.addEventListener('click', function(){
        attendance_record.style.display = 'none'
    });

    fetch(`get-attendance/${eventId}/`)
        .then(response => response.json())
        .then(data => {
            const attendees = data.attendees;
            tableBody.innerHTML = '';
            attendees.forEach(attendee => {
                const tableRow = document.createElement('tr');
                tableRow.innerHTML = `
                    <td>${attendee.first_name} ${attendee.last_name}</td>
                    <td>${attendee.status}</td>

                `;
                tableBody.appendChild(tableRow);
        });
    });
}
