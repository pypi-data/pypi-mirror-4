/**
 * ZTFY.file cthumb management
 */

(function($) {

	if (typeof($.ZTFY) == "undefined") {
		$.ZTFY = {};
	}

	$.ZTFY.file = {

		cthumb: {

			endSelect: function(image, selection) {
				var form = $(image).parents('FORM');
				var name = $(image).attr('name');
				$('INPUT[name="'+name+'__x"]', form).val(selection.x1);
				$('INPUT[name="'+name+'__y"]', form).val(selection.y1);
				$('INPUT[name="'+name+'__w"]', form).val(selection.width);
				$('INPUT[name="'+name+'__h"]', form).val(selection.height);
			}

		}   // $.ZTFY.file.cthumb

	};  // $.ZTFY.file

})(jQuery);
