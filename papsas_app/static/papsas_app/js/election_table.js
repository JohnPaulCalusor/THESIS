document.addEventListener('DOMContentLoaded', function() {
    // Select all table rows
    const rows = document.querySelectorAll('tbody tr');
    
    // Iterate through each row
    rows.forEach(row => {
        // Find the status cell (5th column based on the HTML structure)
        const statusCell = row.cells[4];
        
        // Check if the status is "Top Candidate"
        if (statusCell && statusCell.textContent.trim() === 'Top Candidate') {
            // Apply background color to the entire row
            row.style.backgroundColor = '#e6f3ff';  // Light blue highlight
            
            // Optional: You can also add a border or other styling
            row.style.borderLeft = '4px solid #007bff';  // Blue accent border
        }
    });
});