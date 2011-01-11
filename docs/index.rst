=======================
api.creativecommons.org
=======================

:Author: Nathan R. Yergler, John E. Doig III
:Updated: $Date: 2009-04-02 10:57:29 -0700 (Thu, 02 Apr 2009) $

Creative Commons provides web service APIs which can be used to integrate 
the Creative Commons licensing engine into third party applications. 

The following versions are available:

.. toctree::
   :maxdepth: 1

   1.0 <readme_10>
   1.5 <readme_15>
   Development <readme_dev>

The current in-development API is described in the 
:doc:`development version documentation <readme_dev>`.  These APIs are currently in beta, and we are soliciting 
feedback and suggestions. As such, the API may change in the future.

The CC REST API source code can be browsed at http://code.creativecommons.org/viewgit/cc.api.git/.
To download the source code, you can clone its Git repository by running `git clone http://code.creativecommons.org/cc.api.git`.

.. Attention:: If you are using the `staging` version of the API, we ask that your code be updated to use the `dev` version instead. Requests made to the `staging` API URLs are still supported at the moment, but will be turned off in favor of the `dev` version in the near future.

Sample Code
~~~~~~~~~~~

ccPublisher uses the REST interface. See class CcRest in
wizard/pages/license.py for an example.

Other example usages:

* Python: The ccwsclient package provides basic abstraction of the
  REST interface via a Python class (`ccwsclient SVN`_).
* Java: The org.creativecommons.api package provides the CcRest class
  for using the REST web service from Java. Relies on JDOM and
  Jaxen. (`org.cc.api SVN`_)

Your comments, feedback and suggestions can be sent to
software@creativecommons.org.

Revision History
~~~~~~~~~~~~~~~~~
 * 2 April 2009: Converted to Sphinx.
 * 19 July 2007: Updated links.
 * 30 August 2005: 1.5 (:doc:`documentation <readme_15>`)
 * 2005 1.0 (:doc:`documentation <readme_10>`)

.. _`ccwsclient SVN`: http://cctools.svn.sourceforge.net/viewvc/cctools/api_client/trunk/python/ccwsclient/
.. _`org.cc.api SVN`: http://cctools.svn.sourceforge.net/viewvc/cctools/api_client/trunk/java/
