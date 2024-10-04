document.addEventListener('DOMContentLoaded', function(){

})

let pollingInterval;

function openForm(id){
    document.getElementById('overlay').style.display = 'block';
    document.getElementById("popup_container").style.display = "block";
    const dataContainer = document.getElementById('data-container')
    const tableBody = document.getElementById('electionData');

    function fetchData(){
        fetch(`get-candidates/${id}/`)
        .then(response => response.json())
        .then(data => {
            const candidates = data.officers;
            candidates.sort((a, b) => b.total_votes - a.total_votes);
            console.log(candidates)
            tableBody.innerHTML = '';
            var rank = 0
    
            dataContainer.innerHTML = `
            <p> Number of Elected Officers : ${data.num_elected}</p>
            `
            dataContainer.append();
    
            candidates.forEach(candidate => {
                rank += 1
                const tableRow = document.createElement('tr');
                tableRow.innerHTML = `
                    <td>${rank}</td>   
                    <td>${candidate.name}</td>   
                    <td>${candidate.total_votes}</td>   
                `
                tableBody.appendChild(tableRow);
            })
        })
    }
    fetchData();
    pollingInterval = setInterval(fetchData, 5000);


}

function closeForm() {
    document.getElementById('popup_container').style.display = "none";
    document.getElementById('overlay').style.display = 'none'; // Hide the overlay

    if (pollingInterval) {
        clearInterval(pollingInterval);
    }

    document.getElementById('dataContainer').innerHTML = '';
}

function fetchAttendanceData(url) {
    htmx.ajax('GET', url, {target: '#attendees-body'});
}