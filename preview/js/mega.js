// Mega Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
  var menu = document.getElementById('megaMenu');
  var triggers = document.querySelectorAll('.header-nav-link.has-menu');
  var hideTimeout;

  triggers.forEach(function(trigger) {
    trigger.addEventListener('mouseenter', function() {
      clearTimeout(hideTimeout);
      var target = this.getAttribute('data-menu');
      menu.classList.add('active');
      document.querySelectorAll('.mega-col').forEach(function(col) {
        col.classList.remove('active');
      });
      var col = document.querySelector('.mega-col[data-menu="' + target + '"]');
      if (col) col.classList.add('active');
      triggers.forEach(function(t) { t.classList.remove('active'); });
      this.classList.add('active');
    });

    trigger.addEventListener('mouseleave', function() {
      hideTimeout = setTimeout(function() {
        menu.classList.remove('active');
        triggers.forEach(function(t) { t.classList.remove('active'); });
        document.querySelectorAll('.mega-col').forEach(function(col) {
          col.classList.remove('active');
        });
      }, 200);
    });
  });

  menu.addEventListener('mouseenter', function() {
    clearTimeout(hideTimeout);
  });
  menu.addEventListener('mouseleave', function() {
    hideTimeout = setTimeout(function() {
      menu.classList.remove('active');
      triggers.forEach(function(t) { t.classList.remove('active'); });
      document.querySelectorAll('.mega-col').forEach(function(col) {
        col.classList.remove('active');
      });
    }, 200);
  });
});