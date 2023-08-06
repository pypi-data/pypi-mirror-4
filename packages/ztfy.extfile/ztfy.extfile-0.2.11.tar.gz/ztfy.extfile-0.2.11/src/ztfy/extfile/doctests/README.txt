====================
ZTFY.extfile package
====================

Introduction
------------

This package includes a set of interfaces, classes, adapters and utilities
which can be used to store files data into external files instead
of into the Zope Object Database (ZODB) to avoid a quick increase of
database size. This external file system can be a local one or a remote one
available via SFTP.

A cache mechanism is available to improve performances when files are accessed
via SFTP, notably useful when network connection between Zope front-end and
files storage server is not very efficient.


Blob files
----------

The simplest way to handle external files is to use new blobs, directly available
in the ZODB package and easily usable with ZEO.
ZTFY.extfile package just provides a simple wrapper around ZODB blobs so that you can
define a FileProperty content class to be defined as a blob, and then use this file as
a normal one transparently.


ZTFY.extfile architecture
-------------------------

ZTFY.extfile package is based on three main components :
 - the ExtFile class itself, which is a persistent component handling data storage
 outside of the ZODB.
 - a "name chooser" ; this kind of utility is used to define the file name (including
 parent directories names) on it's final location. A default name chooser is provided,
 which defines timestamp-based file names.
 - a "file handler" ; this kind of utility is used to actually handle storage and
 retrieving of files data from their external location. Two handlers are provided, to
 store external files locally or on a remote storage server via SFTP.


Names choosers
--------------

IExtFileNameChooser only provides a single method : getName(parent,extfile,name)
The result will be the file storage's path of the given file ; 'parent' is the
extfile's container, and 'name' is the actual name of the file.


External files handlers
-----------------------

An external files handler is responsible for actually handling the external files data. This
implies :
 - copying files data to their final location
 - get actual content of external files when needed.
Some external file handlers (SFTP handler for example) also keep a local cached copy of
files contents to improve performances.


Local external files handler
----------------------------

This handler store external files on the local files system of the Zope application server.
It just keeps a link to the external file.


SFTP external file handler
--------------------------

This handler can store external files on a remote files server accessed via SFTP.
Connection can be defined via a username/password tuple or via a reference to a private
SSH key file.
External files "filename" property is a relative path name defined by a names chooser ; the actual
physical location is defined via the external files handler configuration.

SFTP handler can keep a local cached copy of remote files, very useful when network connection
to remote server is not very efficient.


The ExtFile content class
-------------------------

The ExtFile class is the actual persistent class used to handle storage of files data into
external files.
External files properties can be defined via the FileProperty field defined in ztfy.file.property
package, and via the I18nFileProperty defined in ztfy.i18n.property package ; both of them are
designed to correctly handle external files.
The package also provides an ExtImage class, which handles images in the same way, and is
fully compatible with all options defined in ztfy.file package.


Copying external files
----------------------

ztfy.extfile.extfile module is automatically using a catalog index to reference external files ; the
filename property is indexed.
When an external file is copied, only metadatas are duplicated ; the actual external file data is kept
"as is", so that the original file and it's copy are pointing to the same location.
When an external file is modified, a query is launched against "filename" catalog's index ; if a single file
is retrieved, it's current content is removed and replaced by the new content ; if several files are
retrieved, the original content is kept, and a new file storage location is created to store the new content.
When an external file is deleted, the same process occurs and the file storage location is actually deleted
only when the last file pointing to the given location is actually removed.

WARNING: of course, this process doesn't occur if the file's modification is made outside of the Zope's
process...


External files usage
--------------------

Usage of external files and images content classes is not really different from usage of a common file
or image class:

    >>> import zope.component
    >>> import zope.interface
    >>> from zope.interface import Interface
    >>> from zope.annotation.interfaces import IAnnotations, IAttributeAnnotatable
    >>> from ztfy.file.schema import FileField, ImageField, CthumbImageField

But before anything we have to register a set of required utilities and adapters ; process is very similar
to which is required for ztfy.file package:

    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> zope.component.provideAdapter(AttributeAnnotations)
    >>> from ztfy.file.adapter import FilePropertiesContainerAttributesAdapter
    >>> zope.component.provideAdapter(FilePropertiesContainerAttributesAdapter)

Let's reuse our IDocumentInfo interface:

    >>> class IDocumentInfo(Interface):
    ...     """Declare basic document interface"""
    ...     data = FileField(title=u'Document content',
    ...                      required=False)
    ...     illustration = ImageField(title=u'Document illustration',
    ...                               required=False)
    ...     thumbnail = CthumbImageField(title=u'Document thumbnail',
    ...                                  required=False)

We can then create a modified version of our document class:

    >>> from zope.interface import implements
    >>> from ztfy.file.property import FileProperty, ImageProperty
    >>> from ztfy.extfile.extfile import ExtFile, ExtImage
    >>> class Document(object):
    ...     implements(IDocumentInfo, IAttributeAnnotatable)
    ...     data = FileProperty(IDocumentInfo['data'], klass=ExtFile)
    ...     illustration = ImageProperty(IDocumentInfo['illustration'], klass=ExtImage)
    ...     thumbnail = ImageProperty(IDocumentInfo['thumbnail'], klass=ExtImage)

We can then create a document:

    >>> import os
    >>> doc = Document()
    >>> doc.data is None
    True

Before being able to assign a value to "data" field, which will be converted automatically to an
ExtFile object, we have to register several utilities:

 - a name chooser:

    >>> from ztfy.extfile.namechooser.interfaces import IExtFileNameChooser
    >>> class CustomNameChooser(object):
    ...     implements(IExtFileNameChooser)
    ...     def getName(self, parent, extfile, name):
    ...         return name

    >>> name_chooser = CustomNameChooser()
    >>> zope.component.provideUtility(name_chooser, IExtFileNameChooser)

 - an external files handler:

    >>> from ztfy.extfile.handler.interfaces import IExtFileHandler
    >>> from ztfy.extfile.handler.local.interfaces import ILocalExtFileHandlerConfig
    >>> from ztfy.extfile.handler.local import LocalExtFileHandler
    >>> handler = LocalExtFileHandler()
    >>> handler.local_root = os.path.join(current_dir, '.local')
    >>> zope.component.provideUtility(handler, IExtFileHandler)
    >>> zope.component.provideUtility(handler, ILocalExtFileHandlerConfig)

    >>> datafile = os.path.join(current_dir, '..', 'doctests', 'README.txt')
    >>> data = open(datafile).read()
    >>> doc.data = data
    >>> doc.data
    <ztfy.extfile.extfile.ExtFile object at ...>
    >>> doc.data.data.startswith('====================\nZTFY.extfile package\n====================')
    True
    >>> os.unlink(doc.data._v_filename)

If you define custom names choosers or external files handlers, you can use optional arguments of
FileProperty and ImageProperty constructors to specify them:

    >>> zope.component.provideUtility(name_chooser, IExtFileNameChooser, 'myChooser')
    >>> zope.component.provideUtility(handler, IExtFileHandler, 'myHandler')
    >>> class Document(object):
    ...     implements(IDocumentInfo, IAttributeAnnotatable)
    ...     data = FileProperty(IDocumentInfo['data'], klass=ExtFile, **{'nameChooser': 'myChooser'})
    ...     illustration = ImageProperty(IDocumentInfo['illustration'], klass=ExtImage, **{'handler': 'myHandler'})
    ...     thumbnail = ImageProperty(IDocumentInfo['thumbnail'], klass=ExtImage)

'nameChooser' and 'handler' parameters values are the names under which matching utilities are registered.

All other files and images related functions and adapters described into ztfy.file and ztfy.i18n packages
are completely usable with ExtFile and ExtImage objects, without any modification.


Blob files usages
-----------------

You can define external files as blobs as easily as you have define them before:

    >>> from ztfy.extfile.blob import BlobFile, BlobImage
    >>> class Document2(object):
    ...     implements(IDocumentInfo, IAttributeAnnotatable)
    ...     data = FileProperty(IDocumentInfo['data'], klass=BlobFile)
    ...     illustration = ImageProperty(IDocumentInfo['illustration'], klass=BlobImage)
    ...     thumbnail = ImageProperty(IDocumentInfo['thumbnail'], klass=BlobImage)

    >>> doc = Document2()
    >>> doc.data is None
    True
    >>> doc.data = data
    >>> doc.data
    <ztfy.extfile.blob.BlobFile object at ...>
    >>> doc.data.data.startswith('====================\nZTFY.extfile package\n====================')
    True
