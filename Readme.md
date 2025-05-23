## App Description

This application serves as a reference implementation for Mastercard Click to Pay (C2P) within Agentic platforms. It provides a simple checkout experience where users can securely pay for grocery items using their Mastercard credit or debit cards.

**Components:**

* **app.py:** This Python script is the entry point of the application. It handles user authentication, initializes the Mastercard Checkout service, and sets up the necessary routes for handling user interactions.
* **c2p.js:** This JavaScript file contains the logic for making payment requests to Mastercard and handling the response. It interacts with the `src-card-list` and `src-otp-input` components to collect user input and submit the payment request.
* **index.html:** This HTML file provides the user interface for the checkout flow. It includes a list of grocery items, a total amount, a "Pay Now" button, and a success modal.

**Features:**

- Mastercard C2P integration for secure online payments.
- Display of a card list with the option to add new cards.
- OTP input for 3D Secure authentication.
- Confirmation modal upon successful payment.

**Objective:**

The objective of this application is to showcase Mastercard C2P within Agentic platforms, demonstrating a smooth and secure checkout experience for customers.

**Benefits:**

- Enhanced customer experience with a seamless checkout process.
- Increased sales due to the convenience and security of C2P.
- Improved conversion rates by removing the need for traditional payment forms.

**Note:**

This application is for demonstration purposes only. For production use, additional security measures and server-side validation may be required.
