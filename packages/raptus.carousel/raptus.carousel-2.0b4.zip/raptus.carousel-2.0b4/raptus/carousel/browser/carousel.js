(function($) {
  /**
   * $ is an alias to jQuery object
   *
   */
  $.fn.carousel = function(settings) {
    settings = jQuery.extend({
      imagePrev:        '++resource++carousel-prev.gif',
      imageNext:        '++resource++carousel-next.gif',
      scrollSpeed:      50,
      mouseControl:     false,
      buttonControl:    true,
      buttonOffOpacity: 0.3,
      buttonOnOpacity:  0.8
    },settings);
    $(this).each(function() {
      _initialize($(this), settings);
    });
    return $(this);
  };
  
  function _initialize(o, settings) {
    // ie 7 bugfix
    if($.browser.msie && $.browser.version < 8)
      o.find('.carouselContent li a img').each(function() {
        var img = $(this);
        var li = img.closest('li');
        if(!img.complete)
          img.load(function() {
            li.width(img.width());
          });
        else
          li.width(img.width());
      });
    
    o.addClass('carouselActive');
    var left = parseInt(o.find('.carouselContent').css('padding-left'));
    var right = parseInt(o.find('.carouselContent').css('padding-right'));
    o.find('.carouselContent').css({'padding-left': 0, 'padding-right': 0});
    o.find('.carouselContent > *:first-child').css('padding-left', parseInt(o.find('.carouselContent > *:first-child').css('padding-left'))+left);
    o.find('.carouselContent > *:last-child').css('padding-right', parseInt(o.find('.carouselContent > *:last-child').css('padding-right'))+right);
    var width = 0;
    o.find('.carouselContent > *').each(function() {
      var margin_left = parseInt(jQuery(this).css('margin-left'));
      var margin_right = parseInt(jQuery(this).css('margin-right'));
      if (isNaN(margin_left))margin_left=0;
      if (isNaN(margin_right))margin_right=0;
      width += jQuery(this).outerWidth() + margin_left + margin_right;
    });
    o.find('.carouselContent').width(width);
    
    var margin_top = parseInt(o.find('.carouselContent').css('margin-top'))
    var margin_bottom = parseInt(o.find('.carouselContent').css('margin-bottom'))
    if (isNaN(margin_top))margin_top=0;
    if (isNaN(margin_bottom))margin_bottom=0;
    var height = o.find('.carouselContent').height() + margin_top + margin_bottom;
    o.css('height', height);
    var data = {carousel: o, settings: settings};
    
    if(settings.buttonControl) {
      $('<a class="next"></a><a class="prev"></a>').appendTo(o);
      o.find('.next, .prev').css('height', height).fadeTo(200, settings.buttonOffOpacity);
      o.find('.next, .prev').bind('mouseover', data, function(event) { 
          if ($(this).hasClass('active')) {
            $(this).stop();
            $(this).fadeTo(200, event.data.settings.buttonOnOpacity);
          }
        });
      o.find('.next, .prev').bind('mouseout', data, function(event) { 
          $(this).stop(); 
          $(this).fadeTo(200, event.data.settings.buttonOffOpacity);
        });
      
      o.find('.next').bind('mousedown', data, _move_left);
      o.find('.next').bind('mouseout', data, _stop);
      o.find('.next').bind('mouseup', data, _stop);
      
      o.find('.prev').bind('mousedown', data, _move_right);
      o.find('.prev').bind('mouseout', data, _stop);
      o.find('.prev').bind('mouseup', data, _stop);
    }
    
    if(settings.mouseControl) {
      o.bind('mousemove', data, _move);
    }
    
    $(window).bind('resize', data, _resize);
    _resize({data:data});
  };
  
  function _move(event) {
    var o = event.data.carousel;
    var settings = event.data.settings;
    
    var carouselwidth = o.outerWidth();
    var contentwidth = o.find('.carouselContent').outerWidth();
    var contentleft = parseInt(o.find('.carouselContent').css('left')) * -1;
    
    var mouseleft = event.pageX - o.offset().left;
    
    if(carouselwidth >= contentwidth) {
      o.find('.carouselContent').css('left', 0);
      return
    }
    
    o.find('.carouselContent').css('left', '-'+((contentwidth-carouselwidth)/carouselwidth*mouseleft)+'px')
  };
  
  function _resize(event) {
    var o = event.data.carousel;
    var settings = event.data.settings;
    
    var carouselwidth = o.outerWidth();
    var contentwidth = o.find('.carouselContent').outerWidth();
    var contentleft = parseInt(o.find('.carouselContent').css('left')) * -1;
    
    o.find('.next,.prev').css('cursor', 'default').css('backgroundImage', 'none');
    if(carouselwidth >= contentwidth) {
      o.find('.next,.prev').removeClass('active');
      o.find('.carouselContent').css('left', '0');
    } else {
      o.find('.next,.prev').addClass('active');
      if(contentleft >= contentwidth - carouselwidth) {
        o.find('.next').removeClass('active');
        o.find('.carouselContent').css('left', '-'+(contentwidth-carouselwidth)+'px');
      } if(contentleft <= 0) {
        o.find('.prev').removeClass('active');
        o.find('.carouselContent').css('left', '0');
      }
    }
    o.find('.active').css('cursor', 'pointer').css('backgroundImage', 'url("'+settings.imageNext+'")');
    o.find('.prev.active').css('backgroundImage', 'url("'+settings.imagePrev+'")');
  };
  
  function _move_left(event) {
    if(!jQuery(this).hasClass('active'))
      return;
    var o = event.data.carousel;
    var settings = event.data.settings;
    var carouselwidth = o.outerWidth();
    var contentwidth = o.find('.carouselContent').outerWidth();
    var contentleft = parseInt(o.find('.carouselContent').css('left')) * -1;
    o.find('.carouselContent').animate({left: '-'+(contentwidth-carouselwidth)+'px'}, (contentwidth-carouselwidth-contentleft)*100/settings.scrollSpeed, 'swing', function() {
      $(this).parent().find('.next').removeClass('active').css('cursor', 'default').css('backgroundImage', 'none').fadeTo(200, settings.buttonOffOpacity);
    });
    o.find('.prev').addClass('active').css('cursor', 'pointer').css('backgroundImage', 'url("'+settings.imagePrev+'")');
  };
  
  function _move_right(event) {
    if(!jQuery(this).hasClass('active'))
      return;
    var o = event.data.carousel;
    var settings = event.data.settings;
    var contentleft = parseInt(o.find('.carouselContent').css('left')) * -1;
    o.find('.carouselContent').animate({left: "0"}, contentleft*100/settings.scrollSpeed, 'swing', function() {
      $(this).parent().find('.prev').removeClass('active').css('cursor', 'default').css('backgroundImage', 'none').fadeTo(200, settings.buttonOffOpacity);
    });
    o.find('.next').addClass('active').css('cursor', 'pointer').css('backgroundImage', 'url("'+settings.imageNext+'")');
  };
  
  function _stop(event) {
    var o = event.data.carousel;
    o.find('.carouselContent').stop();
    _resize(event);
  }
})(jQuery); // Call and execute the function immediately passing the jQuery object