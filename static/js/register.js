const API_BASE_URL = 'http://127.0.0.1:5000/api';

// DOM elements
const registerForm = document.getElementById('registerForm');
const usernameInput = document.getElementById('username');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirmPassword');
const togglePasswordBtn = document.getElementById('togglePassword');
const toggleConfirmPasswordBtn = document.getElementById('toggleConfirmPassword');
const errorMessage = document.getElementById('errorMessage');
const registerButton = document.getElementById('registerButton');
const buttonText = registerButton.querySelector('.button-text');
const buttonLoader = registerButton.querySelector('.button-loader');

togglePasswordBtn.addEventListener('click', () => {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    
    const eyeIcon = togglePasswordBtn.querySelector('.eye-icon');
    eyeIcon.textContent = type === 'password' ? '👁️' : '🙈';
});

toggleConfirmPasswordBtn.addEventListener('click', () => {
    const type = confirmPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    confirmPasswordInput.setAttribute('type', type);
    
    const eyeIcon = toggleConfirmPasswordBtn.querySelector('.eye-icon');
    eyeIcon.textContent = type === 'password' ? '👁️' : '🙈';
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    hideError();
    resetInputStates();
    
    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    
    if (!username || !email || !password || !confirmPassword) {
        showError('Kérjük, töltse ki az összes mezőt!');
        return;
    }
    
    if (username.length < 3) {
        showError('A felhasználónévnek legalább 3 karakter hosszúnak kell lennie!');
        usernameInput.classList.add('error');
        return;
    }
    
    if (password.length < 3) {
        showError('A jelszónak legalább 3 karakter hosszúnak kell lennie!');
        passwordInput.classList.add('error');
        return;
    }
    
    if (password !== confirmPassword) {
        showError('A jelszavak nem egyeznek meg!');
        passwordInput.classList.add('error');
        confirmPasswordInput.classList.add('error');
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('Kérjük, adjon meg egy érvényes email címet!');
        emailInput.classList.add('error');
        return;
    }
    
    setLoadingState(true);
    
// Make API call
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            const errorMsg = data.error || 'Regisztrációs hiba történt';
            showError(errorMsg);
            setInputErrorState(true);
            return;
        }
        
        showSuccess('Sikeres regisztráció! Átirányítás a bejelentkezési oldalra...');
        
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
        
    } catch (error) {
        console.error('Registration error:', error);
        showError('Hálózati hiba történt. Kérjük, próbálja újra később.');
        setInputErrorState(true);
    } finally {
        setLoadingState(false);
    }
});

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.className = 'error-message';
}

function showSuccess(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.className = 'error-message success-message';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function setLoadingState(isLoading) {
    registerButton.disabled = isLoading;
    if (isLoading) {
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'inline-flex';
    } else {
        buttonText.style.display = 'inline-block';
        buttonLoader.style.display = 'none';
    }
}

function resetInputStates() {
    usernameInput.classList.remove('error', 'success');
    emailInput.classList.remove('error', 'success');
    passwordInput.classList.remove('error', 'success');
    confirmPasswordInput.classList.remove('error', 'success');
}

function setInputErrorState(hasError) {
    if (hasError) {
        usernameInput.classList.add('error');
        emailInput.classList.add('error');
        passwordInput.classList.add('error');
        confirmPasswordInput.classList.add('error');
    }
}

usernameInput.addEventListener('input', () => {
    if (usernameInput.value.trim()) {
        usernameInput.classList.remove('error');
    }
});

emailInput.addEventListener('input', () => {
    if (emailInput.value.trim()) {
        emailInput.classList.remove('error');
    }
});

passwordInput.addEventListener('input', () => {
    if (passwordInput.value) {
        passwordInput.classList.remove('error');
    }
    
    if (confirmPasswordInput.value) {
        if (passwordInput.value === confirmPasswordInput.value) {
            confirmPasswordInput.classList.remove('error');
            confirmPasswordInput.classList.add('success');
        } else {
            confirmPasswordInput.classList.remove('success');
            confirmPasswordInput.classList.add('error');
        }
    }
});

confirmPasswordInput.addEventListener('input', () => {
    if (confirmPasswordInput.value) {
        if (passwordInput.value === confirmPasswordInput.value) {
            confirmPasswordInput.classList.remove('error');
            confirmPasswordInput.classList.add('success');
        } else {
            confirmPasswordInput.classList.remove('success');
            confirmPasswordInput.classList.add('error');
        }
    }
});

