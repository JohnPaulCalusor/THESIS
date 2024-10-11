document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.update-button').forEach(button => {
        button.addEventListener('click', function(){
            var id = this.dataset.venueId;
            console.log(id)
            showUpdate(id)
        })
    })
})

function showUpdate(id) {
    const updateContainer = document.getElementById('update-container');
    updateContainer.style.display = 'block';
    console.log(id)

    fetch(`/venue/update/${id}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_name').value = data.name;
            document.getElementById('id_address').value = data.address;
            document.getElementById('id_capacity').value = data.capacity;
            console.log(data)
            // Add the achievement ID to the form for submission
            const form = updateContainer.querySelector('form');
            form.action = `/venue/update/${id}/`;
        })
        .catch(error => console.error('Error:', error));
        
}
function showPopup() {
    document.querySelector('#update-container').style.display = 'block';
    document.body.insertAdjacentHTML('beforeend', '<div class="popup-overlay"></div>');
}

function closePopup() {
    document.querySelector('#update-container').style.display = 'none';
    const overlay = document.querySelector('.popup-overlay');
    if (overlay) {
        overlay.remove();
    }
}

document.querySelector('.popup-overlay')?.addEventListener('click', closePopup);