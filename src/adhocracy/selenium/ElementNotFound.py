#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ElementNotFound(Exception):
    def __init__(self, message): #, Errors):
        Exception.__init__(self, message)

        #self.Errors = Errors
