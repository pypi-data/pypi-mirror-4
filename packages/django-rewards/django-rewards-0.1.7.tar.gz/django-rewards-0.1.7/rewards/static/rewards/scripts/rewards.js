$(function() {
    $(document).on('hover', '.goal-stars .star', function(e) {
        if(e.type == "mouseenter") {
            $(this).addClass('hover');
        } else if(e.type == "mouseleave") {
            $(this).removeClass('hover');
        }
    });

    var childFancyBox= {
        'wrapCSS': 'children',
        'padding': 30,
        'helpers': {
            overlay: {
                opacity: 0.67,
                css: {'background-color': '#000'}
            }
        }
    };

    // AJAX when clicking on goal stars.
    $(document).on('click', '.goal-stars .star', function() {
        var star = $(this),
            goalsWrapper = star.closest('.goals-wrapper'),
            incrementForm = goalsWrapper.find('.increment-form'),
            decrementForm = goalsWrapper.find('.decrement-form');

        var formSubmit = function(form, targetStar) {
            targetStar.toggleClass('selected').removeClass('hover');
            $.ajax({
                type: 'post',
                url: form.attr('action'),
                data: form.serialize(),
                success: function (data, textResponce) {
                    if (typeof(data)=='string') {
                        $.fancybox(data, childFancyBox);
                    }
                },
                error: function() {
                    targetStar.toggleClass('selected');
                    goalsWrapper.slideDown()
                }
            });
        };
        // Submit forms
        if(star.is('.selected')) {
            formSubmit(decrementForm, star);
        } else {
            formSubmit(incrementForm, star);
        }

        // If there aren't any more stars open a lightbox.
        if(goalsWrapper.find('.star:not(.selected)').not(star).length === 0) {
            goalsWrapper.slideUp()
        }
    });
});
