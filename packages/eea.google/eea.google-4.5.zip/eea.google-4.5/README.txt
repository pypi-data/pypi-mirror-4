EEA Google product
==================

This package contains useful tools for talking with Google Analytics.


Contents
========

.. contents::


Main features
=============

  1. A low level API to access Google API;
  2. A CMF portal tool to store Google connections;
  3. Logic to authenticate with Google Analytics without touching Google
     credentials using `AuthSub tokens`_
  4. Logic to create custom Google Analytics reports using
     `Google Analytics Data Export API`_.

Google Analytics reports created this way can be made available via portlets. Right
now there is an example under skins folder.


Google API (eea.google.api)
===========================

A python package that provides a low level Google Connection and a generic
connection error GoogleClientError. To use this connection you'll need an
AuthBase authentication token. You can get one by calling Google like:

  https://www.google.com/accounts/AuthSubRequest?scope=https://www.google.com/analytics/feeds/&session=1&next=http://yourdomain.com/do_something_with_token

After you login into your Google Analytics account, you'll be asked to grant
access to **yourdomain.com** to access Analytics statistics. If you do so, Google
will redirect your browser to the **next** link provided, adding a request
parameter **token=<one-session-authsub-token>**, in our case

  http://yourdomain.com/do_something_with_token?token=ADFAFDDKLJH14234__ASDD

As this token was provided in clear to you, it can be used only once to query
Google API, that's why you'll need to exchange it for a multi-session one.
But this time you can not do it from browser. So here eea.google.api comes in.

  >>> from eea.google.api import Connection
  >>> google = Connection(token='ADFAFDDKLJH14234__ASDD')
  >>> new_token = google.token2session()

If you provided an invalid token it will quietly fail and return you a
None object, else it will return you a multi-session token. Now you are
connected with Google, forever :).

With this connection you can check it's status:

  >>> google.status
  (200, 'OK')

Or make a call:

  >>> response = google(scope, data, method='GET')

  - scope  - the Google service you want to access;
  - data   - query parameters
  - method - request method: GET or POST

If something doesn't work well this will raise a GoogleClientError, else
it will return a `Google Data Feed Response`_

  >>> response.read()
  <?xml ...

You can also make a safe request by calling **.request** method. This will return
a None object if something works wrong.

  >>> google.request(scope, data, method='GET')


Google Tool (eea.google.tool)
=============================

A CMF portal tool that can be retrieved using CMF method getToolByName: This a
simple container for Google connections. It provides a basic browser interface
to add and remove connections.

  >>> from Products.CMFCore.utils import getToolByName
  >>> tool = getToolByName(portal, 'portal_google')


Google Analytics (eea.google.analytics)
=======================================

This package provides the browser interface to register with Google Analytics
and defines two storage models: Analytics and AnalyticsReport. Also it provides
a utility to easily access low level api.Connection and another one to parse
Google response XML.

Analytics
---------
This will store AuthSub token and it's also a container for Analytics Reports.
It provides a basic browser interface to get token from Google and to manage
reports.

Analytics Report
----------------
A Google Analytics custom report by dimensions, metrics, start-date, end-date,
filters and sort order. It is actually a query object for Google Analytics API.

  >>> from zope.component import getMultiAdapter
  >>> report = tool.analytics.report
  >>> xml = getMultiAdapter((report, request), 'index.xml')

Now you have a custom XML report based on defined filters.

Connection Utility
------------------
Easily access low level eea.google.api.Connection using zope components

  >>> from zope.component import getUtility
  >>> from eea.google.analytics.interfaces import IGoogleAnalyticsConnection
  >>> utility = getUtility(IGoogleAnalyticsConnection)
  >>> conn = utility(token='ABCDEFGH__FAH')

XML Parser utility
------------------
Parse Google reponse XML

  >>> from zope.component import getUtility
  >>> from eea.google.analytics.interfaces import IXMLParser
  >>> parse = getUtility(IXMLParser)
  >>> table = parse(xml)

Here table is a (dimensions, metrics) python generator

  >>> dimensions, metrics = table.next()
  >>> dimensions
  {'ga:pagePath': '/some/doc/path', 'ga:browser': 'Firefox'}

  >>> metrics
  {'ga:pageviews': u'34235', 'ga:timeOnPage': '2433.0'}


Dependencies
============

  1. python2.4+
  2. Plone 2.5.x or Plone 3.x. (optional if you're using only eea.google.api package).


Source code
===========

Latest source code (Plone 4 compatible):
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.google/trunk

Plone 2 and 3 compatible:
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.google/branches/plone25


Copyright and license
=====================

The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Google (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

Contributor(s): Alin Voinea (Eau de Web),
                Antonio De Marinis (European Environment Agency),

More details under docs/License.txt


Funding
=======

  EEA_ - European Enviroment Agency (EU)


.. _EEA: http://www.eea.europa.eu/
.. _`AuthSub tokens`: http://code.google.com/apis/accounts/docs/AuthSub.html
.. _`Google Analytics Data Export API`: http://code.google.com/apis/analytics/docs/gdata/gdataReferenceDataFeed.html
.. _`Google Data Feed Response`: http://code.google.com/apis/analytics/docs/gdata/gdataReferenceDataFeed.html#dataResponse
