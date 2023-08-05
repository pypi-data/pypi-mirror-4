;(function($){
	function Fullscreen(el, opts){
		self = this
		self.el = $(el);
		self.defaults = {};
		self.opts = $.extend(self.defaults, opts);
		self.init();
	}
	Fullscreen.prototype.init = function(){
		// set original height and width
		self.original_width = self.el.width();
		self.original_height = self.el.height();
		// set the icon up
		self.icon = $('<a>', {className: 'fullscreen'});
		self.icon.click(self.dispatch)
		self.el.before(self.icon);
		// add the class names
		self.el.parent().addClass('fullscreen-container');
		// bind keys
		Mousetrap.bind('esc', self._deactivate);
		Mousetrap.bind(['meta+s', 'ctrl+s'], self._save);
		// add the mousetrap class so that events fire
		self.el.addClass('mousetrap');
		// handle tabs
		self.el.keydown(function(e) {
			if(e.keyCode === 9) { // tab was pressed
				var start = this.selectionStart;
					end = this.selectionEnd;
				var $this = $(this);
				$this.val($this.val().substring(0, start)
							+ "\t"
							+ $this.val().substring(end));
				this.selectionStart = this.selectionEnd = start + 1;
				// prevent the focus lose
				return false;
			}
		});
		// add in the loading div
		self.loading = $('<div>')
			.addClass('loading')
			.hide()
			.text('saving');
		$('body').append(self.loading);
	}
	/* 
	 * save
	 */
	Fullscreen.prototype._save = function(e){
		// select the elements in the filter horizontals etc
		$('div.selector-chosen option').each(function(){
			$(this).attr('selected', 'selected');
		})
		data = $('#content-main form').serialize();
		$.ajax({
			type: 'POST',
			url: window.location.href,
			data: data,
			beforeSend: function(){
				self.loading
					.text('saving')
					.removeClass('saved')
					.fadeIn(100);
			},
			success : function(){
				self.loading
					.addClass('saved')
					.text('saved');
				setTimeout(function(){self.loading.fadeOut(500);} ,1000);
			}
		});
		// prevent the default
		e.preventDefault();
}
/*
	 * Activate the fullscreen
	 */
	Fullscreen.prototype._activate = function(e){
		self.el.parent().addClass('active')
	}
	/*
	 * Deactivate the fullscreen
	 */
	Fullscreen.prototype._deactivate = function(e){
		self.el.parent().removeClass('active')
	}
	/*
	* when the icon is clicked
	*/
	Fullscreen.prototype.dispatch = function(e){
		if(self.el.parent().hasClass('active')){
			self._deactivate(e);
		}else{
			self._activate(e);
		}
	}
	/* 
	* register the plugin
	*/
	$.fn.omfs = function(opts) {
		return this.each(function() {
			new Fullscreen(this, opts);
		});
	};
})( django.jQuery );



// now call it
django.jQuery(function($){
    $('textarea.fullscreen').omfs();
});
