
$(document).ready(function() {


    
    // Auto-submit quantity changes on change 
    $('.quantity-input').on('change', function() {
        $(this).closest('form').submit();
    });
});