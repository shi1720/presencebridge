import json,csv,pathlib,collections,statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
colors={'null_is_value':'#ba493d','null_is_omit':'#d6893a','selective':'#187d82','tagged':'#3457a0'}
rows=json.loads((ROOT/'results/effects_summary.json').read_text())
fig,ax=plt.subplots(figsize=(6.4,2.65))
for m,label,style in [('null_is_value','Forward null / drop null (same rate)','--o'),('selective','PresenceBridge / full tags','-s')]:
 rr=[r for r in rows if r['mode']==m];ax.plot([r['n'] for r in rr],[100*r['effect_correct']/r['total'] for r in rr],style,label=label,color=colors[m],lw=1.7,ms=4)
ax.set(xlabel='Optional nullable Boolean fields',ylabel='Correct final states (%)',ylim=(0,105),xticks=range(1,7));ax.grid(alpha=.18);ax.legend(frameon=False,fontsize=8,loc='lower left');fig.savefig(ROOT/'paper/effects.pdf');plt.close(fig)
tokens=list(csv.DictReader((ROOT/'results/token_costs.csv').open()));summary=[]
fig,axs=plt.subplots(1,2,figsize=(6.4,2.5),sharey=True)
for ax,enc in zip(axs,['cl100k_base','o200k_base']):
 for m,label in [('nullable','Nullable (lossy at c > 0)'),('selective','PresenceBridge'),('tagged','Full tags')]:
  vals=[]
  for n in [0,2,4]:
   rr=[int(r['tokens']) for r in tokens if r['mode']==m and r['encoding']==enc and int(r['nullable_fields'])==n]
   vals.append(statistics.mean(rr));summary.append(dict(encoding=enc,mode=m,nullable_fields=n,mean_tokens=statistics.mean(rr),cases=len(rr)))
  ax.plot([0,2,4],vals,'o-',ms=3,lw=1.5,label=label,color=colors.get(m,'#888888'))
 ax.set(title=enc,xlabel='Nullable fields out of four',xticks=[0,2,4]);ax.grid(alpha=.18)
axs[0].set_ylabel('Mean payload tokens');handles,labels=axs[1].get_legend_handles_labels();fig.legend(handles,labels,frameon=False,fontsize=7,ncol=3,loc='lower center');fig.tight_layout(rect=[0,.12,1,1]);fig.savefig(ROOT/'paper/tokens.pdf');plt.close(fig)
(ROOT/'results/token_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
fig,ax=plt.subplots(figsize=(6.4,2.4))
for n in [1,2,4,6]:
 p=np.linspace(0,1,101);ax.plot(p,100*(1-(1-p)/4)**n,label=f'{n} fields',lw=1.5)
ax.set(xlabel='Probability an initial field is already null',ylabel='Apparent correctness (%)',ylim=(0,105));ax.grid(alpha=.18);ax.legend(frameon=False,ncol=2,fontsize=8);fig.savefig(ROOT/'paper/state_masking.pdf');plt.close(fig)
print(json.dumps(summary,indent=2))
