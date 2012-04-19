# -*- coding: utf-8 -*-
__all__ = ('CodeInput', )

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import BBCodeFormatter

from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.cache import Cache
from kivy.properties import BooleanProperty
from kivy.factory import Factory

Cache.register('codeinput.label.width', timeout=260.)
Cache.register('codeinput.label', timeout=260.)

# TODO: use a config/rc file kivy config ?? for highlighting
# TODO: color chooser new styli
# TODO: use utf8 every where
# TODO: fix unicode keyboard input # kde issue
# TODO: undo
# TODO: fix scroll while deletion
# Known Issue pasting text is slow
# selecting text is slow


class CodeInput(TextInput):
    '''CodeInput class, see module documentation for more information.

    :Events:
        `ccc`
            description
    '''

    #show_line_numbers = BooleanProperty(True)
    #'''
    #Show Line Numbers at the left of the window.

    #:data:`show_line_numbers` is a :class:`~kivy.properties.BooleanProperty`, #default to True
    #'''

    def __init__(self, **kwargs):
        super(CodeInput, self).__init__(**kwargs)
        self._line_options = kw = self._get_line_options()
        self._markup_label_cached = Label(markup = True, **kw)
        self.lexer = PythonLexer()
        self.formatter = BBCodeFormatter()
        text_color = kwargs.get('foreground_color')
        #use text_color as foreground color
        if text_color:
            self.text_color = (text_color[0], text_color[1], text_color[2],
                text_color[3])
        else:
            self.text_color = (0, 0, 0, 1)
        # set foreground to white to allow text colors to show
        # use text_color as the default color in bbcodes
        self.foreground_color = [1, 1, 1, 1]
        if not kwargs.get('background_color'):
            self.background_color = [.9, .92, .92, 1]

    def _create_line_label(self, text):
        #TODO: optimize this func, it's horribly inefficient

        ntext = text.replace('\n', '').replace('\t', ' ' * self.tab_width)
        # Create a label from a text, using line options
        kw = self._line_options
        cid = '%s\0%s' % (ntext, str(kw))
        texture = Cache.get('codeinput.label', cid)
        if not texture:
            #if multiple lines render empty texture wait for refresh text'
            if text.find('\n') > 0:
                label = self._label_cached
                label.text = ''
                label.refresh()
                texture = label.texture
                Cache.append('codeinput.label', cid, texture)
                return texture 
            #get bbcoded text for python
            try:
                ntext[0]
                # replace brackets with special chars that aren't highlighted
                # by pygment. can't use &bl; ... cause & is highlighted
                # if at some time support for braille is added then replace these
                # characters with something else
                ntext = ntext.replace('[', u'⣿;').replace(']', u'⣾;')
                ntext = highlight(ntext, self.lexer, self.formatter)
                ntext = ntext.replace(u'⣿;', '&bl;').replace(u'⣾;', '&br;')
                # replace special chars with &bl; and &br;
                ntext = ''.join(('[color=rgba', str(self.text_color), ']',
                    ntext, '[/color]'))
            except IndexError:
                pass

            # FIXME right now, we can't render very long line...
            # if we move on "VBO" version as fallback, we won't need to do this.
            # try to found the maximum text we can handle
            label = self._markup_label_cached
            label.text = ntext
            label.texture_update()

            texture = label.texture
            label.text = ''
            Cache.append('codeinput.label', cid, texture)
        return texture

    # overriden to get accurate cursor position for markup text
    def _get_text_width(self, text):
        # fix cursor placement diff cause of markup
        kw = self._line_options
        ntext = text.replace('\t', ' ' * self.tab_width)
        cid = '%s\0%s' % (ntext, str(kw))
        width = Cache.get('textinput.label.width', cid)
        if not width:
            texture = self._create_line_label(ntext)
            # use width of texture of '.' instead of ' ' in start of line,
            # which is of 0 width in markup
            width =  texture.width if texture else\
                self._label_cached.get_extents('.')[0] * len(ntext)
            Cache.append('codeinput.label.width', cid, width)
        return width

    # overriden to prevent cursor position off screen
    def _cursor_offset(self):
        '''Get the cursor x offset on the current line
        '''
        offset = 0
        try:
            if self.cursor_col:
                offset = self._get_text_width(
                    self._lines[self.cursor_row][:self.cursor_col])
        except:
            pass
        finally:
            return offset

Factory.register('CodeInput', CodeInput)