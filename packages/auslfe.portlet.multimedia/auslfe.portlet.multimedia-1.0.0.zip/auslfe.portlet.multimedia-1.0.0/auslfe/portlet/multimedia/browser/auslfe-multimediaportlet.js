/*
 * Multimedia Javascript for auslfe.portlet.multimedia 
 */

jQuery.auslfe_multimedia = {
    timeout: 30000,
	i18n: {
		en: {
			stopReload: 'Click to stop auto-reload',
			restartReload: 'Click to restart auto-reload'
		},
		it: {
			stopReload: 'Click per fermare il caricamento automatico',
			restartReload: 'Click per avviare di nuovo il caricamento automatico'
		}
	}
};

jq(document).ready(function() {
	
	// Site language
	var lang = jq("html").attr('lang') || 'en';
	var i18n = jq.auslfe_multimedia.i18n[lang] || jq.auslfe_multimedia.i18n['en'];
	
	/**
	 * A function for random sorting an array or aray-like object
	 */
	function randOrd(){
		return (Math.round(Math.random())-0.5);
	} 
	
	/**
	 * At load time, remove all images and stop links HREF
	 */
	jq('.portletMultimedia .galleryMultimedia a').each(function() {
		jq(this).attr("href", "javascript:;").find("img").remove();
	});
	
	/**
	 * Prepare portlets to AJAX load images from server
	 */
	jq('.portletMultimedia').each(function(index) {
		var portlet = jq(this);
		// Load random images?
		var rnd = jq("span.random",portlet).length>0;
		// Client reload images?
		var client_reload = jq("span.client_reload",portlet).length>0;
		var link = jq(".portletFooter a", portlet);
		// var timestamps = new Date().getTime();
		var images = null;
		
		/**
		 * Change order on the stored images
		 * @param {boolean} startHidden true if images must start hidden
		 */
		function reorder(startHidden) {
			var startHidden = startHidden || false;
			if (rnd) images.sort(randOrd);
			jq(".galleryMultimedia a", portlet).each(function(index) {
				var link = jq(this);
				var curData = images[index];
				if (!curData.image)
					curData.image = jq('<img alt="'+curData.description+'" title="'+curData.title+'" src="'+curData.url+'/image_tile" '+(startHidden?' style="display:none"':'')+'/>');
				link.append(curData.image);
				curData.image.imagesLoaded(function(e) {
					jq(this).fadeIn("fast");
				});
				link.attr("href", curData.url+"/image_view_fullscreen");
			});
		}
		
		jq.get(link.attr('href')+'/@@query_images', {}, function(data) {
			images = data;
			reorder();
			portlet.removeClass("hideFlag");
		}, dataType='json');
		
		if (rnd && client_reload) {
			// 1 - bind the reload image event
			portlet.bind("portletRefresh", function(event) {
				jq("img", portlet).fadeOut("fast", function() {
					jq("img", portlet).remove();
					reorder(true);
				});
			});
			
			var reloadEventHandler = function() {
				portlet.trigger("portletRefresh");
			};
			var reload_timeout = this.getAttribute('data-reloadtimeout') || jq.auslfe_multimedia.timeout;
			var intval = setInterval(reloadEventHandler, reload_timeout);

			// 2 - handle clicks on portlet title
			jq(".portletHeader", this).attr('title', i18n['stopReload']);
			jq(".portletHeader", this).click(function(e) {
				client_reload = !client_reload;
				if (client_reload) {
					jq(this).attr('title', i18n['stopReload']);
					intval = setInterval(reloadEventHandler, reload_timeout);
					reloadEventHandler();
				}
				else {
					jq(this).attr('title', i18n['restartReload']);
					clearInterval(intval);
				}
			});
		}
		
	});
});

