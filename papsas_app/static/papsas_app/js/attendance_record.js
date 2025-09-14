let pollingInterval;

document.addEventListener('DOMContentLoaded', function(){
    const closeRegButtons = document.querySelectorAll('.reg-close-modal');

    closeRegButtons.forEach(button => {
        button.addEventListener('click', function () {
            hideRegistrationModal();
        });
    });
});

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

// KAILANGANG ILIPAT

function showUpdate(id) {
    const updateContainer = document.getElementById('update-container');
    updateContainer.style.display = 'block';
    console.log(id);

    setTimeout(() => {
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
    }, 10); 
}