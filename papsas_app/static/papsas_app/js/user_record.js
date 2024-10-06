function fetchUserInfo(userId) {
    fetch(`/get-user-info/${userId}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_email').value = data.username;
            document.getElementById('id_first_name').value = data.firstName
            document.getElementById('id_last_name').value = data.lastName
            document.getElementById('id_mobileNum').value = data.mobileNum
            document.getElementById('id_region').value = data.region
            document.getElementById('id_address').value = data.address
            document.getElementById('id_occupation').value = data.occupation
            document.getElementById('id_age').value = data.age
            document.getElementById('id_birthdate').value = data.birthdate
            document.getElementById('id_institution').value = data.institution
        .catch(error => console.error('Error fetching user info:', error));
    
    });
    document.querySelector('#popup_container').style.display = 'block';
}
