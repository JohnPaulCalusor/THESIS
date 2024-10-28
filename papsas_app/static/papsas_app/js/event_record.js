document.addEventListener('DOMContentLoaded', function(){
    function bindButtons(){
        document.querySelectorAll('.view-button').forEach(button => {
            button.addEventListener('click', function () {
                const eventId = this.getAttribute('data-event-id');
                showEventDetails(eventId);
            });
        });
    
        // View Registration - dynamically load registration record
        document.querySelectorAll('.reg-button').forEach(button => {
            button.addEventListener('click', function () {
                const eventId = this.getAttribute('data-event-id');
                showRegistrationRecord(eventId);
            });
        });
    
        document.querySelectorAll('.view-button').forEach(button => {
            button.addEventListener('click', function () {
                const eventId = this.getAttribute('data-event-id');
                showEventDetails(eventId);
            });
        });
    
        // View Attendance - dynamically load attendance modal
        document.querySelectorAll('.attendance-button').forEach(button => {
            button.addEventListener('click', function () {
                const url = this.getAttribute('data-url');
                showAttendanceModal(url);
            });
        });
    
        // Update event - show update form dynamically
        document.querySelectorAll('.update-button').forEach(button => {
            button.addEventListener('click', function () {
                const eventId = this.getAttribute('data-event-id');
                showUpdate(eventId);
            });
        });
    
        document.querySelectorAll('.reg-close-modal').forEach(button => {
            button.addEventListener('click', function () {
                hideRegistrationModal()
            });
        });
    
        document.querySelectorAll('.att-close-modal').forEach(button => {
            button.addEventListener('click', function () {
                hideAttendanceModal()
            });
        });
    
        document.querySelectorAll('.upd-close-modal').forEach(button => {
            button.addEventListener('click', function () {
                hideUpdateModal()
            });
        });

        document.querySelectorAll('.det-close-modal').forEach(button => {
            button.addEventListener('click', function () {
                closePopup()
            });
        });
    }

    bindButtons()
})
    

function hideUpdateModal(){
    document.getElementById('update-container').style.display = 'none';
}

function showEventDetails(eventId) {
    const body = document.getElementById('details-body');

    fetch(`/event/update/${eventId}/`)
    .then(response => response.json())
    .then(data => {
        body.innerHTML = `
        <img src="${data.pubmat}" alt="Event Image">
        <h2>${data.name}</h2>
        <p><strong>Description:</strong> ${data.description}</p>
        <p><strong>Start Date:</strong> ${data.startDate}</p>
        <p><strong>End Date:</strong> ${data.endDate}</p>
        <p><strong>Start Time:</strong> ${data.startTime}</p>
        <p><strong>End Time:</strong> ${data.endTime}</p>
        <p><strong>Venue:</strong> ${data.venue}</p>
        <p><strong>Price:</strong> ${data.price}</p>
        `;
    });

    document.querySelector('#details-container').style.display = 'block';
}

function showUpdate(id) {
    const updateContainer = document.getElementById('update-container');
    updateContainer.style.display = 'block';
    console.log(id);

    fetch(`/event/update/${id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.pubmat) {
                document.getElementById('img').src = data.pubmat;
            } else {
                document.getElementById('img').src = '';
            }

            document.getElementById('id_eventName').value = data.name;
            document.getElementById('id_startDate').value = data.startDate;
            document.getElementById('id_endDate').value = data.endDate;
            document.getElementById('id_venue').value = data.venue;
            document.getElementById('id_exclusive').value = data.exclusive;
            document.getElementById('id_eventDescription').value = data.description;
            document.getElementById('id_price').value = data.price;
            document.getElementById('id_startTime').value = data.startTime;
            document.getElementById('id_endTime').value = data.endTime;
            console.log(data.endDate);
            
            const form = updateContainer.querySelector('form');
            form.action = `/event/update/${id}/`;
        })
        .catch(error => console.error('Error:', error));
}
function showPopup() {
    document.querySelector('#details-container').style.display = 'block';
    document.body.insertAdjacentHTML('beforeend', '<div class="popup-overlay"></div>');
}

function closePopup() {
    document.querySelector('#details-container').style.display = 'none';
    const overlay = document.querySelector('.popup-overlay');
    if (overlay) {
        overlay.remove();
    }
}

document.querySelector('.popup-overlay')?.addEventListener('click', closePopup);