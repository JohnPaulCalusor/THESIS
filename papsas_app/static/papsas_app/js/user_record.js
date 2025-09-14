document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.update-button').forEach(button => {
        button.addEventListener('click', function(){
            var id = this.dataset.venueId;
            console.log(id)
            showUpdate(id)
        })
    })
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
            const updateUrl =  `/user/update/${userId}`;
            form.setAttribute("hx-post", updateUrl)
            form.setAttribute("hx-confirm", `Are you sure ypu want to update ${data.firstName}'s account?`);

            htmx.process(form)
            console.log("hx-post set to:", form.getAttribute("hx-post"));
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


