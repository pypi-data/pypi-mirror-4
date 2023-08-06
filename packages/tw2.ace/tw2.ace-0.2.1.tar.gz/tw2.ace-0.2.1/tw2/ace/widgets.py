import os
import tw2.core as twc
import tw2.forms as twf


ace_js = twc.JSLink(
    modname=__name__,
    filename='static/ace/ace.js',
    edit=twc.js_function('ace.edit'),
    require=twc.js_function('ace.require'),
    )
ext_textarea_js = twc.JSLink(
    modname=__name__,
    filename='static/ace/ext-textarea.js',
    #Not safe for multiple widget instances per request
    #transformTextarea=ace_js.require('ace/ext/textarea').transformTextarea
    )
tw2_ace_js = twc.JSLink(
    modname=__name__,
    filename='static/tw2_ace.js',
    resources = [ace_js, ext_textarea_js],
    tw2_ace=twc.js_function('tw2_ace'),
    )

ace_modes = dict(
    (f.strip('mode-').rstrip('.js'), twc.JSLink(modname=__name__, filename=os.path.join('static/ace', f)))
    for f in os.listdir(os.path.join(os.path.dirname(__file__), 'static/ace')) if f.startswith('mode-'))
ace_themes = dict(
    (f.strip('theme-').rstrip('.js'), twc.JSLink(modname=__name__, filename=os.path.join('static/ace', f)))
    for f in os.listdir(os.path.join(os.path.dirname(__file__), 'static/ace')) if f.startswith('theme-'))


def mode_name(mode):
    '''Tries best-effortly to get the right mode name'''

    if mode:
        l = mode.lower()

        if l in ('c', 'c++', 'cxx'):
            return 'c_cpp'

        if l in ('bash', ):
            return 'sh'

        if l in ace_modes:
            return l

    return None


class AceWidget(twf.TextArea):
    # declare static resources here
    # you can remove either or both of these, if not needed
    resources = [tw2_ace_js]

    mode = twc.Param('The highlighting mode for ace', default='')

    show_gutter = twc.Param(default=True)
    soft_wrap = twc.Param(u'''Possible values:
False:
    No soft wrap
True:
    Free soft wrap on editor border
Integer:
    Soft wrap after specified characters
''', default=True)
    clone_pre_style = twc.Param(default=True)
    settings_panel = twc.Param(default=False)

#    @classmethod
#    def post_define(cls):
#        pass
#        # put custom initialisation code here

    def prepare(self):
        super(AceWidget, self).prepare()
        # put code here to run just before the widget is displayed
        self.safe_modify('resources')
        mode = mode_name(self.mode)
        options = dict(
            show_gutter=self.show_gutter,
            soft_wrap=self.soft_wrap,
            clone_pre_style=self.clone_pre_style,
            settings_panel=self.settings_panel,
            )
        self.add_call(tw2_ace_js.tw2_ace(self.compound_id, None, mode, options))
