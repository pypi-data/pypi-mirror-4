# -*- coding: utf-8 -*-

class Parser(object):
    def translate_path(self, path):
        """
        Translate absolute web path to storage path.
        """

        if path.startswith("/static/"):
            path = path[8:]
        return path
