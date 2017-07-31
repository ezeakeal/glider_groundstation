function handleImages(telemJson) {
    image_panel = $('#image_display');
    var image_list = telemJson['images'];
    for (var image_id in image_list) {
        var image_data = image_list[image_id];
        var dom_id = image_id .slice(0, -4)
        if ($('#' + dom_id ).length && image_data['status'] == "Finished")
            continue;
        image_data['parts'] = image_data['parts'].join(" ");
        img_panel_content = [
            '<div class="col-xs-12" id="'+dom_id +'">',
                '<div class="col-xs-6">',
                    '<img class="img-responsive" src="static/images/' + image_id + '">"',
                '</div>',
                '<div class="col-xs-6">',
                    '<pre>'+JSON.stringify(image_data, null, 2)+'</pre>',
                '</div>',
            '</div>'
        ].join("");

        if ($('#' + dom_id ).length)
            $('#' + dom_id ).html(img_panel_content);
        else
            image_panel.prepend(img_panel_content);
    }
}

