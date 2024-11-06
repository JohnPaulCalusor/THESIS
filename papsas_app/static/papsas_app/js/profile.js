document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.update-button').forEach(button => {
        button.addEventListener('click', function(){
            showUpdate()
        })
    })
})

function showUpdate(){
    const updateContainer = document.getElementById('update-container');
    updateContainer.style.display = 'block';   
}

function closePopup() {
    document.querySelector('#update-container').style.display = 'none';
    const overlay = document.querySelector('.popup-overlay');
    if (overlay) {
        overlay.remove();
    }
}

document.querySelector('.popup-overlay')?.addEventListener('click', closePopup);