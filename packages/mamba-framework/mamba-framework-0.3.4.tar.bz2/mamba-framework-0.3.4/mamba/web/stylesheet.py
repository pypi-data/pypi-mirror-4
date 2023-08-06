# -*- test-case-name: mamba.test.test_web -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module: stylesheet
    :platform: Linux
    :synopsis: Mamba page stylesheets IResources

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import re
from os.path import normpath

from mamba.core import GNU_LINUX

if GNU_LINUX:
    from zope.interface import implements
    from twisted.internet import inotify
    from twisted.python._inotify import INotifyError
    from mamba.core.interfaces import INotifier

from twisted.python import filepath

from mamba.utils import filevariables


class StylesheetError(Exception):
    """Generic class for Stylesheet exceptions"""


class InvalidFileExtension(StylesheetError):
    """Fired if the file has not a valid extension (.css or .less)"""


class InvalidFile(StylesheetError):
    """Fired if a file is lacking the mamba css or less headers"""


class FileDontExists(StylesheetError):
    """Raises if the file does not exists"""


class Stylesheet(object):
    """
    Object that represents an stylesheet or a less script

    :param path: the path of the stylesheet
    :type path: str
    :param prefix: the prefix where the stylesheets reside
    :type prefix: str
    """

    def __init__(self, path='', prefix='styles'):
        self.path = path
        self.prefix = prefix
        self.name = ''
        self.data = ''

        self._fp = filepath.FilePath(self.path)
        if self._fp.exists():
            basename = filepath.basename(self.path)
            extension = filepath.splitext(basename)[1]
            if not basename.startswith('.') and (extension == '.css' or
                                                 extension == '.less'):
                file_variables = filevariables.FileVariables(self.path)
                filetype = file_variables.get_value('mamba-file-type')
                if filetype != 'mamba-css' and filetype != 'mamba-less':
                    raise InvalidFile(
                        'File {} is not a valid CSS or LESS mamba file'.format(
                            self.path
                        )
                    )

                res = '{}/{}'.format(self.prefix, self._fp.basename())
                self.data = res
                self.name = self._fp.basename()
            else:
                raise InvalidFileExtension(
                    'File {} has not a valid extension (.css or .less)'.format(
                        self.path
                    )
                )
        else:
            raise FileDontExists(
                'File {} does not exists'.format(self.path)
            )


class StylesheetManager(object):
    """
    Manager for Stylesheets
    """
    if GNU_LINUX:
        implements(INotifier)

    def __init__(self):
        self._stylesheets = {}

        if GNU_LINUX:
            # Create and setup Linux iNotify mechanism
            self.notifier = inotify.INotify()
            self.notifier.startReading()
            try:
                self.notifier.watch(
                    filepath.FilePath(self._styles_store),
                    callbacks=[self._notify]
                )
                self._watching = True
            except INotifyError:
                self._watching = False

    @property
    def stylesheets(self):
        return self._stylesheets

    @stylesheets.setter
    def stylesheets(self, value):
        raise StylesheetError("'stylesheets' is read-only")

    def setup(self):
        """
        Setup the loader and load the stylesheets
        """

        try:
            files = filepath.listdir(self._styles_store)
            pattern = re.compile('[^_?]\%s$' % '.css|.less', re.IGNORECASE)
            for stylefile in filter(pattern.search, files):
                stylefile = normpath(
                    '{}/{}'.format(self._styles_store, stylefile)
                )
                self.load(stylefile)
        except OSError:
            pass

    def load(self, filename):
        """
        Load a new stylesheet file
        """

        style = Stylesheet(filename)
        self._stylesheets.update({style.name: style})

    def reload(self, style):
        """Send a COMET / WebSocket petition to reload a specific CSS file.

        :param style: the CSS file to reload
        :type style: :class:`~mamba.application.appstyle.AppStyle`

        JavaScript to use:

        .. sourcecode:: javascript

            var queryString = '?reload=' + new Date().getTime();
            // ExtJS - Sencha
            var el = Ext.get(styleName);
            // jQuery
            var el = $(styleName);
            // LungoJS
            var el = $$(styleName);

            el.dom.href = el.dom.href.replace(/\?.*|$/, queryString);
        """

        # TODO: Make client to reload the CSS
        pass

    def lookup(self, key):
        """
        Find and return a stylesheet from the pool
        """
        return self._stylesheets.get(key, None)

    def _notify(self, wd, file_path, mask):
        """Notifies the changes on stylesheets file_path """

        if not GNU_LINUX:
            return

        if mask is inotify.IN_MODIFY:
            style = filepath.splitext(file_path.basename())[0]
            if style in self._stylesheets:
                self.reload(style)

        if mask is inotify.IN_CREATE:
            if file_path.exists():
                self.load(file_path)


__all__ = ['StylesheetError', 'Stylesheet', 'StylesheetManager']
