(function($){

	var initLayout = function() {

		$('#form\\.body_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.body_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.header_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.header_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});



		$('#form\\.header_font_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.header_font_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});


		$('#form\\.header_link_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.header_link_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.header_active_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.header_active_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.topnav_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.topnav_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});



		$('#form\\.topnav_font_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.topnav_font_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});


		$('#form\\.topnav_link_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.topnav_link_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.topnav_active_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.topnav_active_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});


		$('#form\\.leftnav_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.leftnav_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});



		$('#form\\.leftnav_font_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.leftnav_font_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});


		$('#form\\.leftnav_link_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.leftnav_link_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.leftnav_active_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.leftnav_active_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.content_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.content_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});



		$('#form\\.content_font_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.content_font_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});


		$('#form\\.content_link_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.content_link_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.content_active_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.content_active_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});


		$('#form\\.default_font_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.default_font_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.page_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.page_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});



		$('#form\\.unvisited_link_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.unvisited_link_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.active_link_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.active_link_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.visited_link_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.visited_link_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.default_border_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.default_border_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.secondary_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.secondary_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.secondary_text_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.secondary_text_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.loggedin_tabs_border_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.loggedin_tabs_border_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.loggedin_tabs_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.loggedin_tabs_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.loggedin_tabs_text_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.loggedin_tabs_text_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.form_inputtext_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.form_inputtext_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.evenrow_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.evenrow_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});


		$('#form\\.oddrow_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.oddrow_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.notification_border_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.notification_border_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.notification_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.notification_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});

		$('#form\\.discreet_text_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.discreet_text_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});


		$('#form\\.info_popup_bkg_color').ColorPicker({
			onSubmit: function(hsb, hex, rgb) {
				$('#form\\.info_popup_bkg_color').val('#' + hex);
			},
			onBeforeShow: function () {
				$(this).ColorPickerSetColor(this.value);
			}
		})
		.bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});




	};
		
	EYE.register(initLayout, 'init');
})(jQuery)
