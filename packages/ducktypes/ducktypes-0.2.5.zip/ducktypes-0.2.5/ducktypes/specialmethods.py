from abc import ABCMeta
import collections

collections_classes = [getattr(collections, c) for c in dir(collections)
                       if getattr(collections, c).__class__ is ABCMeta]
