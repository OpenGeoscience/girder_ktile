import $ from 'jquery';
import _ from 'underscore';
import { wrap } from 'girder/utilities/PluginUtils';
import FileListWidget from 'girder/views/widgets/FileListWidget';
import 'girder/utilities/jquery/girderModal';

import MapTileWidget from './views/MapTileWidget.js';
import buttonViewTemplate from './templates/buttonView.pug';

import './stylesheets/style.styl';

wrap(FileListWidget, 'render', function (render) {
    render.call(this);
    _.each(this.$('.g-file-list-link'), (link) => {
        const file = this.collection.get($(link).attr('cid'));
        if (file.get('mimeType') === 'image/tiff' ||
	    file.get('mimeType') === 'application/x-esri-shape') {
            $(link).after(buttonViewTemplate({cid: file.cid}));
        }
    });
});

FileListWidget.prototype.events['click a.g-visualize-layer'] = function (e) {
    let cid = $(e.currentTarget).attr('file-cid');
    new MapTileWidget({
        el: $('#g-dialog-container'),
        model: this.collection.get(cid),
        parentView: this
    }).render();
};
