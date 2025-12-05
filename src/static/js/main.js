/**
 * Black Magic - Minimal JS
 */
(function() {
    'use strict';

    // Auto-dismiss messages
    document.querySelectorAll('.message').forEach(function(msg) {
        setTimeout(function() {
            msg.style.opacity = '0';
            setTimeout(function() { msg.remove(); }, 300);
        }, 4000);
    });
})();
