# -*- coding: utf-8 -*-
"""Modulo"""
def imp_list(la_list):
    """Funcion"""
    for each_item in la_list:
        if isinstance(each_item,list):
            imp_list(each_item)
        else:
            print(each_item)
