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
        document.addEventListener("DOMContentLoaded", function() {
            const receiptLinks = document.querySelectorAll('.receipt-link');
            const idLinks = document.querySelectorAll('.id-link');
            const receiptContainer = document.getElementById('receipt-container');
            const idContainer = document.getElementById('id-container');
            const closeButtons = document.querySelectorAll('.close-modal');
            const receiptImg = document.getElementById('receipt-img');
            const idImg = document.getElementById('id-img');
        
            // Show receipt pop-up
            receiptLinks.forEach(link => {
                link.addEventListener('click', function(event) {
                    event.preventDefault();
                    const userId = this.getAttribute('data-id');
                    // Load the receipt image dynamically
                    receiptImg.src = `/path-to-receipt-image/${userId}/`;
                    receiptContainer.style.display = 'flex';
                });
            });
        
            // Show ID pop-up
            idLinks.forEach(link => {
                link.addEventListener('click', function(event) {
                    event.preventDefault();
                    const userId = this.getAttribute('data-id');
                    // Load the ID image dynamically
                    idImg.src = `/path-to-id-image/${userId}/`;
                    idContainer.style.display = 'flex';
                });
            });
        
            // Close the modal pop-up
            closeButtons.forEach(button => {
                button.addEventListener('click', function() {
                    document.getElementById('receipt-container').style.display = 'none';
                    document.getElementById('id-container').style.display = 'none';
                    document.body.classList.remove('modal-open');
                });
            });
        
            // Close modal when clicking outside the modal content
            window.addEventListener('click', function(event) {
                if (event.target === receiptContainer || event.target === idContainer) {
                    receiptContainer.style.display = 'none';
                    idContainer.style.display = 'none';
                    document.body.classList.remove('modal-open');
                }
            });
        });
        