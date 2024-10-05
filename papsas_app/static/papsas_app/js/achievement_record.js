function showUpdate(achievementId) {
    const updateContainer = document.getElementById('update-container');
    updateContainer.style.display = 'block';
    console.log(achievementId)

    fetch(`/get-achievement-data/${achievementId}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('name-id').value = data.name;
            document.getElementById('id_description').value = data.description;
            if (data.pubmat) {
                document.getElementById('img').src = data.pubmat
            } else {
                document.getElementById('img').src = ''
            }
            console.log(data)
            // Add the achievement ID to the form for submission
            const form = updateContainer.querySelector('form');
            form.action = `/get-achievement-data/${achievementId}/`;
        })
        .catch(error => console.error('Error:', error));
}

// Optional: Close update form
function closeUpdateForm() {
    document.getElementById('update-container').style.display = 'none';
}