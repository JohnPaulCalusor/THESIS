document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.edit-btn').forEach(button =>{
        button.addEventListener('click', function(){
            const id = this.dataset.id;
            showUpdate(id)
            console.log(id)
        })
    })
})

function showUpdate(electionId) {
    const updateContainer = document.getElementById('details-container');
    id = electionId

    fetch(`/election/update/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_title').value = data.title;
            document.getElementById('id_numWinners').value = data.numWinners;
            document.getElementById('id_endDate').value = data.endDate;

            
            const form = updateContainer.querySelector('form');
            const updateUrl = `/election/update/${id}`;
            form.setAttribute("hx-post", updateUrl);
            form.setAttribute("hx-confirm", `Are you sure you want to update '${data.title}' `);
            
            htmx.process(form);
            updateContainer.style.display = 'block';
        })
        .catch(error => console.error('Error:', error));
}

function closePopup() {
    document.querySelector('#details-container').style.display = 'none';
    const overlay = document.querySelector('.popup-overlay');
    if (overlay) {
        overlay.remove();
    }
}