const codeBoxes = document.querySelectorAll('.code-box');

codeBoxes.forEach(function(box, index) {
    box.addEventListener('input', function() {
        if (this.value.length === 1) {
            this.blur(); // blur the current box to update its value
            if (index < codeBoxes.length - 1) {
                codeBoxes[index + 1].focus();
            }
        }
    });

    box.addEventListener('keydown', function(event) {
        if (event.key === 'Backspace' && this.value === '') {
            if (index > 0) {
                codeBoxes[index - 1].focus();
            }
        }
    });
});