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
})