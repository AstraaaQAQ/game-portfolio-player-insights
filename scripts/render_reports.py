"""Render the two static portfolio walkthroughs from audited aggregate CSVs.

Requires matplotlib and reportlab. No private review text is used in the PDF.
The original Power BI files are historical sources, not edited by this script.
"""
from pathlib import Path
from io import BytesIO
from html import escape
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
OUT=ROOT/'dashboards'
W,H=996,576
GROUPS=['0-10h','10-50h','50-100h','100-300h','300-1000h','1000h+']
COLORS=['#a1232a','#b88b12','#60507e','#3b8091','#6c8558']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'axes.axisbelow':True,'axes.labelcolor':'#353535','xtick.color':'#555555','ytick.color':'#555555'})


def para(c,text,x,y,width,size=12,leading=None,color='#262626'):
    p=Paragraph(text,ParagraphStyle('p',fontName='Helvetica',fontSize=size,leading=leading or size*1.38,textColor=HexColor(color),spaceAfter=0))
    _,height=p.wrap(width,1000)
    if y-height<34:
        raise ValueError(f'Text overflows page: {text[:70]}')
    p.drawOn(c,x,y-height)
    return y-height


def header(c,title,subtitle,page,total):
    c.setFillColor(HexColor('#252525'))
    c.setFont('Helvetica-Bold',25)
    c.drawCentredString(W/2,H-48,title)
    c.setFont('Helvetica',10)
    c.setFillColor(HexColor('#646464'))
    c.drawCentredString(W/2,H-70,subtitle)
    c.setStrokeColor(HexColor('#d8d8d8'))
    c.line(36,30,W-36,30)
    c.setFont('Helvetica',8)
    c.drawString(36,17,'Yuxuan Chi (Astra) | Static report rebuilt from audited tables | 14 Oct 2026')
    c.drawRightString(W-36,17,f'{page} / {total}')


def figure(c,fig,x=45,y=178,width=906,height=304):
    stream=BytesIO()
    fig.savefig(stream,format='png',dpi=180,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    stream.seek(0)
    c.drawImage(ImageReader(stream),x,y,width=width,height=height,preserveAspectRatio=True,anchor='c',mask='auto')


def table(c,rows,x,top,widths,font=11):
    t=Table(rows,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),font),('TEXTCOLOR',(0,0),(-1,-1),HexColor('#252525')),('BACKGROUND',(0,0),(-1,0),HexColor('#eeeeee')),('LINEBELOW',(0,0),(-1,0),.7,HexColor('#b8b8b8')),('LINEBELOW',(0,-1),(-1,-1),.6,HexColor('#d8d8d8')),('ALIGN',(1,1),(-1,-1),'RIGHT'),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    _,height=t.wrap(sum(widths),1000)
    if top-height<34: raise ValueError('Table overflows page')
    t.drawOn(c,x,top-height)
    return top-height


def findings(c,text,note=None):
    y=para(c,'<b>What the sample shows</b>',45,154,906,12)
    y=para(c,text,45,y-8,906,11.3)
    if note:
        para(c,note,45,y-10,906,9.5,color='#555555')


def render_case1():
    life=pd.read_csv(DATA/'lifecycle_risk_map_pct.csv')
    provenance=json.loads((DATA/'case1_provenance.json').read_text())
    c=canvas.Canvas(str(OUT/'Steam Review Diagnostics by Playtime Stage.pdf'),pagesize=(W,H))
    c.setTitle('Steam Review Diagnostics by Playtime Stage')
    c.setAuthor('Yuxuan Chi (Astra)')
    header(c,'Steam Review Diagnostics by Playtime Stage','Apex Legends, Icarus and Path of Exile | Frozen review snapshots',1,11)
    y=para(c,'<b>Question:</b> How do recommendation rates and theme mentions differ between reviewers with different amounts of cumulative playtime?',64,466,868,16)
    y=para(c,'<b>My contribution:</b> review analysis, Python aggregation, dashboard interpretation and documented product hypotheses. The revised report reconciles its counts and rates to the same frozen review cohort for each game.',64,y-24,868,13)
    rows=[['Game','All reviews','Negative reviews','Positive reviews with 50h+']]
    for game,p in provenance['games'].items(): rows.append([game,f"{p['review_count']:,}",f"{p['negative_count']:,}",f"{p['positive_50h_count']:,}"])
    y=table(c,rows,64,y-24,[235,145,175,313],11)
    y=para(c,'<b>Measure:</b> Steam recommendation label. Negative rate = negative reviews / all reviews in the same game and playtime group. Playtime means cumulative hours at collection, not hours when the review was posted.',64,y-24,868,12)
    para(c,'<b>Interpretation:</b> These are comparisons between self-selected reviewers. They do not measure retention, churn, conversion or how individual players change over time. Theme matches identify mentions, not the sentiment of each feature.',64,y-18,868,12)
    c.showPage()
    game_reads={
        'apex':('Apex Legends','The 0-10h group has 63 negative reviews out of 138 (45.65%). The lowest negative rate is 21.90% at 10-50h; the 1000h+ group is 50.00%. This motivates investigating concerns voiced by highly experienced reviewers, without attributing the difference to time spent playing.'),
        'icarus':('Icarus','The highest negative rate is 59.66% in the 0-10h group (71/119). Groups above 50h range from 11.09% to 19.49%. These differences support investigating first-session expectations and perceived value; they do not show that players left the game.'),
        'poe':('Path of Exile','The 0-10h group has a 40.91% negative rate (36/88). Later groups range from 13.66% to 16.61%. This supports exploring access to complex systems as a research question; the review sample cannot establish when a complaint first emerged.'),
    }
    for idx,(slug,(game,read)) in enumerate(game_reads.items()):
        frame=life[life.game.eq(game)].sort_values('sort_order')
        header(c,f'{game}: recommendation rates','Cumulative playtime at collection | Each bar shows its own sample size',2+idx*3,11)
        fig,ax=plt.subplots(figsize=(11.9,3.45))
        xs=np.arange(6); rates=frame.negative_rate.to_numpy()*100
        ax.bar(xs,rates,width=.56,color=COLORS[0],label='Not recommended')
        ax.bar(xs,100-rates,bottom=rates,width=.56,color='#dddddd',label='Recommended')
        for x,row in zip(xs,frame.itertuples()):
            ax.text(x,row.negative_rate*50,f'{row.negative_rate:.2%}',ha='center',va='center',color='white',fontweight='bold',fontsize=11)
            ax.text(x,104,f'n = {row.review_count}',ha='center',fontsize=9)
        ax.set_xticks(xs,GROUPS);ax.set_ylim(0,115);ax.set_yticks([0,25,50,75,100],[f'{x}%' for x in [0,25,50,75,100]])
        ax.set_ylabel('Share of reviews');ax.legend(loc='upper center',bbox_to_anchor=(.5,1.15),ncol=2,frameon=False);ax.grid(axis='y',alpha=.2)
        fig.tight_layout();figure(c,fig)
        findings(c,read,'Groups use lower-inclusive, upper-exclusive boundaries: exactly 50h belongs to 50-100h. Small groups should be read cautiously.')
        c.showPage()
        themes=pd.read_csv(DATA/f'{slug}_theme_by_playtime.csv')
        summary=pd.read_csv(DATA/f'{slug}_theme_pattern_summary.csv').sort_values('overall_rate_pct')
        header(c,f'{game}: themes in negative reviews','Explicit dictionary v2 | A review can mention several themes',3+idx*3,11)
        fig,(ax,bar)=plt.subplots(1,2,figsize=(12,3.45),gridspec_kw={'width_ratios':[1.3,1]})
        for col,(theme,rows) in zip(COLORS,themes.groupby('theme',sort=False)):
            rows=rows.sort_values('sort_order')
            ax.plot(np.arange(6),rows.mention_rate_pct,marker='o',color=col,label=theme.replace('_',' / '),lw=1.7)
        ax.set_xticks(np.arange(6),GROUPS,rotation=15);ax.set_ylabel('Mention rate within negative reviews (%)');ax.grid(axis='y',alpha=.2)
        ax.legend(loc='upper center',bbox_to_anchor=(.5,1.35),ncol=2,frameon=False,fontsize=8)
        bar.barh(summary.theme_display,summary.overall_rate_pct,color=COLORS[0]);bar.set_xlabel('Mentions / all negative reviews (%)');bar.grid(axis='x',alpha=.2)
        bar.tick_params(axis='y',labelsize=8)
        for i,row in enumerate(summary.itertuples()): bar.text(row.overall_rate_pct+.5,i,f'{row.overall_rate_pct:.1f}%',va='center',fontsize=9)
        bar.set_xlim(0,max(summary.overall_rate_pct)*1.3)
        fig.tight_layout(w_pad=3);figure(c,fig,y=184,height=300)
        top=summary.iloc[-1]
        denominators=', '.join(str(x) for x in frame.negative_count)
        findings(c,f'The most frequently matched theme is <b>{escape(top.theme_display)}</b>: {int(top.theme_mentions)} of {int(top.negative_reviews)} negative reviews ({top.overall_rate_pct:.2f}%). The overall chart weights by review count; it is not an unweighted mean of the six stage percentages.',f'Negative-review denominators, left to right: {denominators}. A stage peak based on few reviews is exploratory. Keyword matches can include praise, negation or sarcasm.')
        c.showPage()
        cmp=pd.read_csv(DATA/f'{slug}_attachment_vs_friction_signals.csv')
        header(c,f'{game}: positive and negative review language','50h+ positive reviews compared with negative reviews at all playtimes',4+idx*3,11)
        fig,ax=plt.subplots(figsize=(11.9,3.6))
        yy=np.arange(len(cmp));pos=cmp.stayed_positive_mention_rate_pct;neg=cmp.negative_mention_rate_pct
        ax.hlines(yy,np.minimum(pos,neg),np.maximum(pos,neg),color='#cccccc',lw=2)
        ax.scatter(pos,yy,color=COLORS[3],label=f'50h+ positive (n={int(cmp.stayed_positive_reviews.iloc[0])})',zorder=3)
        ax.scatter(neg,yy,color=COLORS[0],label=f'Negative, all hours (n={int(cmp.negative_reviews.iloc[0])})',zorder=3)
        ax.set_yticks(yy,cmp.theme);ax.invert_yaxis();ax.set_xlabel('Reviews mentioning the theme (%)');ax.grid(axis='x',alpha=.2)
        ax.legend(loc='upper center',bbox_to_anchor=(.6,1.14),ncol=2,frameon=False,fontsize=9)
        fig.tight_layout();figure(c,fig)
        diff=(neg-pos).to_numpy();pick=cmp.iloc[int(np.argmax(diff))]
        findings(c,f'<b>{escape(pick.theme)}</b> is mentioned in {pick.negative_mention_rate_pct:.2f}% of negative reviews and {pick.stayed_positive_mention_rate_pct:.2f}% of 50h+ positive reviews. This is a useful topic for follow-up reading, not a measured cause of dissatisfaction.',"The two groups differ in both recommendation label and playtime eligibility. '50h+ positive' is a descriptive subset, not evidence that a player stayed active or stayed positive over time.")
        c.showPage()
    header(c,'Findings and next questions','Observed differences first; product and marketing ideas require testing',11,11)
    rows=[['Game']+GROUPS]
    for game in game_reads.values():
        f=life[life.game.eq(game[0])].sort_values('sort_order')
        rows.append([game[0]]+[f'{r:.2%}' for r in f.negative_rate])
    y=table(c,rows,45,475,[180]+[121]*6,11)
    y=para(c,'<b>Apex Legends:</b> investigate fairness, technical reliability and ranked-system expectations in experienced reviewers. The sample shows differing recommendation rates; it does not establish trust erosion in the same people over time.',45,y-24,906,12)
    y=para(c,'<b>Icarus:</b> investigate how early-session guidance and price/DLC expectations relate to expressed dissatisfaction. Test clearer product messaging or onboarding with new users before claiming an effect.',45,y-17,906,12)
    y=para(c,'<b>Path of Exile:</b> investigate technical access and explanations of complex systems. A guide or creator-led introduction is a testable marketing/content hypothesis, not a validated conversion lever.',45,y-17,906,12)
    para(c,'<b>Limits:</b> historical English-review snapshots, self-selection and keyword rules. The report contains no retention telemetry, causal experiment or campaign outcome. Rebuild inputs and hashes are recorded in data/case1_provenance.json; method and revisions are documented in docs/case1-method.md.',45,y-22,906,10.5)
    c.save()


def render_case2():
    overall=pd.read_csv(DATA/'narrative_overall_combined_1.csv')
    comp=pd.read_csv(DATA/'narrative_vs_nonnarrative.csv')
    cats=pd.read_csv(DATA/'narrative_by_category_combined.csv')
    lift=pd.read_csv(DATA/'narrative_lift_by_playtime_stable.csv')
    games=['God of War','RDR2','The Witcher 3']
    c=canvas.Canvas(str(OUT/'Narrative as a Satisfaction Buffer.pdf'),pagesize=(W,H))
    c.setTitle('Narrative as a Satisfaction Buffer: Review Associations')
    c.setAuthor('Yuxuan Chi (Astra)')
    header(c,'Narrative as a Satisfaction Buffer','Review associations in God of War, Red Dead Redemption 2 and The Witcher 3',1,5)
    y=para(c,'Narrative mentions were associated with higher positive recommendation rates.',64,467,868,20)
    y=para(c,'<b>Scope:</b> 5,000 English Steam reviews per game, each with at least 10 cumulative hours of playtime and 20 English words. The 15,000-review snapshot is fixed for this analysis.',64,y-28,868,13)
    y=para(c,'<b>My contribution:</b> review filtering, explicit narrative keyword categories, Python aggregation, dashboard comparisons and interpretation for game and content teams.',64,y-21,868,13)
    y=para(c,'<b>Narrative lift</b> means the positive recommendation-rate gap between reviews with narrative keywords and reviews without those keywords. <b>Compensation signal</b> means narrative mentions in reviews that also contain potential gameplay-issue keywords; it is a co-occurrence pattern.',64,y-21,868,13)
    y=para(c,'<b>Five categories:</b> story and quest engagement; character and relationship attachment; world and genre immersion; emotional payoff; theme and meaning.',64,y-21,868,13)
    para(c,'<b>Limit:</b> "satisfaction buffer" is a research hypothesis. These associations do not demonstrate retention, re-engagement, a causal narrative effect or improved marketing performance. Keyword presence does not prove praise, criticism or actual exposure to a story beat.',64,y-21,868,12)
    c.showPage()
    header(c,'Narrative themes mentioned by reviewers','Category mention rates | Denominator: 5,000 reviews per game',2,5)
    category_order=list(cats.category.unique())
    fig,ax=plt.subplots(figsize=(12,3.65));xx=np.arange(len(category_order));width=.24
    for i,game in enumerate(games):
        f=cats[cats.game.eq(game)].set_index('category').loc[category_order]
        vals=f.mention_rate.to_numpy()
        bars=ax.bar(xx+(i-1)*width,vals,width,label=game,color=COLORS[i])
        ax.bar_label(bars,fmt='%.1f',fontsize=8,padding=3)
    labels=['Story / quest','Character / relationship','World / genre','Emotional payoff','Theme / meaning']
    labelmap=dict(zip(['Story & Quest Engagement','Character & Relationship Attachment','World & Genre Immersion','Emotional Payoff','Theme & Meaning'],labels))
    ax.set_xticks(xx,[labelmap[k] for k in category_order]);ax.set_ylabel('Review mention rate (%)');ax.set_ylim(0,75);ax.grid(axis='y',alpha=.2);ax.legend(frameon=False,ncol=3,loc='upper center',bbox_to_anchor=(.5,1.15))
    fig.tight_layout();figure(c,fig)
    findings(c,'Story and quest keywords are the most frequent category in each sample. God of War has a relatively prominent character category; The Witcher 3 has a strong world/genre category. These profiles describe what reviewers mention, rather than the contribution of each asset to satisfaction.','Categories overlap. Game-specific terms are included in the dictionary, so cross-game comparisons depend partly on coding choices.')
    c.showPage()
    header(c,'Positive recommendation rates and narrative mentions','Observed percentage-point gaps; no causal attribution',3,5)
    fig,(ax,gap)=plt.subplots(1,2,figsize=(12,3.5),gridspec_kw={'width_ratios':[1.5,1]})
    yy=np.arange(3);gaps=[]
    for typ,shift,col in [('Narrative Reviews',-.16,COLORS[0]),('Non-Narrative Reviews',.16,'#a9a9a9')]:
        vals=[comp[comp.game.eq(g)&comp.type.eq(typ)].positive_rate.iloc[0] for g in games]
        bars=ax.barh(yy+shift,vals,height=.3,label=typ,color=col)
        ax.bar_label(bars,fmt='%.2f%%',padding=3,fontsize=9)
    for g in games:
        r=overall[overall.game.eq(g)].iloc[0];gaps.append(r.narrative_positive_rate-r.non_narrative_positive_rate)
    ax.set_yticks(yy,games);ax.invert_yaxis();ax.set_xlim(0,110);ax.set_xlabel('Positive recommendation rate (%)');ax.grid(axis='x',alpha=.2);ax.legend(frameon=False,fontsize=9,loc='upper center',bbox_to_anchor=(.5,1.15),ncol=2)
    bars=gap.barh(yy,gaps,color=COLORS[2]);gap.bar_label(bars,fmt='%.2f pp',padding=4,fontsize=10);gap.set_yticks(yy,games);gap.invert_yaxis();gap.set_xlim(0,15);gap.set_xlabel('Narrative minus non-narrative (pp)');gap.grid(axis='x',alpha=.2)
    fig.tight_layout(w_pad=3);figure(c,fig)
    findings(c,'Narrative-mentioning reviews have higher positive recommendation rates in all three samples. RDR2 has the largest observed gap (about 11.8 percentage points), followed by God of War (5.3) and The Witcher 3 (3.0).','Reviewers who mention narrative may differ in many other ways. The comparison does not isolate narrative quality or prove that narrative offsets mechanical problems.')
    c.showPage()
    header(c,'Narrative association by playtime group','Cumulative hours at collection | Cross-sectional reviewer groups',4,5)
    fig,ax=plt.subplots(figsize=(11.5,3.3));labels=['10-50h','50-100h','100-300h']
    for game,col in zip(games,COLORS):
        f=lift[lift.game.eq(game)].sort_values('playtime_sort')
        ax.plot(labels,f.narrative_lift_pp,color=col,marker='o',label=game,lw=2)
        for x,v in enumerate(f.narrative_lift_pp): ax.annotate(f'{v:.2f}',(x,v),xytext=(0,8 if game!='The Witcher 3' else -16),textcoords='offset points',ha='center',fontsize=9)
    ax.set_ylim(-2,20);ax.set_ylabel('Positive-rate gap (percentage points)');ax.grid(axis='y',alpha=.2);ax.legend(frameon=False,ncol=3,loc='upper center',bbox_to_anchor=(.5,1.17))
    fig.tight_layout();figure(c,fig,y=197,height=278)
    findings(c,'RDR2 has a 16.19 pp gap at 10-50h, 5.54 pp at 50-100h and 10.92 pp at 100-300h. These are different groups of reviewers. The rise in the last group cannot establish re-engagement, an emotional payoff effect or the timing of a specific story event.','Later groups are omitted because their samples are smaller. Narrative/non-narrative subgroup counts are published in narrative_lift_by_playtime_stable.csv; the filename does not imply a formal statistical stability test.')
    c.showPage()
    header(c,'Implications to test','Use the observed patterns to generate research and content hypotheses',5,5)
    y=para(c,'<b>Observed:</b> Narrative mentions were associated with higher positive recommendation rates. Story, character and world categories have different mention profiles across the three samples.',54,469,888,15)
    y=para(c,'<b>God of War - character framing:</b> compare a relationship-focused content concept with a mechanics-focused concept. Assess whether the intended audience understands and values the central relationship; do not infer campaign effectiveness from review mentions.',54,y-24,888,12.5)
    y=para(c,'<b>RDR2 - emotional framing:</b> test character and emotional stakes as communication hypotheses. The review data cannot identify when players reached an emotional payoff or show that a story beat brought them back.',54,y-21,888,12.5)
    y=para(c,'<b>The Witcher 3 - world framing:</b> explore content that communicates world identity and meaningful quest choices. High mention rates justify further investigation, not a proven allocation of production or marketing resources.',54,y-21,888,12.5)
    y=para(c,'<b>Validation plan:</b> define an audience, compare content variants, preselect an outcome such as qualified click-through or stated interest, and record uncertainty. These are proposed tests; no campaign or experiment was conducted in this portfolio case.',54,y-21,888,12.5)
    para(c,'<b>Method limits:</b> self-selected English reviews; keyword-based coding; cumulative hours rather than tracked progression; no causal controls, retention telemetry or purchase conversion outcomes. Supporting tables and reproducible code are linked from the repository homepage.',54,y-23,888,11)
    c.save()


if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    render_case1()
    render_case2()
    print('Rendered Case 1 (11 pages) and Case 2 (5 pages).')
