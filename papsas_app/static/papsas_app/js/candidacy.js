document.addEventListener('DOMContentLoaded', function() {
    const nextButton = document.getElementById('step2-next');
    const previousButton = document.getElementById('step3-prev');

    if (nextButton) {
        nextButton.addEventListener('click', function() {
            const step2Text = document.getElementById('step2-credentials').value;
            step3TextContent = step2Text; // Save content for step 3
            document.getElementById('step3-credentials').value = step3TextContent;

            // Switch fieldset: Hide Step 2, Show Step 3
            const step2Fieldset = document.querySelector('#step2-fieldset');
            const step3Fieldset = document.querySelector('#step3-fieldset');
            const formcard = document.querySelector('#step3-form')

            step2Fieldset.style.opacity = 0;
            step2Fieldset.style.display = 'none';

            step3Fieldset.style.display = 'block';
            step3Fieldset.style.opacity = 1;

            formcard.style.display = 'block';
            formcard.style.opacity = 1;
        });
    }

    if (previousButton) {
        previousButton.addEventListener('click', function() {
            // Restore the Step 2 credentials text
            document.getElementById('step2-credentials').value = step3TextContent;

            // Switch fieldset: Hide Step 3, Show Step 2
            const step2Fieldset = document.querySelector('#step2-fieldset');
            const step3Fieldset = document.querySelector('#step3-fieldset');

            step3Fieldset.style.opacity = 0;
            step3Fieldset.style.display = 'none';

            step2Fieldset.style.display = 'block';
            step2Fieldset.style.opacity = 1;


        });
    }
});
