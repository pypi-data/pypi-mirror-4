Wrappers for the `NICTA fork <https://bitbucket.org/nicta_biomed/clearparser_flex>`_
of `ClearParser <https://code.google.com/p/clearparser>`_ dependency parser
allowing customisation of the parsing process. It was developed primarily for the
`StructuRX <https://bitbucket.org/nicta_biomed/structurx>`_ prescription 
interpretation tool.

Certain features also work with the regular unforked ClearParser but this is
very much untested. 

To use this code an installation of ClearParser must be present on your system.

Usage example, if ClearParser is installed to `/usr/local/clearparser`::

 >>> from clearparser import ClearWrapper
 >>> wrapper = ClearWrapper('parsing-config.xml', 'pos-tagging-config.xml', 
 ... 'dep-model.jar', '/usr/local/clearparser')
 >>> sentences = ['I ran']
 >>> parsed = wrapper.parse_in_bulk(sentences)


