var sc_plugin = function() {

    function add_media_listeners(sound) {
        clicks = 1;
        $('#play-pause').click(function() {
            clicks++;
            if(clicks % 2 == 0) { // if even
                sound.pause();
                $(this).html('Play');
            } else {
                sound.play();
                $(this).html('Pause');
            }
        });
    }

    function async_like() {
        $('#like').click(function(e) {
            $.ajax({
                url: $('#like').attr('href')
            }).done(function(html) {
                console.log(html);
            });

            e.preventDefault();
        });
    }

    /**
     * Public functions, or interfaces
     */
    return {
        init : function(sound) {
            sound.play();
            async_like();
        },

        add_media_listeners : function(sound) {
            add_media_listeners(sound);
        }
    }
}();
