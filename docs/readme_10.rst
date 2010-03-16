-------------------------
Version 1.0 Documentation
-------------------------

 :Author: Nathan R. Yergler
 :Version: 1.0
 :Updated: $Date: 2009-04-02 10:57:29 -0700 (Thu, 02 Apr 2009) $

This document covers the 1.0 release of CC Web Services.  Information on the version in development can be found at http://api.creativecommons.org.

Access Method
=============

The 1.0 Web Services are accessible via a REST interface.  The interface is rooted at http://api.creativecommons.org/rest/1.0.
  
Valid Calls
===========

http://api.creativecommons.org/rest/1.0
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
     </licenses>

http://api.creativecommons.org/rest/1.0/license/[class]
  Called with a license class id from the call above as [class].  Returns an XML
  document describing the list of fields which must be supplied in order to issue
  a license of the given class.

  A partial example of the returned document for 
  http://api.creativecommons.org/rest/1.0/license/standard ::

    <license id="standard">
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
   </license>


  Note that a given field or enum element may have more than one label, so long as they
  have unique xml:lang attributes.  Future language translations may be added at any time
  in the future without breaking 1.0 compatibility.

http://api.creativecommons.org/rest/1.0/license/[class]/issue
  Called with an HTTP POST whose contents are a single form variable, ``answers``. 
  The value of answers is an XML string containing values which match each ``field``
  element found in the earlier license/[class] call.  A sample answers string for the 
  previous example is::

    <answers>
      <license-standard>
        <commercial>n</commercial>
        <derivatives>y</derivatives>
        <jurisdiction></jurisdiction>
      </license-standard>
    </answers>

  This example would issue a by-nc license in the generic (default) jurisdiction.  Note
  each element name matches a field id, and the content of the elements match the 
  enum id for the selected choice.

  The issue method uses the chooselicense.xsl document to generate the resulting XML 
  document.  The result of this sample call would be an XML document, such as::

    <?xml version="1.0"?>

    <result>
      <license-uri>http://creativecommons.org/licenses/by/2.0/Generic/</license-uri>
      <license-name>Attribution 2.0</license-name>
      <rdf>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://web.resource.org/cc/" xmlns:dc="http://purl.org/dc/elements/1.1/">
          <Work rdf:about="">
            <license rdf:resource="http://creativecommons.org/licenses/by/2.0/Generic/"/>
          </Work>
          <License rdf:about="http://creativecommons.org/licenses/by/2.0/Generic/">
            <permits rdf:resource="http://web.resource.org/cc/Reproduction"/>
            <permits rdf:resource="http://web.resource.org/cc/Distribution"/>
            <requires rdf:resource="http://web.resource.org/cc/Notice"/>
            <requires rdf:resource="http://web.resource.org/cc/Attribution"/>
            <permits rdf:resource="http://web.resource.org/cc/DerivativeWorks"/>
          </License>
        </rdf:RDF>
      </rdf>
      <html><!--Creative Commons License-->
          <a rel="license" href="http://creativecommons.org/licenses/by/2.0/Generic/">
          <img alt="Creative Commons License" border="0" src="http://creativecommons.org/images/public/somerights20.gif"/></a><br/>
		This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/2.0/Generic/">Creative Commons License</a>.
		<!--/Creative Commons License--><!-- <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://web.resource.org/cc/" xmlns:dc="http://purl.org/dc/elements/1.1/"><Work rdf:about=""><license rdf:resource="http://creativecommons.org/licenses/by/2.0/Generic/"/></Work><License rdf:about="http://creativecommons.org/licenses/by/2.0/Generic/"><permits rdf:resource="http://web.resource.org/cc/Reproduction"/><permits rdf:resource="http://web.resource.org/cc/Distribution"/><requires rdf:resource="http://web.resource.org/cc/Notice"/><requires rdf:resource="http://web.resource.org/cc/Attribution"/><permits rdf:resource="http://web.resource.org/cc/DerivativeWorks"/></License></rdf:RDF> --></html>
    </result>
        
  Note the <html> element contains the entire RDF-in-comment which the standard CC license
  engine returns.
