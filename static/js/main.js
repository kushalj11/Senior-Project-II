/**
 * BookShelf - Main JavaScript File
 * Handles client-side interactivity
 */

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(flash) {
        setTimeout(function() {
            flash.style.transition = 'opacity 0.5s';
            flash.style.opacity = '0';
            setTimeout(function() {
                flash.remove();
            }, 500);
        }, 5000);
    });
});

// Form validation for registration
const registerForm = document.querySelector('form[action*="register"]');
if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        if (password !== confirmPassword) {
            e.preventDefault();
            alert('Passwords do not match!');
            return false;
        }
        
        if (password.length < 8) {
            e.preventDefault();
            alert('Password must be at least 8 characters long!');
            return false;
        }
    });
}

// Confirm before removing book from shelf
const removeButtons = document.querySelectorAll('form[action*="remove"] button');
removeButtons.forEach(function(button) {
    if (!button.getAttribute('onclick')) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to remove this book from the shelf?')) {
                e.preventDefault();
                return false;
            }
        });
    }
});

// Search input auto-focus
const searchInput = document.getElementById('search-query');
if (searchInput && window.location.pathname === '/search') {
    searchInput.focus();
}

// Star rating hover effect
const starLabels = document.querySelectorAll('.star-rating-input label');
if (starLabels.length > 0) {
    starLabels.forEach(function(label, index) {
        label.addEventListener('mouseenter', function() {
            // Highlight all stars up to this one
            for (let i = starLabels.length - 1; i >= starLabels.length - 1 - index; i--) {
                starLabels[i].style.color = '#f59e0b';
            }
        });
        
        label.addEventListener('mouseleave', function() {
            // Reset color
            starLabels.forEach(function(l) {
                l.style.color = '';
            });
        });
    });
}

// Form submission loading state
const forms = document.querySelectorAll('form');
forms.forEach(function(form) {
    form.addEventListener('submit', function(e) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton && !submitButton.disabled) {
            submitButton.disabled = true;
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Processing...';
            
            // Re-enable after 3 seconds as a fallback
            setTimeout(function() {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }, 3000);
        }
    });
});

// Image preview for book cover upload
const coverImageInput = document.getElementById('cover_image');
if (coverImageInput) {
    coverImageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Check file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size must be less than 5MB');
                e.target.value = '';
                return;
            }
            
            // Check file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                alert('Please upload a valid image file (JPG, PNG, or GIF)');
                e.target.value = '';
                return;
            }
            
            // Show preview (optional enhancement)
            const reader = new FileReader();
            reader.onload = function(event) {
                // You could add an image preview here if desired
                console.log('Image loaded successfully');
            };
            reader.readAsDataURL(file);
        }
    });
}

// Scroll to top button (optional enhancement)
const scrollToTopBtn = document.createElement('button');
scrollToTopBtn.innerHTML = '↑';
scrollToTopBtn.className = 'scroll-to-top';
scrollToTopBtn.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: #2563eb;
    color: white;
    border: none;
    font-size: 24px;
    cursor: pointer;
    display: none;
    z-index: 999;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s;
`;

document.body.appendChild(scrollToTopBtn);

window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
        scrollToTopBtn.style.display = 'block';
    } else {
        scrollToTopBtn.style.display = 'none';
    }
});

scrollToTopBtn.addEventListener('click', function() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

scrollToTopBtn.addEventListener('mouseenter', function() {
    this.style.backgroundColor = '#1d4ed8';
    this.style.transform = 'scale(1.1)';
});

scrollToTopBtn.addEventListener('mouseleave', function() {
    this.style.backgroundColor = '#2563eb';
    this.style.transform = 'scale(1)';
});

// Console message
console.log('📚 BookShelf - Reading Management Platform');
console.log('Developed with Flask, SQLAlchemy, and vanilla JavaScript');
