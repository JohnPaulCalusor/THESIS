function disableButton() {
    const approveButton = querySelector('#approve-button');
    const declineButton = querySelector('#decline-button');
    approveButton.disabled = true;
    declineButton.disabled = true;}

document.addEventListener('DOMContentLoaded', function(){
    const statusColumn = document.querySelectorAll('.status-column')
    statusColumn.forEach(column => {
        if (column.textContent.trim() === 'Approved') {
            const approveButton = column.parentNode.querySelector('#approve-button');
            if (approveButton) {
                approveButton.disabled = true; 
            }
        } else if (column.textContent.trim() === 'Declined') {
            const declineButton = column.parentNode.querySelector('#decline-button');
            if (declineButton) {
                declineButton.disabled = true; 
            }
        }
    });

    const form = document.querySelector('form');
    form.onsubmit = disableButton();


})