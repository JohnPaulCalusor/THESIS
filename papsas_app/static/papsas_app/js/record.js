// Get the img elements

// Add event listeners to the View Receipt and View ID links
document.addEventListener('DOMContentLoaded', function(){
    const receiptLinks = document.querySelectorAll('.receipt-link')
    receiptLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();  // Prevent the default action of the link
            const userId = event.target.dataset.id;  // Use the data-id attribute to get the user ID
            const dataId = link.getAttribute('data-id');
            show_receipt(dataId);
        }); 
    });
    
    const idLinks = document.querySelectorAll('.id-link')
    idLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();  // Prevent the default action of the link
            const userId = event.target.dataset.id;  // Use the data-id attribute to get the user ID
            const dataId = link.getAttribute('data-id');
            show_id(dataId);
        }); 
    });

    const closeButtons = document.querySelectorAll('.close-modal')
    closeButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();  // Prevent the default action of the link
            const modal = event.target.closest('.modal');
            modal.style.display = 'none';

        }); 
    });

});
              
function show_receipt(userId){
    const receiptImg = document.getElementById('receipt-img');

    fetch(`get-receipt/${userId}/`)
        .then(response => response.json())
        .then(data => {
            const url = data.receipt;
            console.log(data.receipt);
            receiptImg.src = url;
            document.getElementById('receipt-container').style.display = 'block';
            document.getElementById('id-container').style.display = 'none';
            });
        }

function show_id(userId){
    const idImg = document.getElementById('id-img');

    fetch(`get-id/${userId}/`)
        .then(response => response.json())
        .then(data => {
            const url = data.id;
            console.log(data.id);
            idImg.src = url;
            document.getElementById('id-container').style.display = 'block';
            document.getElementById('receipt-container').style.display = 'none';
            });
        }
