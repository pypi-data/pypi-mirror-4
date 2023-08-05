django.jQuery(function($) {
    var importer_form_filter = {
        OSM:new Array('field-filtr', 'field-default_name', 'field-categories',
                      'field-source', 'field-overwrite'),
        KML:new Array('field-source', 'field-source_file', 'field-default_name',
                      'field-filtr', 'field-zipped', 'field-origin',
                      'field-license', 'field-categories', 'field-overwrite'),
        SHP:new Array('field-source', 'field-source_file', 'field-default_name',
                      'field-zipped', 'field-origin', 'field-srid',
                      'field-license', 'field-categories', 'field-overwrite'),
        RSS:new Array('field-source', 'field-default_name', 'field-origin',
                      'field-srid', 'field-license', 'field-categories',
                      'field-overwrite'),
        CSV:new Array('field-source', 'field-source_file', 'field-default_name',
                      'field-origin', 'field-srid', 'field-license',
                      'field-categories', 'field-overwrite')
    }
    var map_initialized;
    function refresh_importer_form(){
        $('.form-row').not('.field-importer_type').hide();
        var importer_val = $('.field-importer_type select').val();
        if (!importer_val) return;
        var form_filters = importer_form_filter[importer_val];
        for (k=0; k<form_filters.length;k++){
            $('.form-row.'+form_filters[k]).show();
        }
        if (importer_val == 'KML'){
            $('.help-kml').show();
        } else {
            $('.help-kml').hide();
        }
        if (importer_val == 'OSM'){
            $('.form-row.field-filtr').addClass('field-map');
            $('#map_edit').show();
            if(!$('#id_source').val()){
                $('#id_source').val(default_xapi);
            }
            $('#id_filtr').attr('readonly', true);
            $('.help-osm').show();
            $('.input-osm').show();
            if (!map_initialized){
                init_map_form();
                map_initialized = true;
            }
        } else {
            $('.form-row.field-filtr').removeClass('field-map');
            $('#id_filtr').attr('readonly', false);
            $('#map_edit').hide();
            $('.help-osm').hide();
            $('.input-osm').hide();
            if($('#id_source').val() == default_xapi) $('#id_source').val('');
        }
    }
    refresh_importer_form();
    $('.field-importer_type select').change(refresh_importer_form);
    function refresh_filtr_form(){
        if (!$('#upper_left_lat').val() ||
           !parseFloat($('#upper_left_lat').val())){
            alert(msg_missing_area);
            return false;
        }
        if (!$('input[name=id_filtr_type]:checked').val()){
            alert(msg_missing_type);
            return false;
        }
        if (!$('#id_filtr_tag').val()){
            alert(msg_missing_filtr);
            return false;
        }
        value = $('input[name=id_filtr_type]:checked').val();
        value += '[' + $("#id_filtr_tag").val() + ']';
        value += '[bbox=';
        value += $('#upper_left_lon').val() + ',';
        value += $('#lower_right_lat').val() + ',';
        value += $('#lower_right_lon').val() + ',';
        value += $('#upper_left_lat').val();
        value += ']';
        $('#id_filtr').val(value);
        return false;
    }
    $('#id_refresh_filtr').click(refresh_filtr_form);
});
