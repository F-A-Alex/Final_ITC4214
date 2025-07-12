$(document).ready(function() {
    // Auto-submit quantity changes after a delay
    let quantityTimeout;
    $('.quantity-input').on('input', function() {
        clearTimeout(quantityTimeout);
        const form = $(this).closest('form');
        quantityTimeout = setTimeout(function() {
            form.submit();
        }, 1000);
    });
});