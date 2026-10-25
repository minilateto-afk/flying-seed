"""Reproduce the two flight-seed experiments separately.

Requires Python 3, numpy, matplotlib. Run beside seed_measurements.csv.
Page 14 contains wing-length data; page 13 contains original weight values.
The author confirmed weight units as g and standardized model specifications
and release speed/orientation on 2026-10-24. Model IDs/counts remain unspecified.
"""
from pathlib import Path
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

ROOT=Path(__file__).resolve().parent
with (ROOT/'seed_measurements.csv').open(encoding='utf-8') as f:
    records=list(csv.DictReader(f))

def analyze(experiment):
    rows=[r for r in records if r['experiment']==experiment]
    x=np.array([float(r['predictor_value']) for r in rows])
    t=np.array([float(r['time_s']) for r in rows])
    levels,counts=np.unique(x,return_counts=True)
    means=np.array([t[x==v].mean() for v in levels])
    sd=np.array([t[x==v].std(ddof=1) for v in levels])
    b=float(((x-x.mean())*(t-t.mean())).sum()/((x-x.mean())**2).sum())
    a=float(t.mean()-b*x.mean())
    X=np.column_stack([np.ones(len(x)),x])
    theta=np.linalg.lstsq(X,t,rcond=None)[0]
    Xg=np.column_stack([np.ones(len(levels)),levels])
    theta_group=np.linalg.lstsq(Xg,means,rcond=None)[0]
    assert len(rows)==15 and np.all(counts==5)
    assert np.allclose(theta,[a,b]) and np.allclose(theta_group,theta)
    residual=t-a-b*x
    mean_residual=means-a-b*levels
    sse=float(residual@residual);sst=float(((t-t.mean())**2).sum())
    mean_sse=float(mean_residual@mean_residual)
    mean_sst=float(((means-means.mean())**2).sum())
    within=float(sum(((t[x==v]-m)**2).sum() for v,m in zip(levels,means)))
    weighted=float((counts*mean_residual**2).sum())
    assert np.isclose(sse,within+weighted)
    assert np.allclose(X.T@residual,0,atol=1e-12)
    summary={
        'predictor_unit':rows[0]['predictor_unit'],
        'source_page':int(rows[0]['source_page']),
        'n_recorded_releases':len(t),'n_settings':len(levels),
        'n_independent_models':'not recorded','intercept_s':a,
        'slope_per_original_predictor_unit':b,
        'all_releases':{'SSE_s2':sse,'SST_s2':sst,'R2':1-sse/sst,
                        'in_sample_RMSE_s':float(np.sqrt(sse/len(t)))},
        'group_means':{'SSE_s2':mean_sse,'SST_s2':mean_sst,'R2':1-mean_sse/mean_sst},
        'within_setting_SS_s2':within,'weighted_means_residual_SS_s2':weighted,
        'groups':[{'predictor_value':float(v),'count':int(n),'mean_s':float(m),
                   'sample_sd_s':float(s),'fitted_s':float(a+b*v),
                   'mean_residual_s':float(r)}
                  for v,n,m,s,r in zip(levels,counts,means,sd,mean_residual)]}
    plot_data=(x,t,levels,means,sd,a,b,residual,mean_residual)
    return summary,plot_data

results={};plots={}
for experiment in ['wing_length','weight']:
    results[experiment],plots[experiment]=analyze(experiment)
summary={'experiments':results,'analysis':'separate one-predictor fits; no pooled fit',
         'author_clarification':{'date':'2026-10-24','weight_unit':'g',
         'model_specifications':'same specifications before manipulation',
         'release_controls':'height 259 cm; initial speed and orientation held consistent',
         'model_counts_and_assignment':'not specified'}}
(ROOT/'seed_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')

available={f.name for f in font_manager.fontManager.ttflist}
font=next((f for f in ['Noto Sans TC','Noto Sans CJK TC','Microsoft JhengHei'] if f in available),None)
plt.rcParams.update({'font.family':font or 'DejaVu Sans','font.size':10,
                     'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False})
if font:
    xlabels=['翅長（cm）','模型質量（g）']
    titles=['翅長實驗','重量實驗']
    time_label='滯空時間（s）';residual_label='殘差（s）'
    legend=['原始測量','最小平方直線','平均 ± 樣本標準差']
else:
    xlabels=['Wing length (cm)','Model mass (g)']
    titles=['Wing-length experiment','Weight experiment']
    time_label='Time aloft (s)';residual_label='Residual (s)'
    legend=['Recorded releases','Least-squares fit','Mean +/- sample SD']

for kind,filename in [('data','seed_figures.png'),('residual','seed_residuals.png')]:
    fig,axes=plt.subplots(1,2,figsize=(10.2,3.65),layout='constrained')
    for k,experiment in enumerate(['wing_length','weight']):
        x,t,levels,means,sd,a,b,residual,mean_residual=plots[experiment]
        ax=axes[k];pad=(levels[-1]-levels[0])*.08
        if kind=='data':
            ax.scatter(x,t,s=28,color='#486b8a',alpha=.75,label=legend[0],zorder=3)
            grid=np.linspace(levels[0],levels[-1],200)
            ax.plot(grid,a+b*grid,color='#202020',lw=1.4,label=legend[1])
            ax.errorbar(levels,means,yerr=sd,fmt='s',color='#b16b31',capsize=4,
                         markersize=5,label=legend[2],zorder=4)
            ax.set(ylabel=time_label,ylim=(1.3,2.78))
            if k==0:ax.legend(frameon=False,fontsize=8.3,loc='upper left')
        else:
            ax.axhline(0,color='#202020',lw=1)
            ax.scatter(x,residual,s=28,color='#486b8a',alpha=.8,zorder=3)
            ax.scatter(levels,mean_residual,marker='s',s=32,color='#b16b31',zorder=4)
            ax.set(ylabel=residual_label,ylim=(-.31,.31))
        ax.set(xlabel=xlabels[k],title=titles[k],xticks=levels,
               xlim=(levels[0]-pad,levels[-1]+pad))
        ax.grid(axis='y',color='#dfdfdf',lw=.7)
    fig.savefig(ROOT/filename,dpi=220,facecolor='white');plt.close(fig)

print(json.dumps({e:{'a':v['intercept_s'],'b':v['slope_per_original_predictor_unit'],
                       'R2_all':v['all_releases']['R2'],'R2_means':v['group_means']['R2']}
                  for e,v in results.items()},ensure_ascii=False))
