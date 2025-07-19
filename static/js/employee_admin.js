// Dynamic subcategory filtering based on category selection (so that when we add or edit product and select subcategory 
// it shows appropriate subcategories based on category chosen)

$(document).ready(function() {
    
    $('#id_category').on('change', function() {
        var categoryId = $(this).val();
        var subcategorySelect = $('#id_subcategory');
        
        if (categoryId) {
            // Enable subcategory field
            subcategorySelect.prop('disabled', false);
            
            // Clear current options
            subcategorySelect.empty();
            subcategorySelect.append('<option value="">---------</option>');
            
            // Fetch subcategories for selected category
            $.ajax({
                url: '/employee-admin/get-subcategories/',
                data: {
                    'category_id': categoryId
                },
                dataType: 'json',
                success: function(data) {
                    $.each(data.subcategories, function(index, subcategory) {
                        subcategorySelect.append(
                            '<option value="' + subcategory.id + '">' + subcategory.name + '</option>'
                        );
                    });
                    
                    // If editing and there's a current subcategory, select it
                    var currentSubcategory = subcategorySelect.data('current-value');
                    if (currentSubcategory) {
                        subcategorySelect.val(currentSubcategory);
                    }
                },
                error: function() {
                    console.error('Error fetching subcategories');
                }
            });
        } else {
            // Disable and clear subcategory field if no category selected
            subcategorySelect.prop('disabled', true);
            subcategorySelect.empty();
            subcategorySelect.append('<option value="">---------</option>');
        }
    });
    
    // Initialize subcategory field state on page load
    if ($('#id_category').val()) {
        $('#id_category').trigger('change');
    }
});