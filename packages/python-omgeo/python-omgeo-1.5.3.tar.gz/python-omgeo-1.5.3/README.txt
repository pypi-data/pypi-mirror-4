**The Oatmeal Geocoder - Python Edition**

``python-omgeo`` is a geocoding abstraction layer written in python.  Currently
supported geocoders:

* Bing
* Citizen Atlas (Washington DC)
* ESRI European address locator (REST & SOAP)
* ESRI North American locator (REST & SOAP)
* ESRI `World Geocoding Service <http://geocode.arcgis.com/arcgis/geocoding.html>`_
* MapQuest Licensed Data API
* MapQuest-hosted Nominatim Open Data API

**Installation**::

    sudo pip install python-omgeo

**Documentation**

Docs are available in `HTML <http://python-omgeo.readthedocs.org/en/latest/>`_ 
or `PDF <http://media.readthedocs.org/pdf/python-omgeo/latest/python-omgeo.pdf>`_ format.

**Usage Example**

Make a new geocoder and geocode and address::

    >>> from omgeo import Geocoder 
    >>> g = Geocoder() 
    >>> result = g.geocode('340 12th St, Philadelphia PA')

Take a look at the result::

    >>> result
    {'candidates': [
      <340 S 12th St, Philadelphia, PA, 19107 (-75.161461, 39.94532) EsriWGS>,
      <340 N 12th St, Philadelphia, PA, 19107 (-75.158434, 39.958728) EsriWGS>
     ],
     'upstream_response_info': [<EsriWGS 1054ms>]}

Take a closer look at the information in our address Candidate objects::

    >>> [c.__dict__ for c in result["candidates"]]
	[{'geoservice': 'EsriWGS',
	  'locator': u'USA.AddressPoint',
	  'locator_type': u'PointAddress',
	  'match_addr': u'340 S 12th St, Philadelphia, PA, 19107',
	  'score': 90.87,
	  'wkid': 4326,
	  'x': -75.161461,
	  'y': 39.94532},
	 {'geoservice': 'EsriWGS',
	  'locator': 'interpolation',
	  'locator_type': u'StreetAddress',
	  'match_addr': u'340 N 12th St, Philadelphia, PA, 19107',
	  'score': 90.87,
	  'wkid': 4326,
	  'x': -75.158434,
	  'y': 39.958728}]