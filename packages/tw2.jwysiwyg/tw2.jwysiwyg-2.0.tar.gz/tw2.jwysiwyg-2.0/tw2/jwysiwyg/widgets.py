from tw2.jquery import jquery_js
from tw2.jquery.base import jQuery
from tw2.jquery.version import JSLinkMixin
from tw2.core import JSLink, CSSLink
from tw2.forms import TextArea
import defaults

class MyLinkMixin(JSLinkMixin):
    dirname = '0.6/jwysiwyg'
    basename = 'jquery.wysiwyg'
    name='jquery.jwysiwyg'
    version = '0.6'
    modname = 'tw2.jwysiwyg'

class MyJSLink(JSLink, MyLinkMixin):
    pass

class MyCSSLink(CSSLink, MyLinkMixin):
    extension = 'css'

# SwitchView
jwysiwyg_js = MyJSLink(name='jwysiwyg', location='bodybottom')
jwysiwyg_css = MyCSSLink(name='jwysiwyg')

class JWysiwyg(TextArea):
    resources = jquery_js, jwysiwyg_css, jwysiwyg_js
    def prepare(self):
        self.add_call(jQuery('#%s'%self.id).wysiwyg())
        return super(JWysiwyg, self).prepare()