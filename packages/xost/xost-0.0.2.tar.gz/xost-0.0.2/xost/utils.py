# -*- coding: utf-8 -*-

def url_to_list(url):
    path = url.split('/')
    if path[0] == '':
        del path[0]
    if len(path) > 1 and path[len(path) - 1] == '':
        del path[len(path) - 1]
    return path

