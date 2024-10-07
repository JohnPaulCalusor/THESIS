// Global variable to track search state
let isSearchActive = false;
let pollingInterval = null;

function initializeEventList() {
    const searchInput = document.getElementById('searchInput');
    const eventListBody = document.getElementById('event-list-body');
    
    // Setup search handler
    searchInput.addEventListener('input', function(e) {
        if (this.value.trim()) {
            isSearchActive = true;
            // Clear existing polling if it exists
            if (pollingInterval) {
                clearInterval(pollingInterval);
                pollingInterval = null;
            }
        } else {
            isSearchActive = false;
            // Restart polling when search is cleared
            startPolling();
        }
    });

    function startPolling() {
        if (!isSearchActive && !pollingInterval) {
            pollingInterval = setInterval(() => {
                if (!isSearchActive) {
                    htmx.ajax('GET', '/partial/event/', {target: '#event-list-body', swap: 'innerHTML'});
                }
            }, 5000);
        }
    }

    // Initial polling start
    startPolling();

    // Handle cleanup when leaving the page
    window.addEventListener('beforeunload', () => {
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }
    });
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', initializeEventList);

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
}

document.addEventListener('htmx:afterSwap', function (event) {
    // Check if the swap target is the event-list-body
    if (event.detail.target.id === 'event-list-body') {
        // Rebind your event listeners here
        bindButtons();
    }
});


function showEventDetails(eventId) {
    body = document.getElementById('details-body')
    document.querySelector('#details-container').style.display = 'block';

    fetch(`/event/update/${eventId}/`)
    .then(response => response.json())
    .then(data => {
        body.innerHTML = `
        <img src="${data.pubmat}" alt="">
        <h2>${data.name}</h2>
        <p>${data.description}</p>
        <p>${data.startDate}</p>
        <p>${data.endDate}</p>
        <p>${data.startTime}</p>
        <p>${data.endTime}</p>
        <p>${data.venue}</p>
        <p>${data.price}</p>
        `
    })

}

// Show Registration Record
function showRegistrationRecord(eventId) {
    document.getElementById('registration_record').style.display = 'block';
    const eventRegBody = document.querySelector('#event-reg-body');

    function fetchEventReg(id) {
        fetch(`/record/event/${id}/registration/`)
            .then(response => response.json())
            .then(data => {
                eventRegBody.innerHTML = '';
                
                const validRecords = data.filter(reg => 
                    reg.status === 'Pending' || reg.status === 'Approved'
                );

                // Create and append rows for each valid record
                validRecords.forEach(reg => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${reg.name}</td>
                        <td><img src="${reg.receipt}" alt="Receipt"></td>
                        <td>${reg.status}</td>
                        <td>
                            ${reg.status === 'Approved' ? 
                                `<button class="decline-button" data-reg-id="${reg.id}">Decline</button>` 
                                : 
                                `<button class="approve-button" data-reg-id="${reg.id}">Approve</button>
                                 <button class="decline-button" data-reg-id="${reg.id}">Decline</button>`
                            }
                        </td>
                    `;
                    eventRegBody.appendChild(row);
                });

                // Add event listeners to the newly created buttons
                attachButtonListeners();
            })
            .catch(error => {
                console.error('Error fetching registration data:', error);
            });
    }

    function attachButtonListeners() {
        const approveButtons = document.querySelectorAll('.approve-button');
        const declineButtons = document.querySelectorAll('.decline-button');

        approveButtons.forEach(button => {
            button.addEventListener('click', function() {
                const regId = this.getAttribute('data-reg-id');
                fetch(`/record/event-registration/approve/${regId}`, {
                    method: 'PUT',
                    body: JSON.stringify({status: 'Approved'})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        alert(data.message);
                    } else if (data.error) {
                        alert(data.error);
                    }
                    });

                fetchEventReg(eventId);
            });
        });

        declineButtons.forEach(button => {
            button.addEventListener('click', function() {
                const regId = this.getAttribute('data-reg-id');
                fetch(`/record/event-registration/decline/${regId}`, {
                    method: 'PUT',
                    body: JSON.stringify({status: 'Declined'})
                })

                fetchEventReg(eventId);
            });
        });
    }

    fetchEventReg(eventId);

    pollingInterval = setInterval(() => {
        fetchEventReg(eventId);
    }, 10000);
}

function hideRegistrationModal() {
    const registrationModal = document.getElementById('registration_record');
    registrationModal.style.display = 'none';
    document.querySelector('#event-reg-body').innerHTML = '';

    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
}

function showAttendanceModal(url) {
    document.getElementById('attendance_record').style.display = 'block';
    
    fetchAttendanceData(url);
    
    pollingInterval = setInterval(() => {
        fetchAttendanceData(url);
    }, 5000);
}

function fetchAttendanceData(url) {
    fetch(url)
    .then(response => response.json())
    .then(data => {
        const attendanceBody = document.getElementById('attendees-body');
        attendanceBody.innerHTML = '';
        const attendanceRecords = data

        attendanceRecords.forEach(record=>{
            const row = document.createElement('tr');
            row.innerHTML = `
            <td>${record.first_name} ${record.last_name}</td>
            <td>${record.status}</td>
            `
            attendanceBody.appendChild(row);

        })
    })
}

function hideAttendanceModal() {
    document.getElementById('attendance_record').style.display = 'none';
    
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    document.getElementById('attendees-body').innerHTML = '';
}

function hideUpdateModal() {
    document.getElementById('img').src = '';
    document.getElementById('update-container').style.display = 'none';
    
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
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
            console.log(data);
            
            const form = updateContainer.querySelector('form');
            form.action = `/event/update/${id}/`;
        })
        .catch(error => console.error('Error:', error));
}