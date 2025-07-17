
$(document).ready(function() {
    // Auto-submit quantity changes on change (removed timeout for immediate response)
    $('.quantity-input').on('change', function() {
        $(this).closest('form').submit();
    });
});