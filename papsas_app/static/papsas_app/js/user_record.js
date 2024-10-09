document.addEventListener('DOMContentLoaded', function(){
    const update_button = document.querySelectorAll('.update-button')

    update_button.forEach(button => {
        button.addEventListener('click', function(){
            const userId = this.getAttribute('data-user-id')
            fetchUserInfo(userId);
        })
    })
})

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

            const container = document.getElementById('popup_container')
            const form = container.querySelector('form');
            form.action = `/user/update/${userId}`;
            })
        .catch(error => console.error('Error fetching user info:', error));
    
    document.querySelector('#popup_container').style.display = 'block';
}
function showPopup() {
    document.querySelector('#popup_container').style.display = 'block';
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
    document.querySelector('#popup_container').style.display = 'none';
    const overlay = document.querySelector('.popup-overlay');
    if (overlay) {
        overlay.remove();
    }
}
document.querySelector('.popup-overlay')?.addEventListener('click', closePopup);


