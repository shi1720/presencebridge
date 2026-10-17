"""Presence-preserving codecs for a deliberately bounded JSON Schema fragment.

No API calls or writes occur in this module. Callers must validate authorization,
completion status and backend business rules independently before execution.
"""
from copy import deepcopy
from jsonschema import Draft202012Validator

ANNOTATIONS = {'title', 'description', 'default', 'examples', '$comment', '$schema'}
SCALAR_KEYS = {'type','enum','const','minimum','maximum','exclusiveMinimum',
               'exclusiveMaximum','multipleOf','minLength','maxLength','pattern'}
OBJECT_KEYS = {'type','properties','required','additionalProperties'}
ARRAY_KEYS = {'type','items','minItems','maxItems'}

class UnsupportedSchema(ValueError):
    pass


def normalize(schema):
    """Accept closed, finite-tree objects, homogeneous arrays and scalar constraints.

    Nullable single-branch anyOf is normalized; arbitrary unions, references,
    conditionals, dependencies and open maps are rejected, never approximated.
    """
    s = {k:deepcopy(v) for k,v in schema.items() if k not in ANNOTATIONS}
    if 'anyOf' in s:
        parts=s.pop('anyOf')
        if s or len(parts)!=2 or {'type':'null'} not in parts:
            raise UnsupportedSchema('Only a single type plus null anyOf is supported')
        other=next(p for p in parts if p!={'type':'null'})
        s=normalize(other)
        t=s['type'];s['type']=[t,'null'] if isinstance(t,str) else list(dict.fromkeys(t+['null']))
        if 'enum' in s and None not in s['enum']:s['enum'].append(None)
        if 'const' in s:raise UnsupportedSchema('nullable const union')
    t=s.get('type')
    ts=set(t if isinstance(t,list) else [t])
    base=ts-{'null'}
    if len(base)>1 or not ts<= {'object','array','string','integer','number','boolean','null'}:
        raise UnsupportedSchema('Require one explicit base type, optionally null')
    kind=next(iter(base),'null')
    allowed=OBJECT_KEYS if kind=='object' else ARRAY_KEYS if kind=='array' else SCALAR_KEYS
    if set(s)-allowed:raise UnsupportedSchema('Unsupported keywords: '+str(set(s)-allowed))
    if kind=='object':
        if s.get('additionalProperties') is not False:
            raise UnsupportedSchema('Object must explicitly disallow additional properties')
        props=s.get('properties',{})
        if not set(s.get('required',[]))<=set(props):raise UnsupportedSchema('Unknown required field')
        s['properties']={k:normalize(v) for k,v in props.items()}
    elif kind=='array':
        if not isinstance(s.get('items'),dict):raise UnsupportedSchema('Require homogeneous items')
        s['items']=normalize(s['items'])
    Draft202012Validator.check_schema(s)
    return s


def is_nullable(s):
    return Draft202012Validator(s).is_valid(None)


def kind_of(s):
    t=s['type'];return next((x for x in (t if isinstance(t,list) else [t]) if x!='null'),'null')


def null_union(s):
    return s if is_nullable(s) else {'anyOf':[s,{'type':'null'}]}


def tagged(s):
    return {'anyOf':[
        {'type':'object','properties':{'op':{'type':'string','enum':['omit']}},
         'required':['op'],'additionalProperties':False},
        {'type':'object','properties':{'op':{'type':'string','enum':['set']},'value':s},
         'required':['op','value'],'additionalProperties':False}]}


class Codec:
    def __init__(self, schema, mode='selective'):
        if mode not in ('selective','tagged'):raise ValueError(mode)
        self.source=normalize(schema);self.mode=mode
        self.wire=self._compile(self.source)
        self._source_validator=Draft202012Validator(self.source)
        self._wire_validator=Draft202012Validator(self.wire)

    def needs_tag(self,s):
        return self.mode=='tagged' or is_nullable(s)

    def _compile(self,s):
        out=deepcopy(s);kind=kind_of(s)
        if kind=='object':
            req=set(s.get('required',[]));props={}
            for k,v in s['properties'].items():
                w=self._compile(v)
                props[k]=w if k in req else tagged(w) if self.needs_tag(v) else null_union(w)
            out.update(properties=props,required=list(props))
        elif kind=='array':out['items']=self._compile(s['items'])
        return out

    def _encode(self,s,x):
        if x is None:return None
        kind=kind_of(s)
        if kind=='array':return [self._encode(s['items'],v) for v in x]
        if kind!='object':return deepcopy(x)
        out={};req=set(s.get('required',[]))
        for k,v in s['properties'].items():
            if k in req:out[k]=self._encode(v,x[k])
            elif self.needs_tag(v):
                out[k]={'op':'set','value':self._encode(v,x[k])} if k in x else {'op':'omit'}
            else:out[k]=self._encode(v,x[k]) if k in x else None
        return out

    def _decode(self,s,x):
        if x is None:return None
        kind=kind_of(s)
        if kind=='array':return [self._decode(s['items'],v) for v in x]
        if kind!='object':return deepcopy(x)
        out={};req=set(s.get('required',[]))
        for k,v in s['properties'].items():
            y=x[k]
            if k in req:out[k]=self._decode(v,y)
            elif self.needs_tag(v):
                if y['op']=='set':out[k]=self._decode(v,y['value'])
            elif y is not None:out[k]=self._decode(v,y)
        return out

    def encode(self, x):
        self._source_validator.validate(x)
        y=self._encode(self.source,x);self._wire_validator.validate(y);return y

    def decode(self, y):
        self._wire_validator.validate(y)
        x=self._decode(self.source,y);self._source_validator.validate(x);return x
