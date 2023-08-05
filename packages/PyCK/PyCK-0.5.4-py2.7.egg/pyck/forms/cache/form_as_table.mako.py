# -*- encoding:utf8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1336407223.622515
_enable_loop = True
_template_filename = '/mnt/md0/MyWork/MyProjects/PyCK/pyck/forms/templates/form_as_table.mako'
_template_uri = 'form_as_table.mako'
_source_encoding = 'utf8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        str = context.get('str', UNDEFINED)
        form = context.get('form', UNDEFINED)
        labels_position = context.get('labels_position', UNDEFINED)
        errors_position = context.get('errors_position', UNDEFINED)
        include_table_tag = context.get('include_table_tag', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1

        num_cols = 2
        num_rows = 2
        
        if labels_position in ['left', 'right'] and errors_position in ['left', 'right']:
            num_cols = 3
            num_rows = 1
        elif labels_position in ['top', 'bottom'] and errors_position in ['top', 'bottom']:
            num_cols = 1
            num_rows = 3
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['num_rows','num_cols'] if __M_key in __M_locals_builtin_stored]))
        # SOURCE LINE 11
        __M_writer(u'\n')
        # SOURCE LINE 12
        if include_table_tag:
            # SOURCE LINE 13
            __M_writer(u'<table>\n')
            pass
        # SOURCE LINE 15
        if form._use_csrf_protection:
            # SOURCE LINE 16
            __M_writer(u'    <input type="hidden" name="csrf_token" value="')
            __M_writer(unicode(form._csrf_token))
            __M_writer(u'" />\n')
            pass
        # SOURCE LINE 18
        if '_csrf' in form.errors:
            # SOURCE LINE 19
            __M_writer(u'    <tr><td class="errors" colspan="')
            __M_writer(unicode(num_cols))
            __M_writer(u'">')
            __M_writer(unicode(form.errors['_csrf'][0]))
            __M_writer(u'</td></tr>\n')
            pass
        # SOURCE LINE 21
        for field in form:
            # SOURCE LINE 22
            __M_writer(u'    ')

            field_label = '<td>' + str(field.label) + '</td>'
            field_content = '<td>' + str(field) + '</td>'
            field_errors = '<td></td>'
            if field.errors:
                field_errors = '<td class="errors">'
                for e in field.errors:
                    field_errors += e + ', '
                
                field_errors = field_errors[:-2] + '</td>'
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field_label','field_errors','e','field_content'] if __M_key in __M_locals_builtin_stored]))
            # SOURCE LINE 32
            __M_writer(u'\n')
            # SOURCE LINE 33
            if 1 == num_rows:
                # SOURCE LINE 34
                __M_writer(u'    <tr>\n')
                # SOURCE LINE 35
                if 'left'==labels_position:
                    # SOURCE LINE 36
                    __M_writer(u'        ')
                    __M_writer(unicode(field_label))
                    __M_writer(u'\n')
                    pass
                # SOURCE LINE 38
                if 'left'==errors_position:
                    # SOURCE LINE 39
                    __M_writer(u'        ')
                    __M_writer(unicode(field_errors))
                    __M_writer(u'\n')
                    pass
                # SOURCE LINE 41
                __M_writer(u'        ')
                __M_writer(unicode(field_content))
                __M_writer(u'\n')
                # SOURCE LINE 42
                if 'right'==labels_position:
                    # SOURCE LINE 43
                    __M_writer(u'        ')
                    __M_writer(unicode(field_label))
                    __M_writer(u'\n')
                    pass
                # SOURCE LINE 45
                if 'right'==errors_position:
                    # SOURCE LINE 46
                    __M_writer(u'        ')
                    __M_writer(unicode(field_errors))
                    __M_writer(u'\n')
                    pass
                # SOURCE LINE 48
                __M_writer(u'    </tr>\n')
                # SOURCE LINE 49
            elif 3 == num_rows:
                # SOURCE LINE 50
                __M_writer(u'    <tr>\n    <td>\n        <table>\n')
                # SOURCE LINE 53
                if 'top'==labels_position:
                    # SOURCE LINE 54
                    __M_writer(u'        <tr>')
                    __M_writer(unicode(field_label))
                    __M_writer(u'</tr>\n')
                    pass
                # SOURCE LINE 56
                if 'top'==errors_position:
                    # SOURCE LINE 57
                    __M_writer(u'        <tr>')
                    __M_writer(unicode(field_errors))
                    __M_writer(u'</tr>\n')
                    pass
                # SOURCE LINE 59
                __M_writer(u'        <tr>')
                __M_writer(unicode(field_content))
                __M_writer(u'</tr>\n')
                # SOURCE LINE 60
                if 'bottom'==labels_position:
                    # SOURCE LINE 61
                    __M_writer(u'        <tr>')
                    __M_writer(unicode(field_label))
                    __M_writer(u'</tr>\n')
                    pass
                # SOURCE LINE 63
                if 'bottom'==errors_position:
                    # SOURCE LINE 64
                    __M_writer(u'        <tr>')
                    __M_writer(unicode(field_errors))
                    __M_writer(u'</tr>\n')
                    pass
                # SOURCE LINE 66
                __M_writer(u'        </table>\n    </td>\n    </tr>\n')
                # SOURCE LINE 69
            else: ## 2 rows and 2 cols
                # SOURCE LINE 70
                __M_writer(u'    <tr>\n    <td>\n        <table>\n')
                # SOURCE LINE 73
                if 'top'==labels_position:
                    # SOURCE LINE 74
                    __M_writer(u'        <tr>')
                    __M_writer(unicode(field_label))
                    __M_writer(u'</tr> \n        <tr> ')
                    # SOURCE LINE 76
                elif 'left'==labels_position:
                    # SOURCE LINE 77
                    __M_writer(u'        <tr>')
                    __M_writer(unicode(field_label))
                    __M_writer(u' ')
                    pass
                # SOURCE LINE 79
                __M_writer(u'        ')
                # SOURCE LINE 80
                if 'top'==errors_position:
                    # SOURCE LINE 81
                    __M_writer(u'        <tr>')
                    __M_writer(unicode(field_errors))
                    __M_writer(u'</tr> \n        <tr> ')
                    # SOURCE LINE 83
                elif 'left'==errors_position:
                    # SOURCE LINE 84
                    __M_writer(u'        <tr>')
                    __M_writer(unicode(field_errors))
                    __M_writer(u' ')
                    pass
                # SOURCE LINE 86
                __M_writer(u'        ')
                # SOURCE LINE 87
                __M_writer(u'        ')
                __M_writer(unicode(field_content))
                __M_writer(u'\n        ')
                # SOURCE LINE 89
                if 'bottom'==labels_position:
                    # SOURCE LINE 90
                    __M_writer(u'        </tr>\n        <tr>')
                    # SOURCE LINE 91
                    __M_writer(unicode(field_label))
                    __M_writer(u'</tr>\n')
                    # SOURCE LINE 92
                elif 'right'==labels_position:
                    # SOURCE LINE 93
                    __M_writer(u'        ')
                    __M_writer(unicode(field_label))
                    __M_writer(u'</tr>\n')
                    pass
                # SOURCE LINE 95
                __M_writer(u'        ')
                # SOURCE LINE 96
                if 'bottom'==errors_position:
                    # SOURCE LINE 97
                    __M_writer(u'        </tr>\n        <tr>')
                    # SOURCE LINE 98
                    __M_writer(unicode(field_errors))
                    __M_writer(u'</tr>\n')
                    # SOURCE LINE 99
                elif 'right'==errors_position:
                    # SOURCE LINE 100
                    __M_writer(u'        ')
                    __M_writer(unicode(field_errors))
                    __M_writer(u'</tr>\n')
                    pass
                # SOURCE LINE 102
                __M_writer(u'        </table>\n    </td>\n    </tr>\n')
                pass
            # SOURCE LINE 106
            __M_writer(u'    \n')
            pass
        # SOURCE LINE 108
        if include_table_tag:
            # SOURCE LINE 109
            __M_writer(u'</table>\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


