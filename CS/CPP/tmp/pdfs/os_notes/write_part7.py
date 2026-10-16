import json
from pathlib import Path
H=Path(__file__).resolve().parent
src={'pdf':[615],'printed':[679]}
blocks=[
 {'type':'p','text':'**보안**은 저장된 자료와 코드의 무결성뿐 아니라 물리 자원의 보호를 위해 사용자 인증을 보장한다. 인가되지 않은 접근, 접근 후의 악의적인 파괴·자료 변경, 우연한 비일관성 도입을 막는 역할을 한다.'},
 {'type':'p','text':'**보호**는 사용자의 파일 접근 유형을 제한해 제어된 접근을 제공한다. 운영체제에서 적절한 권한을 얻은 프로세스만 메모리 세그먼트·CPU 등의 자원에 작업할 수 있도록 한다. 프로그램·프로세스·사용자의 자원 접근을 제어하는 기법에는 부과할 제어를 지정하는 방법과 시행하는 방법이 필요하다.'},
 {'type':'p','text':'이 페이지는 제7부의 도입이다. 뒤의 제16장 보안과 제17장 보호 본문은 제공되지 않아, 구체적인 위협·암호 기법·접근 행렬 등의 설명은 원문에서 확인되지 않음으로 남긴다.'}
]
ch={'id':'OP7','order':16,'title':'제7부 도입. 보안과 보호','source':src,'available':True,
 'overview':['제공된 마지막 도입 페이지에서 보안과 보호의 역할을 구별한다.'],
 'flow':[], 'sections':[{'number':'P7.1','title':'도입에서 확인되는 보안과 보호의 역할','source':src,'blocks':blocks}],
 'codes':[],'figures':[],
 'key_points':['보안은 사용자 인증과 인가되지 않은 접근·자료 훼손의 방지를 다룬다.','보호는 권한에 따른 자원 접근 제어를 다룬다. 제어를 지정하고 시행하는 방법이 필요하다.'],
 'comparisons':[{'title':'도입에서 구별한 보안과 보호','source':src,'headers':['개념','도입에 제시된 역할'],'rows':[['보안','사용자 인증, 무결성과 물리 자원 보호, 인가되지 않은 접근과 파괴·변경 방지'],['보호','파일 접근 유형 제한과 권한에 따른 자원 접근 제어, 제어의 지정과 시행']]}],
 'review':['보안과 보호의 역할 구별은 제공된 도입의 범위에서만 복습한다.'],
 'checklist':[{'text':'제공된 도입에 따라 보안과 보호의 역할을 구별할 수 있는가?','source':src}],
 'index_terms':[{'term':'보안 / 보호의 도입','section':'P7.1'}],
 'coverage':[{'number':'P7.1','title':'제7부 도입','source':src,'topics':['보안','인증과 무결성','보호','자원 접근 제어']}],
 'limitations':['제16~21장 및 부록 본문은 미제공이다. 제7부 도입만으로 해당 장의 내용을 보충하지 않았다.'],
 'verification':{'read_pdf_pages':[615],'visually_checked_pdf_pages':[615],'notes':['원문 마지막 페이지 전체의 세 문단과 대조했다.']}}
(H/'chapters'/'16.json').write_text(json.dumps(ch,ensure_ascii=False,indent=2),encoding='utf-8')
print('part7 intro written')
