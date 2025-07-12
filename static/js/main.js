$(document).ready(function() {
    // Product card click handling
    $('.product-card').on('click', function(e) {
        // Don't navigate if clicking on buttons
        if (!$(e.target).closest('.btn, .btn-group').length) {
            var url = $(this).data('url') || $(this).find('a[href*="product"]').first().attr('href');
            if (url) {
                window.location.href = url;
            }
        }
    });

    // Category card click handling
    $('.category-card').on('click', function() {
        var url = $(this).find('a').attr('href');
        if (url) {
            window.location.href = url;
        }
    });

    // Product image hover effects
    $('.product-card img').on('mouseenter', function() {
        $(this).css('transform', 'scale(1.05)');
    }).on('mouseleave', function() {
        $(this).css('transform', 'scale(1)');
    });
});