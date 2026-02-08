/*
 * FormBuilder Admin JavaScript
 * - Auto-updates position fields for FormField and FieldOption inlines
 * - Handles formset add/remove events to maintain sequential ordering
 */

(function() {
    'use strict';
    
    // Wait for document ready and check for jQuery
    function init() {
        // Try multiple jQuery sources
        const $ = window.django && window.django.jQuery ? window.django.jQuery : 
                  window.jQuery ? window.jQuery : 
                  window.$ ? window.$ : null;
        
        if (!$) {
            console.error('FormBuilder Admin: jQuery not found. Position auto-update disabled.');
            return;
        }
        
        console.log('FormBuilder Admin: jQuery found, initializing...');
        
        /**
         * Updates position fields for all visible rows in a formset
         * @param {string} formsetPrefix - The formset prefix identifier
         */
        function updatePositions(formsetPrefix) {
            console.log('Updating positions for formset:', formsetPrefix);
            
            // Find all inline rows - try multiple selectors
            let rows = $(`.inline-related:has(input[name^="${formsetPrefix}-"])`);
            
            // Alternative: find by the inline group
            if (rows.length === 0) {
                rows = $(`#${formsetPrefix}-group .inline-related`);
            }
            
            // Filter out deleted rows
            rows = rows.filter(function() {
                const deleteCheckbox = $(this).find('input[name$="-DELETE"]');
                const isDeleted = deleteCheckbox.length && deleteCheckbox.is(':checked');
                return !isDeleted;
            });
            
            console.log(`Found ${rows.length} rows to update`);
            
            // Re-index positions sequentially starting from 1
            rows.each(function(index) {
                const $row = $(this);
                const positionInput = $row.find('input[name$="-position"]');
                
                if (positionInput.length) {
                    const newPosition = index + 1;
                    const oldValue = positionInput.val();
                    
                    if (oldValue != newPosition) {
                        console.log(`Row ${index}: Updating position from ${oldValue} to ${newPosition}`);
                        positionInput.val(newPosition);
                        
                        // Visual feedback
                        positionInput.addClass('position-updated');
                        setTimeout(() => positionInput.removeClass('position-updated'), 800);
                    }
                }
            });
        }
        
        // Listen to Django's formset events
        $(document).on('formset:added', function(event, $row, formsetName) {
            console.log('Formset added event:', formsetName, $row);
            
            // If parameters aren't provided, try to find all formsets and update them
            if (!formsetName || !$row || !$row.length) {
                console.log('FormBuilder Admin: Parameters not provided, updating all formsets');
                $('.inline-group').each(function() {
                    const groupId = $(this).attr('id');
                    if (groupId) {
                        const fsName = groupId.replace('-group', '');
                        console.log('Updating formset after add:', fsName);
                        setTimeout(() => updatePositions(fsName), 200);
                    }
                });
                return;
            }
            
            if (!formsetName) {
                // Try to extract from the row
                const nameAttr = $row.find('input[name*="-"]').first().attr('name');
                if (nameAttr) {
                    formsetName = nameAttr.split('-')[0];
                }
            }
            
            if (formsetName) {
                console.log('Updating after add:', formsetName);
                setTimeout(() => updatePositions(formsetName), 200);
            }
        });
        
        $(document).on('formset:removed', function(event, $row, formsetName) {
            console.log('Formset removed event:', formsetName, $row);
            
            // If parameters aren't provided, try to find all formsets and update them
            if (!formsetName || !$row || !$row.length) {
                console.log('FormBuilder Admin: Parameters not provided, updating all formsets');
                $('.inline-group').each(function() {
                    const groupId = $(this).attr('id');
                    if (groupId) {
                        const fsName = groupId.replace('-group', '');
                        console.log('Updating formset after remove:', fsName);
                        setTimeout(() => updatePositions(fsName), 200);
                    }
                });
                return;
            }
            
            if (!formsetName) {
                const nameAttr = $row.find('input[name*="-"]').first().attr('name');
                if (nameAttr) {
                    formsetName = nameAttr.split('-')[0];
                }
            }
            
            if (formsetName) {
                console.log('Updating after remove:', formsetName);
                setTimeout(() => updatePositions(formsetName), 200);
            }
        });
        
        // Handle manual deletion checkbox changes
        $(document).on('change', 'input[name$="-DELETE"]', function() {
            const $row = $(this).closest('.inline-related');
            const nameAttr = $row.find('input[name$="-position"]').attr('name');
            
            if (nameAttr) {
                const formsetName = nameAttr.split('-')[0];
                console.log('Delete checkbox changed, updating:', formsetName);
                setTimeout(() => updatePositions(formsetName), 200);
            }
        });
        
        // Initialize on page load
        $(document).ready(function() {
            console.log('FormBuilder Admin: Initializing position auto-update');
            
            // Find all formsets and update their positions
            $('.inline-group').each(function() {
                const $group = $(this);
                const groupId = $group.attr('id');
                
                if (groupId) {
                    // Extract formset name from id (e.g., "fields-group" -> "fields")
                    const formsetName = groupId.replace('-group', '');
                    console.log('Initializing formset:', formsetName);
                    updatePositions(formsetName);
                }
            });
            
            console.log('FormBuilder Admin: Initialization complete');
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
