/**
 * jQuery lightBox plugin
 * This jQuery plugin was inspired and based on Lightbox 2 by Lokesh Dhakar (http://www.huddletogether.com/projects/lightbox2/)
 * and adapted to me for use like a plugin from jQuery.
 * @name jquery-lightbox-0.5.js
 * @author Leandro Vieira Pinho - http://leandrovieira.com
 * @version 0.5
 * @date April 11, 2008
 * @category jQuery plugin
 * @copyright (c) 2008 Leandro Vieira Pinho (leandrovieira.com)
 * @license CC Attribution-No Derivative Works 2.5 Brazil - http://creativecommons.org/licenses/by-nd/2.5/br/deed.en_US
 * @example Visit http://leandrovieira.com/projects/jquery/lightbox/ for more informations about this jQuery plugin
 */

// Offering a Custom Alias suport - More info: http://docs.jquery.com/Plugins/Authoring#Custom_Alias
(function($) {
  $.fn.loaded = function(callback) {
    if($(this).data('interval'))
      window.clearInterval($(this).data('interval'));
    $(this).data('interval', window.setInterval($.proxy(function(){
      for (i = 0; i < this.obj.length; i++) {
        if (this.obj.eq(i).complete == false) 
          return;
        this.callback();
        window.clearInterval(this.obj.data('interval'));
      }
    }, {obj: $(this), callback: callback}), 50));
  }
  /**
   * $ is an alias to jQuery object
   *
   */
  $.fn.inlineLightBox = function(settings) {
    // Settings to configure the jQuery lightBox plugin how you like
    settings = jQuery.extend({
      // Configuration related to navigation
      fixedNavigation:    false,    // (boolean) Boolean that informs if the navigation (next and prev button) will be fixed or not in the interface.
      // Configuration related to images
      imageLoading:     '++resource++inlinelightbox-loading.gif',    // (string) Path and the name of the loading icon
      imageBtnPrev:     '++resource++inlinelightbox-prev.gif',     // (string) Path and the name of the prev button image
      imageBtnNext:     '++resource++inlinelightbox-next.gif',     // (string) Path and the name of the next button image
      imageBlank:       '++resource++inlinelightbox-blank.gif',      // (string) Path and the name of a blank image (one pixel)
      // Configuration related to container image box
      containerBorderSize:  10,     // (integer) If you adjust the padding in the CSS for the container, #lightbox-container-image-box, you will need to update this value
      containerResizeSpeed: 400,    // (integer) Specify the resize duration of container image. These number are miliseconds. 400 is default.
      // Configuration related to texts in caption. For example: Image 2 of 8. You can alter either "Image" and "of" texts.
      txtImage:         '',  // (string) Specify text "Image"
      txtOf:            ' / ',   // (string) Specify text "of"
      txtVisible:       true,
      // Don´t alter these variables in any way
      imageArray:       [],
      activeImage:      0,
      // Caption selector
      captionAttr:      'title',
      captionSelector:  '',
      captionHTML:      false,
      captionVisible:   true,
      // Image selector
      imageSelector:    '',
      imageAttr:        'href',
      
      // Link selector
      linkSelector:     '',
      linkAttr:         'href',
      linkSetOn:        '.lightbox-nav', // the given link (linkSelector) will be set on this element
      
      autoStart:        true,
      playTimeout:      0,
      showButtons:      true,
      showLoading:      true,
      allowRoundtrip:   true,
      effect:           'fade',
      direction:        'left',
      effectSpeed:      200,
      slideSpeed:       400,
      fixedHeight:      false,
      fixedWidth:       false,
      hAlign:           'center',
      vAlign:           'center',
      initialHeight:    250,
      initialWidth:     250,
      responsive:       false,
      
      // Callbacks
      preStart: false,
      postStart: false,
      preSetInterface: false,
      postSetInterface: false,
      preSetImageToView: false,
      postSetImageToView: false,
      preResizeContainer: false,
      postResizeContainer: false,
      preShowImage: false,
      postShowImage: false,
      preShowImageData: false,
      postShowImageData: false,
      preSetNavigation: false,
      postSetNavigation: false,
      prePreloadNeighbor: false,
      postPreloadNeighbor: false,
      prePreloadNeighbor: false,
      postPreloadNeighbor: false
    },settings);
    if(!this.length)
      return
    settings.matchedObjects = this;
    /**
     * Initializing the plugin calling the start function
     *
     * @return boolean false
     */
    function _initialize(event) {
      event.preventDefault();
      _start(event.currentTarget, event.data.settings); // This, in this context, refer to object (link) which the user have clicked
    };
    /**
     * Start the jQuery lightBox plugin
     *
     * @param object objClicked The object (link) whick the user have clicked
     * @param object jQueryMatchedObj The jQuery object with all elements matched
     */
    function _start(objClicked, settings) {
      _callback(settings, 'preStart', {'objClicked': objClicked});
      settings.started = true;
      var o = $(objClicked);
      var parent = o.parent();
      while(!parent.hasClass('inlinelightbox') && parent.tagName != 'body')
        parent = parent.parent();
      // Call the function to create the markup structure; style some elements; assign events in some elements.
      _set_interface(objClicked, parent, settings);
      // Unset total images in imageArray
      settings.imageArray = [];
      // Unset image active information
      var cimg = settings.activeImage;
      settings.activeImage = 0;
      // Add an Array (as many as we have), with href and title atributes, inside the Array that storage the images references    
      for ( var i = 0; i < settings.matchedObjects.length; i++ ) {
        var a = $(settings.matchedObjects[i]);
        var img = a;
        var link = false;
        if(settings.captionSelector)
          a = a.find(settings.captionSelector);
        if(settings.captionHTML)
          var caption = a.html();
        else
          var caption = a.attr(settings.captionAttr);
        if(settings.imageSelector)
          img = img.find(settings.imageSelector);
        if(settings.linkSelector)
          link = $(settings.matchedObjects[i]).find(settings.linkSelector).attr(settings.linkAttr);
        settings.imageArray.push(new Array(img.attr(settings.imageAttr),caption,link));
      }
      var img = o;
      if(settings.imageSelector)
        img = img.find(settings.imageSelector);
      while ( settings.imageArray[settings.activeImage][0] != img.attr(settings.imageAttr) ) {
        settings.activeImage++;
      }
      settings.direction = settings.activeImage < cimg ? 'right' : 'left';
      
      // Call the function that prepares image exibition
      _set_image_to_view(parent, settings);
      _callback(settings, 'postStart', {'objClicked': objClicked});
    };
    /**
     * Create the jQuery lightBox plugin interface
     *
     * The HTML markup will be like that:
      <div class="jquery-lightbox">
        <div class="lightbox-container-image-box">
          <div class="lightbox-container-image">
            <img src="../fotos/XX.jpg" class="lightbox-image">
            <div class="lightbox-nav">
              <a href="#" id="lightbox-nav-btnPrev"></a>
              <a href="#" id="lightbox-nav-btnNext"></a>
            </div>
            <div class="lightbox-loading">
              <a href="#" class="lightbox-loading-link">
                <img src="../images/lightbox-ico-loading.gif">
              </a>
            </div>
          </div>
        </div>
        <div class="lightbox-container-image-data-box">
          <div class="lightbox-container-image-data">
            <div class="lightbox-image-details">
              <span class="lightbox-image-details-caption"></span>
              <span class="lightbox-image-details-currentNumber"></span>
            </div>
          </div>
        </div>
      </div>
     *
     */
    function _set_interface(objClicked, parent, settings) {
      // Apply the HTML markup into body tag
      if(!parent.find('.jquery-lightbox').length) {
        _callback(settings, 'preSetInterface', {'parent': parent, 'objClicked': objClicked});
        var caption = settings.captionVisible ? '<span class="lightbox-image-details-caption"></span>' : '';
        var number = settings.txtVisible ? '<span class="lightbox-image-details-currentNumber"></span>' : '';
        var previmage = !settings.showLoading ? '<span class="lightbox-container-image-prev"><img class="lightbox-image-prev"></span>' : '';
        var loading = settings.showLoading ? '<div class="lightbox-loading"><a href="#" class="lightbox-loading-link"><img src="' + settings.imageLoading + '"></a></div>' : '';
        parent.prepend('<div id="'+$(objClicked).attr('rel')+'" class="jquery-lightbox"><div class="lightbox-container-image-box">'+previmage+'<div class="lightbox-container-image"><img class="lightbox-image"><div style="" class="lightbox-nav"><a href="#" class="lightbox-nav-btnPrev"></a><a href="#" class="lightbox-nav-btnNext"></a></div>' + loading + '</div></div><div class="lightbox-container-image-data-box"><div class="lightbox-container-image-data"><div class="lightbox-image-details">'+caption+''+number+'</div></div></div></div>'); 
        parent.find('.lightbox-container-image-data-box').css('padding', '0 '+settings.containerBorderSize+'px 0').hide();
        parent.find('.lightbox-container-image-box').width(settings.initialWidth).height(settings.initialHeight).css('padding', settings.containerBorderSize+'px');
        if(settings.fixedHeight)
          parent.find('.lightbox-container-image-box, .lightbox-container-image, .lightbox-nav-btnPrev,.lightbox-nav-btnNext').height(settings.fixedHeight);
        if(settings.fixedWidth)
          parent.find('.lightbox-container-image-box, .lightbox-container-image, .lightbox-container-image-data-box').width(settings.fixedWidth);
        if(settings.responsive) {
          parent.find('.lightbox-image, .lightbox-image-prev').css('max-width', '100%');
          parent.find('.lightbox-container-image-box, .lightbox-container-image, .lightbox-container-image-data-box').width('100%');
          $(window).resize(function() {
            if(settings.cIntImageWidth) {
              parent.find('.lightbox-container-image-prev, .lightbox-container-image, .lightbox-container-image-box').stop();
              _resize_container_image_box(parent, settings, settings.cIntImageWidth, settings.cIntImageHeight);
            }
          });
        }
        if(!settings.showLoading)
          parent.find('.lightbox-container-image-prev').hide();
        _callback(settings, 'postSetInterface', {'parent': parent, 'objClicked': objClicked});
      }
    }
    /**
     * Prepares image exibition; doing a image´s preloader to calculate it´s size
     *
     */
    function _set_image_to_view(parent, settings) { // show the loading
      _callback(settings, 'preSetImageToView', {'parent': parent});
      window.clearTimeout(settings.timer);
      // Show the loading
      var img = parent.find('.lightbox-image');
      if(settings.showLoading) {
        img.hide();
        parent.find('.lightbox-loading').show();
      } else {
        parent.find('.lightbox-image-prev').hide();
        var width = settings.fixedWidth;
        if(settings.responsive)
          width = parent.width();
        if(width)
          parent.find('.lightbox-image-prev').css('left', settings.hAlign == 'right' ? width-img.width() : (settings.hAlign == 'left' ? 0 : (width-img.width())/2));
        if(settings.fixedHeight)
          parent.find('.lightbox-image-prev').css('top', settings.vAlign == 'bottom' ? settings.fixedHeight-img.height() : (settings.vAlign == 'top' ? 0 : (settings.fixedHeight-img.height())/2));
        parent.find('.lightbox-container-image-prev').height(settings.fixedHeight ? settings.fixedHeight : img.height())
                                                     .width(width ? width : img.width())
        if(img.attr('src')) {
          parent.find('.lightbox-image-prev').loaded($.proxy(function() {
            this.parent.find('.lightbox-image').hide();
            this.parent.find('.lightbox-image-prev').show();
            this.parent.find('.lightbox-container-image-prev').show();
          }, {settings: settings, parent: parent}));
          parent.find('.lightbox-image-prev').attr('src', img.attr('src'));
        } else
          parent.find('.lightbox-container-image-prev').show();
      }
      
      if(!settings.fixedNavigation)
        parent.find('.lightbox-nav,.lightbox-nav-btnPrev,.lightbox-nav-btnNext').hide();
        
      if(parent.find('.lightbox-container-image-data-box').css('display') == 'block') {
        parent.find('.lightbox-container-image-data-box').slideUp(settings.slideSpeed, function() {
          $(this).hide();
        });
      }
      // Image preload process
      if(settings.activeImage < 0)
        settings.activeImage = settings.imageArray.length - 1;
      if(settings.activeImage >= settings.imageArray.length)
        settings.activeImage = 0;
      var objImagePreloader = new Image();
      objImagePreloader.settings = settings;
      objImagePreloader.parent = parent;
      objImagePreloader.onload = function() {
        function __wait(objImagePreloader) {
          if((objImagePreloader.settings.showLoading || objImagePreloader.parent.find('.lightbox-container-image-prev').css('display') != 'none') &&
             objImagePreloader.parent.find('.lightbox-container-image-data-box').css('display') == 'none') {
            objImagePreloader.parent.find('.lightbox-image').attr('src',objImagePreloader.settings.imageArray[objImagePreloader.settings.activeImage][0]);
            // Perfomance an effect in the image container resizing it
            _resize_container_image_box(objImagePreloader.parent,settings,objImagePreloader.width,objImagePreloader.height);
          } else
            window.setTimeout(function() { __wait(objImagePreloader); }, 10);
        }
        //  clear onLoad, IE behaves irratically with animated gifs otherwise
        this.onload=function(){};
        __wait(this);
      };
      objImagePreloader.src = settings.imageArray[settings.activeImage][0];
      _callback(settings, 'postSetImageToView', {'parent': parent});
    };
    /**
     * Perfomance an effect in the image container resizing it
     *
     * @param integer intImageHeight The image´s height that will be showed
     */
    function _resize_container_image_box(parent,settings,intImageWidth,intImageHeight) {
      _callback(settings, 'preResizeContainer', {'parent': parent, 'intImageWidth': intImageWidth, 'intImageHeight': intImageHeight});
      var containerWidth = parent.width();
      if(settings.responsive) {
        settings.cIntImageHeight = intImageHeight;
        settings.cIntImageWidth = intImageWidth;
        if(intImageWidth > containerWidth) {
          intImageHeight *= containerWidth / intImageWidth;
          intImageWidth = containerWidth;
        }
      }
      // Get current width and height
      var intCurrentWidth = parent.find('.lightbox-container-image-box').width();
      var intCurrentHeight = parent.find('.lightbox-container-image-box').height();
      // Perfomance the effect
      var animation = {};
      if(!settings.fixedHeight) {
        animation.height = intImageHeight;
        parent.find('.lightbox-nav-btnPrev,.lightbox-nav-btnNext').css({ height: intImageHeight });
      }
      if(!settings.fixedWidth) {
        animation.width = settings.responsive ? '100%' : intImageWidth;
        parent.find('.lightbox-container-image-data-box').css({ width: settings.responsive ? '100%' : intImageWidth });
      }
      if(animation.width || animation.height) {
        parent.find('.lightbox-container-image-prev, .lightbox-container-image').animate(animation, settings.containerResizeSpeed);
        parent.find('.lightbox-container-image-box').animate(animation, settings.containerResizeSpeed, function() { _show_image(parent, settings); });
        if($.browser.msie)
          settings.dummyTimer = window.setInterval(function() { jq('body').toggleClass('dummy'); }, 10);
      } else
        _show_image(parent, settings);
      _callback(settings, 'postResizeContainer', {'parent': parent, 'intImageWidth': intImageWidth, 'intImageHeight': intImageHeight});
    };
    /**
     * Show the prepared image
     *
     */
    function _show_image(parent,settings) {
      _callback(settings, 'preShowImage', {'parent': parent});
      if($.browser.msie) {
        if(settings.dummyTimer)
          window.clearInterval(settings.dummyTimer);
        jq('body').toggleClass('dummy');
      }
      parent.find('.lightbox-loading').hide();
      if(settings.imageArray[settings.activeImage][2]) {
        parent.find(settings.linkSetOn).bind('click', {url: settings.imageArray[settings.activeImage][2]}, __goto);
        parent.find(settings.linkSetOn).css('cursor', 'pointer');
      } else {
        parent.find(settings.linkSetOn).unbind('click', __goto);
        parent.find(settings.linkSetOn).css('cursor', 'default');
      }
      var img = parent.find('.lightbox-image');
      if(settings.matchedObjects.length > 1){
        if(settings.effect == 'slide') {
          $(img).loaded(function() {
            _slide(img, parent, settings)
          });
        } else {
          $(img).loaded(function() {
            _fade(img, parent, settings)
          });
        }
      } else {
        $(img).loaded(function() {
          var width = settings.fixedWidth;
          if(settings.responsive)
            width = parent.width();
          if(width)
            img.css('left', settings.hAlign == 'right' ? width-img.width() : (settings.hAlign == 'left' ? 0 : (width-img.width())/2));
          if(settings.fixedHeight)
            img.css('top', settings.vAlign == 'bottom' ? settings.fixedHeight-img.height() : (settings.vAlign == 'top' ? 0 : (settings.fixedHeight-img.height())/2));
          img.show();
        });
        _show_image_data(parent,settings);
        _set_navigation(parent,settings);
      }
      _preload_neighbor_images(settings);
      _callback(settings, 'postShowImage', {'parent': parent});
    };
    
    function _fade(img, parent, settings) {
      if(!settings.showLoading)
        parent.find('.lightbox-container-image-prev').stop().fadeOut(settings.effectSpeed, function() {
          parent.find('.lightbox-container-image-prev').hide();
        });
      var width = settings.fixedWidth;
      if(settings.responsive)
        width = parent.width();
      if(width)
        img.css('left', settings.hAlign == 'right' ? width-img.width() : (settings.hAlign == 'left' ? 0 : (width-img.width())/2));
      if(settings.fixedHeight)
        img.css('top', settings.vAlign == 'bottom' ? settings.fixedHeight-img.height() : (settings.vAlign == 'top' ? 0 : (settings.fixedHeight-img.height())/2));
      img.fadeIn(settings.effectSpeed, function() {
        _show_image_data(parent,settings);
        _set_navigation(parent,settings);
      });
    };
    
    function _slide(img, parent, settings) {
      if(!settings.showLoading) {
        parent.find('.lightbox-container-image-prev').stop().animate({
          left: (settings.direction == 'right' ? 1 : -1)*(settings.fixedWidth ? settings.fixedWidth : img.width())
        }, settings.effectSpeed, 'swing', function() {
          parent.find('.lightbox-container-image-prev').hide();
          parent.find('.lightbox-container-image-prev').css('left', 0);
        });
      }
      img.show();
      img.css('left', (settings.direction == 'right' ? -1 : 1)*(settings.fixedWidth ? settings.fixedWidth : img.width()));
      img.css('top', (settings.fixedHeight ? (settings.vAlign == 'bottom' ? settings.fixedHeight-img.height() : (settings.vAlign == 'top' ? 0 : (settings.fixedHeight-img.height())/2)) : 0));
      var width = settings.fixedWidth;
      if(settings.responsive)
        width = parent.width();
      img.stop().animate({
        left: width ? (settings.hAlign == 'right' ? width-img.width() : (settings.hAlign == 'left' ? 0 : (width-img.width())/2)) : 0
        }, settings.effectSpeed, 'swing',
        function() {
          _show_image_data(parent,settings);
          _set_navigation(parent,settings);
      });
    };
    function __goto(event) {
      window.location = event.data.url;
    };
    /**
     * Show the image information
     *
     */
    function _show_image_data(parent,settings) {
      _callback(settings, 'preShowImageData', {'parent': parent});
      parent.find('.lightbox-image-details-caption').hide();
      if ( settings.imageArray[settings.activeImage][1] ) {
        parent.find('.lightbox-image-details-caption').html(settings.imageArray[settings.activeImage][1]).show();
      }
      // If we have a image set, display 'Image X of X'
      if ( settings.imageArray.length > 1 ) {
        parent.find('.lightbox-image-details-currentNumber').html(settings.txtImage + ' ' + ( settings.activeImage + 1 ) + ' ' + settings.txtOf + ' ' + settings.imageArray.length).show();
      }
      if (settings.captionVisible || settings.txtVisible) {
        parent.find('.lightbox-container-image-data-box').slideDown(settings.slideSpeed);
        parent.find('.lightbox-container-image-data-box').css('display', 'block');
      }
      if(settings.playTimeout) {
        window.clearTimeout(settings.timer);
        settings.timer = window.setTimeout(function() {
          if(settings.random && settings.imageArray.length > 2) {
            do {
              var next = Math.floor(Math.random()*settings.imageArray.length);
            } while(next == settings.activeImage);
            settings.activeImage = next;
          } else
            settings.activeImage++;
          settings.direction = 'left';
          _set_image_to_view(parent, settings);
        }, settings.playTimeout);
      }
      _callback(settings, 'postShowImageData', {'parent': parent});
    }
    /**
     * Display the button navigations
     *
     */
    function _set_navigation(parent,settings) {
      _callback(settings, 'preSetNavigation', {'parent': parent});
      parent.find('.lightbox-nav').show();

      // Instead to define this configuration in CSS file, we define here. And it´s need to IE. Just.
      parent.find('.lightbox-nav-btnPrev,#lightbox-nav-btnNext').css({ 'background' : 'transparent url(' + settings.imageBlank + ') no-repeat' });
      
      if(settings.showButtons) {
        // Show the prev button, if not the first image in set
        if ( settings.activeImage != 0 || (settings.allowRoundtrip && settings.imageArray.length > 1) ) {
          if ( settings.fixedNavigation ) {
            parent.find('.lightbox-nav-btnPrev').css({ 'background' : 'url(' + settings.imageBtnPrev + ') left 25% no-repeat' })
              .unbind()
              .bind('click', {settings: settings}, function(event) {
                event.stopPropagation();
                event.preventDefault();
                var parent = $(this).parent();
                var settings = event.data.settings;
                while(!parent.hasClass('jquery-lightbox') && parent.tagName != 'body')
                  parent = parent.parent();
                settings = event.data.settings;
                settings.activeImage = settings.activeImage - 1;
                settings.direction = 'right';
                _set_image_to_view(parent.parent(), settings);
              });
          } else {
            // Show the images button for Next buttons
            parent.find('.lightbox-nav-btnPrev').unbind().hover(function() {
              $(this).css({ 'background' : 'url(' + settings.imageBtnPrev + ') left 25% no-repeat' });
            },function() {
              $(this).css({ 'background' : 'transparent url(' + settings.imageBlank + ') no-repeat' });
            }).css({ 'background' : 'transparent url(' + settings.imageBlank + ') no-repeat' })
              .show().bind('click', {settings: settings}, function(event) {
              event.stopPropagation();
              event.preventDefault();
              var parent = $(this).parent();
              var settings = event.data.settings;
              while(!parent.hasClass('jquery-lightbox') && parent.tagName != 'body')
                parent = parent.parent();
              settings = event.data.settings;
              settings.activeImage = settings.activeImage - 1;
              settings.direction = 'right';
              _set_image_to_view(parent.parent(), settings);
            });
          }
        }
        
        // Show the next button, if not the last image in set
        if ( settings.activeImage != ( settings.imageArray.length -1 ) || (settings.allowRoundtrip && settings.imageArray.length > 1) ) {
          if ( settings.fixedNavigation ) {
            parent.find('.lightbox-nav-btnNext').css({ 'background' : 'url(' + settings.imageBtnNext + ') right 25% no-repeat' })
              .unbind()
              .bind('click', {settings: settings}, function(event) {
                event.stopPropagation();
                event.preventDefault();
                var parent = $(this).parent();
                var settings = event.data.settings;
                while(!parent.hasClass('jquery-lightbox') && parent.tagName != 'body')
                  parent = parent.parent();
                settings = event.data.settings;
                settings.activeImage = settings.activeImage + 1;
                settings.direction = 'left';
                _set_image_to_view(parent.parent(), settings);
              });
          } else {
            // Show the images button for Next buttons
            parent.find('.lightbox-nav-btnNext').unbind().hover(function() {
              $(this).css({ 'background' : 'url(' + settings.imageBtnNext + ') right 25% no-repeat' });
            },function() {
              $(this).css({ 'background' : 'transparent url(' + settings.imageBlank + ') no-repeat' });
            }).css({ 'background' : 'transparent url(' + settings.imageBlank + ') no-repeat' })
              .show().bind('click', {settings: settings}, function(event) {
              event.stopPropagation();
              event.preventDefault();
              var parent = $(this).parent();
                var settings = event.data.settings;
              while(!parent.hasClass('jquery-lightbox') && parent.tagName != 'body')
                parent = parent.parent();
              settings = event.data.settings;
              settings.activeImage = settings.activeImage + 1;
              settings.direction = 'left';
              _set_image_to_view(parent.parent(), settings);
            });
          }
        }
      }
      _callback(settings, 'postSetNavigation', {'parent': parent});
    }
    /**
     * Preload prev and next images being showed
     *
     */
    function _preload_neighbor_images(settings) {
      _callback(settings, 'prePreloadNeighbor');
      if ( (settings.imageArray.length -1) > settings.activeImage ) {
        objNext = new Image();
        objNext.src = settings.imageArray[settings.activeImage + 1][0];
      }
      if ( settings.activeImage > 0 ) {
        objPrev = new Image();
        objPrev.src = settings.imageArray[settings.activeImage -1][0];
      }
      _callback(settings, 'postPreloadNeighbor');
    }
    /**
     * Handles callbacks
     * 
     */
    function _callback(settings, name, params) {
      if(!params) params = {};
      params = $.extend({'name': name, 'settings': settings}, params);
      if(settings[name])
        settings[name](params);
    }
    /**
     * Stop the code execution from a escified time in milisecond
     *
     */
    function ___pause(ms) {
      var date = new Date(); 
      curDate = null;
      do { var curDate = new Date(); }
      while ( curDate - date < ms);
    };
    // Return the jQuery object for chaining. The unbind method is used to avoid click conflict when the plugin is called more than once
    this.unbind('click').bind('click', {settings: settings}, _initialize);
    if((settings.autoStart || settings.playTimeout) && !settings.started)
      $(this.get(settings.activeImage)).trigger('click');
    return this;
  };
})(jQuery); // Call and execute the function immediately passing the jQuery object