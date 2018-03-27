/*
 * Leaflet-IIIF 1.2.2
 * IIIF Viewer for Leaflet
 * by Jack Reed, @mejackreed
 *
 * Rewrite Morgan Legal to remove jquery dependency and make it es6 module compliant
 *
 */

//import L from 'leaflet';
import axios from 'axios';


const L = window.L;
L.TileLayer.Iiif = L.TileLayer.extend({
  options: {
    continuousWorld: true,
    tileSize: 256,
    updateWhenIdle: true,
    tileFormat: 'jpg',
    fitBounds: true,
    setMaxBounds: false
  },

  initialize: function(url, options) {
    options = typeof options !== 'undefined' ? options : {};

    if (options.maxZoom) {
      this._customMaxZoom = true;
    }

    // Check for explicit tileSize set
    if (options.tileSize) {
      this._explicitTileSize = true;
    }

    // Check for an explicit quality
    if (options.quality) {
      this._explicitQuality = true;
    }

    options = L.setOptions(this, options);
    this._infoUrl = url;
    this._baseUrl = this._templateUrl();
    this._getInfo();
  },
  getTileUrl: function(coords) {
    let
      x = coords.x,
      y = (coords.y),
      zoom = this._getZoomForUrl(),
      scale = Math.pow(2, this.maxNativeZoom - zoom),
      tileBaseSize = this.options.tileSize * scale,
      minx = (x * tileBaseSize),
      miny = (y * tileBaseSize),
      maxx = Math.min(minx + tileBaseSize, this.x),
      maxy = Math.min(miny + tileBaseSize, this.y);

    let xDiff = (maxx - minx);
    let yDiff = (maxy - miny);

    return L.Util.template(this._baseUrl, L.extend({
      format: this.options.tileFormat,
      quality: this.quality,
      region: [minx, miny, xDiff, yDiff].join(','),
      rotation: 0,
      size: Math.ceil(xDiff / scale) + ','
    }, this.options));
  },
  onAdd: function(map) {
  },
  _addTileLayer : function () {

    let map = this._map;
    // Set maxZoom for map
    map._layersMaxZoom = this.maxZoom;

    // Call add TileLayer
    L.TileLayer.prototype.onAdd.call(this, map);

    if (this.options.fitBounds) {
      this._fitBounds();
    }

    if(this.options.setMaxBounds) {
      this._setMaxBounds();
    }

    // Reset tile sizes to handle non 256x256 IIIF tiles
    this.on('tileload', function(tile, url) {

      let height = tile.tile.naturalHeight,
        width = tile.tile.naturalWidth;

      // No need to resize if tile is 256 x 256
      if (height === 256 && width === 256) return;

      tile.tile.style.width = width + 'px';
      tile.tile.style.height = height + 'px';

    });
  },
  onRemove: function(map) {
    // Remove maxBounds set for this image
    if(this.options.setMaxBounds) {
      map.setMaxBounds(null);
    }

    // Call remove TileLayer
    L.TileLayer.prototype.onRemove.call(this, map);

  },
  _fitBounds: function() {

    // Find best zoom level and center map
    let initialZoom = this._getInitialZoom(this._map.getSize());
    let imageSize = this._imageSizes[initialZoom];
    let sw = this._map.options.crs.pointToLatLng(L.point(0, imageSize.y), initialZoom);
    let ne = this._map.options.crs.pointToLatLng(L.point(imageSize.x, 0), initialZoom);
    let bounds = L.latLngBounds(sw, ne);

    this._map.fitBounds(bounds, true);
  },
  _setMaxBounds: function() {

    // Find best zoom level, center map, and constrain viewer
    let initialZoom = this._getInitialZoom(this._map.getSize());
    let imageSize = this._imageSizes[initialZoom];
    let sw = this._map.options.crs.pointToLatLng(L.point(0, imageSize.y), initialZoom);
    let ne = this._map.options.crs.pointToLatLng(L.point(imageSize.x, 0), initialZoom);
    let bounds = L.latLngBounds(sw, ne);

    this._map.setMaxBounds(bounds, true);
  },
  _getInfo: function() {

    // Look for a way to do this without jQuery
    axios.get(this._infoUrl)
      .then((response) => {
        let data = response.data;

        this.y = data.height;
        this.x = data.width;

        let tierSizes = [],
          imageSizes = [],
          scale,
          width_,
          height_,
          tilesX_,
          tilesY_;

        // Set quality based off of IIIF version
        if (data.profile instanceof Array) {
          this.profile = data.profile[0];
        }else {
          this.profile = data.profile;
        }

        this._setQuality();

        // Unless an explicit tileSize is set, use a preferred tileSize
        if (!this._explicitTileSize) {
          // Set the default first
          this.options.tileSize = 256;
          if (data.tiles) {
            // Image API 2.0 Case
            this.options.tileSize = data.tiles[0].width;
          } else if (data.tile_width){
            // Image API 1.1 Case
            this.options.tileSize = data.tile_width;
          }
        }

        function ceilLog2(x) {
          return Math.ceil(Math.log(x) / Math.LN2);
        };

        // Calculates maximum native zoom for the layer
        this.maxNativeZoom = Math.max(ceilLog2(this.x / this.options.tileSize),
          ceilLog2(this.y / this.options.tileSize));

        // Enable zooming further than native if maxZoom option supplied
        if (this._customMaxZoom && this.options.maxZoom > this.maxNativeZoom) {
          this.maxZoom = this.options.maxZoom;
        }
        else {
          this.maxZoom = this.maxNativeZoom;
        }

        for (let i = 0; i <= this.maxZoom; i++) {
          scale = Math.pow(2, this.maxNativeZoom - i);
          width_ = Math.ceil(this.x / scale);
          height_ = Math.ceil(this.y / scale);
          tilesX_ = Math.ceil(width_ / this.options.tileSize);
          tilesY_ = Math.ceil(height_ / this.options.tileSize);
          tierSizes.push([tilesX_, tilesY_]);
          imageSizes.push(L.point(width_,height_));
        }

        this._tierSizes = tierSizes;
        this._imageSizes = imageSizes;

        this._addTileLayer();
      })
      .catch(function (error) {
        throw error;
      });
  },

  _setQuality: function() {
    let profileToCheck = this.profile;

    if (this._explicitQuality) {
      return;
    }

    // If profile is an object
    if (typeof(profileToCheck) === 'object') {
      profileToCheck = profileToCheck['@id'];
    }

    // Set the quality based on the IIIF compliance level
    switch (true) {
      case /^http:\/\/library.stanford.edu\/iiif\/image-api\/1.1\/compliance.html.*$/.test(profileToCheck):
        this.options.quality = 'native';
        break;
      // Assume later profiles and set to default
      default:
        this.options.quality = 'default';
        break;
    }
  },

  _infoToBaseUrl: function() {
    return this._infoUrl.replace('info.json', '');
  },
  _templateUrl: function() {
    return this._infoToBaseUrl() + '{region}/{size}/{rotation}/{quality}.{format}';
  },
  _isValidTile: function(coords) {
    let
      zoom = this._getZoomForUrl(),
      sizes = this._tierSizes[zoom],
      x = coords.x,
      y = (coords.y);

    if (!sizes) return false;
    if (x < 0 || sizes[0] <= x || y < 0 || sizes[1] <= y) {
      return false;
    }else {
      return true;
    }
  },
  _getInitialZoom: function (mapSize) {
    let
      tolerance = 0.8,
      imageSize;

    for (let i = this.maxNativeZoom; i >= 0; i--) {
      imageSize = this._imageSizes[i];
      if (imageSize.x * tolerance < mapSize.x && imageSize.y * tolerance < mapSize.y) {
        return i;
      }
    }
    // return a default zoom
    return 2;
  }
});

const tileLayerIiif = L.tileLayer.iiif = function(url, options) {
  return new L.TileLayer.Iiif(url, options);
};
export default tileLayerIiif;
