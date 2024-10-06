function showUpdate(id) {
    const updateContainer = document.getElementById('update-container');
    updateContainer.style.display = 'block';
    console.log(id)

    fetch(`/event/update/${id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.pubmat) {
                document.getElementById('img').src = data.pubmat
            } else {
                document.getElementById('img').src = ''
            }

            document.getElementById('id_eventName').value = data.name;
            document.getElementById('id_startDate').value = data.startDate;
            document.getElementById('id_endDate').value = data.endDate;
            document.getElementById('id_venue').value = data.venue;
            document.getElementById('id_exclusive').value = data.exclusive;
            document.getElementById('id_eventDescription').value = data.description;
            document.getElementById('id_price').value = data.price;
            document.getElementById('id_startTime').value = data.startTime;
            document.getElementById('id_endTime').value = data.endTime;
            console.log(data)
            // Add the achievement ID to the form for submission
            const form = updateContainer.querySelector('form');
            form.action = `/event/update/${id}/`;
        })
        .catch(error => console.error('Error:', error));
}