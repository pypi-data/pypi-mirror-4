if(!window.Collective){
    var Collective = {version: 'collective.diffbot'};
}

Collective.Diffbot = function(context, options){
  var self = this;
  self.context = context;

  self.settings = {
    json: '@@diffbot.json'
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

Collective.Diffbot.prototype = {
  initialize: function(){
    var self = this;
    self.rel = self.context.attr('rel');
    self.rel = jQuery(self.rel);
    if(!self.rel.length){
      return;
    }

    self.context.click(function(evt){
      evt.preventDefault();
      return self.click();
    });
  },

  click: function(){
    var self = this;
    self.context.hide();
    self.rel.html('<img src="++resource++collective.diffbot.loader.gif" alt="Loading..."/>');
    self.rel.show();
    var query = {};
    query.url = self.context.attr('href');
    jQuery.getJSON(self.settings.json, query, function(data){
      return self.onClick(data);
    });
  },

  onClick: function(data){
    var self = this;
    if(data.error){
      window.location = self.context.attr('href');
    }
    if(!data.text){
      window.location = self.context.attr('href');
    }

    var text = data.text;
    text = text.replace(/\n/g, '</p><p>');
    var p = jQuery('<p>').html(text);
    self.rel.html(p);
  }
};

jQuery.fn.CollectiveDiffbot = function(options){
  return this.each(function(){
    var context = jQuery(this);
    var adapter = new Collective.Diffbot(context, options);
    context.data('CollectiveDiffbot', adapter);
  });
};

jQuery(document).ready(function(){
  var brains = jQuery('a.diffbot');
  if(!brains.length){
    return;
  }

  brains.CollectiveDiffbot();
});
