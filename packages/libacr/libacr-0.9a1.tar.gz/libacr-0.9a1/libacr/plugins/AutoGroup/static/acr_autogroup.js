/**
 * ACR autogroup plugin
 */

function acrGroupSlices(page){
  var url = '/plugins/autogroup/group/' + page + '/' + selected_slices.join("/");
  jQuery.get(url, function(){
    window.location.reload();
  });

}