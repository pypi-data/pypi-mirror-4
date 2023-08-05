(function($){

  $.fn.add_anchor = function(title) {
    return this.filter("*[id]").each(function() {
      var link = $("<a class='anchor'>\u00B6</a>").attr("href", "#" + this.id);
      if (title)
        link.attr("title", title);
      link.appendTo(this);
    });
  }

})(jQuery);
