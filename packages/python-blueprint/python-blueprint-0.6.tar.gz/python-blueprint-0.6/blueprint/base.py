# -*- coding: utf-8 -*-
"""blueprint.base -- base metaclasses and other junk for blueprints.
"""
from __future__ import absolute_import
import re
import inspect
import copy
from collections import deque
import random
from six import with_metaclass

from . import taggables
from . import fields

__all__ = ['Blueprint']


class Meta(object):
    """Meta options for Blueprints.

    Default options include:

    - ``fields``: a set of the field names present on the blueprint.

    - ``mastered``: flag indicating whether the blueprint has been
      mastered (i.e. instantiated).

    - ``abstract``: flag indicating whether the blueprint is
      abstract. Abstract blueprints don't show up in tag queries.

    - ``source``: when a blueprint is modded, indicates the source blueprint.

    - ``parent``: when a blueprint is nested inside another blueprint,
      indicates the parent blueprint.

    - ``random``: an instance of ``random.Random``, used for random number generation.

    - ``seed``: the seed used to initialize the ``random.Random`` instance.
    """
    def __init__(self):
        self.fields = set()
        self.mastered = False
        self.abstract = False
        self.source = None
        self.parent = None
        
        self.random = random.Random()
        self.seed = random.random()
        self.random.seed(self.seed)

    def __deepcopy__(self, memo):
        not_there = []
        existing = memo.get(self, not_there)
        if existing is not not_there:
            return existing

        meta = Meta()
        for name, value in self.__dict__.items():
            if name == 'source' or name == 'parent':
                setattr(meta, name, value)
            elif name == 'random':
                meta.random = random.Random()
            else:
                setattr(meta, name, copy.deepcopy(value, memo))
        memo[self] = meta
        return meta

camelcase_cp = re.compile(r'[A-Z][^A-Z]+')


class BlueprintMeta(type):
    """Metaclass for blueprints. Handles the declarative magic.
    """
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'tag_repo'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.tag_repo = taggables.TagRepository()
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.tags = set(cls.tags.split())
            cls.tags.add(cls.__name__)
            cls.tags.update(t.lower() for t in camelcase_cp.findall(cls.__name__))
            cls.last_picked = 0.0
            if 'name' not in attrs:
                cls.name = ' '.join(camelcase_cp.findall(cls.__name__))
            for base in bases:
                if hasattr(base, 'tags'):
                    cls.tags.update(base.tags)
            cls.tag_repo.addObject(cls)

    def __new__(cls, name, bases, attrs):
        _new = attrs.pop('__new__', None)
        new_attrs = {'__new__': _new} if _new is not None else {}
        new_class = super(BlueprintMeta, cls).__new__(cls, name, bases, new_attrs)
        new_class.tags = attrs.pop('tags', '')

        # Set up Meta options
        meta = new_class.meta = Meta()
        if 'Meta' in attrs:
            usermeta = attrs.pop('Meta')
            for key, value in usermeta.__dict__.items():
                if not key.startswith('_'):
                    setattr(meta, key, value)
        meta.fields.update(a for a in attrs.keys() if not a.startswith('_') and not hasattr(attrs[a], 'is_generator'))
        for base in bases:
            if hasattr(base, 'meta'):
                meta.fields.update(base.meta.fields)

        # Transfer the rest of the attributes.
        for name, value in attrs.items():
            new_class.add_to_class(name, value)

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def __repr__(cls):
        return '<%s:\n    %s\n    >' % (
            cls.__name__,
            '\n    '.join(
                '%s -- %s' % (
                    n,
                    '\n'.join(
                        '    %s' % i
                        for i in repr(getattr(cls, n)).splitlines()
                        ).strip()
                    )
                for n in sorted(cls.meta.fields)
                )
            )


class Blueprint(with_metaclass(BlueprintMeta, taggables.TaggableClass)):
    """A magical blueprint.

    To create a blueprint, subclass Blueprint and add your
    fields. Blueprints are automatically tagged by their class name
    (CamelCase names are automatically split into components), and
    inherit their ancestor blueprints' tags.

    Example::

        >>> import blueprint as bp
        
        >>> class Item(bp.Blueprint):
        ...     # Tags are space-separated
        ...     tags = 'foo bar'
        ...     # Simple fields are static values
        ...     name = 'generic item'
        ...     value = 1
        ...     # Dynamic field values use any callable object
        ...     quality = bp.RandomInt(1, 6)
        ...     price = bp.depends_on('value', 'quality')(lambda _: _.value * _.quality)

        >>> Item.tags
        set(['Item', 'foo', 'bar', 'item'])
        >>> item = Item()  # Instantiate a "mastered" blueprint.
        
        >>> item.value
        1
        >>> 1 <= item.quality <= 6
        True
    """

    def __repr__(self):
        return '<%s:\n    %s\n    >' % (
            self.__class__.__name__,
            '\n    '.join(
                '%s -- %s' % (
                    n,
                    '\n'.join(
                        '    %s' % i
                        for i in repr(getattr(self, n)).splitlines()
                        ).strip()
                    )
                for n in sorted(self.meta.fields)
                )
            )

    def __init__(self, parent=None, seed=None, **kwargs):
        self.meta = copy.deepcopy(self.meta)
        if parent is not None:
            self.meta.parent = parent
        self.meta.mastered = True
        if seed is not None:
            self.meta.seed = seed
        elif parent is not None:
            self.meta.seed = parent.meta.seed
        else:
            self.meta.seed = random.random()
        self.meta.random.seed(self.meta.seed)
        self.meta.kwargs = kwargs
        for name, value in kwargs.items():
            setattr(self, name, value)

        # Resolve any unresolved fields.
        resolved = set()
        deferred = deque()
        deferred_to_end = deque()
        deferred_to_end_names = set()

        def resolve(name, field):
            # print "Can we resolve", name
            if callable(field):
                if hasattr(field, 'depends_on') and not field.depends_on.issubset(resolved):
                    if field.depends_on.intersection(deferred_to_end_names):
                        # print "Deferring", name, "to end."
                        deferred_to_end.append(name)
                    else:
                        # print "Deferring", name
                        deferred.appendleft((name, field))
                else:
                    # print "Resolving", name
                    setattr(self, name, fields.resolve(self, field))
                    resolved.add(name)
            else:
                resolved.add(name)
            
        for name in self.meta.fields:
            class_field = getattr(self.__class__, name)
            if hasattr(class_field, '_defer_to_end'):
                deferred_to_end.appendleft(name)
                deferred_to_end_names.add(name)
            else:
                field = getattr(self, name)
                resolve(name, field)

        while deferred:
            name, field = deferred.pop()
            resolve(name, field)

        deferred_to_end_names.clear()
        while deferred_to_end:
            name = deferred_to_end.pop()
            field = getattr(self, name)
            resolve(name, field)

    @fields.generator
    def as_dict(self):
        return dict((n, getattr(self, n)) for n in self.meta.fields)
