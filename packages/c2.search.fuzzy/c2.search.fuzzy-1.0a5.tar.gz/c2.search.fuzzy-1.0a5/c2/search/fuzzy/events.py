# coding: utf-8

from Products.CMFCore.utils import getToolByName

# modified event for contents
def words_store_for_fuzzy_search(obj, event):
    fuzzy_tool = getToolByName(obj, 'words_for_fuzzy', None)
    if fuzzy_tool is None:
        return None
    text = obj.SearchableText()
    fuzzy_tool.add_index_form_text(text)
