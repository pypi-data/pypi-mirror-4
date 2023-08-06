Epubzilla  Documentation
========================

`Epubzilla <http://odeegan.com/epubzilla>`_ is a Python library for extracting data from 
EPUB documents.

Currently, the only version supported is EPUB 2.0.1. There are grand plans
to support EPUB 3.0 in the near future.

Getting Help
----------------
If you have questions about Epubzilla, send an email to 
odeegan @ gmail . com

Requirements
============
 * Python 2.6+
 * `lxml <http://lxml.de/>`_ version 3.0.1 or later is required 

QuickStart
==========
>>> from epubzilla.epubzilla import Epub
>>> epub = Epub.from_file('Manly-DeathValley-images.epub')
>>> epub.author
'Manly, William Lewis'
>>> epub.title
"Death Valley in '49"

Here are a few examples of how to navigate the data::

  epub.metadata[3].tag.localname
  # title

  epub.metadata[3].tag.namespace
  # http://purl.org/dc/elements/1.1/

  epub.metadata[3].tag.text
  # Death Valley in '49

  epub.metadata[3].as_xhtml
  # <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.idpf.org/2007/opf">Death Valley in '49</dc:title>	

  epub.manifest[2].tag.attributes
  # {u'href': 'www.gutenberg.org@files@12236@12236-h@ch_03.png', u'id': 'item3', u'media-type': 'image/png'}


If an element contains other elements, they can be accessed via the 
list property::

  epub.metadata.list
  # [class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>, class <Epub.Element>]


They can also be directly iterated over::

  for element in epub.metadata:
    print "%s : %s" %(element.tag.localname, element.tag.text)
    for k,v in element.tag.iteritems():
      print "\t %s : %s" %(k,v)
        
  # rights : Public domain in the USA.
  # identifier : http://www.gutenberg.org/ebooks/12236
  #  scheme : URI
  #  id : id
  # creator : William Lewis Manly
  #  file-as : Manly, William Lewis
  # title : Death Valley in '49
  # language : en
  #  type : dcterms:RFC4646
  # date : 2004-05-01
  #  event : publication
  # date : 2010-02-15T17:50:02.335756+00:00
  #  event : conversion
  # source : http://www.gutenberg.org/files/12236/12236-h/12236-h.htm
  # meta : 
  #  content : item26
  #  name : cover

If a manifest element references a file, it can be access via the element's 
`get_file()` method. A string buffer will be returned.::

 type(epub.manifest[2].get_file())
 # <type 'str'>

