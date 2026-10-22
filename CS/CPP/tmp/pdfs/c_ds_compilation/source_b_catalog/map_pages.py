import pathlib,json,re,collections
root=pathlib.Path(__file__).parent.parent
maps=[]
for n in range(12,637):
    f=root/'B_ocr'/'lines'/f'{n:04}.json'
    if not f.exists():continue
    j=json.loads(f.read_text('utf-8-sig'))
    options=[]
    for line in j['lines']:
        for w in line['words']:
            if w['y']>j['height']*.87 and (w['x']<j['width']*.22 or w['x']>j['width']*.82):
                t=w['text']
                if re.fullmatch(r'\d{1,3}',t):
                    num=int(t)
                    if -5<=n-num<=15:options.append(num)
    if options:maps.append({'pdf':n,'printed':options[-1],'offset':n-options[-1]})
(root/'source_b_page_ocr_candidates.json').write_text(json.dumps(maps,ensure_ascii=False,indent=2),encoding='utf8')
for a,b in zip(maps,maps[1:]):
    if a['offset']!=b['offset']:print(a,b)
print('count',len(maps),collections.Counter(x['offset'] for x in maps))
print('missing candidates',[n for n in range(12,637) if not any(x['pdf']==n for x in maps)])
