var FacetedHeritor = {version: "1.0.0"};

FacetedHeritor.Load = function(){
  var ancestor = jQuery('input[name=ancestor]:checked');
  if(!ancestor.length){
    jQuery('li#current_ancestor').show();
  }
  jQuery('input[name=ancestor]').click(function(){
    jQuery('li#current_ancestor').hide();
  });
};

FacetedHeritor.Unload = function(){
  jQuery('li#current_ancestor').hide();
};
