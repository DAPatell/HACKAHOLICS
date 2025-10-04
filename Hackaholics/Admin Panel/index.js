const form = document.getElementById("signupForm");
    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmPassword");
    const countrySelect = document.getElementById("country");

    const nameError = document.getElementById("nameError");
    const emailError = document.getElementById("emailError");
    const passwordError = document.getElementById("passwordError");
    const confirmError = document.getElementById("confirmError");
    const countryError = document.getElementById("countryError");
    const successMsg = document.getElementById("successMsg");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      let valid = true;

      // Name validation
      if (nameInput.value.trim() === "") {
        nameError.style.display = "block";
        valid = false;
      } else {
        nameError.style.display = "none";
      }

      // Email validation
      const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;
      if (!emailInput.value.match(emailPattern)) {
        emailError.style.display = "block";
        valid = false;
      } else {
        emailError.style.display = "none";
      }

      // Password validation
      if (passwordInput.value.length < 6) {
        passwordError.style.display = "block";
        valid = false;
      } else {
        passwordError.style.display = "none";
      }

      // Confirm password validation
      if (confirmPasswordInput.value !== passwordInput.value || confirmPasswordInput.value === "") {
        confirmError.style.display = "block";
        valid = false;
      } else {
        confirmError.style.display = "none";
      }

      // Country validation
      if (countrySelect.value === "") {
        countryError.style.display = "block";
        valid = false;
      } else {
        countryError.style.display = "none";
      }

      // If valid
      if (valid) {
        successMsg.style.display = "block";
        form.reset();
        setTimeout(() => {
          successMsg.style.display = "none";
        }, 3000);
      }
    });

