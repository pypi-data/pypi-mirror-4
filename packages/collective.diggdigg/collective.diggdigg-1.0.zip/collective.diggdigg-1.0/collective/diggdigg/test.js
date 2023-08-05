var dd_offset_from_content = 51;
var dd_top_offset_from_content = 51;
$(document).ready(function(){
  $('#content-core').parent().prepend('${view/get_start_embed}');
  $('#content-core').parent().append('${view/get_end_embed}');
  var script = document.createElement('script');
  $(script).attr('src', '${view/site_url}/++resource++collective.diggdigg/js/diggdigg-floating-bar.js');
  $('#content-core').parent().append(script);
});