from tw2.jquery.version import JSLinkMixin
from tw2.core import JSLink, CSSLink, js_function
from tw2.forms import TextArea

class MyLinkMixin(JSLinkMixin):
    dirname = '4.0.1'
    basename = 'ckeditor'
    name='ckeditor'
    version = '4.0.1'
    modname = 'tw2.ckeditor'

class MyJSLink(JSLink, MyLinkMixin):
    pass

class MyCSSLink(CSSLink, MyLinkMixin):
    name='contents'
    extension = 'css'

ckeditor_js = MyJSLink(name='ckeditor', location='bodybottom')

class CKEditor(TextArea):
    resources = ckeditor_js,
    def prepare(self):
        self.add_call(js_function('CKEDITOR.replace')(self.id))
        return super(CKEditor, self).prepare()


__all__ = ['CKEditor']