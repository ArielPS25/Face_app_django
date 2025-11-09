// Global JavaScript functions for Face Attendance System

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add loading state to buttons when clicked
    $('.btn').on('click', function() {
        var $btn = $(this);
        if (!$btn.hasClass('no-loading')) {
            var originalText = $btn.html();
            $btn.html('<span class="loading"></span> ' + $btn.text());
            
            // Restore original text after 2 seconds
            setTimeout(function() {
                $btn.html(originalText);
            }, 2000);
        }
    });

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });

    // Auto-refresh page data every 30 seconds (for dashboard)
    if (window.location.pathname === '/') {
        setInterval(function() {
            // Only refresh if page is visible
            if (!document.hidden) {
                updateDashboardStats();
            }
        }, 30000);
    }
});

// Function to update dashboard statistics
function updateDashboardStats() {
    $.ajax({
        url: '/api/dashboard-stats/',
        method: 'GET',
        success: function(data) {
            if (data.attendance_count !== undefined) {
                $('.attendance-count').text(data.attendance_count);
            }
            if (data.participation_count !== undefined) {
                $('.participation-count').text(data.participation_count);
            }
        },
        error: function() {
            console.log('Failed to update dashboard stats');
        }
    });
}

// Function to format timestamps
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Function to get confidence badge class
function getConfidenceBadgeClass(confidence) {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.6) return 'confidence-medium';
    return 'confidence-low';
}

// Function to show toast notifications
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    if (!$('#toast-container').length) {
        $('body').append('<div id="toast-container" class="toast-container position-fixed bottom-0 end-0 p-3"></div>');
    }
    
    const $toast = $(toastHtml);
    $('#toast-container').append($toast);
    
    const toast = new bootstrap.Toast($toast[0]);
    toast.show();
    
    // Remove toast element after it's hidden
    $toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Function to handle AJAX form submissions
function submitAjaxForm(formSelector, successCallback) {
    $(formSelector).on('submit', function(e) {
        e.preventDefault();
        
        const $form = $(this);
        const formData = new FormData(this);
        
        $.ajax({
            url: $form.attr('action'),
            method: $form.attr('method') || 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(response) {
                if (successCallback) {
                    successCallback(response);
                }
                showToast('Operation completed successfully!', 'success');
            },
            error: function(xhr) {
                let errorMessage = 'An error occurred. Please try again.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                showToast(errorMessage, 'danger');
            }
        });
    });
}

// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to handle image preview
function handleImagePreview(inputSelector, previewSelector) {
    $(inputSelector).on('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $(previewSelector).attr('src', e.target.result).show();
            };
            reader.readAsDataURL(file);
        }
    });
}

// Function to confirm dangerous actions
function confirmAction(message, callback) {
    if (confirm(message || 'Are you sure you want to perform this action?')) {
        if (callback) {
            callback();
        }
        return true;
    }
    return false;
}

// Export functions for use in other scripts
window.AppUtils = {
    showToast,
    submitAjaxForm,
    getCookie,
    handleImagePreview,
    confirmAction,
    formatTimestamp,
    getConfidenceBadgeClass
};