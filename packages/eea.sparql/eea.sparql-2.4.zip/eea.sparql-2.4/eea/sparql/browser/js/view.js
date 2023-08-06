if (window.EEASparql === undefined){
  var EEASparql = {version: '1.0'};
}

/* EEASparql.Preview
*/
EEASparql.Preview = function(context, options){
  var self = this;
  self.context = context;
  self.settings = {};

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEASparql.Preview.prototype = {
  initialize: function(){
    var self = this;
    self.overlay = jQuery('#eea-sparql-overlay');
    if(!self.overlay.length){
      self.overlay = jQuery('<div>')
        .attr('id', 'eea-sparql-overlay')
        .append(jQuery('<div>').addClass('contentWrap'))
        .appendTo(jQuery('body'));
    }

    self.context.attr('rel', '#eea-sparql-overlay');
    self.context.overlay({
      mask: 'black',
      onBeforeLoad: function() {
        var wrap = this.getOverlay().find('.contentWrap');
        wrap.load(this.getTrigger().attr("href") + '/@@sparql.preview');
      },
      onClose: function(){
        var wrap = this.getOverlay().find('.contentWrap');
        wrap.html('<div class="loading">Loading preview...</div>');

      }
    });
  }
};

/* jQuery plugin for EEASparql.Preview
*/
jQuery.fn.EEASparqlPreview = function(options){
  return this.each(function(){
    var context = jQuery(this).addClass('eea');
    var preview = new EEASparql.Preview(context, options);
    context.data('EEASparqlPreview', preview);
  });
};
