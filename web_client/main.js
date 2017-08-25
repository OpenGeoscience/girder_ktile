import View from 'girder/views/View';
import { wrap } from 'girder/utilities/PluginUtils';
import FileListWidget from 'girder/views/widgets/FileListWidget';
import 'girder/utilities/jquery/girderModal';
import geo from 'geojs';
import {getApiRoot, restRequest} from 'girder/rest';
import _ from 'underscore';

import ButtonView from './templates/view.pug';
import MapWidgetTemplate from './templates/mapWidget.pug';

import './stylesheets/map.styl';

wrap(FileListWidget, 'render', function (render) {
    render.call(this);
    this.mapWidget = new MapViewWidget({
        el: $('#g-dialog-container'),
        parentView: this
    });
    _.each(this.$('.g-file-list-link'), (link) => {
        const file = this.collection.get($(link).attr('cid'));
        if (file.get('mimeType') === 'image/tiff') {
            $(link).after(ButtonView({cid: file.cid}));
        }
    });

});

var MapViewWidget = View.extend({
    drawMap: function (fileId) {
        var url = '/ktile/' + fileId + '/info';
        restRequest({
            method: 'GET',
            path: url
        }).done(_.bind(function (resp) {
            var center = [(resp.corners.ulx + resp.corners.lrx) / 2,
                          (resp.corners.uly + resp.corners.lry) / 2];
            var center_wgs84 = geo.transform.transformCoordinates(
                resp.srs, 'EPSG:4326', center
            );
            $(function () {
                'use strict';
                // Create a map object
                var map = geo.map({
                    node: '#map',
                    center: {
                        x: center_wgs84[0],
                        y: center_wgs84[1]
                    },
                    zoom: 12,
                    max: 22
                });

                map.createLayer('osm');
                var layer = map.createLayer('osm', {
                    attribution: null,
                    keepLower: false
                });
                var url = getApiRoot() + '/ktile/' + fileId;
                layer.url((x, y, z) => `${url}/${z}/${x}/${y}`);
            });
        }, this));

    },
    render: function () {
        var fileId = this.parentView.collection.models[0].get('_id');
        this.drawMap(fileId);
        this.$el.html(MapWidgetTemplate({})).girderModal(this);
        return this;
    }
});

FileListWidget.prototype.events['click a.g-visualize-layer'] = function (e) {
    this.mapWidget.render();
};
