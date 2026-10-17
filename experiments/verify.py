"""Independent finite enumerations of fibre sizes and state-coverage formulae."""
import itertools,json,pathlib,collections,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
M='MISSING'
fibre_checks=0;state_checks=0
fibre_rows=[];state_rows=[]
for n in range(1,8):
 groups=collections.Counter()
 for x in itertools.product([M,None,True,False],repeat=n):
  y=tuple(None if a==M else a for a in x);groups[y]+=1
 for y,size in groups.items():
  c=sum(a is None for a in y);assert size==2**c;fibre_checks+=1
  fibre_rows.append(dict(n=n,null_coordinates=c,fibre_size=size))
# Independent source/normalized transitions; no calls to the library or SQL oracle.
for n in range(1,6):
 sources=list(itertools.product([M,None,True,False],repeat=n))
 for initial in itertools.product([None,True],repeat=n):
  k=sum(a is not None for a in initial)
  for policy in ['null_is_value','null_is_omit']:
   correct=0
   for x in sources:
    target=tuple(b if a==M else a for b,a in zip(initial,x))
    y=tuple(None if a==M else a for a in x)
    got=tuple((b if a is None else a) if policy=='null_is_omit' else a for b,a in zip(initial,y))
    correct+=got==target
   expected=3**k*4**(n-k)
   assert correct==expected;state_checks+=1
   state_rows.append(dict(n=n,nonnull_initial=k,mode=policy,total=len(sources),correct=correct))
out=dict(fibre_checks=fibre_checks,state_checks=state_checks,status='all assertions passed')
(ROOT/'results/independent_verification.json').write_text(json.dumps(out,indent=2)+'\n')
(ROOT/'results/state_coverage.json').write_text(json.dumps(state_rows,indent=2)+'\n')
print(json.dumps(out))
