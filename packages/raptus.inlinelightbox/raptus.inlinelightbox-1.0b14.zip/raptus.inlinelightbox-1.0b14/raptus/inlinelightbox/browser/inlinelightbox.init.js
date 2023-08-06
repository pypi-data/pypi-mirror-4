jQuery(document).ready(function() {
  var images = new Array();
  jQuery('a[rel^="inlinelightbox"]').each(function() {
    var o = jQuery(this);
    var rel = o.attr('rel');
    if(jQuery.inArray(rel, images) == -1)
      images.push(rel);
  });
  for(var i=0; i<images.length; i++) {
    jQuery('a[rel="'+images[i]+'"]').inlineLightBox(inlinelightbox.settings['standard']);
  }
});
