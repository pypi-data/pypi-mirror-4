# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1336017512.815094
_enable_loop = True
_template_filename = '/mnt/md0/MyWork/MyProjects/PyCK/pyck/forms/templates/form_as_p.mako'
_template_uri = 'form_as_p.mako'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        errors_position = context.get('errors_position', UNDEFINED)
        labels_position = context.get('labels_position', UNDEFINED)
        form = context.get('form', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        if form._use_csrf_protection:
            # SOURCE LINE 3
            __M_writer(u'<input type="hidden" name="csrf_token" value="')
            __M_writer(unicode(form._csrf_token))
            __M_writer(u'" />\n')
            pass
        # SOURCE LINE 5
        if '_csrf' in form.errors:
            # SOURCE LINE 6
            __M_writer(u'<div class="errors">')
            __M_writer(unicode(form.errors['_csrf'][0]))
            __M_writer(u'</div><br />\n')
            pass
        # SOURCE LINE 8
        for field in form:
            # SOURCE LINE 9

            field_errors = ''
            if field.errors:
                field_errors = '<span class="errors">'
                for e in field.errors:
                    field_errors += e + ', '
                
                field_errors = field_errors[:-2] + '</span>'
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field_errors','e'] if __M_key in __M_locals_builtin_stored]))
            # SOURCE LINE 17
            __M_writer(u'\n<p>\n')
            # SOURCE LINE 19
            if 'top' == labels_position:
                # SOURCE LINE 20
                __M_writer(unicode(field.label))
                __M_writer(u'<br /> ')
                pass
            # SOURCE LINE 23
            if field_errors and 'top'==errors_position:
                # SOURCE LINE 24
                __M_writer(unicode(field_errors))
                __M_writer(u'<br /> ')
                pass
            # SOURCE LINE 27
            if 'left' == labels_position:
                # SOURCE LINE 28
                __M_writer(unicode(field.label))
                __M_writer(u' ')
                pass
            # SOURCE LINE 31
            if field_errors and 'left'==errors_position:
                # SOURCE LINE 32
                __M_writer(unicode(field_errors))
                __M_writer(u' ')
                pass
            # SOURCE LINE 35
            __M_writer(unicode(field))
            __M_writer(u' ')
            # SOURCE LINE 37
            if 'bottom' == labels_position:
                # SOURCE LINE 38
                __M_writer(u'<br />')
                __M_writer(unicode(field.label))
                __M_writer(u' ')
                pass
            # SOURCE LINE 41
            if field_errors and 'bottom'==errors_position:
                # SOURCE LINE 42
                __M_writer(u'<br />')
                __M_writer(unicode(field_errors))
                __M_writer(u' ')
                pass
            # SOURCE LINE 45
            if 'right' == labels_position:
                # SOURCE LINE 46
                __M_writer(unicode(field.label))
                __M_writer(u' ')
                pass
            # SOURCE LINE 49
            if field_errors and 'right'==errors_position:
                # SOURCE LINE 50
                __M_writer(unicode(field_errors))
                __M_writer(u' ')
                pass
            # SOURCE LINE 52
            __M_writer(u'</p>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


