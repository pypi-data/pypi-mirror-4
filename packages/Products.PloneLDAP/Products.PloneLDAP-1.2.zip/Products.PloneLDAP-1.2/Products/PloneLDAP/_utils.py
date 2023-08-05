# In case CMFPlone.utils is available we use it, otherwise we define our own,
# which is a plain copy of it, as of 2010-07-21
try:
    from Products.CMFPlone.utils import safe_unicode
    safe_unicode  # pyflakes
except ImportError:
    def safe_unicode(value, encoding='utf-8'):
        """Converts a value to unicode, even it is already a unicode string.

            >>> from Products.CMFPlone.utils import safe_unicode

            >>> safe_unicode('spam')
            u'spam'
            >>> safe_unicode(u'spam')
            u'spam'
            >>> safe_unicode(u'spam'.encode('utf-8'))
            u'spam'
            >>> safe_unicode('\xc6\xb5')
            u'\u01b5'
            >>> safe_unicode(u'\xc6\xb5'.encode('iso-8859-1'))
            u'\u01b5'
            >>> safe_unicode('\xc6\xb5', encoding='ascii')
            u'\u01b5'
            >>> safe_unicode(1)
            1
            >>> print safe_unicode(None)
            None
        """
        if isinstance(value, unicode):
            return value
        elif isinstance(value, basestring):
            try:
                value = unicode(value, encoding)
            except (UnicodeDecodeError):
                value = value.decode('utf-8', 'replace')
        return value
