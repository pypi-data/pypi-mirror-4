function acr_delete_slice(delete_slice_path, slice_id)
{
  var btn = "#edit_slice_" + slice_id;

    if (confirm('Really delete slice?')) {
        var del_uri = delete_slice_path+'/'+slice_id;
        jQuery.get(del_uri, function() {window.location.reload(true);});
    }
}

function acr_move_slice(move_slice_path, slice_id, value)
{
  var move_uri = move_slice_path + '/' + slice_id + '?value=' + value;
    jQuery.get(move_uri, function() {window.location.reload(true);});
}

function acr_show_slice_bar(slice, enabled)
{
  var slicebar = jQuery(slice).find('.acr_edit_button');
    if (enabled) {
        slicebar.css('z-index', 999);
        slicebar.css('opacity', 1);
    } else {
        slicebar.css('z-index', 0);
        slicebar.css('opacity', 0.3);
    }
}

function acr_show_menu(where)
{
  var menu = jQuery(where).parent().children('ul');
    menu.toggle();
    return false;
}

var edit_bar_visible = true;
function acrToggleEditBarVisibility(){
  edit_bar_visible ? jQuery(".acr_edit_container").hide() : jQuery(".acr_edit_container").show();
  edit_bar_visible = !edit_bar_visible;
  return false;
}

var selected_slices = [];
function acrAddToSelected(btn, slice){
  var slice_index = jQuery.inArray(slice, selected_slices);
  if (slice_index < 0){
    jQuery(btn).css('background-color', 'red');
    selected_slices.push(slice);
  }else{
    jQuery(btn).css('background-color', 'gray');
    selected_slices.splice(slice_index,1);
  }
  return false;
}
