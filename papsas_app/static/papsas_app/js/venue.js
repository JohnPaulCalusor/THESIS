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

    fetch(`/venue/update/${id}/`)
        .then(response => response.json())
        .then(data => {
            // Populate form fields with fetched data
            document.getElementById('id_name').value = data.name;
            document.getElementById('id_address').value = data.address;
            document.getElementById('id_capacity').value = data.capacity;

            // Get the form and set the attribute
            const form = updateContainer.querySelector('form');
            const updateUrl = `/venue/update/${id}/`;
            form.setAttribute("hx-post", updateUrl);
            form.setAttribute("hx-confirm", `Are you sure you want to update '${data.name}' `);
            
            htmx.process(form);
            
            console.log("hx-post set to:", form.getAttribute("hx-post"));
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