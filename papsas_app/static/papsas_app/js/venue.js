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