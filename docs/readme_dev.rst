---------------------------------
Development Version Documentation
---------------------------------

 :Author: Nathan R. Yergler, John E. Doig III
 :Version: Development
 :Updated: Date: 2011-01-11 13:45:00 -0700 (Tue, 11 Jan 2010)

.. contents:: Document Index
   :backlinks: None
   :class: docindex

This document covers the current development release of CC Web Services.  
This should be considered unstable and only used for application testing 
and development.  Production applications should use the current stable 
version, as the development API can and will change.  Information on the 
curent version can be found at http://api.creativecommons.org.


Changes Since 1.5
=================
  * Added the ``zero`` license class and aliased the ``publicdomain`` class to issue a CC0 result.
  * Added the ``mark`` license class (Public Domain Mark).
  * Refinement of Work Information parameters
  * /rest/dev/details
      Added validation for the specified license URI; returns error 
      block if invalid
  * /simple/chooser
      The ``language`` parameter is no longer supported; use ``locale`` 
      instead.
  * /support/jurisdictions
      The ``language`` parameter is no longer supported; use ``locale`` 
      instead.
  * /license/[class]/
      License questions for a class may now include <description>s for
      enumeration items.

Access Method
=============

The Creative Commons Web Services are accessible via a REST interface.  
The interface is rooted at http://api.creativecommons.org/rest/dev.

Valid Calls
^^^^^^^^^^^

/locales
~~~~~~~~
  Returns an XML document detailing the available values which may be specified
  for ``locale`` in other calls.  The returned document has the following 
  format ::

    <locales>
      <locale id="en_CA"/>
      <locale id="fr"/>

      ...
    </locales>

  A future development version may include labels for the locales if users
  desire it.

/[?locale=xx]
~~~~~~~~~~~~~
  (synonym for /classes)

  Returns an XML document describing the available license classes.  A license class
  is a "family" of licenses.  Current classes are standard (basic CC licenses), 
  publicdomain, and recombo (the Sampling licenses).  
  Classes may be added at any time in the future without
  breaking 1.0 compatibility.

  A partial example of the returned document is::

     <licenses>
       <license id="standard">Creative Commons</license>
       <license id="publicdomain">Public Domain</license>
       <license id="recombo">Sampling</license>
       <license id="zero">CC0</license>
       <license id="mark">Public Domain Mark</license> 
     </licenses>

  If a value for locale is supplied, the service will attempt to return
  localized class descriptions.  If not specified, English will
  be returned.

  .. note:: With the release of the `Public Domain Mark`, the `Public Domain Dedication and Certification` license has been retired. As a result, the `publicdomain` license class has been aliased to the `zero` license class so that the deprecated `Public Domain Dedication and Certification` license is never issued and the `CC0 Public Domain Dedication` license is issued instead. You can read more about Creative Commons' retired licenses here http://creativecommons.org/retiredlicenses.

/license/<class>[?locale=xx]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  Called with a license class id from the call above as <class>.  
  Returns an XML
  document describing the list of fields which must be supplied in 
  order to issue
  a license of the given class.

  If a value for locale is supplied, the service will attempt to return
  localized labels and descriptions.  If not specified, English will
  be returned.

  A partial example of the returned document for 
  http://api.creativecommons.org/rest/dev/license/standard ::

    <licenseclass id="standard">
     <label xml:lang="en">Creative Commons</label>
      <field id="commercial">
     <label xml:lang="en">Allow commercial uses of your work?</label>
     <description xml:lang="en">The licensor permits others to copy, distribute, display, and perform the work.  In return, the licensee may not use the work for commercial purposes, unless they get the licensor's permission.</description>
     <type>enum</type>
     <enum id="y">
       <label xml:lang="en">Yes</label>
     </enum>
     <enum id="n">
       <label xml:lang="en">No</label>
     </enum>
    </field>
    <field id="derivatives">
     <label xml:lang="en">Allows modifications of your work?</label>
     <description xml:lang="en">The licensor permits others to copy, distribute and perform only unaltered copies of the work, not derivative works based on it.</description>
     <type>enum</type>
     <enum id="y">
       <label xml:lang="en">Yes</label>
     </enum>
     <enum id="sa">
       <label xml:lang="en">ShareAlike</label>
     </enum>
     <enum id="n">
       <label xml:lang="en">No</label>
     </enum>
    </field>
    <field id="jurisdiction">
     <label xml:lang="en">Jurisdiction of your license:</label>
     <description xml:lang="en">If you desire a license governed by the Copyright Law of a specific jurisdiction, please select the appropriate jurisdiction.</description>
     <type>enum</type>
     <enum id="">
       <label xml:lang="en">Generic</label>
     </enum>
     <enum id="at">
       <label xml:lang="en">Austria</label>
     </enum>
    </field>
   </licenseclass>


  Note that a given field or enum element may have more than one label, so long as they
  have unique xml:lang attributes.  Future language translations may be added at any time
  in the future without breaking 1.0 compatibility.

/license/<class>/issue
~~~~~~~~~~~~~~~~~~~~~~

  Called with an HTTP POST whose contents are a single form variable, 
  ``answers``.  The value of answers is an XML string containing values 
  which match each ``field`` element found in the earlier  
  `/license/<class>[?locale=xx]`_ call.  A sample answers string for the 
  previous example is::

    <answers>
      <locale>en</locale>
      <license-standard>
        <commercial>n</commercial>
        <derivatives>y</derivatives>
        <jurisdiction></jurisdiction>
      </license-standard>
    </answers>

  This example would issue a by-nc license in the generic (default) 
  jurisdiction. 


<answers> XML syntax
--------------------  
    The ``<answers>`` block is structured using the following
    rules:

      * The ``<locale>`` element is optional and specifies the language to use
        when localizing the license HTML and name.  If omitted, English (US)
        will be used.  See `/locales`_ for information on obtaining a 
	list of valid locales.
      * The ``<license-standard>`` tag is the license class prepended 
        with ``license-``.
      * Each sub-element of ``<license-xxx>`` matches a field id, 
        and the content of the elements matches the 
        enum id for the selected choice.  Only values specified as the ``id``
        attribute for ``enum`` elements are accepted as values for each field.
        If other values are specified, the server will return an 
	``invalidanswer`` error.
      * The exception to this rule is the ``<jurisdiction>`` tag.  If an unknown
        jurisdiction is specified, the web services will silently fall back to
        the generic jurisdiction.

  
Providing work information
--------------------------

  The information passed to the licensing web service may be augmented with
  optional information about the work to be licensed.  If included this 
  information will be used in the returned RDF and RDFa.  For example::

    <answers>
      <locale>en</locale>
      <license-standard>
        <commercial>n</commercial>
        <derivatives>y</derivatives>
        <jurisdiction></jurisdiction>
      </license-standard>
      <work-info>
        <work-url>http://example.com/work</work-url>
        <title>The Title</title>
        <source-url>http://example.com/source</source-url>
        <type>Text</type>
        <year>2006</year>
        <description>A brief description...</description>
        <creator>John Q. Public</creator>
        <holder>John Q. Public</holder>
        <actor_href>http://example.com/actor</actor_href>
        <territory>US</territory>
        <attribution_url>http://example.com/attribution</attribution_url>
        <attribution_name>Example</attribution_name>
        <more_permissions_url>http://example.com/more_permissions</more_permissions_url>
      </work-info>
    </answers>
  
  

  The work-info element and all sub-elements are optional.

  Only certain sub-elements will affect the Licenses' RDFa formatting, 
  the table below details how the elements are used in the RDFa formatting. 

  +---------------+------------------------+--------------------+---------------------------------+
  | License class | Additional Information |   RDFa property    |   Valid work-info elements      | 
  +===============+========================+====================+=================================+
  |               | Attribute work to name | cc:attributionName | attribution_name, creator,      |
  |               |                        |                    | holder                          |
  |               +------------------------+--------------------+---------------------------------+
  |               | Attribute work to URL  | cc:attributionURL  | attribution_url, work-url       |
  |               +------------------------+--------------------+---------------------------------+
  | standard      | Title of work          | dc:title           | title                           | 
  |               +------------------------+--------------------+---------------------------------+
  |               | Source work URL        | dc:source          | source-url                      |
  |               +------------------------+--------------------+---------------------------------+
  |               | Format of the work     | dc:type            | type                            |
  |               +------------------------+--------------------+---------------------------------+
  |               | More permissions URL   | cc:morePermissions | more_permissions_url            |
  +---------------+------------------------+--------------------+---------------------------------+
  |               | Your name              | dct:title          | attribution_name, creator,      |
  |               |                        |                    | name                            |
  | zero,         +------------------------+--------------------+---------------------------------+
  | publicdomain  | Your URL               | dct:publisher      | attribution_url, actor_href     |
  |               +------------------------+--------------------+---------------------------------+
  |               | Title of work          | dct:title          | title                           |
  |               +------------------------+--------------------+---------------------------------+
  |               | Territory              | vcard:Country      | territory                       |
  +---------------+------------------------+--------------------+---------------------------------+
  |               | Work name              | dct:title          | title                           |
  |               +------------------------+--------------------+---------------------------------+
  |               | Author name            | dct:title of       | author_title, attribution_name, |
  |               |                        | dct:creator        | name                            |
  |               +------------------------+--------------------+---------------------------------+
  |               | Author URL             | dct:creator        | author_url, attribution_url     |
  | mark          +------------------------+--------------------+---------------------------------+
  |               | Identifying Individual | dct:title of       | curator_title                   |
  |               | or Organization name   | dct:publisher      |                                 |
  |               +------------------------+--------------------+---------------------------------+
  |               | Identifying Individual | dct:publisher      | curator_url                     |
  |               | or Organization URL    |                    |                                 |
  +---------------+------------------------+--------------------+---------------------------------+
  
  The "Additional Information" column represents fields that are made available 
  via the license choosers at http://creativecommons.org/choose/, 
  http://creativecommons.org/choose/zero/, and http://creativecommons.org/choose/mark/. 
  These fields will have an effect on how the resulting License RDFa is structured. 
  The work-info elements are listed in order of searching priority, i.e. in determining 
  a value for RDFa inclusion, a work-info element will override the elements that 
  follow it in the valid elements list.
  

Additional work-info details
----------------------------
  
  *type*
    The work type should be specified as a valid Dublin Core dc:type; common 
    values are:
    
      * Text
      * StillImage
      * MovingImage
      * InteractiveResource
      * Sound
    
    This may also be left blank, in which case no assertion about the work type
    will be included.

  *territory*
    Must be a valid, uppercased ISO 3166-1-alpha-2 country code. A list of available codes 
    can be found `here <http://www.iso.org/iso/english_country_names_and_code_elements>`_.

License return format
---------------------
  
  The issue method forms an XML document based on the parameters provided by the 
  answers xml. The result of this sample call would be an XML document, such as::

    <?xml version="1.0" encoding="utf-8"?>
    <result>
     <license-uri>http://creativecommons.org/licenses/by/3.0/us/</license-uri>
     <license-name>Attribution 3.0 United States</license-name>
     <rdf>
       <rdf:RDF xmlns="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <Work rdf:about="">
         <license rdf:resource="http://creativecommons.org/licenses/by/3.0/us/"/>
        </Work>

        <License rdf:about="http://creativecommons.org/licenses/by/3.0/us/">
         <permits rdf:resource="http://creativecommons.org/ns#Reproduction"/>
         <permits rdf:resource="http://creativecommons.org/ns#Distribution"/>
         <requires rdf:resource="http://creativecommons.org/ns#Notice"/>
         <requires rdf:resource="http://creativecommons.org/ns#Attribution"/>
         <permits rdf:resource="http://creativecommons.org/ns#DerivativeWorks"/>
        </License>
       </rdf:RDF>
     </rdf>
     <licenserdf>
      <rdf:RDF xmlns="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
       <License rdf:about="http://creativecommons.org/licenses/by/3.0/us/">
         <permits rdf:resource="http://creativecommons.org/ns#Reproduction"/>
         <permits rdf:resource="http://creativecommons.org/ns#Distribution"/>
         <requires rdf:resource="http://creativecommons.org/ns#Notice"/>
         <requires rdf:resource="http://creativecommons.org/ns#Attribution"/>
         <permits rdf:resource="http://creativecommons.org/ns#DerivativeWorks"/>
       </License>
      </rdf:RDF>
     </licenserdf>
     <html><a rel="license" href="http://creativecommons.org/licenses/by/3.0/us/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/3.0/us/88x31.png"/></a><br/>This <span xmlns:dc="http://purl.org/dc/elements/1.1/" href="http://purl.org/dc/dcmitype/" rel="dc:type">work</span> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/3.0/us/">Creative Commons Attribution 3.0 United States License</a>.</html>
    </result>

  Note the ``<html>`` element contains the HTML as generated by the
  `CC License Chooser <http://creativecommons.org/license/>`_,
  including machine readable RDFa.


/license/<class>/get?
~~~~~~~~~~~~~~~~~~~~~

  Called with an HTTP GET and a query string containing a parameter for each
  ``field`` specified in the previous call to `/license/<class>[?locale=xx]`_
  The value of each parameter should match one of the enum values provided.

  For example, a call to retrieve a Creative Commons standard license might
  look like:

  /license/standard/get?commercial=n&derivatives=y&jurisdiction=

  This example would issue a by-nc license in the generic (default) 
  jurisdiction.  The guidelines regarding `<answers> XML syntax`_ apply to
  the parameters on the querystring.

  The XML returned from this call is identical to the return from 
  `/license/<class>/issue`_.

/details?license-uri=[uri]
~~~~~~~~~~~~~~~~~~~~~~~~~~

  Called with an HTTP POST or GET with a single form variable, 
  ``license-uri``.  The
  value of license-uri is the URI of an existing Creative Commons license.  
  The call returns the same result as issue.  Note that at this time
  ``details`` does not support localization.

  If the uri specified by ``license-uri`` is not a valid Creative Commons 
  license, the web service will reject the request and return an error block.
  For example, ::

    <error>
      <id>invalid</id>
      <message>Invalid license uri.</message>
    </error>

  If your application requires more information about a license, the full
  RDF is available by appending /rdf to the end of any valid Creative Commons
  License URI. e.g. http://creativecommons.org/licenses/by/3.0/us/rdf

/simple/chooser
~~~~~~~~~~~~~~~

  Returns a simple license chooser in the form of an HTML-drop down.  The
  format of the returned chooser can be customized with the following 
  parameters

  ============== ========= ==============================================
  Name           Number    Description
  ============== ========= ==============================================
  jurisdiction   0 or 1    Returns licenses for the specified 
                           jurisdiction.  Example: de
  exclude        0 or more Excludes license urls containing the specified
                           string.  Example: nc will exclude 
                           NonCommercial licenses.
  locale         0 or 1    Locale to use for license names; defaults to
                           English (en).  Example: ja
  language       0 or 1    **DEPRECATED** *This parameter is deprecated
                           in favor of locale for consistency.*

                           Language to use for license names; defaults to
                           English (en).  Example: ja
  select         0 or 1    If specified, the value used for the name 
                           attribute of the <select> element; if not 
                           specified, the select element is omitted.
  ============== ========= ==============================================

  If an unknown or unsupported locale is specified, the service will fall
  back to English.  If an unknown jurisdiction is specified, the service
  will fall back to the Generic jurisdiction.

  In addition to these parameters, the Simple Chooser can be further 
  customized by invoking as either /simple/chooser or /simple/chooser.js.
  If invoked as the former, the result is raw HTML.  If invoked as the
  latter, the result is wrapped in ``document.write()`` calls.

/support/jurisdictions
~~~~~~~~~~~~~~~~~~~~~~

  Returns a simple jurisdiction chooser in the form of an HTML drop-down. The
  format of the returned chooser can be customized with the following 
  parameters

  ============== ========= ==============================================
  Name           Number    Description
  ============== ========= ==============================================
  locale         0 or 1    Locale to use for license names; defaults to
                           English (en).  Example: ja
  language       0 or 1    **DEPRECATED** *This parameter is deprecated 
                           in favor of locale for consistency.*

                           Language to use for license names; defaults to
                           English (en).  Example: ja
  select         0 or 1    If specified, the value used for the name 
                           attribute of the <select> element; if not 
                           specified, the select element is omitted.
  ============== ========= ==============================================

  In addition to these parameters, the dropdown call can be further 
  customized by invoking as either /support/jurisdictions or 
  /support/jurisdictions.js.
  If invoked as the former, the result is raw HTML.  If invoked as the
  latter, the result is wrapped in ``document.write()`` calls.


Error Handling
==============

 Errors occuring from either invalid input or server-side problems are 
 returned as an XML block, with an ``<error>`` top level element.  For 
 example, a call to details with no ``license-uri`` would return the following
 text::

   <error>
     <id>missingparam</id>
     <message>A value for license-uri must be supplied.</message>
   </error>

 Error messages are currently not localized.

 If the error occurs due to a server side error, two additional elements
 may be specified: ``<exception>`` and ``<traceback>``.  
 ``<traceback>`` will contain
 the text of the Python stack trace.  This is usually uninteresting for
 end users, but may help developers when reporting errors.

 ``<exception>`` contains the Python exception information.  
 A contrived example::

   <exception type="KeyError">
     Unknown Key.
   </exception>

 Note that the actual contents of the ``<exception>`` element is dependent
 on the actual error that occurs; these will only be returned when an 
 otherwise unhandled error has occured.


Currently Defined Errors
^^^^^^^^^^^^^^^^^^^^^^^^

 ============== ==================================================
   id            description
 ============== ==================================================
 missingparam    A required parameter is missing; for convenience
                 the web service
                 will check both GET and POST for form values.
 invalidclass    Returned when details are requested for an 
                 invalid license class.  For example, calling
                 ``/license/blarf`` will return this error code.
 pythonerr       A Python exception has occured.
 invalidanswer   Returned when a value passed into issue or get
                 for a field (question) is not a valid value.
 ============== ==================================================

Additional Resources
====================

 * The Creative Commons developer mailing list, cc-devel; information available
   at http://lists.ibiblio.org/mailman/listinfo/cc-devel
 * `Creative Commons Developer Wiki`_ 
 * `CC Web Services in the Wiki`_

.. _`Creative Commons Developer Wiki`: http://wiki.creativecommons.org/wiki/Developer
.. _`CC Web Services in the Wiki`: http://wiki.creativecommons.org/Creative_Commons_Web_Services
