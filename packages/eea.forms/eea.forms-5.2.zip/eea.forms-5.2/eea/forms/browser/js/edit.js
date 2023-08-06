if(window.EEAFormsEdit === undefined){
  var EEAFormsEdit = {'version': '1.0'};
}

// Custom jQuery Tools effect
if((jQuery.tools !== undefined) && (jQuery.tools.tabs !== undefined)){
  jQuery.tools.tabs.addEffect("eea-forms", function(tabIndex, done) {
    // hide all panes and show the one that is clicked
    var easing = jQuery.easing.easeOutQuad ? 'easeOutQuad' : 'swing';
    var panes = this.getPanes();
    if(panes.effect === undefined){
      panes.hide().eq(tabIndex).show();
    }else{
      var index = this.getIndex() !== undefined ? this.getIndex() : 0;
      var direction = 'right';
      if(tabIndex < index){
        direction = 'left';
      }
      panes.hide().eq(tabIndex).EEASlide({duration: 500, easing: easing, direction: direction});
    }
    // the supplied callback must be called after the effect has finished its job
    done.call();
  });
}


/* Make Tabs in ATCT edit form a wizard like form
*/
EEAFormsEdit.Wizard = function(context, options){
  var self = this;
  self.context = context;
  self.context.parent().addClass('eea-forms-wizard');
  self.settings = {};

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEAFormsEdit.Wizard.prototype = {
  initialize: function(){
    var self = this;
    self.api = self.context.data('tabs');
    self.api.onClick(function(e, index){
      self.toggleButtons(index);
    });
    self.api.getConf().effect = 'eea-forms';
    self.leftButton();
    self.rightButton();
    self.toggleButtons();
  },

  leftButton: function(){
    var self = this;
    self.left = jQuery('<div>')
      .addClass('wizard-left')
      .html('<span>&lsaquo;</span>')
      .click(function(){
        self.api.prev();
        self.toggleButtons();
    }).prependTo(self.context.parent());

    jQuery(document).bind('eea-wizard-changed', function(evt, data){
      data = data || {};
      var parent_height = self.left.parent().height() - 70;
      var height = data.height || parent_height || '80%';
      self.left.height(height);
      self.right.height(height);
    });
  },

  rightButton: function(){
    var self = this;
    self.right = jQuery('<div>')
      .addClass('wizard-right')
      .html('<span>&rsaquo;</span>')
      .click(function(){
        self.api.next();
        self.toggleButtons();
    }).prependTo(self.context.parent());
  },

  toggleButtons: function(index){
    var self = this;
    if(index === undefined){
      index = self.api.getIndex();
    }

    var current = jQuery(self.api.getPanes()[index]);
    current.css('margin-left', '4em');
    current.css('margin-right', '4em');
    jQuery(document).trigger('eea-wizard-changed', {height: current.height()});
    self.left.show();
    self.right.show();

    if(index === 0){
      self.left.hide();
      current.css('margin-left', '0');
    }
    if(index === (self.api.getTabs().length - 1)){
      self.right.hide();
      current.css('margin-right', '0');
    }

  }
};


/* Group AT Widgets with jQuery UI Accordion
*/
EEAFormsEdit.Group = function(context, options){
  var self = this;
  self.context = context;
  self.settings = {
    group: []
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEAFormsEdit.Group.prototype = {
  initialize: function(){
    var self = this;
    self.groupFields();
  },

  groupFields: function(){
    var self = this;
    jQuery.each(self.settings.group, function(index, field){
      var errors = jQuery.data(field[0], 'errors');
      self.handleErrors(field, errors);
      field.addClass('eeaforms-presentation-group');
      var label = jQuery('label.formQuestion', field);
      label.after(jQuery('.formHelp', field).css('display', 'block'));
      var title = label.text();
      label.remove();
      var h3 = jQuery('<h3>').addClass('eeaforms-presentation-group')
        .addClass(errors ? 'eeaforms-error': '').append(
          jQuery('<a>').addClass('eeaforms-ajax')
            .attr('href', '#' + field.attr('id')).html(title)
          );
      field.before(h3);
      self.handleHelp(field, h3);
    });

    var parent = self.context.parent();
    jQuery('.eeaforms-presentation-group', parent).wrapAll(
      '<div class="eeaforms-group-accordion" />');
    var container = jQuery('.eeaforms-group-accordion', parent);
    container.accordion({
      change: function(evt, ui){
        jQuery(document).trigger('eea-wizard-changed');
      }
    });

    jQuery.each(self.settings.group, function(index, field){
      field.height('auto');
    });
  },

  handleErrors: function(field, errors){
    var self = this;
    if(!errors){
      return;
    }

    var errorsBox = jQuery('.fieldErrorBox', field);
    if(!errorsBox.length){
      errorsBox = jQuery('<div>').addClass('fieldErrorBox').prependTo(field);
    }
    errorsBox.removeClass('fieldErrorBox').addClass('error').html(errors);
  },

  handleHelp: function(field, header){
    var self = this;
    var formHelp = jQuery('.formHelp', field);
    var help = jQuery('<a>')
      .attr('href', '#')
      .addClass('eeaforms-group-help')
      .text('Help')
      .click(function(){
        formHelp.toggle('blind');
        return false;
      });
    header.prepend(help);
    formHelp.hide();
  }
};

/* collective.quickupload extension to be used within QuickUpload AT Widget
*/
EEAFormsEdit.QuickUpload = function(context, options){
  var self = this;
  self.context = context;
  self.settings = {
    basket: null,
    relatedItems: 'relatedItems'
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  if(!self.settings.basket){
    return;
  }

  // Events
  jQuery(document).bind('qq-file-uploaded', function(evt, data){
    self.onFileUpload(data);
  });

  self.initialize();
};

EEAFormsEdit.QuickUpload.prototype = {
  initialize: function(){
    var self = this;
    self.settings.basket.empty();
  },

  onFileUpload: function(data){
    var self = this;

    var name = self.settings.relatedItems + ':list';

    var label = jQuery('<label>').text(data.title);
    self.settings.basket.append(label);

    jQuery('<input>').attr('type', 'checkbox')
      .val(data.uid)
      .attr('checked', 'checked')
      .attr('name', name)
      .prependTo(self.settings.basket);
  }
};

/* jQuery plugin for EEAFormsEdit.Group
*/
jQuery.fn.EEAFormsGroup = function(options){
  return this.each(function(){
    var context = jQuery(this).addClass('ajax');
    var spreadsheet = new EEAFormsEdit.Group(context, options);
    context.data('EEAFormsGroup', spreadsheet);
  });
};


/* jQuery plugin for EEAFormsEdit.Wizard
*/
jQuery.fn.EEAFormsWizard = function(options){
  return this.each(function(){
    var context = jQuery(this).addClass('ajax');
    var wizard = new EEAFormsEdit.Wizard(context, options);
    context.data('EEAFormsWizard', wizard);
  });
};

/* jQuery plugin for EEAFormsEdit.QuickUpload
*/
jQuery.fn.EEAFormsQuickUpload = function(options){
  return this.each(function(){
    var context = jQuery(this).addClass('ajax');
    var quickUpload = new EEAFormsEdit.QuickUpload(context, options);
    context.data('EEAFormsQuickUpload', quickUpload);
  });
};

/*!
 * Customized jQuery UI Effects Slide to get rid of createWrapper
 */
jQuery.fn.EEASlide = function(options) {

    return this.queue(function() {

        // Create element
        var el = jQuery(this);

        // Set options
        var mode = options.mode || 'show'; // Set Mode
        var direction = options.direction || 'left'; // Default Direction
        var easing = options.easing || 'swing';
        var parent = el.parent();

        // Adjust
         el.show().css('position', 'relative'); // Save & Show
         parent.css('overflow', 'hidden');

        var ref = (direction == 'up' || direction == 'down') ? 'top' : 'left';
        var motion = (direction == 'up' || direction == 'left') ? 'pos' : 'neg';
        var distance = options.distance || (ref == 'top' ? el.outerHeight({margin:true}) : el.outerWidth({margin:true}));
        if (mode == 'show'){
            var tmp_pos = motion == 'pos' ? (isNaN(distance) ? "-" + distance : -distance) : distance;
            el.css(ref, tmp_pos); // Shift

            // fix for chrome when page is zoomed
            if (el.css(ref) != tmp_pos){
                // if the position is different than what we wanted, 
                // recalculate it with the ratio between the original value and the one we get from the element
                var el_pos = el.css(ref);
                var ratio = tmp_pos/parseInt(el_pos, 10);
                el.css(ref, tmp_pos * ratio);
            }
            // end of fix

        }
        var pos = parseInt(el.css('left'), 10);
            pos = pos < 0 ? pos * -1 : pos;
        distance =  pos > distance ? pos : distance;
        // Animation
        var animation = {};
        animation[ref] = (mode == 'show' ? (motion == 'pos' ? '+=' : '-=') : (motion == 'pos' ? '-=' : '+=')) + distance;

        // Animate
        el.animate(animation, { queue: false, duration: options.duration, easing: easing, complete: function() {
            if(mode == 'hide'){ el.hide(); }// Hide
            if(options.callback){
                options.callback.apply(this, arguments); // Callback
            }
            el.dequeue();
            parent.css('overflow', '');
        }});

    });
};
