if(window.Browser === undefined){
  var Browser = {};
  Browser.onUploadComplete = function(){
    jQuery(document).trigger('eea-forms-widget-quickupload');
  };
}

jQuery(document).ready(function(){
  var context = jQuery('.eea-forms-quick-upload');
  if(!context.length){
    return;
  }

  context = context.parent();
  var relatedItems = jQuery('.eea-forms-autorelate', context);
  if(!relatedItems.length){
    return;
  }

  // EEAFormsQuickUpload not initialized, see eea.forms
  if(context.EEAFormsQuickUpload === undefined){
    return;
  }

  var options = {
    basket: relatedItems,
    relatedItems: relatedItems.text()
  };

  // Call jQuery plugin EEAFormsQuickUpload
  context.EEAFormsQuickUpload(options);

});
