A Google Maps solution for Plone
--------------------------------

The main purpose of this product is to provide a very simple to use
Google Maps integration for Plone. The following goals were set for
development:

- Ease of use
    - Add locations to a folder
    - Set the view of the folder to Map
    - It figures out how to center and zoom the map automatically
- Flexibility for enhancement by using the Zope 3 component architecture
- Sane fallbacks when Javascript is not available
- Clean separation of javascript, templates and logic
- Works on Topics

Installation
------------

Maps shows up in the "Add-ons" configuration panel.

To use Google Maps you need an "Google Maps API key from
Google":http://www.google.com/apis/maps/signup.html.

You can use the "Maps settings" configuration panel to add keys.

You need to use the URL at which your site is normally available from the
outside (most likely your own domain). You can just use the root of your site
for the registration and the key will automatically be used for all maps on
the site. If you have a map on your site which sees much traffic, then you
may want to register another key for it's URL, so the volume limits from
Google Maps are spread out a bit.

Two keys are included for testing with the following URLs:

- http://localhost:8080
- http://testing:8080


UK and China address search
---------------------------

The default Google Maps geocoding (search for coordinates by address) doesn't
work everywhere. As of May 2007 it doesn't work in the UK and China for
example.

We have added a workaround for this. To activate this workaround feature
you'll have to add a key for Google AJAX Search to enable search for those
regions.

To use the Google AJAX Search fallback, you need an "Google AJAX Search API
key from Google":http://code.google.com/apis/ajaxsearch/signup.html.

The same rules as for the map key apply, see above.

Implementing custom content with map field
------------------------------------------

If you want to add location foeld to your custom content type, you should
implement the following steps:

Add GeoLocation field::

    from Products.Maps.field import LocationWidget, LocationField
    from Products.Maps.interfaces import IMapEnabled, ILocation

    MyContentSchema = ...

        LocationField('geolocation',
                  required=False,
                  searchable=False,
                  validators=('isGeoLocation',),
                  widget = LocationWidget(label = u'Event location'),
        ),
        ... 

Update your class definition::

    class MyContent(ATCTContent):
        """ my content description """
        implements(IMyContent, IMapEnabled, ILocation)
    
        ... 

        def getMarkerIcon(self):
            """ Can be implemented as select field. See Maps.Location content """
            return "Red Marker"

Add following snippet to custom content view/template::

    <div class="googleMapView googleMapLocation"
         tal:define="view context/@@maps_googlemaps_view">
        <dl metal:use-macro="here/maps_map/macros/markers">
        </dl>
    </div>


Dependencies
------------

- Plone 4.x


Credits
-------

Created by Florian Schulze for Jarn AS in 2007.

Parts are based on:

- "ATGoogleMaps":http://takanory.net/plone/develop/atgooglemaps
- "qPloneGoogleMaps":http://projects.quintagroup.com/products/wiki/qPloneGoogleMaps
- "geolocation":http://svn.quintagroup.com/products/geolocation/


Development sponsored by
------------------------

The "Student Services of Bergen, Norway":http://sib.no

"University of Oxford":http://medsci.ox.ac.uk (Medical Sciences Division)


A Jarn AS product
-----------------

"http://www.jarn.com":http://www.jarn.com

"info@jarn.com":mailto:info@jarn.com
