import pathlib,json
r=pathlib.Path(__file__).parent
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)
errors=[]
for n in range(11,16):
    j=json.loads((r/f'unit_{n:02}.json').read_text('utf8'))
    checks={q['source']:q['pages'] for q in j['checked_images']}
    refs=0
    for x in walk(j):
        if 'refs' not in x:continue
        refs+=1
        if not x.get('evidence'):errors.append((n,'missing evidence',x))
        for ref in x['refs']:
            for p in ref['pages']:
                if p not in checks.get(ref['source'],[]):errors.append((n,'unchecked',ref))
    print(n,'core',sum(len(c['items']) for c in j['concepts']),'ref objects',refs)
print('errors',errors)
assert not errors
