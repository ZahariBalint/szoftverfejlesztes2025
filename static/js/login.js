const API_BASE_URL = 'http://127.0.0.1:5000/api';

// DOM elements
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const togglePasswordBtn = document.getElementById('togglePassword');
const errorMessage = document.getElementById('errorMessage');
const loginButton = document.getElementById('loginButton');
const buttonText = loginButton.querySelector('.button-text');
const buttonLoader = loginButton.querySelector('.button-loader');

togglePasswordBtn.addEventListener('click', () => {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    
    const eyeIcon = togglePasswordBtn.querySelector('.eye-icon');
    eyeIcon.textContent = type === 'password' ? '👁️' : '🙈';
});

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    hideError();
    resetInputStates();
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    
    if (!username || !password) {
        showError('Kérjük, töltse ki az összes mezőt!');
        return;
    }
    
    setLoadingState(true);
    
    try {
        const isEmail = username.includes('@');
        const requestBody = {
            password: password
        };
        
        if (isEmail) {
            requestBody.email = username;
        } else {
            requestBody.username = username;
        }
        
        // Make API call
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            const errorMsg = data.error || 'Bejelentkezési hiba történt';
            showError(errorMsg);
            setInputErrorState(true);
            return;
        }
        
        // Success - store token and user info
        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            const role = data.user?.role;
            if (role && role.toLowerCase() === 'admin') {
                window.location.href = '/admin';
            } else {
                window.location.href = '/dashboard';
            }
        } else {
            showError('Váratlan hiba történt a bejelentkezés során');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        showError('Hálózati hiba történt. Kérjük, próbálja újra később.');
        setInputErrorState(true);
    } finally {
        setLoadingState(false);
    }
});

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function setLoadingState(isLoading) {
    loginButton.disabled = isLoading;
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
    passwordInput.classList.remove('error', 'success');
}

function setInputErrorState(hasError) {
    if (hasError) {
        usernameInput.classList.add('error');
        passwordInput.classList.add('error');
    }
}

// Check if user is already logged in
window.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (token) {
        window.location.href = '/dashboard';
    }
});

const registerLink = document.getElementById('registerLink');
if (registerLink) {
    registerLink.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = '/register';
    });
}

usernameInput.addEventListener('input', () => {
    if (usernameInput.value.trim()) {
        usernameInput.classList.remove('error');
    }
});

passwordInput.addEventListener('input', () => {
    if (passwordInput.value) {
        passwordInput.classList.remove('error');
    }
});

