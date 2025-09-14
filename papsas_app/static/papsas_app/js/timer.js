document.addEventListener('DOMContentLoaded', function() {
    var expirationTimestamp = document.getElementById('data').dataset.expiration;
    var timeLeft = expirationTimestamp - Math.floor(Date.now() / 1000);
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
                if (element.name !== 'resend_code') {
                    element.style.display = "none";
                }
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

    window.moveToNext = function(current) {
        if (current.value.length >= current.maxLength) {
            const next = current.nextElementSibling;
            if (next) {
                next.focus();
            }
        }
    };

    document.querySelectorAll('.code-box').forEach(input => {
        input .addEventListener('input', function(event) {
            window.moveToNext(this);
        });

        input.addEventListener('keydown', function(event) {
            if (event.key === 'Backspace' && this.value.length === 0) {
                const previous = this.previousElementSibling;
                if (previous) {
                    previous.focus();
                }
            }
        });
    });
});