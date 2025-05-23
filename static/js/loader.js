document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    const loaderContainer = document.getElementById('loader-container');
    
    // Add form submission event listeners
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            // Show loader when form is submitted
            if (loaderContainer) {
                loaderContainer.style.display = 'flex';
                console.log('Loader displayed');
            }
        });
    });
}); 