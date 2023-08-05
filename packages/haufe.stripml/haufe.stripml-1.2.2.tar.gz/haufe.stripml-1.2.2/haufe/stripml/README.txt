First we want to test the stripml method.

    >>> from haufe.stripml import stripml
    >>> stripml.__doc__
    'stripml(s) -> string'

The one and only argument is a string.

    >>> stripml('foo')
    'foo'
    >>> type(stripml('foo')) == type('')
    True

The stripml method supports unicode, too.

    >>> stripml(u'bar')
    u'bar'
    >>> type(stripml(u'foo')) == type(u'')
    True

Trying an integer as first argument. A TypeError should be raised.

    >>> try:
    ...     stripml(10)
    ... except TypeError, strerror:
    ...     print strerror
    String or unicode string required.

Empty script

    >>> stripml ('<script>')
    ''
    >>> stripml (u'<script>')
    u''
    >>> stripml ('<script></script>')
    ''
    >>> stripml (u'<script></script>')
    u''

Try some huge element name

    >>> stripml ('<some-very-long-element-name-longer-than-foreseeable>')
    ''
    >>> stripml (u'<some-very-long-element-name-longer-than-foreseeable>')
    u''

Now we try some dumb HTML ...

    >>> stripml('<b>foo</b>')
    'foo'
    >>> stripml('foo <i>bar</i>.')
    'foo bar.'
    >>> stripml('''<font size = 12><b>Really <i>big</i> string
    ... </b></font>''')
    'Really big string\n'

... and now as unicode.

    >>> stripml(u'<b>foo</b>')
    u'foo'
    >>> stripml(u'foo <i>bar</i>.')
    u'foo bar.'
    >>> stripml(u'''<font size = 12><b>Really <i>big</i> string
    ... </b></font>''')
    u'Really big string\n'

Sometimes we have `script` tags, which contents nobody needs.

    >>> stripml('''We have a script in here <script language="JavaScript"
    ... type="text/javascript">alert('Hello, World!');</script>, dude.''')
    'We have a script in here , dude.'

Unicode.

    >>> stripml(u'''We have a script in here <script language="JavaScript"
    ... type="text/javascript">alert('Hello, World!');</script>, dude.''')
    u'We have a script in here , dude.'

But on the other hand the contents of `scrip`-Tags (without the trailing 't')
should not be stripped

    >>> stripml('<scrip>KEEP THIS</scrip>')
    'KEEP THIS'
    >>> stripml(u'<scrip>KEEP THIS</scrip>')
    u'KEEP THIS'

And neither should `scripting`-Tags

    >>> stripml('<scripting>KEEP THIS</scripting>')
    'KEEP THIS'
    >>> stripml(u'<scripting>KEEP THIS</scripting>')
    u'KEEP THIS'

How about forgotten </script>-Tags
    >>> stripml('KEEP <script>DO NOT KEEP THIS</script></script>THIS')
    'KEEP THIS'
    >>> stripml(u'KEEP <script>DO NOT KEEP THIS</script></script>THIS')
    u'KEEP THIS'

A much longer string.

    >>> result = stripml(u'''
    ... <?xml version="1.0" encoding="utf-8"?>
    ... <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    ... <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-US" lang="en-US">
    ... <head>
    ... <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    ... <meta name="generator" content="" />
    ... <meta name="keywords" content="" />
    ... <meta name="description" content="" />
    ... <title>Test document</title>
    ... <script language="JavaScript" type="text/javascript">
    ... var foo=1;
    ... function getFoo() {
    ...     return foo;
    ... }
    ... </script>
    ... </head>
    ... <body onLoad="alert('Hello, World!');">
    ...   <h1>Test document</h1>
    ...   <p>This document is<br /> <i>only for testing</i>!</p>
    ...   <script>getFoo();</script>
    ... </body>
    ... </html>
    ... ''')
    >>> result.strip()
    u'Test document\n\n\n\n  Test document\n  This document is only for testing!'
    >>> type(result)
    <type 'unicode'>

A single 'less then' or 'greater then' will be passed through.

    >>> stripml(u'<strong>hundred < thousand < million.</strong>')
    u'hundred < thousand < million.'
    >>> stripml(u'<strong>thousand > hundred.</strong>')
    u'thousand > hundred.'
    >>> stripml('<strong>hundred < thousand < million.</strong>')
    'hundred < thousand < million.'
    >>> stripml('<strong>thousand > hundred.</strong>')
    'thousand > hundred.'

Let's see if a really long string can be handled well.

    >>> s = 5000 * u'<p>This is <span>a span within a paragraph.</span><!-- And this is a comment --></p>\n'
    >>> stripml(s) == 5000 * u'This is a span within a paragraph.\n'
    True

And we should have a look at entities and encodings.

    >>> stripml(u'In Stra&szlig;e und &Uuml;berf&uuml;hrung haben wir Umlaute.')
    u'In Stra&szlig;e und &Uuml;berf&uuml;hrung haben wir Umlaute.'
    >>> stripml('In Stra&szlig;e und &Uuml;berf&uuml;hrung haben wir Umlaute.')
    'In Stra&szlig;e und &Uuml;berf&uuml;hrung haben wir Umlaute.'
    >>> print stripml(u'In Straße und Überführung haben wir Umlaute.').encode('ISO-8859-1') == u'In Straße und Überführung haben wir Umlaute.'.encode('ISO-8859-1')
    True
