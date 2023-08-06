# # -*- coding: utf-8 -*-
#
# from django.utils.translation import gettext as _
#
# class CellFilter(object):
#     title = ""
#     menu_labels = {'lt': _('Less than'),
#                    'gt': _('Greater than'),
#                    'lte': _('Less or equals than'),
#                    'gte': _('Greater or equals than'),
#                    'exact': _('Equals to'),
#                    'not': _('Not equals to'),
#                    'rem': _('Remove filter')}
#
#     def __init__(self, field, request, params, model, model_admin, field_path, column=None):
#         self.column = column or field_path or field.name
#         self.col_operators = model_admin.cell_filter_operators.get(field.name, ('exact', 'not'))
#         self.seed = field_path
#
#
#     def __repr__(self):
#         return "<%s for `%s` as %s>" % (self.__class__.__name__, self.column, id(self))
#
#     def is_active(self, cl):
#         active_filters = cl.params.keys()
#         for x in self.expected_parameters():
#             if x in active_filters:
#                 return True
#         return False
#
#     def has_output(self):
#         return True
#
#     def get_menu_item_for_op(self, op):
#         return CellFilter.menu_labels.get(op), '%s__%s' % (self.seed, op)
#
#     def expected_parameters(self):
#         expected_parameters = []
#         for op in self.col_operators:
#             filter = '%s__%s' % (self.seed, op)
#             expected_parameters.append(filter)
#         return expected_parameters
#
#
# class ChoicesCellFilter(CellFilter, AllValuesFieldListFilter):
#     pass
#
#
# class BooleanCellFilter(CellFilter, AllValuesFieldListFilter):
#     def __init__(self, field, request, params, model, model_admin, field_path, column=None):
#         self.col_operators = model_admin.cell_filter_operators.get(field.name, ('exact', 'not'))
#         super(BooleanCellFilter, self).__init__(field, request, params, model, model_admin, field_path, column)
#
#     def get_menu_item_for_op(self, op):
#         if op in ('exact', ''):
#             return _('Yes'), self.seed
#         else:
#             return _('No'), '%s__not' % self.seed
#
#     def expected_parameters(self):
#         expected_parameters = []
#         ops = [op for op in self.col_operators if op != 'exact']
#         expected_parameters.append(self.seed)
#         for op in ops:
#             filter = '%s__%s' % (self.seed, op)
#             expected_parameters.append(filter)
#         return expected_parameters
#
#
# class FieldCellFilter(CellFilter, AllValuesFieldListFilter):
#     def get_menu_item_for_op(self, op):
#         if op == 'exact':
#             return CellFilter.menu_labels.get(op), self.seed
#         return CellFilter.menu_labels.get(op), '%s__%s' % (self.seed, op)
#
#     def expected_parameters(self):
#         expected_parameters = []
#         ops = [op for op in self.col_operators if op != 'exact']
#         expected_parameters.append(self.seed)
#         for op in ops:
#             filter = '%s__%s' % (self.seed, op)
#             expected_parameters.append(filter)
#         return expected_parameters
#
#
# class RelatedFieldCellFilter(RelatedFieldListFilter, CellFilter):
#     def __init__(self, field, request, params, model, model_admin, field_path, column=None):
#         super(RelatedFieldCellFilter, self).__init__(field, request, params, model, model_admin, field_path)
#         self.column = column or field_path or field.name
#         self.col_operators = model_admin.cell_filter_operators.get(field.name, ('exact', 'not'))
#         self.seed = "__".join(self.lookup_kwarg.split('__')[:-1])
#

class BooleanCellFilter(CellFilter):
    def __init__(self, field):

