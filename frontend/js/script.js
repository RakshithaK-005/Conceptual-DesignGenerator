/* ====================================
   ARCHITECTURAL AI - SCRIPT.JS
   Interactive Features & Animations
   ==================================== */

// ====== SCROLL ANIMATIONS ======
document.addEventListener('DOMContentLoaded', () => {
    initScrollAnimations();
    initNavigation();
    initButtons();
    initFormValidation();
    console.log('✨ ArchAI Frontend Initialized');
});

// Scroll animation observer
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('reveal');
                // Only observe once
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all cards and elements with data-aos
    document.querySelectorAll('[data-aos], .feature-card, .step, .footer-section').forEach(el => {
        observer.observe(el);
    });
}

// ====== NAVIGATION ======
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === '#home')) {
            link.classList.add('active');
        }

        link.addEventListener('click', (e) => {
            // Remove active from all links
            navLinks.forEach(l => l.classList.remove('active'));
            // Add active to clicked link
            link.classList.add('active');

            // Smooth scroll for anchor links
            const targetId = link.getAttribute('href');
            if (targetId.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    // Scroll active link update
    window.addEventListener('scroll', updateActiveNav);
}

function updateActiveNav() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    let current = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// ====== BUTTON ANIMATIONS ======
function initButtons() {
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';

            // Remove old ripple if exists
            const oldRipple = this.querySelector('.ripple');
            if (oldRipple) oldRipple.remove();

            this.appendChild(ripple);

            // Remove ripple after animation
            setTimeout(() => ripple.remove(), 600);
        });

        // Add hover scale effect
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// ====== SMOOTH SCROLLING ======
function smoothScroll(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

function scrollToFeatures() {
    smoothScroll('#features');
}

// ====== FORM VALIDATION ======
function initFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            if (validateForm(form)) {
                showNotification('Form submitted successfully!', 'success');
                form.reset();
                // Here you would normally send data to backend
                console.log('Form valid, ready to submit');
            }
        });

        // Input focus animations
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement?.classList.add('focused');
            });

            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement?.classList.remove('focused');
                }
            });

            input.addEventListener('input', function() {
                validateField(this);
            });
        });
    });
}

function validateForm(form) {
    const fields = form.querySelectorAll('[required]');
    let isValid = true;

    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    return isValid;
}

function validateField(field) {
    let isValid = true;
    const value = field.value.trim();

    // Empty field check
    if (field.hasAttribute('required') && !value) {
        isValid = false;
    }

    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        isValid = emailRegex.test(value);
    }

    // Password validation (min 8 chars)
    if (field.type === 'password' && value) {
        isValid = value.length >= 8;
    }

    // Update visual feedback
    if (isValid) {
        field.style.borderColor = 'rgba(0, 212, 255, 0.5)';
        field.parentElement?.classList.remove('error');
    } else {
        field.style.borderColor = '#ff4444';
        field.parentElement?.classList.add('error');
    }

    return isValid;
}

// ====== PASSWORD TOGGLE ======
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const toggleBtn = document.querySelector(`[data-toggle="${inputId}"]`);

    if (input.type === 'password') {
        input.type = 'text';
        if (toggleBtn) toggleBtn.textContent = '👁‍🗨';
    } else {
        input.type = 'password';
        if (toggleBtn) toggleBtn.textContent = '👁';
    }
}

// ====== NOTIFICATIONS ======
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: inherit; cursor: pointer; font-size: 1.2rem;">×</button>
        </div>
    `;

    document.body.appendChild(notification);

    // Auto remove after 4 seconds
    setTimeout(() => {
        notification.remove();
    }, 4000);
}

// ====== PARALLAX EFFECT ======
function initParallax() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');

    window.addEventListener('scroll', () => {
        parallaxElements.forEach(element => {
            const speed = element.dataset.parallax || 0.5;
            const distance = window.scrollY;
            element.style.transform = `translateY(${distance * speed}px)`;
        });
    });
}

// ====== ANIMATED COUNTER ======
function animateCounter(element, target, duration = 2000) {
    let current = 0;
    const increment = target / (duration / 16);

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// ====== MOBILE MENU ======
document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.navbar-menu');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
            hamburger.classList.toggle('active');
        });

        // Close menu on link click
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.style.display = 'none';
                hamburger.classList.remove('active');
            });
        });
    }
});

// ====== THEME TOGGLE (OPTIONAL) ======
function initThemeToggle() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

// ====== PERFORMANCE: LAZY LOAD IMAGES ======
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
    }
}

// ====== PAGE TRANSITION EFFECTS ======
function pageTransition(URL) {
    let loader = document.querySelector('.page-transition');
    if (!loader) {
        loader = document.createElement('div');
        loader.className = 'page-transition';
        document.body.appendChild(loader);
    }

    loader.style.display = 'block';
    animation InitLoader 0.5s ease-in forwards;

    setTimeout(() => {
        window.location.href = URL;
    }, 300);
}

// ====== TYPING ANIMATION ======
function typeText(element, text, speed = 50) {
    element.textContent = '';
    let i = 0;

    const type = () => {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    };

    type();
}

// ====== GRADIENT TEXT ANIMATION ======
function initGradientText() {
    const gradientElements = document.querySelectorAll('.highlight');

    gradientElements.forEach(el => {
        const text = el.textContent;
        el.innerHTML = '';

        text.split('').forEach((char, index) => {
            const span = document.createElement('span');
            span.textContent = char;
            span.style.animation = `fadeInUp 0.5s ease-out ${index * 0.05}s both`;
            el.appendChild(span);
        });
    });
}

// ====== MOUSE FOLLOWER ======
function initMouseFollower() {
    const follower = document.createElement('div');
    follower.className = 'mouse-follower';
    document.body.appendChild(follower);

    document.addEventListener('mousemove', (e) => {
        follower.style.left = e.clientX + 'px';
        follower.style.top = e.clientY + 'px';
    });
}

// ====== SCROLL PROGRESS BAR ======
function initScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const winScroll = document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        progressBar.style.width = scrolled + '%';
    });
}

// ====== INIT ALL ON LOAD ======
window.addEventListener('load', () => {
    initParallax();
    initThemeToggle();
    initLazyLoading();
    initGradientText();
});

// ====== UTILITY: DEBOUNCE ======
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}
// ====== UTILITY: THROTTLE ======
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
// ====== COPY TO CLIPBOARD ======
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy', 'error');
    });
}

// ====== API INTEGRATION ======
// Configuration
const API_CONFIG = {
    BASE_URL: localStorage.getItem('apiUrl') || 'http://localhost:8000',
    TIMEOUT: 10000
};

// Set API URL (can be changed if backend is deployed elsewhere)
function setApiUrl(url) {
    localStorage.setItem('apiUrl', url);
    API_CONFIG.BASE_URL = url;
    console.log('API URL set to:', url);
}

// Get API URL
function getApiUrl() {
    return API_CONFIG.BASE_URL;
}

// Authentication - Token Management
const AUTH = {
    getToken: () => localStorage.getItem('authToken'),
    setToken: (token) => localStorage.setItem('authToken', token),
    removeToken: () => localStorage.removeItem('authToken'),
    getUser: () => {
        const userStr = localStorage.getItem('currentUser');
        return userStr ? JSON.parse(userStr) : null;
    },
    setUser: (user) => localStorage.setItem('currentUser', JSON.stringify(user)),
    removeUser: () => localStorage.removeItem('currentUser'),
    isAuthenticated: () => !!localStorage.getItem('authToken')
};

// API Request Helper
async function apiCall(endpoint, options = {}) {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    // Add authorization token if it exists
    const token = AUTH.getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers,
        timeout: API_CONFIG.TIMEOUT
    };

    try {
        const response = await fetch(url, config);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || `API Error: ${response.status}`);
        }

        return { success: true, data, status: response.status };
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message, data: null };
    }
}

// Authentication APIs
const API = {
    // User Registration
    register: async (userData) => {
        const result = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify({
                email: userData.email,
                username: userData.username || userData.email.split('@')[0],
                password: userData.password,
                full_name: userData.full_name || ''
            })
        });

        if (result.success && result.data.access_token) {
            AUTH.setToken(result.data.access_token);
            AUTH.setUser(result.data);
        }

        return result;
    },

    // User Login
    login: async (email, password) => {
        // FastAPI ArchAI uses /auth/login with JSON body
        const url = `${API_CONFIG.BASE_URL}/auth/login`;
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            // Store the token from response
            if (data.access_token) {
                AUTH.setToken(data.access_token);
                
                // Fetch user info
                const userResult = await API.getCurrentUser();
                if (userResult.success) {
                    AUTH.setUser(userResult.data);
                }
            }

            return { success: true, data };
        } catch (error) {
            console.error('Login Error:', error);
            return { success: false, error: error.message };
        }
    },

    // Logout
    logout: () => {
        AUTH.removeToken();
        AUTH.removeUser();
        return { success: true };
    },

    // Get Current User
    getCurrentUser: async () => {
        return apiCall('/users/me', { method: 'GET' });
    },

    // Send Contact Form
    sendContact: async (contactData) => {
        return apiCall('/contact', {
            method: 'POST',
            body: JSON.stringify({
                name: contactData.name,
                email: contactData.email,
                phone: contactData.phone || '',
                subject: contactData.subject,
                message: contactData.message
            })
        });
    },

    // Get Projects (for authenticated users)
    getProjects: async () => {
        return apiCall('/projects', { method: 'GET' });
    },

    // Create New Project
    createProject: async (projectData) => {
        return apiCall('/projects', {
            method: 'POST',
            body: JSON.stringify(projectData)
        });
    },

    // Generate Design
    generateDesign: async (projectId, designData) => {
        return apiCall(`/designs`, {
            method: 'POST',
            body: JSON.stringify({
                project_id: projectId,
                ...designData
            })
        });
    },

    // Analyze Environment
    analyzeEnvironment: async (projectId, analysisData) => {
        return apiCall('/environment/analyze', {
            method: 'POST',
            body: JSON.stringify({
                project_id: projectId,
                ...analysisData
            })
        });
    },

    // Validate Compliance
    validateCompliance: async (projectId, designData) => {
        return apiCall('/compliance/validate', {
            method: 'POST',
            body: JSON.stringify({
                project_id: projectId,
                ...designData
            })
        });
    }
};

// Update UI based on authentication state
function updateAuthUI() {
    const isAuth = AUTH.isAuthenticated();
    const user = AUTH.getUser();
    
    // Update navbar if user is logged in
    if (isAuth && user) {
        const authSection = document.querySelector('.auth-section') ||
            document.querySelector('nav .navbar-menu li:last-child');
        
        if (authSection) {
            // You can add a user menu here
            console.log('User logged in:', user);
        }
    }
}

// Initialize auth UI on page load
document.addEventListener('DOMContentLoaded', updateAuthUI);

// ====== CONSOLE EASTER EGG ======
console.log('%c✨ ArchAI - AI-Powered Architectural Design Generator ✨', 
    'color: #00d4ff; font-size: 16px; font-weight: bold; text-shadow: 0 0 10px #00d4ff;');
console.log('%cLet\'s create amazing architecture together!', 
    'color: #6600ff; font-size: 14px;');
