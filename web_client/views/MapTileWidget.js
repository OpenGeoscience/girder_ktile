import geo from 'geojs';
import View from 'girder/views/View';
import { getApiRoot, restRequest } from 'girder/rest';

import template from '../templates/mapTileWidget.pug';

var MapTileWidget = View.extend({
    initialize: function (settings) {
        this.model = settings.model;
    },
    drawMap: function () {
        var url = '/ktile/' + this.model.id + '/info';
        restRequest({
            method: 'GET',
            url: url
        }).done((resp) => {
            var center = [
                (resp.corners.ulx + resp.corners.lrx) / 2,
                (resp.corners.uly + resp.corners.lry) / 2
            ];
            center = geo.transform.transformCoordinates(resp.srs, 'EPSG:4326', center);
            // Create a map object
            var map = geo.map({
                node: this.$('#map'),
                center: {
                    x: center[0],
                    y: center[1]
                },
                zoom: 12,
                max: 22
            });
            this._map = map;

            map.createLayer('osm');
            var layer = map.createLayer('osm', {
                attribution: null,
                keepLower: false
            });
            var url = getApiRoot() + '/ktile/' + this.model.id;
            layer.url((x, y, z) => `${url}/${z}/${x}/${y}`);
        });
    },
    render: function () {
        this.$el.html(template({})).girderModal(this).on('shown.bs.modal', () => {
            this.drawMap();
        }).on('hidden.bs.modal', () => {
            this._map.exit();
        });
        return this;
    }
});

export default MapTileWidget;
