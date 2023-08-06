eea.google

  This package contains useful tools for talking with Google.

  Main features

    1. A low level API to access Google API;

    2. A CMF portal tool to store Google connections;

    3. Logic to authenticate with Google Analytics without touching Google
       credentials using AuthSub tokens

    4. Logic to create custom Google Analytics reports using
       Google Analytics Data Export API.

  *For more informations about this package see the egg README.txt file*

  Requires:

    * "Plone 2.5+", http://launchpad.net/plone/2.5/2.5.5

    * or "Plone 3.2+", https://launchpad.net/plone/3.2/3.2.3

  Install

    1. no zc.buildout

      * Create a file called **001-eea.google.zcml** in the
        **/path/to/instance/etc/package-includes** directory.  The file
        should only contain this::

        <include package="eea.google" file="configure.zcml" />

    2. zc.buildout

      * buildout.cfg should look like::

        ...
        eggs =
            eea.google

        zcml =
            eea.google

    3. use the QuickInstaller to add this product to your Plone site or using
      portal_setup import profile **Google Tool**.

Documentation

  See the **doc** directory in this package.

Authors and contributors

  * "Alin Voinea", mailto:alin@eaudeweb.ro

  * "Antonio De Marinis", mailto:antonio.de.marinis@eea.europa.eu
