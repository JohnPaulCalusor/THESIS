document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('.popup-form');
    const errorContainer = document.getElementById('error-container');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(form);
        const actionUrl = form.action; // Assuming the form has an action attribute

        fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // Indicate that this is an AJAX request
            }
        })
        .then(response => response.json())
        .then(data => {
            // Clear previous errors
            errorContainer.innerHTML = '';

            // Check if there are any errors
            if (data.errors) {
                // Loop through the errors and display them
                for (const [field, messages] of Object.entries(data.errors)) {
                    messages.forEach(message => {
                        const errorMessage = document.createElement('div');
                        errorMessage.textContent = message;
                        errorContainer.appendChild(errorMessage);
                    });
                }
            } else {
                // If there are no errors, you can redirect or update the UI as needed
                window.location.href = '/table/user/'; // Redirect to user table or any other action
            }
        })
        .catch(error => {
            console.error('Error:', error);
            errorContainer.innerHTML = 'An error occurred while updating the record.';
        });
    });
});

function fetchUserInfo(userId) {
    fetch(`/get-user-info/${userId}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_email').value = data.username;
            document.getElementById('id_first_name').value = data.firstName;
            document.getElementById('id_last_name').value = data.lastName;
            document.getElementById('id_mobileNum').value = data.mobileNum;
            document.getElementById('id_region').value = data.region;
            document.getElementById('id_address').value = data.address;
            document.getElementById('id_occupation').value = data.occupation;
            document.getElementById('id_age').value = data.age;
            document.getElementById('id_birthdate').value = data.birthdate;
            document.getElementById('id_institution').value = data.institution;


            const errorContainer = document.querySelector('#error-container');
            if (JSON.response){
                errorContainer.innerHTML = `<pre>${JSON.stringify(JSON.response, null, 2)}</pre>`;
            }

            const container = document.getElementById('details-container')
            const form = container.querySelector('form');
            form.action = `/user/update/${userId}`;
            })
        .catch(error => console.error('Error fetching user info:', error));
    
    document.querySelector('#details-container').style.display = 'block';

}

function showPopup() {
    document.querySelector('#details-container').style.display = 'block';
    document.body.insertAdjacentHTML('beforeend', '<div class="popup-overlay"></div>');
}

function closePopup() {
    document.getElementById('id_email').value = "";
    document.getElementById('id_first_name').value = "";
    document.getElementById('id_last_name').value =  "";
    document.getElementById('id_mobileNum').value =  "";
    document.getElementById('id_region').value =  "";
    document.getElementById('id_address').value =  "";
    document.getElementById('id_occupation').value =  "";
    document.getElementById('id_age').value =  "";
    document.getElementById('id_birthdate').value =  "";
    document.getElementById('id_institution').value =  "";
    document.querySelector('#details-container').style.display = 'none';
    const overlay = document.querySelector('.popup-overlay');
    if (overlay) {
        overlay.remove();
    }
    document.getElementById('error-container').innerHTML = '';
}
document.querySelector('.popup-overlay')?.addEventListener('click', closePopup);


