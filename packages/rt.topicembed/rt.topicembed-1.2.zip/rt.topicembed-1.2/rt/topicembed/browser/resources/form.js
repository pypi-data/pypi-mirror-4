(function($) {
    var code;
    var js_url;
    var scripts = document.getElementsByTagName('script');
    var myScript = scripts[ scripts.length - 1 ];
    var queryString = myScript.src.replace(/^[^\?]+\??/,'');
    var uid = queryString.replace('uid=','');
    if (uid == ''){
        uid = 'element_id';
    };
    var element_id = 'embed_' + uid;
    js_url = window.location.href.replace('topic_embed', 'embed.js');
    code = '<div id=\'' + element_id + '\' class=\'embedwidget\'></div>\n' +
           '&lt;script&gt;\n' +
           '    (function() {\n' +
           '        var s = document.createElement(\'script\');\n' +
           '        s.src = \'' + js_url + '\';\n' +
           '        s.async = true;\n' +
           '        window.topic_options = (window.topic_options || []).concat([ { element_id: \'' + element_id + '\', elements_length: %ELEMENTS%, embed_css: %CSS%, new_window: %NEW_WINDOW%, image_size: "%IMAGE_SIZE%" }]);\n' +
           '        document.body.appendChild(s);\n' +
           '    }());\n' +
           '&lt;/script&gt;'

    function render(result){
        elements_length = $('#number_of_items').val();
        if (elements_length === undefined || elements_length == ''){
            elements_length = 5;
        }
        embed_css = $('#include_css').is(':checked')
        if (embed_css === undefined){
            embed_css = true;
        }
        new_window = $('#new_window_open').is(':checked')
        if (new_window === undefined){
            new_window = true;
        }
        image_size = $("input:radio[name=image_size]:checked").val()
        if (image_size === undefined){
            image_size = 'thumb';
        }
        result = result.replace('%ELEMENTS%', elements_length);
        result = result.replace('%CSS%', embed_css);
        result = result.replace('%NEW_WINDOW%', new_window);
        result = result.replace('%IMAGE_SIZE%', image_size);
        $('#embedcode').html(result);
    };
    render(code);
    $('#embedcode').click(function(){
        this.select();
    });
    $('#number_of_items').keyup(function(){
        render(code);
    });
    $('#new_window_open').click(function(){
        render(code);
    });
    $('#include_css').click(function(){
        render(code);
    });
    $('input:radio[name=image_size]').click(function(){
        render(code);
    });
})(jQuery);
