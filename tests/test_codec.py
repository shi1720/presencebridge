import itertools, json, random
import pytest
from jsonschema import ValidationError
from presencebridge import Codec, UnsupportedSchema

ABSENT=object()
def obj(props,required=()):return dict(type='object',properties=props,required=list(required),additionalProperties=False)

@pytest.mark.parametrize('mode',['selective','tagged'])
def test_exhaustive_boolean_vectors(mode):
 for n in range(1,6):
  c=Codec(obj({f'f{i}':{'type':['boolean','null']} for i in range(n)}),mode)
  for states in itertools.product([ABSENT,None,True,False],repeat=n):
   x={f'f{i}':v for i,v in enumerate(states) if v is not ABSENT}
   assert c.decode(json.loads(json.dumps(c.encode(x))))==x

@pytest.mark.parametrize('seed',range(20))
def test_nested_roundtrip(seed):
 r=random.Random(seed)
 s=obj({'id':{'type':'integer'},'settings':obj({'memo':{'type':['string','null']},'enabled':{'type':'boolean'}}),'items':{'type':'array','items':obj({'label':{'type':['string','null']},'n':{'type':'integer'}})}},['id'])
 for mode in ['selective','tagged']:
  c=Codec(s,mode)
  for _ in range(50):
   x={'id':r.randrange(100)}
   if r.random()<.8:x['settings']={k:v for k,v in [('memo',r.choice([None,'','λ'])),('enabled',r.choice([True,False]))] if r.random()<.6}
   if r.random()<.8:x['items']=[{k:v for k,v in [('label',r.choice([None,'','"op":"omit"'])),('n',r.randrange(10))] if r.random()<.6} for _ in range(r.randrange(4))]
   assert c.decode(c.encode(x))==x

def test_rejects_malformed_tags():
 c=Codec(obj({'a':{'type':['string','null']}}))
 for x in [{},{'a':None},{'a':{'op':'omit','value':None}},{'a':{'op':'set'}},{'a':{'op':'set','value':7}},{'a':{'op':'omit'},'extra':True}]:
  with pytest.raises(ValidationError):c.decode(x)

def test_source_not_coerced():
 c=Codec(obj({'a':{'type':'integer'}},['a']))
 for x in [{},{'a':'1'},{'a':True},{'a':None},{'a':1,'b':0}]:
  with pytest.raises(ValidationError):c.encode(x)

def test_rejects_unsupported():
 for s in [{},{'type':'object','properties':{}},{'type':'string','format':'date'}, {'$ref':'#/$defs/A'}, {'anyOf':[{'type':'string'},{'type':'integer'}]}]:
  with pytest.raises(UnsupportedSchema):Codec(s)

def test_nullable_object_and_array_and_required_null():
 s=obj({'r':{'type':'null'},'o':{'anyOf':[obj({'x':{'type':['string','null']}}),{'type':'null'}]},'a':{'type':['array','null'],'items':{'type':'boolean'}}},['r'])
 c=Codec(s)
 for x in [{'r':None},{'r':None,'o':None,'a':None},{'r':None,'o':{'x':None},'a':[]},{'r':None,'o':{},'a':[True]}]:assert c.decode(c.encode(x))==x
