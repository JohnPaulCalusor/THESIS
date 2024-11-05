let isProcessing = false;

function disableButton(button) {
    if (isProcessing) {
        return;
    }

    isProcessing = true;
    button.disabled = true;
    button.innerHTML = 'Mag antay ka! Be patient because patient is a virtue';
    button.form.submit();
}
