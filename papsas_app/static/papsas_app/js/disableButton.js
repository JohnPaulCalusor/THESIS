let isProcessing = false;

function disableButton(button) {
    if (isProcessing) {
        return;
    }

    isProcessing = true;
    button.disabled = true;
    button.innerHTML = 'Please wait.';
    button.form.submit();
}
