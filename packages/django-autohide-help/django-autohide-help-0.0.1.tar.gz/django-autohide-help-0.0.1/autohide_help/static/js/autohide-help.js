/**
 * Copyright (c)2012 Monwara LLC <branko@monwara.com>
 * All rights reserved.
 *
 * @author Monwara LLC <branko@monwara.com>
 * @version 0.0.1
 * @license BSD
 */

(function(root, factory) {

  if (typeof define === 'function' && define.amd) {
    define(['jquery'], factory);
  } else {
    factory(root.jQuery);
  }

})(this, function($) {

  (function() {
  
    $.fn.autohideHelp = function() {
      $(this).each(function(idx, elem) {
        var $form = $(elem);
        var inputs;

        inputs = $form.find(':input');
        if (inputs.length) {
          inputs.each(function(idx, elem) {
            var $input = $(elem);
            var input_id = $input.attr('id');
            var help_id = '#hint_' + $input.attr('id');
            var $help = $(help_id);

            $help.hide();

            function show() { $help.slideDown(300); }
            function hide() { $help.slideUp(300); }

            $input.on('focus', show);
            $input.on('blur', hide);

          });
        }
      });
    }

  })();

});
