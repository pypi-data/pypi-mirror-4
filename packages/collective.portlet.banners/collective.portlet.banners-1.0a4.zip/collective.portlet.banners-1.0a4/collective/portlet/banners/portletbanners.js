jq.fn.portletBanners = function(delay, fade_speed) {
    jq(this).each(function() {
        var container = jq(this);
        var items = container.find('.portletbanner');
        container.height(container.height());
        container.width(container.width());
        container.css('position', 'relative');
        items.css({
            'position': 'absolute',
            'top': 0,
            'left': 0
        });
        var active = items.eq(0);           
        function rotate() {
            var next = active.next('.portletbanner');
            if (next.length == 0) {
                next = items.eq(0);
            }
            active.fadeOut(fade_speed);
            next.fadeIn(fade_speed, function () {
               active = next;
            });
        }
        var rotate_timer = setInterval(rotate, delay);
    });
    return this;
};