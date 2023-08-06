CubicWeb.require('ajax.js');

function cancelSelectedMergeTag(eid) {
    var holder = jQuery('#tagmergeformholder' + eid);
    jQuery('#acmergetag').val('');
    holder.children("div#tagged_entities_holder").empty();
    toggleVisibility("sgformbuttons");
}

function mergeTags(eid) {
    var input = jQuery('#tagmergeformholder' + eid + ' input')[0];
    var name = jQuery('#acmergetag').val().strip(',');
    var d = asyncRemoteExec('merge_tags', eid, name);

    d.addCallback(function(tagprimaryview) {
      var dom = getDomFromResponse(tagprimaryview);
      //jQuery('#contentmain').replaceWith(dom);
      jQuery('#contentmain').empty().append(dom);
      if (jQuery('#sgformbuttons').hasClass('hidden') == false){
         toggleVisibility("sgformbuttons");
       }
      updateMessage(_("tag has been merged with ")+ name );
      buildWidgets();
      initMergeTags();
   });

}

function tagToMergeSelector(eid) {
  var holder = jQuery('#tagmergeformholder' + eid);
  var name = jQuery('#acmergetag').val().strip(',');
  var entities = asyncRemoteExec("tagged_entity_html", name);
  entities.addCallback(function  (entitieslist) {
    log(entitieslist);
    var dom = getDomFromResponse(entitieslist);
    jQuery('#tagged_entities_holder').empty().append(dom);
    if( jQuery("#tagged_entities_holder").find('div#taggedEntities').length ) {
        jQuery('#sgformbuttons').show();}
    else{
      jQuery('#sgformbuttons').hide();
    }
    });
  jQuery('#acmergetag').focus();
};

function initMergeTags(){
  var input = jQuery('#acmergetag');
  var tageid = jQuery('#tageid').val();
  input.keypress(function (event) {
    if (event.keyCode == KEYS.KEY_ENTER) {
      if (input.val()){
      if (jQuery('#sgformbuttons').hasClass('hidden')){
        toggleVisibility("sgformbuttons");
        }
      tagToMergeSelector(tageid);
      }
    }
  });
  jQuery(input).focus();
}



$(document).ready(function() {
  var input = jQuery('#acmergetag');
  initMergeTags();
});


CubicWeb.provide('tags.js');