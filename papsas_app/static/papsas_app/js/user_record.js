const form = document.querySelector('#filter-form');
form.addEventListener('htmx:send', function() {
    htmx.trigger(document.querySelector('#table-container'), 'cancel');
});