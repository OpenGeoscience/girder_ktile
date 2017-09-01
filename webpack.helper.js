module.exports = function (config) {
    config.resolve = config.resolve || {};
    config.resolve.alias = config.resolve.alias || {};
	// Remove once geojs fix related issue
    config.resolve.alias['Hammer'] = 'hammerjs/hammer.js';
    return config;
}