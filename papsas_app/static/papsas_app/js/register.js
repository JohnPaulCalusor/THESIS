const termsText = `
    <h2>PAPSAS, Inc. Terms and Conditions</h2>
    <h3>Acceptance of Terms</h3>
    <p>By registering for an account on the PAPSAS, Inc. Management Information System, you agree to abide by these Terms and Conditions, as well as our Privacy Policy.</p>

    <h3>Account Registration</h3>
    <ul>
        <li>You agree to provide accurate, current, and complete information during registration.</li>
        <li>You are responsible for keeping your account information secure and confidential. Any activity conducted under your account will be considered authorized by you.</li>
    </ul>

    <h3>Use of the System</h3>
    <ul>
        <li>The system is provided for PAPSAS members and affiliates only. You agree to use it solely for PAPSAS-related purposes.</li>
        <li>Unauthorized use of the system or its contents may result in the suspension or termination of your account.</li>
    </ul>

    <h3>Data Privacy and Protection</h3>
    <ul>
        <li>You consent to the collection, storage, and processing of your personal data as outlined in the Privacy Policy.</li>
        <li>We take necessary precautions to secure your data but cannot guarantee complete security. You acknowledge that no method of electronic transmission or storage is 100% secure.</li>
    </ul>

    <h3>Limitation of Liability</h3>
    <p>PAPSAS, Inc. shall not be held liable for any damages resulting from the misuse of the system or your failure to comply with these Terms and Conditions.</p>

    <h3>Changes to Terms</h3>
    <p>PAPSAS, Inc. reserves the right to update or change these Terms and Conditions at any time. Continued use of your account following such changes constitutes acceptance of the new terms.</p>

    <h3>Contact Information</h3>
    <p>For inquiries regarding these Terms and Conditions, contact us at bienjoshua23@gmail.com.</p>
`;

const privacyText = `
    <h2>Privacy Policy for PAPSAS, Inc. Management Information System</h2>
    <p><strong>Effective Date:</strong> 12/11/2024</p>

    <h3>1. Introduction</h3>
    <p>PAPSAS, Inc. is committed to protecting the privacy of our members and users of our Management Information System. This Privacy Policy outlines how we collect, use, disclose, and safeguard your information when you register for and use our system, accessible at papsasinc.com.</p>

    <h3>2. Information We Collect</h3>
    <ul>
        <li><strong>Personal Information:</strong> When you register, we may collect personal information such as your name, email address, contact details, and any valid identification document for membership verification.</li>
        <li><strong>Usage Data:</strong> We automatically collect information on how you access and use the system, including device information, IP addresses, browser type, and pages viewed.</li>
        <li><strong>Transaction Records:</strong> While we do not process payments directly, we may store information related to completed payments, including payment confirmation or receipts for verification purposes.</li>
    </ul>

    <h3>3. How We Use Your Information</h3>
    <ul>
        <li>Process your registration and verify your membership eligibility.</li>
        <li>Manage your participation in PAPSAS events, programs, and activities.</li>
        <li>Provide you with updates on the latest news, research, seminars, and workshops.</li>
        <li>Enhance decision-making by analyzing data to improve PAPSAS services.</li>
        <li>Ensure the security and integrity of our system.</li>
        <li>Generate reports for resource allocation and attendance tracking for events.</li>
    </ul>

    <h3>4. Data Security</h3>
    <p>We implement administrative, technical, and physical security measures to protect your personal data from unauthorized access, alteration, disclosure, or destruction. Only authorized personnel have access to personal data, and we regularly review our security practices.</p>

    <h3>5. Data Retention</h3>
    <p>We retain your information only for as long as necessary to fulfill the purposes outlined in this policy. Once your data is no longer needed, we securely delete or anonymize it.</p>

    <h3>6. Data Sharing and Disclosure</h3>
    <ul>
        <li>PAPSAS, Inc. does not sell or share your personal information with third parties except when necessary to:</li>
        <ul>
            <li>Comply with legal obligations.</li>
            <li>Protect the rights and safety of our members, PAPSAS, Inc., and the public.</li>
            <li>Provide services through trusted third-party providers who adhere to privacy and security standards.</li>
        </ul>
    </ul>

    <h3>7. Your Rights and Choices</h3>
    <ul>
        <li>Access, update, or delete your personal data stored in the system.</li>
    </ul>

    <h3>8. Changes to Our Privacy Policy</h3>
    <p>PAPSAS, Inc. reserves the right to modify this Privacy Policy at any time. We will notify members of any material changes and update the effective date at the top of this page.</p>

    <h3>9. Contact Us</h3>
    <p>For any questions, concerns, or requests regarding this Privacy Policy or your personal data, please contact us at:</p>
    <p>Email: bienjoshua23@gmail.com<br>
`;

function showModal(type) {
    document.getElementById('modal-text').innerHTML = type === 'terms' ? termsText : privacyText;
    document.getElementById('modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

document.querySelector('.modal-close').addEventListener('click', closeModal);

window.onclick = function(event) {
    if (event.target == document.getElementById('modal')) {
        closeModal();
    }
};

document.addEventListener('DOMContentLoaded', function() {
    const toggleIcons = document.querySelectorAll('.togglePassword');

    toggleIcons.forEach(icon => {
        icon.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const passwordField = document.getElementById(targetId);

            if (passwordField) {
                const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordField.setAttribute('type', type);
                this.classList.toggle('fa-eye-slash');
            }
        });
    });
});

function disableSubmitButton(form) {
    const button = form.querySelector('.submit-btn');
    button.disabled = true;
    button.innerHTML = 'Processing...';
}