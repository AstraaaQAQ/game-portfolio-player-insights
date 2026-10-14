"""Validate public data contracts and local artifact links without private data."""
from pathlib import Path
import csv, json, math, re
from urllib.parse import unquote, urlsplit
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]


def rows(name):
    with (ROOT/'data'/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def near(a,b,tol=1e-9):
    assert abs(float(a)-float(b)) <= tol, (a,b)


def validate():
    life=rows('lifecycle_risk_map_pct.csv')
    assert len(life)==18
    keys={(r['game'],r['playtime_group']):r for r in life}
    assert len(keys)==18
    manifest=json.loads((ROOT/'data/case1_provenance.json').read_text())
    for r in life:
        n,neg,pos=[int(r[k]) for k in ['review_count','negative_count','positive_count']]
        assert n>0 and neg>=0 and pos>=0 and n==neg+pos
        near(r['negative_rate'],neg/n)
    for slug,game in [('apex','Apex Legends'),('icarus','Icarus'),('poe','Path of Exile')]:
        source=manifest['games'][game]
        assert sum(int(r['review_count']) for r in life if r['game']==game)==source['review_count']
        assert sum(int(r['negative_count']) for r in life if r['game']==game)==source['negative_count']
        themes=rows(f'{slug}_theme_by_playtime.csv')
        assert len(themes)==30
        for r in themes:
            n,mentions=int(r['negative_reviews']),int(r['theme_mentions'])
            assert n==int(keys[(game,r['playtime_group'])]['negative_count'])
            assert 0<=mentions<=n
            assert int(r['negative_review_count'])==n and int(r['theme_negative_count'])==mentions
            near(r['mention_rate'],mentions/n)
            near(r['mention_rate_pct'],100*mentions/n)
        for r in rows(f'{slug}_theme_pattern_summary.csv'):
            subset=[x for x in themes if x['theme']==r['theme']]
            count=sum(int(x['theme_mentions']) for x in subset)
            near(r['overall_rate_pct'],100*count/source['negative_count'])
            near(r['average_rate_pct'],sum(float(x['mention_rate_pct']) for x in subset)/6)
            assert int(r['theme_mentions'])==count
        for r in rows(f'{slug}_attachment_vs_friction_signals.csv'):
            pos_n,neg_n=int(r['stayed_positive_reviews']),int(r['negative_reviews'])
            assert pos_n==source['positive_50h_count'] and neg_n==source['negative_count']
            pos,neg=int(r['stayed_positive_mentions']),int(r['negative_mentions'])
            assert 0<=pos<=pos_n and 0<=neg<=neg_n
            near(r['stayed_positive_mention_rate_pct'],100*pos/pos_n)
            near(r['negative_mention_rate_pct'],100*neg/neg_n)
    full=rows('narrative_lift_by_playtime.csv')
    stable=rows('narrative_lift_by_playtime_stable.csv')
    assert stable==[r for r in full if int(r['playtime_sort'])<=3]
    for r in full:
        assert int(r['total_reviews'])==int(r['narrative_reviews'])+int(r['non_narrative_reviews'])
        if int(r['narrative_reviews'])==0 or int(r['non_narrative_reviews'])==0:
            assert r['narrative_lift_pp']==''
        else:
            near(r['narrative_lift_pp'],float(r['narrative_positive_rate'])-float(r['non_narrative_positive_rate']),.011)
    for game in ['God of War','RDR2','The Witcher 3']:
        assert sum(int(r['total_reviews']) for r in full if r['game']==game)==5000
    notebooks=list((ROOT/'notebooks').glob('*.ipynb'))
    assert len(notebooks)==6
    for p in notebooks:
        nb=json.loads(p.read_text(encoding='utf-8'))
        assert nb['cells'][0]['cell_type']=='markdown'
        assert 'Public portfolio method note' in ''.join(nb['cells'][0]['source'])
        for cell in nb['cells']:
            if cell['cell_type']=='code':
                assert cell['outputs']==[] and cell['execution_count'] is None
    links=0
    for p in ROOT.rglob('*.md'):
        if '.git' in p.parts or 'private_data' in p.parts: continue
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            target=target.split(' "')[0].strip('<>')
            parsed=urlsplit(target)
            if parsed.scheme or not parsed.path: continue
            assert (p.parent/unquote(parsed.path)).exists(), (p.relative_to(ROOT),target)
            links+=1
    for filename,n_pages in [('Steam Review Diagnostics by Playtime Stage.pdf',11),('Narrative as a Satisfaction Buffer.pdf',5)]:
        reader=PdfReader(ROOT/'dashboards'/filename)
        assert len(reader.pages)==n_pages
        texts=[page.extract_text() or '' for page in reader.pages]
        assert all(len(t)>100 for t in texts)
        whole='\n'.join(texts).lower()
        for phrase in ['retention mechanism','can re-engage players','loses players before','where players drop off']:
            assert phrase not in whole,(filename,phrase)
    assert not (ROOT/'private_data').exists() or 'private_data/' in (ROOT/'.gitignore').read_text()
    print(f'PASS: 18 stage rows, 90 theme rows, 27 comparisons, Case 2 groups, 6 notebooks, {links} local links and 16 PDF pages.')


if __name__=='__main__':
    validate()
