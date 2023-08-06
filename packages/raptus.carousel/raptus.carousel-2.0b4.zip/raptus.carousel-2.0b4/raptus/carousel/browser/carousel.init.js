jQuery(window).load(function() {
  var settings = carousel.settings['standard'];
  jQuery('.carousel').carousel(settings);
  jQuery('.mousecarousel').carousel({mouseControl: true, buttonControl: false});
});
