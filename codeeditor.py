# -*- coding: utf-8 -*-
__all__ = ('CodeEditor', )

from kivy.uix.boxlayout import BoxLayout
from codeinput import CodeInput
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder

from functools import partial


Builder.load_string('''
<CodeEditor>
    codeinput: codein
    scrollview: scrlv
    lbl_line_no: lbl_line_no
    ScrollView:
        id: scrlv
        GridLayout:
            rows: 1
            size_hint: 1, None
            TextInput:
                id: lbl_line_no
                size_hint: None, 1
                pos: self.parent.pos
                font_size: codein.font_size
                foreground_color: codein.text_color
                background_color: codein.background_color
                readonly: True
            CodeInput:
                id: codein
                font_name: 'data/fonts/DejaVuSans.ttf'
''')


class CodeEditor(BoxLayout):

    def __init__(self, **kwargs):
        super(CodeEditor, self).__init__(**kwargs)
        _codeinput = self.codeinput
        _codeinput.bind(cursor = self.on_cursor_pos,
                         line_height = self.on_line_height,
                         _lines = self.on_line_height)
        self.last_line_no = 0

    def on_line_height(self, *l):
       _codeinput = self.codeinput
       len_lines = len(_codeinput._lines)
       _codeinput.parent.height = max((len_lines + 1.) *
                (_codeinput.line_height + (_codeinput._line_spacing)),
                self.height)
       self.line_height = (_codeinput.parent.height /(len_lines + 1.))
       lbl = '1'
       for line in xrange(1, len_lines):
           lbl = ''.join(
               (lbl, '\n', str(line+1)))
       lbl_line_no = self.lbl_line_no
       lbl_line_no.width =\
           _codeinput._label_cached.get_extents(str(len_lines))[0]\
           + (_codeinput.padding_x * 2)
       lbl_line_no.text = lbl

    def on_cursor_pos(self, *l):
        _line_no = l[1][1]
        if self.last_line_no != _line_no:
            # cursor on new line
            self.last_line_no = _line_no
            _codeinput = self.codeinput
            _codeinput.parent.do_layout()
            _cur_pos = _codeinput.cursor_pos[1]
            _line_height = self.line_height
            _scrollview = self.scrollview

            if _cur_pos < _line_height:
                # scroll down
                while _cur_pos < _line_height:
                    _scrollview.scroll_y -= (
                        ((_line_height + 0.) - _cur_pos)
                            /(_codeinput.height + 0.))
                    _codeinput.parent.do_layout()
                    _cur_pos = _codeinput.cursor_pos[1]
            elif _cur_pos > _scrollview.top:
                #scroll up
                while _cur_pos > _scrollview.top:
                    # if partial line is displayed at the botton display it fully
                    _scrollview.scroll_y += (
                        ((_cur_pos  - _scrollview.top)+ 0.0)
                            /(_codeinput.height+0.0))
                    _codeinput.parent.do_layout()
                    _cur_pos = _codeinput.cursor_pos[1]

Factory.register('CodeInput', CodeInput)

from kivy.app import App

class MyApp(App):
    def build(self):
        return CodeEditor()

if __name__ == '__main__':
    MyApp().run()