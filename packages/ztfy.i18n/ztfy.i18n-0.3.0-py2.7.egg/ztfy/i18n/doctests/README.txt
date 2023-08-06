=========
ZTFY.i18n
=========

Introduction
------------

This package is used to define schema fields and properties handling
I18n management, which is the availability for a given property to be
displayed in several languages, according to the user's browser's
configuration.

Instead of storing attributes values in simple properties, I18n values
for a given property are stored in a dictionary where language is
the key.

You should create and register an instance of INegotiatorManager (as defined
in interfaces of z3c.language.negotiator package) to be able to dynamically
use all features defined by ztfy.i18n package.


Simple usage
------------

This is a simple usage sample. First we have to write an interface 
defining I18n schema fields, and then we will define a content class
handling a set of matching I18n properties:

    >>> import zope.interface
    >>> import zope.component
    >>> import ztfy.i18n.interfaces
    >>> import ztfy.i18n.schema
    >>> import ztfy.i18n.property

    >>> class IDocument(ztfy.i18n.interfaces.II18nAttributesAware):
    ...     """Declare basic document interface"""
    ...     title = ztfy.i18n.schema.I18nTextLine(title=u'Title',
    ...                                           description=u'The title of the document',
    ...                                           default=u'My default title',
    ...                                           required=True)
    ...     description = ztfy.i18n.schema.I18nTextLine(title=u'Description',
    ...                                                 description=u'Description of the document',
    ...                                                 required=False)

Note that II18nAttributesAware interface is used, because ztfy.i18n provides
an adapter from this interface to II18n interface (see below).
We can now create a class to implement I18n properties:

    >>> class Document(object):
    ...     zope.interface.implements(IDocument)
    ...
    ...     title = ztfy.i18n.property.I18nProperty(IDocument['title'])
    ...     description = ztfy.i18n.property.I18nProperty(IDocument['description'])
    
    >>> doc = Document()
    >>> doc2 = Document()

You can actually retrieve default value of the new object:

    >>> doc.title.get(u'en')
    u'My default title'

And then validate and modify object properties:

    >>> title = { u'en': u'My document title',
    ...           u'fr': u'Le titre de mon document' }
    >>> title_field = IDocument.get('title')
    >>> title_bound = title_field.bind(doc)
    >>> title_bound.validate(title)
    >>> doc.title = title
    >>> doc.title.get(u'fr')
    u'Le titre de mon document'

Of course, default value must by maintained even after setting a new title:

    >>> doc.title.get(u'de')
    u'My default title'

And the title of the second document (still unchanged) should always be the
default one:

    >>> doc2.title.get(u'fr')
    u'My default title'
    >>> doc2.title.get(u'de')
    u'My default title'

And you can always modify value for a given language:

    >>> doc.title[u'de'] = u'German title'
    >>> doc.title[u'de']
    u'German title'
    >>> doc.title[u'fr']
    u'Le titre de mon document'

A set of basic constraints are automatically enabled, as for a TextLine field:

    >>> title_bound.validate({u'en': 0})
    Traceback (most recent call last):
    ...
    WrongContainedType: ([WrongType(0, <type 'unicode'>, '')], 'title')
    >>> title_bound.validate({u'en': 'Multi-line \n text'})
    Traceback (most recent call last):
    ...
    WrongContainedType: ([WrongType('Multi-line ... text', <type 'unicode'>, '')], 'title')

You can define more constraints, on the full dict itself or on individual
values ; suppose here that we want to have a title of less than 10 characters,
not starting by '0', and with a maximum of three recorded languages:

    >>> class IDocument2(ztfy.i18n.interfaces.II18nAttributesAware):
    ...     """Declare basic document interface"""
    ...     title = ztfy.i18n.schema.I18nTextLine(title=u'Title',
    ...                                           description=u'The title of the document',
    ...                                           max_length=3,
    ...                                           value_max_length=10,
    ...                                           value_constraint=lambda x: not x.startswith('0'))
    >>> class Document2(object):
    ...     zope.interface.implements(IDocument2)
    ...     title = ztfy.i18n.property.I18nProperty(IDocument2['title'])
    
    >>> doc2 = Document2()
    >>> title_field = IDocument2.get('title')
    >>> title_bound = title_field.bind(doc2)
    >>> title_bound.validate({u'en': u'This is OK'})
    >>> title_bound.validate({u'en': u'This is NOT OK !'})
    Traceback (most recent call last):
    ...
    WrongContainedType: ([TooLong(u'This is NOT OK !', 10)], 'title')
    >>> title_bound.validate({u'en': u'0 Not good'})
    Traceback (most recent call last):
    ...
    WrongContainedType: ([ConstraintNotSatisfied(u'0 Not good')], 'title')
    >>> title_bound.validate({u'en': u'English text',
    ...                       u'fr': u'French text',
    ...                       u'de': u'German text',
    ...                       u'error': u'This one is too much !'})
    Traceback (most recent call last):
    ...
    TooLong: ({...}, 3)


Using converters
----------------

You can assign a converter to a property definition ; this allows assigned
value to be converted according to specified converter function:

    >>> from ztfy.utils.unicode import uninvl,unidict
    >>> class IDocument3(ztfy.i18n.interfaces.II18nAttributesAware):
    ...     """Declare basic document interface"""
    ...     title = ztfy.i18n.schema.I18nTextLine(title=u'Title',
    ...                                           description=u'The title of the document')
    >>> class Document3(object):
    ...     zope.interface.implements(IDocument3)
    ...     title = ztfy.i18n.property.I18nProperty(IDocument3['title'], converters=(unidict,))
    >>> doc3 = Document3()
    >>> doc3.title = {u'fr': 'Caractères accentués'}
    >>> doc3.title
    {u'fr': u'Caract\xc3\xa8res accentu\xc3\xa9s'}

Another converter could, for example, automatically handle unicode and
uppercase conversion:

    >>> import string
    >>> class Document4(object):
    ...     zope.interface.implements(IDocument3)
    ...     title = ztfy.i18n.property.I18nProperty(IDocument3['title'], value_converters=(uninvl,string.upper))
    >>> doc4 = Document4()
    >>> doc4.title = {u'fr': 'Caractères accentués'}
    >>> doc4.title
    {u'fr': u'CARACT\xc3\xa8RES ACCENTU\xc3\xa9S'}

I18nTextProperty is a specific subclass which already provides converters to
handle unicode conversion:

    >>> class Document5(object):
    ...     zope.interface.implements(IDocument3)
    ...     title = ztfy.i18n.property.I18nTextProperty(IDocument3['title'])
    >>> doc5 = Document5()
    >>> doc5.title = {u'fr': 'Caractères accentués'}
    >>> doc5.title
    {u'fr': u'Caract\xc3\xa8res accentu\xc3\xa9s'}

But you can always provide your own converters, which will be added to those
provided by I18nTextProperty:

    >>> class Document6(object):
    ...     zope.interface.implements(IDocument3)
    ...     title = ztfy.i18n.property.I18nTextProperty(IDocument3['title'], value_converters=(string.upper,))
    >>> doc6 = Document6()
    >>> doc6.title = {u'fr': 'Caractères accentués'}
    >>> doc6.title
    {u'fr': u'CARACT\xc3\xa8RES ACCENTU\xc3\xa9S'}


Using II18n adapter
-------------------

ZTFY.i18n package provides a z3c.language.switch.interfaces.II18n adapter for
any class implementing ztfy.i18n.interfaces.II18nAttributesAware:

    >>> from z3c.language.switch.interfaces import II18n
    >>> from ztfy.i18n.adapter import I18nAttributesAdapter
    >>> zope.component.provideAdapter(I18nAttributesAdapter,
    ...                               (ztfy.i18n.interfaces.II18nAttributesAware,),
    ...                               II18n)

Before using this adapter, we have to setup several adapters to handle
languages settings correctly:

    >>> from ztfy.i18n.adapter import I18nLanguagesAdapter
    >>> zope.component.provideAdapter(I18nLanguagesAdapter,
    ...                               (ztfy.i18n.interfaces.II18nManager,),
    ...                               ztfy.i18n.interfaces.II18nManagerInfo)
    >>> class I18nManager(object):
    ...     zope.interface.implements(ztfy.i18n.interfaces.II18nManager)
    ...     defaultLanguage = u'en'
    ...     availableLanguages = [ u'en', u'fr' ]

    >>> from zope.location import locate
    >>> from zope.app.folder import Folder
    >>> i18n_parent = Folder()
    >>> i18n_manager = I18nManager()
    >>> locate(i18n_manager, i18n_parent)
    >>> locate(doc, i18n_manager)

    >>> i18n = II18n(doc)
    >>> i18n.getDefaultLanguage()
    u'en'
    >>> i18n.getAvailableLanguages()
    [u'en']
    >>> i18n.getPreferedLanguage()
    u'en'
    >>> i18n.getAttribute('title', language=u'en')
    u'My document title'
    >>> i18n.getAttribute('title', language=u'fr')
    u'Le titre de mon document'

If an attribute is undefined in a given language, the "getAttribute" method
returns None while the "queryAttribute" method returns value defined in the
default language:

    >>> doc.description[u'en'] = u'Document description'
    >>> i18n.getAttribute('description', language=u'fr') is None
    True
    >>> i18n.queryAttribute('description', language=u'fr')
    u'Document description'

The II18n interface also defines methods to update attributes:

    >>> i18n.setAttribute('description', u'Modified document description', language=u'en')
    >>> i18n.getAttribute('description', language=u'en')
    u'Modified document description'
    >>> i18n.setAttributes(u'en', **{ 'description': u'Document description' })
    >>> i18n.getAttribute('description', language=u'en')
    u'Document description'


Using ZTFY.i18n TAL namespace
-----------------------------

ZTFY.i18n defines a TAL namespace which allows access to distinct values of
I18n attributes. The syntax of the namespace is 'context/i18n:attribute_name',
for example : 'context/i18n:title' in the above example.
The displayed value is based on settings of the INegotiatorManager utility,
as well as the configuration of the user browser. It also uses
II18n.queryAttribute method so if the specified attribute is not defined in
the given language, the default language value will be returned.

At first, let's declare the I18n namespace adapter:

    >>> from ztfy.i18n.tal.api import I18nTalesAdapter
    >>> from zope.traversing.interfaces import IPathAdapter, ITraversable
    >>> from zope.traversing.adapters import DefaultTraversable
    >>> zope.component.provideAdapter(I18nTalesAdapter,
    ...                               (zope.interface.Interface,),
    ...                               IPathAdapter,
    ...                               name='i18n')
    >>> zope.component.provideAdapter(DefaultTraversable,
    ...                               (zope.interface.Interface,),
    ...                               ITraversable)

Now let's continue by defining our template:

    >>> import os, tempfile
    >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
    >>> from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
    >>> temp_dir = tempfile.mkdtemp()
    >>> temp_filename = os.path.join(temp_dir, 'template.pt')
    >>> open(temp_filename,'w').write('''
    ... <html>
    ...     <body>
    ...         <h1 tal:content="context/i18n:title" />
    ...         <p tal:content="context/i18n:description" />
    ...     </body>
    ... </html>
    ... ''')
    >>> TestPage = SimpleViewClass(temp_filename, name='test.html')
    >>> zope.component.provideAdapter(TestPage,
    ...                               (zope.interface.Interface,IDefaultBrowserLayer),
    ...                               zope.interface.Interface,
    ...                               name='test.html')

Finally, check out request:

    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> doc.description[u'fr'] = u'Description du document'
    >>> view = zope.component.getMultiAdapter((doc, request), name='test.html')
    >>> print view().strip()
    <html>
        <body>
            <h1>My document title</h1>
            <p>Document description</p>
        </body>
    </html>

A 'language' form input can be used to force a specific language selection:

    >>> request = TestRequest(form={'language': u'fr'})
    >>> view = zope.component.getMultiAdapter((doc, request), name='test.html')
    >>> print view().strip()
    <html>
        <body>
            <h1>Le titre de mon document</h1>
            <p>Description du document</p>
        </body>
    </html>

Otherwise, browser languages settings are used to select content's language:

    >>> request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGES': u'fr,en'})
    >>> view = zope.component.getMultiAdapter((doc, request), name='test.html')
    >>> print view().strip()
    <html>
        <body>
            <h1>My document title</h1>
            <p>Document description</p>
        </body>
    </html>

But why did I get english property values ? Because you have to register a
NegotiatorManager utility, which will be used to detect browser's preferred
language ; just for example needs and to avoid to setup too much components
and adapters, we force the negotiator in 'server' policy mode:

    >>> from z3c.language.negotiator.interfaces import INegotiatorManager
    >>> from z3c.language.negotiator.app import Negotiator
    >>> negotiator = Negotiator()
    >>> negotiator.policy = 'server'
    >>> negotiator.serverLanguage = u'fr'
    >>> zope.component.provideUtility(negotiator, INegotiatorManager)
    >>> print view().strip()
    <html>
        <body>
            <h1>Le titre de mon document</h1>
            <p>Description du document</p>
        </body>
    </html>


Using ZTFY.i18n with ZTFY.file
------------------------------

All fields and properties defined in the ztfy.file package to handle files or
images as interfaces attributes can be used in an "I18n" way ; for example,
you can define a document, with a set of synthesis in different languages
defined as a single attribute. For this, you can use the I18nFile, I18nImage
and I18nCthumbImage interface fields, as well as I18nFileProperty and
I18nImageProperty contents properties. A file or image defined as an I18n
attribute can be accessed via the "++i18n++" namespace.
