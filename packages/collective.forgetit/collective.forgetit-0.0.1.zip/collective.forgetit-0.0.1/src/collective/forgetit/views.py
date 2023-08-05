#!/usr/bin/python
# -*- coding: utf-8 -*-

from BTrees.check import check
from pickle import dumps, PicklingError
from Products.Five import BrowserView
from ZODB.broken import BrokenModified
from zope.component import queryUtility


class RemoveResidue(BrowserView):

    def __init__(self, request, response):
        self.action = False
        self.results = []
        super(RemoveResidue, self).__init__(request, response)

    def __call__(self, doit=False):
        if doit:
            self.action = True
            self.doit()
        return super(RemoveResidue, self).__call__()

    def doit(self):
        self.clean_zc_relation()

    def clean_zc_relation(self):
        broken_btree_keys = []
        broken_btree_set_elements = []
        unordered_btrees = []
        try:
            from zc.relation.interfaces import ICatalog
        except ImportError:
            return
        utility = queryUtility(ICatalog)
        if not utility:
            return

        for (btree_key, btree_value) in \
            utility._name_TO_mapping.items():
            if not self.is_ordered(btree_value):
                btree_value = self.copy(utility._name_TO_mapping, btree_key)
                unordered_btrees.append(btree_key)

            keys_to_remove = []
            for inner_key in btree_value.keys():
                if not self.can_serialize(inner_key):
                    keys_to_remove.append(inner_key)
            for inner_key in keys_to_remove:
                try:
                    del btree_value[inner_key]
                except TypeError:
                    btree_value.remove(inner_key)
                broken_btree_keys.append(inner_key)

        for (btree_key, btree_value) in \
            utility._reltoken_name_TO_objtokenset.items():
            if not self.is_ordered(btree_value):
                self.copy(utility._reltoken_name_TO_objtokenset, btree_key)
                unordered_btrees.append(btree_key)

            keys_to_remove = []
            for key in btree_value or []:
                if not self.can_serialize(key):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                try:
                    del btree_value[key]
                except TypeError:
                    btree_value.remove(key)
                broken_btree_keys.append(key)

        if broken_btree_keys:
            self.results.append('In zc.relation %i keys were broken. These keys and their values have ben removed. Unique List of keys: %s'
                                 % (len(broken_btree_keys), set([str(x)
                                for x in broken_btree_keys])))

        if broken_btree_set_elements:
            self.results.append('In zc.relation %i values lists of BTrees contained values that are broken. These values have been removed. Unique list of keys: %s'
                                 % (len(broken_btree_set_elements),
                                set([str(x) for x in
                                broken_btree_set_elements])))

        if unordered_btrees:
            self.results.append('In zc.relation %i btrees where unordered have been ordered'
                                 % len(unordered_btrees))

    def can_serialize(self, item):
        try:
            dumps(item)
        except (BrokenModified, PicklingError):
            return False
        return True

    def is_ordered(self, item):
        if item is None:
            return True
        try:
            check(item)
        except AssertionError:
            return False
        return True

    def copy(self, dictitem, key):
        dictitem[key] = dictitem[key].__class__(dictitem[key])
        return dictitem[key]
