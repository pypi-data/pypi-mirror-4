/**
 * ZTFY.file cthumb management
 */

(function($) {

	if (typeof($.ZTFY) == "undefined") {
		$.ZTFY = {};
	}

	$.ZTFY.file = {

		imgAreaSelect: function(element) {
			var $element = $(element);
			var data = $(element).data();
			var imageWidth = data.imgAreaSelectImageWidth || $element.width();
			var imageHeight = data.imgAreaSelectImageHeight || $element.height();
			var areaWidth = data.imgAreaSelectWidth;
			var areaHeight = data.imgAreaSelectHeight;
			var left = data.imgAreaSelectLeft;
			var top = data.imgAreaSelectTop;
			var right = Math.min(left + Math.max(areaWidth,30), imageWidth);
			var bottom = Math.min(top + Math.max(areaHeight,30), imageHeight);
			$element.imgAreaSelect({
				parent: $element.closest(data.imgAreaSelectParent),
				position: data.imgAreaSelectPosition || 'relative',
				aspectRatio: data.imgAreaSelectRatio,
				handles: data.imgAreaSelectHandles === undefined ? true : data.imgAreaSelectHandles,
				persistent: data.imgAreaSelectPersistent === undefined ? false : data.imgAreaSelectHandles,
				imageWidth: imageWidth,
				imageHeight: imageHeight,
				minWidth: Math.max(data.imgAreaSelectMinWidth || 0, 30),
				maxWidth: imageWidth,
				minHeight: Math.max(data.imgAreaSelectMaxHeight || 0, 30),
				maxHeight: imageWidth,
				x1: left,
				y1: top,
				x2: Math.min(left + Math.max(areaWidth,30), imageWidth),
				y2: Math.min(top + Math.max(areaHeight,30), imageHeight),
				onSelectEnd: $.ZTFY.getFunctionByName(data.imgAreaSelectCallback)
			});
		},

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
