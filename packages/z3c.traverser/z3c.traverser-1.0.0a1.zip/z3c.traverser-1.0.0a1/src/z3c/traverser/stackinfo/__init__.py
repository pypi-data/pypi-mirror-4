from __future__ import absolute_import
from .traversing import applyStackConsumers

def applyStackConsumersHandler(obj, event):
    applyStackConsumers(obj, event.request)

