function acr_create_gmap(who, where, zoom) {
	if (GBrowserIsCompatible()) {
		var element = document.getElementById(who);
		var map = new GMap2(element);
		var geocoder = new GClientGeocoder();
		geocoder.getLatLng(
		    where,
		    function(point) {
		      if (!point) {
		        jQuery(element).html('Address not found');
		      } else {
		        map.setCenter(point, zoom);
		        var marker = new GMarker(point);
		        map.addOverlay(marker);
		        marker.openInfoWindowHtml("<div class='acr_map_baloon'><b>"+where+"</b></div>");
		      }
		    }
		);
	}
}