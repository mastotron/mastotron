// 
// jQuery Flash plugin v1.0
// 
//  - Created by Joel Moss at Codaset (joel@codaset.com)
//  - http://codaset.com/codaset/jquery-flash
// 
// 
// Simply call the following to show a flash message with the text "This is my message":
// 
//    $.flash('This is my message');
// 
// Or you can call it on an element, where the flash message will be populated from the
// contents of the element:
// 
//    $('#my-element').flash();
// 
// 
// To install, just include this javascript file and the accompanying CSS file into your
// HTML page. And that's it!
// 
// 
// If you need help, found a bug, or would like to contribute, head on over to
// http://codaset.com/codaset/jquery-flash
// 

(function($){ 
  
  $(function() {

    var flashDiv = '<div id="flash" style="display:none;"> \
                      <div class="flash_close"></div> \
                      <div class="flash_inner"></div> \
                    </div>';
    $(flashDiv).appendTo('body');
  
    $.extend({
      flash: function(content, options) {
        var flash = $('#flash');
      
        flash.find('.flash_inner').html(content);
        flash
          .show()
          .css({opacity: 0})
          .bottom()
          .animate({
            top: (($(window).height()-flash.height()))-50+'px',
            opacity: 0.8
          });
        
        $(document).click(function(){
          flash.animate({
            top: ($(window).height()+50)+'px',
            opacity: 0
          });
        });
      }
    });
  
    $.fn.extend({
      bottom: function() {
        var offLeft = Math.floor((($(window).width()-this.width())/2)-20),
            offTop = Math.floor($(window).height()+50);
        this.css({
          top: ((offTop != null && offTop > 0) ? offTop : '0')+ 'px',
          left: ((offLeft != null && offLeft > 0) ? offLeft :'0') + 'px'
        });
        return this;
      },
    
      flash: function(options) {
        $.flash(this.html(), options);
        return this;
      }
    });

  });
  
})(jQuery); 
