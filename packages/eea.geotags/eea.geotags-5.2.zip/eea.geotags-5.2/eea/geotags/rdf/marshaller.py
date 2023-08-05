""" RDF Marshaller module for geotags """

from eea.geotags.field.location import GeotagsFieldMixin
from eea.geotags.interfaces import IGeoTags
from eea.rdfmarshaller.archetypes.fields import ATField2Surf
from eea.rdfmarshaller.archetypes.interfaces import IATField2Surf
from eea.rdfmarshaller.interfaces import ISurfSession
from zope.component import adapts, getAdapter
from zope.interface import implements, Interface

import surf
import rdflib

class GeotagsField2Surf(ATField2Surf):
    """Adapter to express geotags field with RDF using Surf."""
    implements(IATField2Surf)
    adapts(GeotagsFieldMixin, Interface, ISurfSession)

    prefix = "dcterms"
    name = "spatial"

    def value(self):
        """desired RDF output is like:

        <document:Document
        rdf:about="
        http://www.eea.europa.eu/data-and-maps/daviz/learn-more/prepare-data">
        ...
        <dct:spatial>
            <geo:SpatialThing>
            <rdfs:label>Rome</rdfs:label>
            <geo:lat>41.901514</geo:lat>
            <geo:long>12.460774</geo:long>
            </geo:SpatialThing>
        </dct:spatial>
        <dct:spatial>
            <geo:SpatialThing>
            <rdfs:label>Bucharest</rdfs:label>
            <geo:lat>44.437711</geo:lat>
            <geo:long>26.097367</geo:long>
            <owl:sameAs rdf:resource="http://sws.geonames.org/683506/">
            </geo:SpatialThing>
        </dct:spatial>
        ...
        </document:Document>

        """
        # create a GeoPoint Class
        SpatialThing = self.session.get_class(surf.ns.GEO.SpatialThing)

        geo = getAdapter(self.context, IGeoTags)

        output = []
        i = 0

        for feature in geo.getFeatures():
            rdfp = self.session.get_resource("#geotag%s" % i, SpatialThing)

            label = feature['properties']['title']
            rdfp[surf.ns.RDFS['label']] = label

            latitude = feature['properties']['center'][0]
            rdfp[surf.ns.GEO['lat']] = float(latitude)

            longitude = feature['properties']['center'][1]
            rdfp[surf.ns.GEO['long']] = float(longitude)

            if feature['properties']['other'].has_key('geonameId'):
                geonamesURI = 'http://sws.geonames.org/%s/' % (
                            str(feature['properties']['other']['geonameId']))
                rdfp[surf.ns.OWL['sameAs']] = rdflib.URIRef(geonamesURI)
            rdfp.update()
            output.append(rdfp)

            i += 1

        return output

