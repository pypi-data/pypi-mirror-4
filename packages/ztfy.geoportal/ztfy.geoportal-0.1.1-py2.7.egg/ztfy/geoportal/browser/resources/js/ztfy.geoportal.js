(function($) {

	if (typeof($.ZTFY) == 'undefined') {
		$.ZTFY = {};
	}

	$.ZTFY.geoportal = {

		/**
		 * 
		 */
		open: function(prefix, target) {
			$.ZTFY.dialog.open(target + '?prefix=' + prefix);
		},

		/**
		 * Initialize GeoPortal map
		 * 
		 * @param target: DIV target ID
		 * @param apiKey: IGN API key
		 * @param territory: ISO territory code
		 * @param projection: SRID or IGNF projection code
		 * @param displayProjection: SRID or IGNF display projection code
		 */
		initViewer: function(target, apiKey, territory, projection, displayProjection) {

			/**
			 * Class: GeoXYForm
			 * Helper class to automate form update of (X,Y) coordinates
			 */
			Geoportal.GeoXYForm = OpenLayers.Class({

				containerId: null,					/* HTML map container ID */
				buttonId: null,						/* HTML ID of a container used to enable/disable map visualization */
				imgButton: null,					/* Image associated to HTML container */
				lonId: null,						/* ID of HTML field containing longitude */
				latId: null,						/* ID of HTML field containing latitude  */
				vectorProjection: 'IGNF:RGF93G',	/* Name of corodinates projection */
				precision: 1000000,					/* Corodinates precision; equivalent of 30cm in geographic projections */
				marker: null,						/* Path to image used to display coordinates */
				container: null,
				button: null,
				Lon: null,
				Lat: null,

				initialize: function(options) {
					OpenLayers.Util.extend(this, options);
					if (typeof(this.vectorProjection) == 'string') {
						this.vectorProjection = new OpenLayers.Projection(this.vectorProjection);
					}
					this.container = parent.document.getElementById(this.containerId);
					this.button = parent.document.getElementById(this.buttonId);
					this.Lon = parent.document.getElementById(this.lonId);
					this.Lat = parent.document.getElementById(this.latId);
				},

				/**
				 * APIMethod: getXInput
				 * Returns the coordinates input field associated with abscissa or longitude
				 */
				getXInput: function() {
					return this.Lon;
				},

				/**
				 * APIMethod: getYInput
				 * Returns the coordinates input field associated with ordinate or latitude.
				 */
				getYInput: function() {
					return this.Lat;
				},

				/**
				 * APIMethod: getX
				 * Returns the coordinates input field value associated with abscissa or longitude.
				 */
				getX: function() {
					if (this.Lon) {
						return parseFloat(this.Lon.value);
					}
					return NaN;
				},

				/**
				 * APIMethod: getY
				 * Returns the coordinates input field value associated with ordinate or latitude.
				 */
				getY: function() {
					if (this.Lat) {
						return parseFloat(this.Lat.value);
					}
					return NaN;
				},

				/**
				 * APIMethod: setX
				 * Assigns the coordinates input field value associated with abscissa or longitude.
				 */
				setX: function(x) {
					if (this.Lon && !isNaN(parseFloat(x))) {
						this.Lon.value = x;
					}
				},

				/**
				 * APIMethod: setY
				 * Assigns the coordinates input field value associated with ordinate or latitude.
				 */
				setY: function(y) {
					if (this.Lat && !isNaN(parseFloat(y))) {
						this.Lat.value = y;
					}
				},

				/**
				 * APIMethod: getPrecision
				 * Returns the 10**number of figures
				 */
				getPrecision: function() {
					return this.precision ? this.precision : 1000000;
				},

				/**
				 * APIMethod: getNativeProjection
				 * Returns the projection of the vector layer
				 */
				getNativeProjection: function() {
					return this.vectorProjection;
				},

				/**
				 * Constant: CLASS_NAME
				 */
				CLASS_NAME: 'Geoportal.GeoXYForm'
			});

			var options = {
				mode: 'normal',
				territory: territory || 'FXX',
				projection: projection || 'IGNF:GEOPORTALFXX',
				displayProjection: displayProjection || 'IGNF:RGF93G',
				proxy: 'http://api.ign.fr/geoportail/api/xmlproxy?url='
			};
			var viewer = new Geoportal.Viewer.Default(target, OpenLayers.Util.extend(
				options,
				window.gGEOPORTALRIGHTSMANAGEMENT === undefined ? { 'apiKey': apiKey } : gGEOPORTALRIGHTSMANAGEMENT
			));
			viewer.addGeoportalLayers(['ORTHOIMAGERY.ORTHOPHOTOS',
			                           'GEOGRAPHICALGRIDSYSTEMS.MAPS'], {});

			var target = $('DIV[id=' + target + ']').get(0);
			$.data(target, 'ztfy.geoportal.viewer', viewer);

			var lonId = 'location-widgets-longitude';
			var latId = 'location-widgets-latitude';

			var formInfo = {
				containerId: target,
				lonId: lonId,
				latId: latId,
				vectorProjection: new OpenLayers.Projection('EPSG:4326'),  /* WGS84 coordinates */
				precision: 1000000,
				marker: '/--static--/ztfy.geoportal/img/pin.png'
			};
			var gpForm = new Geoportal.GeoXYForm(formInfo);
			viewer.setVariable('gpForm', gpForm);
			var styles = null;
			if (gpForm.marker) {
				styles = new OpenLayers.StyleMap({
					'default': OpenLayers.Util.extend({
						externalGraphic: gpForm.marker,
						graphicOpacity: 1,
						graphicWidth: 14,
						graphicHeight: 14,
						graphicXOffset: 0,
						graphicYOffset: -14,
						fill : false
					}, OpenLayers.Feature.Vector['default']),
					'temporary': OpenLayers.Util.extend({
						display: 'none'
					}, OpenLayers.Feature.Vector['temporary'])
				});
			}

			var dialogs = $.ZTFY.dialog.dialogs;
			if (dialogs.length > 0) {
				var src = dialogs[dialogs.length-1].src;
				var prefix = $.ZTFY.getQueryVar(src, 'prefix');
				if (prefix) {
					prefix = prefix.replace(/\./g, '-');
					lonId = prefix + '-longitude';
					latId = prefix + '-latitude';
				}
			}

			var parentFormInfo = {
				containerId: target,
				lonId: lonId,
				latId: latId,
				vectorProjection: new OpenLayers.Projection('EPSG:4326'),
				precision: 1000000,
				marker: '/--static--/ztfy.geoportal/img/pin.png'
			};
			var gpParentForm = new Geoportal.GeoXYForm(parentFormInfo);
			viewer.setVariable('gpParentForm', gpParentForm);

			var vlayer= new OpenLayers.Layer.Vector(
				'POINT_XY', {
					projection: gpForm.vectorProjection,
					displayInLayerSwitcher:false,
					calculateInRange: function() { return true; },
					styleMap: styles
				}
			);
			viewer.getMap().addLayer(vlayer);

			var draw_feature= new OpenLayers.Control.DrawFeature(
				vlayer,
				OpenLayers.Handler.Point,
				{
					autoActivate:true,
					callbacks: {
						done: function (geometry) {
							this.layer.destroyFeatures();
							var feature= new OpenLayers.Feature.Vector(geometry, {'pictoUrl': '/--static--/ztfy.geoportal/img/pin.png'});
							feature.state = OpenLayers.State.INSERT;
							this.layer.addFeatures([feature]);
							$.ZTFY.geoportal.updateXYForm(feature);
						}
					},
					handlerOptions: {
						persist: false,
						layerOptions:{
							projection: gpForm.vectorProjection
						}
					}
				}
			);
			viewer.getMap().addControl(draw_feature);

			OpenLayers.Event.observe(gpForm.getXInput(), "change", $.ZTFY.geoportal.updateFeature);
			OpenLayers.Event.observe(gpForm.getYInput(), "change", $.ZTFY.geoportal.updateFeature);
			$.ZTFY.geoportal.updateFeature();

			return viewer;
		},

		/**
		 * Get viewer associated with a given target
		 */
		getViewer: function(target) {
			if (typeof(target) == 'string') {
				var target = $('DIV[id='+target+']').get(0);
			}
			return $.data(target, 'ztfy.geoportal.viewer');
		},

		updateXYForm: function(feature, pix) {
			if (!feature || !feature.geometry  || !feature.geometry.x || !feature.geometry.y) {
				return;
			}
			var viewer = $.ZTFY.geoportal.getViewer('mapviewer');
			var pt = feature.geometry.clone();
			/* form update */
			var gpForm = viewer.getVariable('gpForm');
			pt.transform(viewer.getMap().getProjection(), gpForm.getNativeProjection());
			var invp = gpForm.getPrecision();
			gpForm.setX(Math.round(pt.x*invp)/invp);
			gpForm.setY(Math.round(pt.y*invp)/invp);
			/* parent form update */
			var gpParentForm = viewer.getVariable('gpParentForm');
			if (gpParentForm) {
				var invp = gpParentForm.getPrecision();
				gpParentForm.setX(Math.round(pt.x*invp)/invp);
				gpParentForm.setY(Math.round(pt.y*invp)/invp);
			}
			delete pt;
		},

		updateFeature: function (elt, val) {
			var viewer = $.ZTFY.geoportal.getViewer('mapviewer');
			var vlayer = viewer.getMap().getLayersByName('POINT_XY')[0];
			var feature = vlayer.features[0];
			var gpForm = viewer.getVariable('gpForm');
			var x = gpForm.getX();
			var y = gpForm.getY();
			if (!isNaN(x) && !isNaN(y)) {
				// Delete previous point
				vlayer.destroyFeatures();
				// Transform coordinates
				var geometry = new OpenLayers.Geometry.Point(x,y);
				geometry.transform(gpForm.getNativeProjection(), viewer.getMap().getProjection());
				// Add marker
				feature = new OpenLayers.Feature.Vector(geometry);
				feature.state = OpenLayers.State.INSERT;
				vlayer.addFeatures(feature);
				// Set map position, keeping previous zoom scale
				viewer.getMap().setCenterAtLonLat(x, y);
			}
			// Initialize
			$.ZTFY.geoportal.updateXYForm(feature);
			return true;
		},

		/**
		 * Hide viewer controls
		 * 
		 * @param viewer: GeoPortal viewer containing controls to hide
		 */
		hideControls: function(viewer) {
			viewer.lyrSwCntrl.showControls('none');
			viewer.toolBoxCntrl.showControls('none');
			viewer.infoCntrl.minimizeControl();
		},

		/**
		 * Define map position
		 */
		setPosition: function(viewer, position, layer, zoom, extent) {
			var map = viewer.map;
			map.setCenterAtLonLat(position.lon, position.lat);
			if (layer) {
				if (!extent) {
					var extent = layer.getDataExtent();
				}
				if (extent) {
					var zoom = map.getZoomForExtent(extent.transform(map.getDisplayProjection(), layer.projection), true);
				}
			}
			if (!zoom) {
				var zoom = 10;
			}
			map.setCenterAtLonLat(position.lon, position.lat, zoom);
		}
	}

})(jQuery);