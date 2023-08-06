function acr_asset_choose(btn, assets_box_url) {
    var selected_asset = jQuery(btn).siblings('input').val();
    selected_asset = selected_asset.split(':')[1];
    jQuery(btn).siblings('.asset_box_container').load(assets_box_url+'?uid='+selected_asset);
}

function acr_asset_use(entry, assets_box_url, asset_id, asset_name) {
    var assets_box = jQuery(entry).parents('.asset_box_container');
    assets_box.siblings('.current_asset').text(asset_name);
    assets_box.siblings('input').val('asset:'+asset_id);
    assets_box.html('');
}

function acr_asset_upload(entry, assets_upload_url) {
    
}
