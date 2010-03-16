chooselicense-xml

The idea is to encapsulate the "choose license" process (see
<http://creativecommons.org/license/> in a file or a few files that
can be reused in different environments (e.g., standalone apps) without
having those apps reproduce the core language surrounding the process
or the rules for translating user answers into a license choice and
associated metadata.

Making the "questions" available as XML (questions.xml) and "rules" as
XSL (chooselicense.xsl) attempts to maximize accessibility and minimize
reimplementation of logic across multiple implementations.

An implementation will render questions.xml in some UI and produce
an XML document with the user's "answers" see (the ./test directory
for examples).  This document is then fed through chooselicense.xsl,
which produces another XML document with the chosen license's URL and
associated metadata (including complete RDF and HTML with embedded RDF).

CVS: http://sourceforge.net/cvs/?group_id=80503 (module chooselicense-xml)
ViewCVS: http://cvs.sourceforge.net/viewcvs.py/cctools/chooselicense-xml
