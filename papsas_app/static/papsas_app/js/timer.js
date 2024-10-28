            // Handle timer logic
            var expirationTime = {{ expiration_timestamp }};
            var currentTime = Math.floor(Date.now() / 1000);
            var timeLeft = expirationTime - currentTime;

            var timer = document.getElementById("timer");
            var form = document.querySelector("form");

            function updateTimer() {
                if (timeLeft > 0) {
                    timeLeft -= 1;
                    var minutes = Math.floor(timeLeft / 60);
                    var seconds = timeLeft % 60;
                    timer.innerHTML = "Verification code expires in " + minutes + " minutes and " + seconds + " seconds";
                    setTimeout(updateTimer, 1000);
                } else {
                    form.querySelectorAll("input, button, label").forEach(function(element) {
                        element.style.display = "none";
                    });
                    timer.innerHTML = "Verification code has expired. Click the button to resend code.";
                    form.querySelector("button[name='resend_code']").style.display = "block";
                }
            }

            if (timeLeft > 0) {
                updateTimer();
            } else {
                timer.innerHTML = "Verification code has expired. Click the button to resend code.";
                form.querySelector("button[name='resend_code']").style.display = "block";
                form.querySelectorAll("input, button, label").forEach(function(element) {
                    if (element.name !== 'resend_code') {
                        element.style.display = "none";
                    }
                });
            }

            // Handle automatic input focusing between the boxes
            const codeInputs = document.querySelectorAll(".code-box");

            codeInputs.forEach((input, index) => {
                input.addEventListener('input', (e) => {
                    // Move to the next input field if a number is entered
                    if (input.value.length === 1 && index < codeInputs.length - 1) {
                        codeInputs[index + 1].focus();
                    }
                });

                input.addEventListener('keydown', (e) => {
                    // Move to the previous input field if the backspace is pressed and the input is empty
                    if (e.key === "Backspace" && input.value.length === 0 && index > 0) {
                        codeInputs[index - 1].focus();
                    }
                });
            });