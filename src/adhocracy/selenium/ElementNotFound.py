#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ElementNotFound(BaseException):
    def __init__(self, message): #, Errors):
        BaseException.__init__(self, message)

        #self.Errors = Errors
