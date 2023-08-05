from fanstatic import Library
from fanstatic import Resource
from js.jquery import jquery


library = Library(
    'highcharts',
    'resources')
highcharts = Resource(
    library,
    'highcharts.src.js',
    minified='highcharts.js',
    depends=[jquery, ])
highcharts_exporting = Resource(
    library,
    'modules/exporting.src.js',
    minified='modules/exporting.js',
    depends=[highcharts, ])
