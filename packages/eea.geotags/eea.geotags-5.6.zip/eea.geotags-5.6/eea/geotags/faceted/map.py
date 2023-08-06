"""  Map view
"""
from Products.Five.browser import BrowserView
import json
import urllib
from Products.CMFCore.utils import getToolByName


class MapView(BrowserView):
    """ Map View faceted navigation logic
    """

    def map_points(self, brains):
        """ Return geotags information found on brains
        """
        res = []
        props = getToolByName(self.context, 'portal_properties').site_properties
        for brain in brains:
            if brain.geotags:
                # we only need the features items
                features = json.loads(brain.geotags).get('features')
                for feature in features:
                    location = feature['properties']['description']
                    feature['properties']['description'] = urllib.quote(
                                        location.encode('utf-8'))
                    # #10006 don't fail when urllib can't quote Description
                    try:
                        desc = urllib.quote(brain.Description)
                    except KeyError:
                        desc = brain.Description.encode('utf-8')
                        desc = urllib.quote(desc)
                    feature.update({"itemDescription": desc}) 
                    # title, adminName and name, also need to be escaped 
                    #otherwise jquery will find the json invalid
                    title = feature['properties']['title']
                    feature['properties']['title'] = urllib.quote(
                                        title.encode('utf-8'))
                    adminName = feature['properties'].get('adminName1')
                    if adminName:
                        feature['properties']['adminName1'] = urllib.quote(
                                adminName.encode('utf-8'))
                    name = feature['properties'].get('name')
                    if name:
                        feature['properties']['name'] = urllib.quote(
                                        name.encode('utf-8'))

                    feature.update({"itemUrl": brain.getURL()})
                    feature.update({"itemTitle":
                                        urllib.quote(brain.Title)})
                    feature.update({"itemType": brain.Type})
                    feature.update({"itemIcon": brain.getIcon})
                    start_date = brain.start.strftime(props.localLongTimeFormat)
                    end_date = brain.end.strftime(props.localLongTimeFormat)
                    feature.update({"itemDate": '%s to %s' % (
                                                        start_date, end_date)})
                    feature = json.dumps(feature)
                    res.append(feature)
        return res
