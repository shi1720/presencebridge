"""Exhaustive effect replay, independent SQLite oracle, SDK probes and token costs."""
import itertools,json,pathlib,sqlite3,csv,time,statistics,platform,importlib.metadata,hashlib,inspect
from copy import deepcopy
import tiktoken
from pydantic import BaseModel,create_model
from openai.lib._pydantic import to_strict_json_schema
from agents.strict_schema import ensure_strict_json_schema
from presencebridge import Codec
ROOT=pathlib.Path(__file__).resolve().parents[1]
ABSENT=object()
def obj(props,required=()):return dict(type='object',properties=props,required=list(required),additionalProperties=False)
def dump(x):return json.dumps(x,separators=(',',':'),ensure_ascii=False)

def sql_effect(before,patch):
 # JSON text per column preserves null/false/true and avoids Python bool equality.
 db=sqlite3.connect(':memory:');db.execute('CREATE TABLE record (key TEXT PRIMARY KEY, value TEXT)')
 db.executemany('INSERT INTO record VALUES (?,?)',[(k,dump(v)) for k,v in before.items()])
 # Source patch is the independent oracle: only keys actually in patch are updated.
 for k,v in patch.items():db.execute('UPDATE record SET value=? WHERE key=?',(dump(v),k))
 out={k:json.loads(v) for k,v in db.execute('SELECT key,value FROM record')};db.close();return out

def run():
 rows=[];counts={};timings=[]
 encs={n:tiktoken.get_encoding(n) for n in ['cl100k_base','o200k_base']}
 tokenrows=[]
 for n in range(1,7):
  keys=[f'f{i}' for i in range(n)];s=obj({k:{'type':['boolean','null']} for k in keys})
  codecs={m:Codec(s,m) for m in ['selective','tagged']}
  for case_id,states in enumerate(itertools.product([ABSENT,None,True,False],repeat=n)):
   source={k:v for k,v in zip(keys,states) if v is not ABSENT}
   wire={k:source.get(k) for k in keys}
   # These baseline adapters are explicit experimental policies, not SDK defaults.
   patches={'null_is_value':wire,'null_is_omit':{k:v for k,v in wire.items() if v is not None}}
   for mode,c in codecs.items():
    t=time.perf_counter_ns();patches[mode]=c.decode(c.encode(source));timings.append((time.perf_counter_ns()-t)/1000)
   before={k:True for k in keys};gold=sql_effect(before,source)
   for mode,p in patches.items():
    actual={**before,**p};ok=dump(actual)==dump(gold)
    # Insertion order differs when patch order differs; all constructed patches use keys order.
    ok=actual==gold
    rows.append(dict(n=n,case_id=case_id,mode=mode,exact_patch=p==source,effect_correct=ok))
   # Negative control: current values already null; action distinctions still differ,
   # but final-state agreement may conceal them.
   before_null={k:None for k in keys};gold_null=sql_effect(before_null,source)
   rows.append(dict(n=n,case_id=case_id,mode='null_is_value_null_state',exact_patch=wire==source,effect_correct={**before_null,**wire}==gold_null))
 # Payload cost: mix collision-free and collision-prone fields, fully enumerate
 # n=4 fields across three nullability patterns and all valid patches.
 for nullable in [0,2,4]:
  keys=['enabled','archived','notify','locked'];s=obj({k:{'type':['boolean','null'] if i<nullable else 'boolean'} for i,k in enumerate(keys)})
  codecs={m:Codec(s,m) for m in ['selective','tagged']}
  domains=[[ABSENT,None,True,False] if i<nullable else [ABSENT,True,False] for i in range(4)]
  for case_id,values in enumerate(itertools.product(*domains)):
   x={k:v for k,v in zip(keys,values) if v is not ABSENT}
   payloads={'source':x,'nullable':{k:x.get(k) for k in keys},**{m:c.encode(x) for m,c in codecs.items()}}
   for encoding,e in encs.items():
    for mode,y in payloads.items():tokenrows.append(dict(nullable_fields=nullable,case_id=case_id,encoding=encoding,mode=mode,tokens=len(e.encode(dump(y))),bytes=len(dump(y).encode())))
 for name,records in [('effect_replay',rows),('token_costs',tokenrows)]:
  with (ROOT/f'results/{name}.csv').open('w') as f:
   w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
 summary=[]
 for n in range(1,7):
  for mode in ['null_is_value','null_is_omit','selective','tagged','null_is_value_null_state']:
   rr=[r for r in rows if r['n']==n and r['mode']==mode]
   summary.append(dict(n=n,mode=mode,total=len(rr),effect_correct=sum(r['effect_correct'] for r in rr),exact_patch=sum(r['exact_patch'] for r in rr)))
 (ROOT/'results/effects_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 # Actual installed SDK conversion and Pydantic hydration, without hosted inference.
 class Update(BaseModel):
  note: str = 'existing-default'
  owner: str = 'default-owner'
 NullableUpdate=create_model('NullableUpdate', note=(__import__('typing').Optional[str],None), owner=(__import__('typing').Optional[str],None))
 probes=[]
 for model in [Update,NullableUpdate]:
  original=model.model_json_schema()
  for sdk,fn in [('openai',lambda s:to_strict_json_schema(model)),('agents',ensure_strict_json_schema)]:
   converted=fn(deepcopy(original))
   probe=dict(model=model.__name__,sdk=sdk,source_schema=original,wire_schema=converted,
              omitted_fields_set=sorted(model.model_validate({}).model_fields_set),
              null_fields_set=None,source_dump_unset=model.model_validate({}).model_dump(exclude_unset=True),
              source_dump_all=model.model_validate({}).model_dump())
   if model==NullableUpdate:
    v=model.model_validate({'note':None,'owner':None})
    probe.update(null_fields_set=sorted(v.model_fields_set),wire_dump_unset=v.model_dump(exclude_unset=True),wire_dump_none=v.model_dump(exclude_none=True))
   probes.append(probe)
 (ROOT/'results/sdk_probes.json').write_text(json.dumps(probes,indent=2)+'\n')
 env=dict(python=platform.python_version(),platform=platform.platform(),packages={p:importlib.metadata.version(p) for p in ['openai','openai-agents','pydantic','jsonschema','tiktoken','openapi-schema-validator']},sdk_sources={})
 for name,fn in [('openai',to_strict_json_schema),('agents',ensure_strict_json_schema)]:
  p=pathlib.Path(inspect.getfile(fn));env['sdk_sources'][name]=dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 env['timing_microseconds']={'median':statistics.median(timings),'p95':sorted(timings)[int(.95*len(timings))],'n':len(timings),'scope':'encode+decode with validation; in-process; observational only'}
 (ROOT/'results/environment.json').write_text(json.dumps(env,indent=2)+'\n')
 print(json.dumps(env,indent=2));print('effect rows',len(rows),'token rows',len(tokenrows))
if __name__=='__main__':run()
