"""Pinned OpenAPI census. Counts exposure, not failures or PATCH semantics."""
import json, pathlib, hashlib, requests, csv, sys, warnings
from openapi_schema_validator import OAS30Validator
with warnings.catch_warnings():
 warnings.simplefilter("ignore", DeprecationWarning)
 from jsonschema import RefResolver
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCES=json.loads((ROOT/'data/sources.json').read_text())

def deref(s,doc,seen=()):
 if '$ref' not in s:return s
 ref=s['$ref']
 if ref in seen or not ref.startswith('#/'):raise ValueError(ref)
 out=doc
 for part in ref[2:].split('/'):out=out[part.replace('~1','/').replace('~0','~')]
 return {**deref(out,doc,seen+(ref,)),**{k:v for k,v in s.items() if k!='$ref'}}

def null_status(s,doc):
 s=deref(s,doc)
 # Deliberately use explicit OpenAPI null declarations, rather than treating an
 # absent type as permissive. This is a lower-bound exposure audit.
 return bool(s.get('nullable')) or s.get('type')=='null' or ('null' in s.get('type',[]) if isinstance(s.get('type'),list) else False) or any(null_status(x,doc) for x in s.get('anyOf',[])+s.get('oneOf',[]))

def main():
 cache=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'.cache'
 cache.mkdir(exist_ok=True)
 fields=[];summary=[]
 for meta in SOURCES:
  url=f"https://raw.githubusercontent.com/{meta['repository']}/{meta['commit']}/{meta['path']}"
  target=cache/(meta['name']+'.json')
  if not target.exists():
   r=requests.get(url,timeout=120);r.raise_for_status();target.write_bytes(r.content)
  raw=target.read_bytes()
  expected=meta['sha256']
  if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Source hash mismatch: '+meta['name'])
  doc=json.loads(raw)
  meta.update(url=url,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
  stats=dict(source=meta['name'],operations=0,body_operations=0,object_operations=0,fields=0,optional=0,optional_null_marked=0,optional_null_accepted=0,marked_null_rejected=0,operations_exposed=0,patch_operations=0,patch_exposed=0,skipped_union_roots=0)
  for path,item in doc['paths'].items():
   for method,op in item.items():
    if method not in ('get','put','post','patch','delete','options','head','trace'):continue
    stats['operations']+=1
    if method=='patch':stats['patch_operations']+=1
    body=op.get('requestBody')
    if not body:continue
    stats['body_operations']+=1
    body=deref(body,doc);content=body.get('content',{})
    # JSON preferred, otherwise form encoding (Stripe); count operation once.
    media=next((m for m in ['application/json','application/x-www-form-urlencoded'] if m in content),None)
    if not media:continue
    schema=deref(content[media].get('schema',{}),doc)
    if 'properties' not in schema:
     stats['skipped_union_roots']+=1;continue
    stats['object_operations']+=1
    req=set(schema.get('required',[]));exposed=False
    for key,field in schema['properties'].items():
     f=deref(field,doc);optional=key not in req;nullable=null_status(f,doc)
     errors=list(OAS30Validator(f,resolver=RefResolver.from_schema(doc)).iter_errors(None)) if optional and nullable else []
     accepted=optional and nullable and not errors
     row=dict(source=meta['name'],method=method,path=path,operation=op.get('operationId',''),media=media,field=key,optional=optional,null_marker=nullable,marked_null_accepted=accepted,null_rejection_keywords=','.join(e.validator for e in errors),default_present='default' in f,description=f.get('description',''))
     fields.append(row);stats['fields']+=1;stats['optional']+=optional
     stats['optional_null_marked']+=optional and nullable
     stats['optional_null_accepted']+=accepted
     stats['marked_null_rejected']+=optional and nullable and bool(errors)
     exposed|=accepted
    stats['operations_exposed']+=exposed
    stats['patch_exposed']+=exposed and method=='patch'
  summary.append(stats)
 with (ROOT/'data/field_inventory.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields[0].keys());w.writeheader();w.writerows(fields)
 (ROOT/'data/sources.json').write_text(json.dumps(SOURCES,indent=2)+'\n')
 (ROOT/'results/census.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
