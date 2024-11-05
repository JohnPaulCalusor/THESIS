document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.update-button').forEach(button =>{
        button.addEventListener('click', function(){
            const id = this.dataset.id;
            console.log(id)
            showUpdate(id)
        })
    })
})

function showUpdate(achievementId) {
    const updateContainer = document.getElementById('update-container');
    updateContainer.style.display = 'block';
    console.log(achievementId)

    fetch(`/get-achievement-data/${achievementId}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_name').value = data.name;
            document.getElementById('id_description').value = data.description;
            if (data.pubmat) {
                document.getElementById('img').src = data.pubmat
            } else {
                document.getElementById('img').src = ''
            }
            document.getElementById('id_pubmat').src = data.pubmat;
            console.log(data)
  
            const form = updateContainer.querySelector('form');
            const updateUrl = `/get-achievement-data/${achievementId}/`;

            form.setAttribute("hx-post", updateUrl);
            form.setAttribute("hx-confirm", `Are you sure you want to update '${data.name}' `);
            
            htmx.process(form);
        })
        .catch(error => console.error('Error:', error));
}

// Optional: Close update form


// setTimeout(function(){
//     const element = document.getElementById('message-container');
//     element.remove();
// }, 5000);

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