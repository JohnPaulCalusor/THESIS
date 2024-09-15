document.addEventListener('DOMContentLoaded', function(){
    document.body.addEventListener('click', function(event) {
        if (event.target && event.target.id === 'view_button') {
            fetchUserInfo(event.target.dataset.id);
        }
    });
});

function fetchUserInfo(userId) {
    fetch(`get-user-info/${userId}/`)
        .then(response => response.json())
        .then(data => {
            const userInfo = `
                <div>
                    <h3>User Information</h3>
                    <p><strong>Username:</strong> ${data.username}</p>
                    <p><strong>Name:</strong> ${data.name}</p>
                    <p><strong>Mobile Number:</strong> ${data.mobileNum}</p>
                    <p><strong>Region:</strong> ${data.region}</p>
                    <p><strong>Address:</strong> ${data.address}</p>
                    <p><strong>Occupation:</strong> ${data.occupation}</p>
                    <p><strong>Age:</strong> ${data.age}</p>
                    <p><strong>Date of Birth:</strong> ${data.birthdate}</p>
                </div>
            `;
            document.querySelector('#popup_container').innerHTML = userInfo;
        })
        .catch(error => console.error('Error fetching user info:', error));
}
