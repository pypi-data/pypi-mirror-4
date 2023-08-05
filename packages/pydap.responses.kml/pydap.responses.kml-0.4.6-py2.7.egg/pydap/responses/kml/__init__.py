from urllib import urlencode

from paste.request import construct_url, parse_dict_querystring

from pydap.model import *
from pydap.responses.lib import BaseResponse
from pydap.util.template import GenshiRenderer, StringLoader, TemplateNotFound
from pydap.lib import walk

from pydap.responses.wms import is_valid, fix_map_attributes


LINKS = """<?xml version="1.0" encoding="UTF-8"?>
<kml
        xmlns="http://earth.google.com/kml/2.0"
        xmlns:py="http://genshi.edgewall.org/">
<Document>
<name>$name</name>
<description>$description</description>
<visibility>1</visibility>
<open>1</open>
<NetworkLink py:for="layer in layers">
  <name>${layer.name}</name>
  <flyToView>0</flyToView>
  <visibility>0</visibility>
  <Url>
    <href>${layer.location}</href>
    <viewRefreshMode>onStop</viewRefreshMode>
    <viewRefreshTime>1</viewRefreshTime>
    <ViewFormat>BBOX=[bboxWest],[bboxSouth],[bboxEast],[bboxNorth]</ViewFormat>
  </Url>
<refreshVisibility>1</refreshVisibility>
</NetworkLink>
</Document>
</kml>"""

OVERLAYS = """<?xml version="1.0" encoding="UTF-8"?>
<kml
        xmlns="http://earth.google.com/kml/2.0"
        xmlns:py="http://genshi.edgewall.org/">
<Document>
<GroundOverlay>
  <name>WMS image for $name</name>
  <Icon>
    <href>$location</href>
  </Icon>
  <LatLonBox>
    <north>${bbox[3]}</north>
    <south>${bbox[1]}</south>
    <east>${bbox[2]}</east>
    <west>${bbox[0]}</west>
  </LatLonBox>
</GroundOverlay>

<ScreenOverlay>
  <name>Colorbar for $name</name>
  <overlayXY x="0" y="0" xunits="fraction" yunits="fraction"/>
  <screenXY x="20" y="20" xunits="pixels" yunits="pixels"/>
  <size x="-1" y="-1" xunits="fraction" yunits="fraction"/> 
  <Icon>
    <href>$colorbar</href>
  </Icon>
</ScreenOverlay> 
</Document>
</kml>"""


class KMLResponse(BaseResponse):

    __description__ = "Google Earth"

    renderer = GenshiRenderer(
            options={}, loader=StringLoader( {
                'links.kml': LINKS,
                'overlays.kml': OVERLAYS } ))

    def __init__(self, dataset):
        BaseResponse.__init__(self, dataset)
        self.headers.append( ('Content-description', 'dods_kml') )
        self.headers.append( ('Content-type', 'application/vnd.google-earth.kml+xml') )

    def __call__(self, environ, start_response):
        query = parse_dict_querystring(environ)
        layers = query.get('LAYERS')
        if not layers:
            # Return a network link for each layer, pointing back to this
            # file but with a LAYERS variable.
            self.serialize = self._links(environ)
        else:
            # Return overlay for this layer.
            self.serialize = self._overlays(environ)

        return BaseResponse.__call__(self, environ, start_response)

    def _links(self, environ):
        """
        Return links to each layer.

        """
        query = parse_dict_querystring(environ)

        def serialize(dataset):
            layers = []
            fix_map_attributes(dataset)
            for grid in walk(dataset, GridType):
                if is_valid(grid, dataset):
                    query['LAYERS'] = grid.id
                    layers.append({
                        'name': getattr(grid, 'long_name', grid.name),
                        'location': construct_url(environ,
                            querystring=urlencode(query)),
                    })
            context = {
                    'description': getattr(dataset, 'history', ''),
                    'name': dataset.name,
                    'layers': layers,
                    }
            return self._render(context, 'links.kml', dataset, environ)
        return serialize

    def _overlays(self, environ):
        query = parse_dict_querystring(environ)
        layers = query['LAYERS']
        bbox = query.get('BBOX', '-180,-90,180,90').split(',')

        # Additional info,
        query['SERVICE'] = 'WMS'
        query['VERSION'] = '1.1.1'
        query['SRS'] = 'EPSG:4326'
        query['WIDTH'] = '512'
        query['HEIGHT'] = '512'
        query['TRANSPARENT'] = 'TRUE'
        query['FORMAT'] = 'image/png'

        def serialize(dataset):
            context = {
                    'name': layers,
                    'bbox': bbox,
                    }

            query['REQUEST'] = 'GetMap'
            context['location'] = construct_url(environ,
                    path_info=environ['PATH_INFO'].replace('.kml', '.wms'),
                    querystring=urlencode(query))

            query['REQUEST'] = 'GetColorbar'
            context['colorbar'] = construct_url(environ,
                    path_info=environ['PATH_INFO'].replace('.kml', '.wms'),
                    querystring=urlencode(query))

            return self._render(context, 'overlays.kml', dataset, environ)
        return serialize

    def _render(self, context, filename, dataset, environ):
        """
        Load the template using the specified renderer, or fallback to the 
        default template since most of the people won't bother installing
        and/or creating a capabilities template -- this guarantee that the
        response will work out of the box.

        """
        try:
            renderer = environ.get('pydap.renderer', self.renderer)
            template = renderer.loader(filename)
        except TemplateNotFound:
            renderer = self.renderer
            template = renderer.loader(filename)

        output = renderer.render(template, context, output_format='application/vnd.google-earth.kml+xml')
        if hasattr(dataset, 'close'): dataset.close()
        return [output]
