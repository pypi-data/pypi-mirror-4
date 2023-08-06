"""
P(r)e-(Seriali)z(ation)

When serializing an object, and the objects it in turn references thereby
forming an object tree, we typically need to transform that object tree into
something that can be fed into a more general serializer for language
primitives (e.g. dicts, lists, ints, strings, etc).

Rather than write that transformation processing for each target serialization
use this library to declaratively construct the transformation logic once
using what are called 'specs' and feed the results to a primitives serializer.

Transform 'specs' are very simple: any callable that takes a traversal context
and the object to transform. Those transformation specs are then associated
with your custom classes so that pez can find the right transformation to apply
while traversing the object tree.

The motivating use case is mime-serializing ORM objects. The pre-serialization
pass encapsulates the transformation of ORM objects to primitives that can be
mime-serialized largely independent of application logic. In this case pez is
used to build the views portion of the MVC pattern.

Example::

    import json

    from flask import url_for
    import pez

    from myapp.db import Session
    from myapp.models import MyType, Actor


    class PermissionFilter(pez.Spec):
        def __init__(self, spec, permission, mask=pez.NONE):
            self.spec = spec
            self.permission = permission
            self.mask = mask

        def __call__(self, ctx, o):
            if not ctx.actor.can(self.permission):
                return self.mask
            return self.spec(ctx, o)


    EchoField = pez.Field()
    EchoPrivateField = pez.PermissionFilter(EchoField, 'see-privates')


    class MyTypeView(pez.FieldMapping):
        field1 = EchoField
        field2 = EchoPrivateField

        @staticmethod
        def one_off(ctx, o)
            return o.x + o.y

        @staticmethod
        def one_off_2(ctx, o)
            ctx.name = 'my_name_is' + str(o.z)
            return o.x - o.y

        @staticmethod
        def uri(ctx, o):
             return url_for('my_types.show', my_type_id=o.guid)


    actor = (
        Session
        .query(Actor)
        .filter_by(first_name='Harry', last_name='Ball').one()
    pre_serialize = pez.Serialize(actor=actor)
    pre_serialize.register(MyType, MyTypeView)
    json.dumps(pre_serialize(Session.query(MyType).all()))
"""
from __future__ import unicode_literals

import inspect
import logging

from functools import wraps


__version__ = '0.0.2'
logger = logging.getLogger(__name__)


NONE = object()  # to distinguish from None (e.g. None is an accepted value)
SKIP = object()  # to indicate 'skip' behavior (e.g. when encountering cycles)


# specs

class _CreatedCountMixin(object):

    _created_count = 0

    def __init__(self):
        _CreatedCountMixin._created_count += 1
        self._count = _CreatedCountMixin._created_count


class field_type(_CreatedCountMixin):
    def __init__(self, type_):
        super(field_type, self).__init__()
        self.type = type_

    def __call__(self, f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            if args[0] == 'TELL_ME_YOUR_TYPE':
                return self.type
            return f(*args, **kwargs)
        setattr(wrapped_f, '_count', self._count)
        return wrapped_f


class Spec(_CreatedCountMixin):
    """
    Base for all class specs. If you don't need to parameterize a spec's
    behavior you can just write a function.

    It is not necessary to derive from this class (although it may be
    instructive to do so) only that instances of class specs be callable and
    accept two arguments: a context and an object.

    A spec is simply used to transform an object to some other object, possibly
    based on the context. That transform might be to simply pull an attribute
    off of the object and return its value or it might be a string formatting
    of a bunch of attributes.

    The return value of NONE (not None) is a significant special case. It
    indicates that the spec should be entirely filtered from (i.e. not included
    in) the transformed object.
    """
    def __init__(self):
        _CreatedCountMixin.__init__(self)

    def __call__(self, ctx, o):
        raise NotImplementedError


class Constant(Spec):
    """
    Simply returns the same value for all objects.

    `value`
        The value to return whenever this spec is called to transform an
        object.
    """
    def __init__(self, value):
        super(Constant, self).__init__()
        self.value = value

    def __call__(self, ctx, o):
        return self.value


class Field(Spec):
    """
    Resolves a particular field of an object (e.g. o.some.random.field). It
    will also check if this object is part is part of a cycle as indicated by
    context's `cycle` attribute and what to do about it as indicated by
    context's `cycle_default` attribute. If SKIP then the spec returns NONE
    indicating the spec should be ignored otherwise a ValueError is raised.

    `name`
        The name of the field to pull off the object and return. If name is
        None (the default) it is taken from context's `name` attribute. For
        details on how fields are parsed and how they resolve to the attribute
        value(s) of an object see `resolve_field`.

    `default`
        Determines how to handle the case where the field cannot be resolved
        for an object which should be either SKIP or NONE. If SKIP then the
        spec will return NONE when the field cannot be resolved otherwise it is
        NONE and an AttributeError is raised.
    """
    def __init__(self, name=None, default=SKIP):
        super(Field, self).__init__()
        self.name = name
        self.default = default

    def __call__(self, ctx, o):
        if ctx.cycle:
            if ctx.cycle_default is not SKIP:
                raise ValueError(
                    'Cycle detected for {0}, use cycle_default=SKIP to skip '
                    'cycles'.format(o))
            return NONE
        name = self.name if self.name else ctx.name
        return resolve_field(ctx, o, name, self.default)


class IntegerField(Field):
    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)


class StringField(Field):
    def __init__(self, *args, **kwargs):
        super(StringField, self).__init__(*args, **kwargs)


class BooleanField(Field):
    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)


class DateTimeField(Field):
    def __init__(self, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)


class ListField(Field):
    """
    List
    """

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)


class KVField(Field):
    """
    Key-Value mapping.
    """

    def __init__(self, *args, **kwargs):
        super(KVField, self).__init__(*args, **kwargs)


class RelationField(Field):
    def __init__(self, name, spec):
        super(RelationField, self).__init__(name)
        self.spec = spec


class DepthSelector(Field):
    def __init__(self, under_spec, over_spec, over_name=None, max_depth=None):
        super(DepthSelector, self).__init__()
        self.under_spec = under_spec
        self.over_spec = over_spec
        self.over_name = over_name
        self.max_depth = max_depth

    def __call__(self, ctx, o):
        max_depth = self.max_depth or ctx.max_depth
        if not max_depth:
            field = self.under_spec
        else:
            if ctx.depth <= max_depth:
                field = self.under_spec
            else:
                field = self.over_spec
                if self.over_name:
                    ctx.name = self.over_name
        return field(ctx, o)


class FormatField(StringField):
    """
    Resolves field(s) for an object and formats their value(s) as a string
    according to some format specification.

    Note that the format string must be of the string.format variety and all
    specifiers must be identified using a keyword. The mapping between
    format specifier keyword and object field is given by **kwargs.

    If any field cannot be resolved an AttributeError exception is raised. For
    details on how fields are parsed and how they resolve to attribute value(s)
    of an object see `resolve_field`.
    """
    def __init__(self, fmt, **kwargs):
        super(FormatField, self).__init__()
        self.fmt = fmt
        self.kwargs = kwargs

    def __call__(self, ctx, o):
        # TODO: allow kwargs to be 2-tuples, in which case [1] is the default
        #       to use when the field cannot be resolved
        kwargs = dict(
            (key, resolve_field(ctx, o, value, default=NONE))
            for key, value in self.kwargs.iteritems()
        )
        return self.fmt.format(**kwargs)


class ContextFilter(Spec):
    """
    Filters out another spec based on some context value.

    `spec`
        The spec to condtionally call if context filters are all True.

    `mask`
        What to return when any one of the context filters is False. Defaults
        to NONE.

    `filters`
        A mapping of context attribute names to values that must all be True
        for the referenced `spec` to be called.
    """
    def __init__(self, spec, mask=NONE, **filters):
        super(ContextFilter, self).__init__()
        self.spec = spec
        self.mask = mask
        self.filters = filters

    def __call__(self, ctx, o):
        for key, value in self.filters.iteritems():
            if getattr(ctx, key) != value:
                return self.mask
        return self.spec(ctx, o)


class FieldMapping(Spec):
    """
    A spec container used to map an object to a dictionary. It is mostly
    useless by itself, you need to derive from it and attach specs::

        class MyMapping(FieldMapping):
            a = Field()
            field1 = Field('a.b')
            field2 = FormatField('{a}...{b}', a='a', b='a.b')
            def hiya(ctx, o):
                return (o.a + o.b)**2
            def hiya2(ctx, o):
                ctx.name = 'could_be_dynamic'
                return (o.a + o.b)**3

    By default a contained field spec will assume the corresponding attribute
    name so you needn't explicitly provide a field name for this case::

        a = Field()

    Additionally you can override the name of a spec in the resulting mapping
    which can be useful if the mapping name is dynamic::

         def hiya2(ctx, o):
            ctx.name = 'could_be_dynamic'
            return (o.a + o.b)**3

    Note that if a contained spec returns NONE it is not included in the
    mapping.
    """
    @property
    def fields(self):
        return get_fields_class(self)

    def __call__(self, ctx, o):
        if ctx.max_depth and ctx.depth > ctx.max_depth:
            return NONE
        result = {}
        for name, spec in self.fields.iteritems():
            with ctx.push(o):
                ctx.name = name
                value = ctx(spec(ctx, o))
                if value is not NONE:
                    result[ctx.name] = value
        return result


def dict_spec(ctx, o):
    """
    Transforms a dictionary by applying specs to each value. Note that if the
    spec for a value returns NONE that key is not included in the transformed
    dictionary.
    """
    result = {}
    for key, value in o.iteritems():
        with ctx.push(o):
            ctx.name = key
            value = ctx(value)
            if value is not NONE:
                result[ctx.name] = value
    return result


def iterable_spec(ctx, o):
    """
    Transforms an iterable to a list by applying specs to each value. Note that
    if the spec for a value returns NONE it is not included in the resulting
    list.
    """
    result = []
    for value in o:
        with ctx.push(o):
            value = ctx(value)
            if value is not NONE:
                result.append(value)
    return result


# helpers

def resolve_field(ctx, o, name, default):
    """
    Resolves the field of an object to a value or values.

    :param ctx: The context.
    :param o: The object.
    :param name: The field to resolve. A field is one or more attributes
                 separated by a string provided by the context `separator`
                 attribute.
    :param default: How to respond when the field cannot be resolved.
                    If SKIP resolution is aborted and NONE is returned.
                    If NONE an AttributeError is raised.
                    Otherwise resolution is aborted and `default` is returned.

    Note that if an intermediate attribute is iterable then this function will
    expand the intermediate result into a list and recurse to resolve each of
    those sub-fields::

        >>> print resolve_field(ctx, o, 'as.b', NONE)
        ['1', 2, 'abc']
        >>> print resolve_field(ctx, o, 'a.bs.c.ds.e', NONE)
        [['1', '2', 45], [1], ['qwe', '111', True]]
    """
    reserved_prefixes = ['http://', 'https://']
    if [n for n in reserved_prefixes if name.startswith(n)]:
        return name
    cur_o = o
    name_parts = name.split(ctx.separator)
    for name_idx, name_part in enumerate(name_parts):
        cur_o = getattr(cur_o, name_part, NONE)
        if cur_o is NONE:
            if default is SKIP:
                return NONE
            elif default is not NONE:
                return default
            raise AttributeError('Could not resolve {0}.{1}'.format(o, name))
        if isinstance(cur_o, (list, tuple)) and name_idx < len(name_parts) - 1:
            name = ctx.separator.join(name_parts[name_idx + 1:])
            cur_o = [resolve_field(ctx, elm, name, default) for elm in cur_o]
            break
    return cur_o


def get_fields_class(o):
    result = {}
    predicate = lambda x: not inspect.isbuiltin(x)
    members = inspect.getmembers(o.__class__, predicate=predicate)
    for name, spec in members:
        if name.startswith('_') or not callable(spec):
            continue
        result[name] = spec
    return result


# serializer


class ContextFrame(object):
    """
    A frame used to house context attributes. A context
    is simply a stack of these frames. You should never need
    to access these directly. They are used by context for
    book keeping during the traversal of an object tree.

    `o`
        The object being transformed for the frame.
    """
    def __init__(self, o):
        self.o = o

    def __eq__(self, o):
        return id(self.o) == id(o)

    def __cmp__(self, o):
        return cmp(id(self.o), id(o))


class Context(object):

    def __init__(self, **kwargs):
        self.stack = []
        self.push(ContextFrame(NONE))
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @property
    def depth(self):
        return len(self.stack)

    def __setattr__(self, k, v):
        if k in ('stack'):
            self.__dict__[k] = v
        else:
            setattr(self.stack[-1], k, v)

    def __getattr__(self, k):
        for frame in reversed(self.stack):
            if hasattr(frame, k):
                return getattr(frame, k)
        raise AttributeError(
            "'{0}' object has no attribute '{1}'".format(
                self.__class__.__name__, k))

    def push(self, o):
        cycle = o in self.stack
        self.stack.append(ContextFrame(o))
        self.stack[-1].cycle = cycle
        return self

    def pop(self):
        self.stack.pop()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.pop()

    def __call__(self, o):
        raise NotImplementedError

    def get_spec(self, o):
        if isinstance(o, Spec):
            return o
        return None


class SerializerContext(Context):
    """
    Context for a transformation pass over an object tree. A context is simply
    a stack of frames with a few reserved attributes (e.g. o, name, cycle). As
    we traverse the object tree to apply spec transformations we push a frame
    as we encounter objects (aka nodes).

    You typically don't need to create these directly. That will be done for
    you by `Serializer` when you call it with an object to transform.

    Note that this interface is often used by transform specs (e.g. see
    `FieldMapping`, `Field`, `ContextFilter`) if they need to alter behavior
    based on the state of traversal or if they need to recurse into some
    structure.

    Here are reserved attributes of context you need to understand.

    `separator`
        This defaults to '.' and is the string we assume to separate attributes
        in a field string. There's probably no good reason to change this.

    `name`
        The intended name of a spec's transformed object. A spec can change an
        objects name by setting this attribute of the context. This is useful
        if the object name is dynamic.

    `cycle`
        Flag indicating whether the current object is part of a cycle in the
        object tree. Typically you want to abort traversal of a branch once
        it has been detected as a cycle as shown in `Field`. Note that it is
        entirely up to the spec on how to handle cycles.

    `cycle_default`
        Either SKIP, NONE or any other value indicating what to do when a cycle
        is encountered. SKIP simply aborts traversal of the branch returning
        NONE to indicate that the spec should be filtered from the transformed
        object tree while a value of NONE proceeds with the traversal. Any
        other value aborts just like SKIP but will be returned rather than
        NONE.

    `max_depth`
        Maximum depth into the tree to traverse. If None then there is no
        limit to traversal depth otherwise traversal will be limited to the
        this value specified. During traversal the current depth accessible via
        `Context.depth`. Note that how to enforce depth limits is entirely up
        to the spec.

    You can specify any other context attributes you like when you create a
    context which will be set on the base context frame.

    All context attributes are tied to the current frame. If an attribute is
    not defined for the current frame it is simply inherited from the previous
    frame. If an attribute is set it is always set on the current frame. If an
    attribute does not exist for any frame in the stack an attempt to access it
    will raise the usual AttributeError. Once the context is popped all
    attributes assume their previous values.
    """
    def __init__(self, serializer, **kwargs):
        super(SerializerContext, self).__init__(**kwargs)
        self.serializer = serializer

    def __call__(self, o):
        return self.serializer.serialize(self, o)

    def serialize(self, ctx, o):
        return self.serializer.serialize(ctx, o)

    def __setattr__(self, k, v):
        if k in ('serializer', 'stack'):
            self.__dict__[k] = v
        else:
            setattr(self.stack[-1], k, v)

    def get_spec(self, o):
        return self.serializer.get_spec(o)


class Serializer(object):
    """
    Transforms an object tree by traversing it and applying specs
    (aka transformers) to each object encountered during traversal.

    An object is mapped to a transformer spec based on its type. If
    no such spec exists each parent class of the object's type is checked
    in order of decreasing specialization (i.e. in mro). If no spec is found
    the object is returned as is (i.e. identity transform) and traversal for
    that branch of the object tree terminates.

    External context values are provided when constructing an instance as
    kwargs which are applied to the context that is passed about when
    traversing the object tree.
    """
    def __init__(self, **kwargs):
        self.specs = {
            list: iterable_spec,
            tuple: iterable_spec,
            dict: dict_spec,
        }
        self.defaults = {
            'separator': '.',
            'cycle_default': NONE,
            'max_depth': None,
        }
        self.defaults.update(kwargs)

    def register(self, type_, spec):
        """
        Registers a transform spec for a type.
        """
        self.specs[type_] = spec

    def __call__(self, o, **kwargs):
        kwargs.update(
            (k, v) for k, v in self.defaults.iteritems() if k not in kwargs)
        ctx = SerializerContext(self, **kwargs)
        return traverse(ctx, o, _EvaluateTraversal())

    def serialize(self, ctx, o):
        spec = self.get_spec(o)
        return spec(ctx, o) if spec else o

    def get_spec(self, o):
        spec = None
        o_type = type(o)
        if o_type in self.specs:  # avoid inspect.getmro if possible
            spec = self.specs[o_type]
        else:
            clses = inspect.getmro(o_type)
            for cls in clses:
                if cls in self.specs:
                    spec = self.specs[cls]
                    break
        return spec


def traverse(ctx, view_or_o, traversal):
    if ctx.max_depth and ctx.depth > ctx.max_depth:
        return NONE
    result = NONE
    with traversal.enter_view(ctx, view_or_o) as vctx:
        spec = ctx.get_spec(view_or_o)
        if hasattr(spec, 'fields'):
            # TODO: do we want to decorate things like exceptions so that pez
            # doesn't choke without a default value?
            items = sorted(spec.fields.items(),
                           key=lambda x: getattr(x[1], '_count', 999))
            for name, field in items:
                with ctx.push(view_or_o):
                    ctx.name = name
                    traversal.visit_field(field, ctx, view_or_o, vctx)
        elif spec:
            return spec(ctx, view_or_o)
        else:
            return view_or_o
        result = traversal.result
    return result


class Traversal(object):

    class _ViewContext(object):

        def __init__(self, traversal, ctx, view, **kwargs):
            self.traversal = traversal
            self.ctx = ctx
            self.view = view
            self.kwargs = kwargs
            self.result = {}

        def __enter__(self):
            return self

        def __exit__(self, type_, value, traceback):
            self.traversal.exit_view(self.ctx, self.view)
            return self.result

        # Pass through attr lookups to the underlying Context object
        def __getattr__(self, name):
            if name not in ['__init__', '__enter__', '__exit__']:
                if name in self.kwargs:
                    return self.kwargs[name]
                return getattr(self.ctx, name)

        def __call__(self, *args, **kwargs):
            return self.ctx(*args, **kwargs)

    def __enter__(self):
        return self

    def enter_view(self, ctx, view, **kwargs):
        return self._ViewContext(self, ctx, view, **kwargs)

    @property
    def result(self):
        return NONE

    def exit_view(self, ctx, view):
        pass

    def __exit__(self, type_, value, traceback):
        pass

    def visit_field(self, spec, ctx, view, vctx):
        raise NotImplementedError


class _EvaluateTraversal(Traversal):

    @property
    def result(self):
        return self.ctx.result

    def enter_view(self, ctx, view):
        self.ctx = super(_EvaluateTraversal, self).enter_view(ctx, view)
        return self.ctx

    def visit_field(self, field, ctx, o, vctx):
        r = ctx(field(ctx, o))
        if r is not NONE:
            self.ctx.result[ctx.name] = r
        return r
