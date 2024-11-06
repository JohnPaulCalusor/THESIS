document.addEventListener("DOMContentLoaded", setupMessageListeners);
document.addEventListener("htmx:afterOnLoad", setupMessageListeners);

function setupMessageListeners() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.classList.add('fade-out');
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);

        const closeButton = alert.querySelector('.btn-close');
        closeButton.addEventListener('click', () => {
            alert.classList.add('fade-out');
            setTimeout(() => {
                alert.remove();
            }, 500);
        });
    });
}
