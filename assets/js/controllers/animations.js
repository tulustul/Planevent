'use strict';

angular.module('planevent').animation('.slideAnimation', function() {
    return {
        addClass : function(element, className, done) {
            $(element).removeClass(className);
            jQuery(element).slideUp(500);

            return function(isCancelled) {
                $(element).addClass(className);
                if(isCancelled) {
                    jQuery(element).stop();
                }
            };
        },

        removeClass : function(element, className, done) {
            element.css('display', 'none');
            jQuery(element).slideDown(500);

            return function(isCancelled) {
                if(isCancelled) {
                    jQuery(element).stop();
                }
            };
        }
    };
});

angular.module('planevent').animation('.slideAnimation2', function() {
    return {
        addClass : function(element, className, done) {
            $(element).removeClass(className);
            jQuery(element).slideUp(500);

            return function(isCancelled) {
                $(element).addClass(className);
                if(isCancelled) {
                    jQuery(element).stop();
                }
            };
        },

        removeClass : function(element, className, done) {
            element.css('display', 'none');
            jQuery(element).slideDown(500);

            return function(isCancelled) {
                if(isCancelled) {
                    jQuery(element).stop();
                }
            };
        }
    };
});

