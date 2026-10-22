import json
from pathlib import Path
ROOT=Path(__file__).parent
def F(text,source,section,pages,evidence=None):
    return {'text':text,'refs':[{'source':source,'section':section,'pages':pages if isinstance(pages,list) else [pages]}],'evidence':evidence or text}
def group(title,*items): return {'title':title,'items':list(items)}
def formula(label,expression,source,section,pages,evidence,note):
    return {'label':label,'expression':expression,'refs':[{'source':source,'section':section,'pages':pages if isinstance(pages,list) else [pages]}],'evidence':evidence,'note':note}
def code(label,text,source,section,page,evidence):
    return {'label':label,'code':text,'refs':[{'source':source,'section':section,'pages':[page]}],'evidence':evidence,'note':None}
def base(n,title,scope):
    return {'unit':n,'title':title,'part':'자료구조','scope':scope,'learning':[],'concepts':[],'procedures':[],'syntax':[],'formulas':[],'comparisons':[],'terms':[],'summary_basis':'편집 요약','summary':[],'review':[],'cheat':{'definitions':[],'comparison_title':'','comparison_headers':['항목','원문 설명'],'comparison_rows':[],'formulas':[],'syntax':[]},'checked_images':[],'editor_notes':[]}
def term(t,f):return {'term':t,'definition':f}
def save(u):
    used={}
    def walk(x):
        if isinstance(x,dict):
            for r in x.get('refs',[]): used.setdefault(r['source'],set()).update(r['pages'])
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(u)
    u['checked_images']=[{'source':s,'pages':sorted(p)} for s,p in used.items()]
    (ROOT/f"unit_{u['unit']:02d}.json").write_text(json.dumps(u,ensure_ascii=False,indent=2),encoding='utf8')
    print(f"saved unit_{u['unit']:02d}.json")

u=base(5,'연결 리스트',[{'source':'A','start':167,'end':244},{'source':'B','start':29,'end':77}])
a=lambda text,p,e=None,s='6.3 연결 리스트':F(text,'A',s,p,e)
b=lambda text,p,e=None,s='1장 리스트':F(text,'B',s,p,e)
fs={
'adt':a('리스트의 객체는 n개의 element형으로 구성된 순서 있는 모임이다.',169,'n개의 element형으로 구성된 순서 있는 모임','6.1 리스트 추상 데이터 타입'),
'ends':b('첫 번째 노드를 헤드(Head), 마지막 노드를 테일(Tail)이라 부르며, 리스트의 길이는 헤드부터 테일까지의 노드 개수이다.',31,'첫 번째 노드를 헤드','1.1.1 리스트의 개념'),
'operations':a('insert(), delete(), get_entry(), get_length(), is_empty(), is_full() 등의 연산으로 리스트를 다룬다.',169,'get_entry(list, pos)','6.1 리스트 추상 데이터 타입'),
'implementation':a('리스트는 배열과 연결 리스트를 이용하여 구현할 수 있다.',169,'배열과 연결 리스트를 이용하여 구현','6.1 리스트 추상 데이터 타입'),
'seq':a('배열을 이용한 리스트 구현은 순차적인 메모리 공간을 할당하므로 순차적 표현(sequential representation)이라고도 한다.',170,'순차적 표현','6.2 배열로 구현된 리스트'),
'fixed':a('배열 리스트는 크기가 고정되고, 중간에 삽입하거나 삭제하려면 기존 데이터를 이동하여야 한다.',170,'기존의 데이터들을 이동','6.2 배열로 구현된 리스트'),
'get':a('배열 리스트의 get_entry 연산은 인덱스로 항목에 바로 접근하므로 O(1)이다.',175,'get_entry','6.2 실행 시간 분석'),
'shift':a('배열 리스트의 삽입이나 삭제는 최악의 경우 O(n)이다.',175,'최악의 경우 O(n)','6.2 실행 시간 분석'),
'append':a('배열 리스트의 맨 끝에 삽입하는 경우는 O(1)이다.',175,'맨 끝에 삽입하는 경우는 O(1)','6.2 실행 시간 분석'),
'node':a('연결 리스트의 노드는 데이터 필드(data field)와 링크 필드(link field)로 구성된다.',177,'데이터 필드(data field)와 링크 필드(link field)'),
'data':a('데이터 필드에는 저장할 데이터가, 링크 필드에는 다른 노드를 가리키는 포인터가 저장된다.',177,'링크 필드에는 다른 노드를 가리키는 포인터'),
'head':a('헤드 포인터(head pointer)는 연결 리스트의 첫 번째 노드를 가리키는 변수이다.',177,'첫 번째 노드를 가리키고 있는 변수'),
'last':a('단순 연결 리스트의 마지막 노드의 링크는 NULL값을 가진다.',178,'마지막 노드의 링크는 NULL값','6.3 연결 리스트의 종류'),
'singly':a('단순 연결 리스트(singly linked list)는 하나의 방향으로만 연결되며 체인(chain)이라고도 한다.',178,'체인(chain)','6.3 연결 리스트의 종류'),
'circular':a('원형 연결 리스트(circular linked list)는 마지막 노드의 링크가 첫 번째 노드를 가리킨다.',178,'마지막 노드의 링크가 첫 번째 노드를 가리킨다','6.3 연결 리스트의 종류'),
'double':a('이중 연결 리스트(doubly linked list)는 각 노드에 앞 노드와 뒤 노드를 가리키는 2개의 링크가 존재한다.',178,'각 노드마다 2개의 링크','6.3 연결 리스트의 종류'),
'overhead':a('연결 리스트는 포인터도 저장하여야 하므로 메모리 공간을 많이 사용하고, i번째 데이터는 앞에서부터 순차적으로 접근하여야 한다.',177,'i번째 데이터를 찾으려면 앞에서부터 순차적으로'),
'self':a('자기 참조 구조체는 자기 자신을 참조하는 포인터를 포함하는 구조체이다.',180,'자기 자신을 참조하는 포인터','6.4 노드의 정의'),
'empty':a('공백인 단순 연결 리스트에서는 헤드 포인터의 값이 NULL이다.',180,'head의 값은 NULL','6.4 공백 리스트의 생성'),
'create':b('SLL_CreateNode()는 malloc()으로 노드를 생성하고 데이터를 저장한 뒤 NextNode를 NULL로 초기화한다.',38,'NextNode = NULL','1.2.2 노드 생성/소멸 연산'),
'destroy':b('SLL_DestroyNode()는 노드의 주소를 free()에 넘겨 노드를 소멸시킨다.',38,'free(Node)','1.2.2 노드 생성/소멸 연산'),
'remove':b('노드 삭제는 리스트에서 노드를 제외하는 연산이다.',35,'노드 삭제는 리스트에서 노드를 제외','1.2.2 링크드 리스트의 주요 연산'),
'memdestroy':b('노드 소멸은 노드를 메모리에서 없애는 연산이다.',35,'노드 소멸은 노드를 메모리에서 없애는','1.2.2 링크드 리스트의 주요 연산'),
'return':a('insert_first()는 변경된 헤드 포인터를 반환하므로 반환값을 헤드 포인터에 저장하여야 한다.',183,'반환된 값을 헤드포인트에 저장','6.5 삽입 연산 insert_first()'),
'pre':a('중간 삽입 insert()는 삽입 위치의 선행 노드를 알아야 가능하다.',184,'선행 노드를 알아야 삽입이 가능','6.5 삽입 연산 insert()'),
'tail':a('헤드 포인터가 마지막 노드를 가리키도록 구성한 원형 연결 리스트는 상수 시간 안에 처음과 끝에 노드를 삽입할 수 있다.',214,'상수 시간 안에 리스트의 처음과 끝','7.1 원형 연결 리스트'),
'headnode':a('헤드 노드(head node)는 데이터를 가지고 있지 않은 특별한 노드로 삽입·삭제 알고리즘을 간편하게 한다.',222,'데이터를 가지고 있지 않는 특별한 노드','7.3 이중 연결 리스트'),
'doublecost':a('이중 연결 리스트는 양방향 검색이 가능하지만 공간을 많이 차지하고 코드가 복잡해진다.',222,'공간을 많이 차지하고 코드가 복잡','7.3 이중 연결 리스트'),
'doubleend':b('더블 링크드 리스트를 환형으로 구현하면 헤드의 이전 노드는 테일이고 테일의 다음 노드는 헤드가 된다.',67,'헤드의 이전 노드가 테일','1.4 환형 링크드 리스트'),
'poly':a('다항식의 연결 리스트 표현에서는 각 항을 하나의 노드로 표현하며 계수(coef), 지수(exp), 링크(link) 필드를 둔다.',201,'각 항을 하나의 노드로 표현','6.6 연결 리스트의 응용: 다항식'),
'use':b('링크드 리스트는 레코드의 추가·삽입·삭제가 잦지만 조회는 드문 곳에서 사용하기 적합하다.',53,'추가, 삽입, 삭제가 잦지만 조회는 드문','1.2.4 링크드 리스트의 장단점'),
}
u['learning']=[fs['implementation'],fs['double']]
u['concepts']=[group('리스트 ADT와 배열 구현',*[fs[k] for k in ['adt','ends','operations','implementation','seq','fixed','get','shift','append']]),group('노드·링크·헤드 포인터',*[fs[k] for k in ['node','data','head','overhead','self','empty']]),group('단순 연결 리스트의 관리',*[fs[k] for k in ['create','destroy','remove','memdestroy','return','pre']]),group('원형·이중 연결 리스트',*[fs[k] for k in ['singly','last','circular','double','tail','headnode','doublecost','doubleend']]),group('원문 응용과 사용 특성',fs['poly'],fs['use'])]
u['procedures']=[{'title':'insert_first()의 처리 순서','steps':[a('동적 메모리 할당으로 새로운 노드 p를 생성한다.',184,'새로운 노드 p를 생성','6.5 알고리즘 6.1'),a('p->data에 value를 저장한다.',184,'p->data에 value','6.5 알고리즘 6.1'),a('p->link를 현재의 head값으로 변경한다.',184,'p->link를 현재의 head값','6.5 알고리즘 6.1'),a('head를 p값으로 변경한다.',184,'head를 p값','6.5 알고리즘 6.1'),a('변경된 헤드 포인터를 반환한다.',184,'변경된 헤드 포인터 반환','6.5 알고리즘 6.1')]}]
u['syntax']=[code('단순 연결 리스트 노드 정의', 'typedef int element;\ntypedef struct ListNode { // 노드 타입을 구조체로 정의한다.\n    element data;\n    struct ListNode *link;\n} ListNode;', 'A','6.4 노드의 정의',180,'typedef struct ListNode')]
u['formulas']=[formula('배열 리스트의 접근','get_entry: O(1)','A','6.2 실행 시간 분석',175,'get_entry','배열의 인덱스로 항목에 바로 접근한다.'),formula('배열 리스트의 삽입·삭제','최악의 경우 O(n); 맨 끝 삽입 O(1)','A','6.2 실행 시간 분석',175,'최악의 경우 O(n)','다른 항목을 이동하는 삽입·삭제의 최악 경우와 맨 끝 삽입을 구분한다.')]
rows=[[a('단순 연결 리스트',178,'단순 연결 리스트','6.3 연결 리스트의 종류'),fs['singly']],[a('원형 연결 리스트',178,'원형 연결 리스트','6.3 연결 리스트의 종류'),fs['circular']],[a('이중 연결 리스트',178,'이중 연결 리스트','6.3 연결 리스트의 종류'),fs['double']]]
u['comparisons']=[{'title':'연결 리스트의 종류','headers':['종류','원문 구조'],'rows':rows}]
u['terms']=[term(k,fs[v]) for k,v in [('리스트','adt'),('헤드·테일','ends'),('순차적 표현','seq'),('노드','node'),('헤드 포인터','head'),('자기 참조 구조체','self'),('원형 연결 리스트','circular'),('헤드 노드','headnode')]]
u['summary']=[fs['implementation'],fs['overhead'],fs['remove'],fs['doubleend']]
u['review']=[{'question':q,'answer':fs[k]} for q,k in [('노드 삭제와 노드 소멸 중 메모리에서 노드를 없애는 연산은 무엇인가?','memdestroy'),('공백인 단순 연결 리스트의 헤드 포인터 값은 무엇인가?','empty'),('배열 리스트에서 삽입·삭제의 최악 시간 복잡도는 무엇인가?','shift'),('헤드 포인터를 마지막 노드에 두는 원형 연결 리스트의 삽입 특성은 무엇인가?','tail')]]
u['cheat'].update({'definitions':[term('리스트',fs['adt']),term('헤드 포인터',fs['head']),term('헤드 노드',fs['headnode'])],'comparison_title':'연결 리스트 종류','comparison_rows':rows,'formulas':u['formulas']})
u['editor_notes']=['A는 단순·원형·이중 연결 리스트, B는 링크드·더블 링크드·환형 링크드 리스트라는 표기를 사용한다.','A 목차에는 연결 스택과 연결 큐가 모두 7.5로 기재되어 있어 해당 단원에서는 절 제목을 함께 적는다.']
save(u)

# Unit 10 is generated after 05-08 below; 09 is assigned to another editor.

u=base(6,'스택·수식·미로',[{'source':'A','start':93,'end':136},{'source':'A','start':231,'end':234},{'source':'B','start':78,'end':120}])
a=lambda t,p,e=None,s='4장 스택':F(t,'A',s,p,e)
b=lambda t,p,e=None,s='2장 스택':F(t,'B',s,p,e)
fs={
'lifo':a('스택의 입출력 형태는 후입선출(LIFO: Last-In First-Out)이다.',94,'후입선출(LIFO: Last-In First-Out)','4.1 스택이란?'),
'top':a('스택의 입출력은 맨 위에서만 일어나며, 입출력이 이루어지는 부분을 스택 상단(stack top)이라 한다.',95,'스택 상단(stack top)','4.1 스택이란?'),
'empty':a('스택에 요소가 하나도 없을 때 공백 스택(empty stack)이라고 한다.',95,'공백 스택(empty stack)','4.1 스택이란?'),
'activation':a('함수 호출 시 시스템 스택에 활성 레코드(activation record)가 만들어지며 복귀주소·매개변수·지역 변수가 저장된다.',95,'활성 레코드(activation record)','4.1 시스템 스택을 이용한 함수 호출'),
'adt':a('추상 자료형 스택의 객체는 0개 이상의 원소를 가지는 유한 선형 리스트이다.',97,'0개 이상의 원소를 가지는 유한 선형 리스트','4.1 ADT 4.1 Stack'),
'push':a('push는 스택의 맨 위에 item을 추가하는 연산이다.',97,'스택의 맨 위에 item을 추가','4.1 ADT 4.1 Stack'),
'pop':a('pop은 스택의 맨 위의 원소를 제거해서 반환하는 연산이다.',97,'맨 위의 원소를 제거해서 반환','4.1 ADT 4.1 Stack'),
'peek':a('peek는 스택의 맨 위의 원소를 제거하지 않고 반환하는 연산이다.',97,'맨 위의 원소를 제거하지 않고 반환','4.1 ADT 4.1 Stack'),
'errors':a('포화 스택의 push와 공백 스택의 pop에서는 오류가 발생한다.',97,'스택이 가득차서 입력이 불가능','4.1 추상 자료형 스택'),
'array':a('배열 스택에서 top은 가장 최근에 입력된 자료를 가리키며, 공백일 때 -1이다.',98,'top 변수는 스택이 비어 있으면 -1','4.2 스택의 구현'),
'full':a('배열 스택에서 top이 MAX_STACK_SIZE-1이면 포화 상태이다.',99,'포화 상태로 판정','4.2 스택의 is_full 연산'),
'pushorder':a('배열 스택의 push는 top을 먼저 증가시킨 후 stack[top]에 요소를 삽입한다.',100,'먼저 top의 값을 증가','4.2 스택의 push 연산'),
'poporder':a('배열 스택의 pop은 공백 여부를 검사한 뒤 top이 가리키는 값을 반환하고 top을 하나 감소시킨다.',100,'top을 하나 감소','4.2 스택의 pop 연산'),
'dynamic':a('동적 배열 스택의 push는 공간이 부족하면 capacity를 2배로 늘리고 realloc()으로 메모리를 확보한다.',109,'공간이 부족하면 메모리를 2배','4.3 동적 배열 스택'),
'linked':a('연결된 스택은 동적 메모리 할당이 가능하면 새로운 요소를 삽입할 수 있으며, top은 노드를 가리키는 포인터이다.',231,'top은 더 이상 정수가 아니고','7.5 연결 리스트로 구현한 스택'),
'linkedpush':a('A의 연결 스택은 단순 연결 리스트의 맨 앞에 노드를 삽입한다.',232,'맨 앞에 데이터를 삽입','7.5 연결 리스트로 구현한 스택'),
'btop':b('B의 링크드 리스트 스택은 List가 헤드를 가리키고 Top이 테일을 가리키는 구현을 사용한다.',92,'Top 포인터는 이 링크드 리스트의 테일','2.3.1 링크드 리스트 기반 스택과 스택의 노드 표현'),
'bracket':a('올바른 괄호는 좌우 개수가 같고, 같은 종류의 왼쪽 괄호가 먼저 나오며, 서로 다른 종류의 괄호 쌍은 교차하지 않는다.',111,'괄호의 검사 조건은 다음의 3가지','4.4 스택의 응용: 괄호 검사 문제'),
'infix':a('중위(infix)는 연산자가 피연산자 사이에 있는 표기법이다.',116,'연산자가 피연산자 사이','4.5 수식의 3가지 표기법'),
'postfix':a('후위(postfix)는 연산자가 피연산자 뒤에 있는 표기법이다.',116,'피연산자 뒤에 있으면 후위','4.5 수식의 3가지 표기법'),
'prefix':a('전위(prefix)는 연산자가 피연산자 앞에 있는 표기법이다.',116,'피연산자 앞에 있으면 전위','4.5 수식의 3가지 표기법'),
'operandcondition':a('A의 후위표기식 계산 프로그램은 피연산자가 한 문자로 된 숫자라고 가정한다.',119,'피연산자가 한 문자로 된 숫자','4.5 프로그램 4.7 후위표기식 계산'),
'priority':a('중위식을 후위식으로 바꿀 때 스택의 연산자 우선순위가 현재 연산자보다 높거나 같으면 먼저 꺼내어 출력한다.',121,'우선순위가 같은 경우에도','4.5 중위표기수식을 후위표기수식으로 변환'),
'left':a('왼쪽 괄호는 무조건 스택에 삽입하고, 스택 안에서는 우선순위가 제일 낮은 연산자로 취급한다.',122,'왼쪽괄호는 무조건 스택에 삽입','4.5 중위표기수식을 후위표기수식으로 변환'),
'right':a('오른쪽 괄호를 만나면 왼쪽 괄호가 삭제될 때까지 그 위에 쌓인 모든 연산자를 출력한다.',122,'모든 연산자들을 출력','4.5 중위표기수식을 후위표기수식으로 변환'),
'token':b('텍스트 분석에서 토큰은 최소 단위의 기호 또는 단어를 말한다.',105,'토큰은 최소 단위의 기호 또는 단어','2.4.2 토큰이 알고 싶다'),
}
u['learning']=[fs['lifo'],fs['postfix']]
u['concepts']=[group('스택 ADT와 함수 호출',*[fs[k] for k in ['lifo','top','empty','activation','adt','push','pop','peek','errors']]),group('배열·동적 배열·연결 스택',*[fs[k] for k in ['array','full','pushorder','poporder','dynamic','linked','linkedpush','btop']]),group('괄호 검사·수식 표기와 변환',*[fs[k] for k in ['bracket','infix','postfix','prefix','operandcondition','priority','left','right','token']])]
u['procedures']=[{'title':'괄호 검사','steps':[a('왼쪽 괄호를 만나면 스택에 삽입한다.',112,'왼쪽 괄호를 만나면 스택에 삽입','4.4 괄호 검사 알고리즘'),a('오른쪽 괄호를 만나면 맨 위의 괄호를 꺼내 짝을 검사하며, 스택이 비었거나 짝이 맞지 않으면 오류이다.',112,'짝이 맞는지를 검사','4.4 괄호 검사 알고리즘'),a('문자열을 모두 조사한 뒤 괄호가 남으면 FALSE, 남지 않으면 TRUE를 반환한다.',112,'성공이므로 TRUE','4.4 괄호 검사 알고리즘')]},{'title':'후위 표기 수식 계산','steps':[a('스택을 생성·초기화하고 후위식을 순서대로 읽어 피연산자를 스택에 삽입한다.',118,'스택 s를 생성하고 초기화','4.5 알고리즘 4.6'),a('연산자 op를 만나면 second, first 순서로 pop하고 first op second의 결과를 push한다.',118,'result ← first op second','4.5 알고리즘 4.6'),a('식의 처리가 끝나면 pop한 값을 최종 결과로 얻는다.',118,'final_result','4.5 알고리즘 4.6')]},{'title':'미로 탐색','steps':[a('스택과 출구·현재 위치를 초기화한다.',129,'현재 생쥐의 위치를 초기화','4.6 알고리즘 4.8'),a('현재 위치를 방문 표시하고, 위·아래·왼쪽·오른쪽의 미방문·이동 가능 위치를 스택에 push한다.',129,'위, 아래, 왼쪽, 오른쪽','4.6 알고리즘 4.8'),a('스택이 비면 실패이고, 그렇지 않으면 하나를 꺼내 현재 위치로 정하여 출구에 이를 때까지 반복한다.',129,'스택에서 하나의 위치를 꺼내어 현재 위치','4.6 알고리즘 4.8')]}]
u['syntax']=[code('동적 배열 스택 구조체','typedef int element;\ntypedef struct {\n    element *data;\n    int capacity;\n    int top;\n} StackType;','A','4.3 동적 배열 스택',109,'element *data;')]
u['formulas']=[formula('A의 배열 스택 상태 조건','공백: top == -1; 포화: top >= (MAX_STACK_SIZE-1)','A','4.2 알고리즘 4.1·4.2',99,'top >= (MAX_STACK_SIZE-1)','배열 인덱스는 0부터 시작한다.')]
rows=[[a('push',97,'push(s, item)','4.1 ADT 4.1 Stack'),fs['push']],[a('pop',97,'pop(s)','4.1 ADT 4.1 Stack'),fs['pop']],[a('peek',97,'peek(s)','4.1 ADT 4.1 Stack'),fs['peek']]]
u['comparisons']=[{'title':'스택의 기본 연산','headers':['연산','책에 나온 정의'],'rows':rows}]
u['terms']=[term(k,fs[v]) for k,v in [('후입선출','lifo'),('스택 상단','top'),('공백 스택','empty'),('활성 레코드','activation'),('중위 표기법','infix'),('후위 표기법','postfix'),('전위 표기법','prefix'),('토큰','token')]]
u['summary']=[fs['lifo'],fs['peek'],fs['dynamic'],fs['priority']]
u['review']=[{'question':q,'answer':fs[k]} for q,k in [('스택의 입출력 순서는 무엇인가?','lifo'),('peek와 pop은 원소 제거에서 어떻게 다른가?','peek'),('A의 후위표기식 계산 프로그램이 두는 피연산자 조건은 무엇인가?','operandcondition'),('후위식 변환 시 스택 연산자와 입력 연산자의 우선순위가 같으면 어떻게 하는가?','priority')]]
u['cheat'].update({'definitions':[term('스택',fs['lifo']),term('후위 표기법',fs['postfix']),term('토큰',fs['token'])],'comparison_title':'기본 연산','comparison_rows':rows,'formulas':u['formulas']})
u['editor_notes']=['연결 스택의 top 위치는 A(리스트 앞)와 B(리스트 테일)의 구현을 구분하여 적었다.','원문의 수식 표기법 표 중 표·본문이 서로 어긋나는 예시는 발췌하지 않았다.']
save(u)

u=base(7,'큐·덱·시뮬레이션',[{'source':'A','start':137,'end':166},{'source':'A','start':235,'end':241},{'source':'B','start':121,'end':148}])
a=lambda t,p,e=None,s='5장 큐':F(t,'A',s,p,e)
b=lambda t,p,e=None,s='3장 큐':F(t,'B',s,p,e)
fs={
'fifo':a('큐(queue)는 먼저 들어온 데이터가 먼저 나가는 선입선출(FIFO: First-In First-Out) 구조이다.',138,'선입선출(FIFO: First-In First-Out)','5.1 큐 추상 데이터 타입'),
'ends':a('큐에서 삽입이 일어나는 곳은 후단(rear), 삭제가 일어나는 곳은 전단(front)이다.',138,'후단(rear)','5.1 큐 추상 데이터 타입'),
'adt':a('큐의 객체는 0개 이상의 요소들로 구성된 선형 리스트이다.',139,'0개 이상의 요소들로 구성된 선형 리스트','5.1 ADT 5.1 큐'),
'enqueue':a('enqueue는 큐의 끝에 요소를 추가하며 포화 큐에서는 queue_full 오류를 낸다.',139,'queue_full 오류','5.1 ADT 5.1 큐'),
'dequeue':a('dequeue는 큐의 맨 앞 요소를 제거하여 반환하며 공백 큐에서는 queue_empty 오류를 낸다.',139,'맨 앞에 있는 e를 제거하여 반환','5.1 ADT 5.1 큐'),
'peek':a('peek는 공백이 아닌 큐의 맨 앞 요소를 읽어서 반환한다.',139,'맨 앞에 있는 e를 읽어서 반환','5.1 ADT 5.1 큐'),
'linear':a('선형큐는 front와 rear가 계속 증가하므로 배열 앞부분이 비어 있어도 사용하지 못할 수 있다.',145,'배열의 앞부분이 비어 있더라도','5.3 원형큐'),
'move':a('선형큐의 오른쪽에 삽입 공간을 만들려면 요소들을 왼쪽으로 이동시켜야 한다.',145,'모든 요소들을 왼쪽으로 이동','5.3 원형큐'),
'circular':a('원형큐는 인덱스가 배열 끝에 도달한 뒤 다시 0으로 돌아가도록 한다.',146,'다음에 증가되는 값은 0','5.3 원형큐'),
'afront':a('A의 원형큐에서 front는 첫 번째 요소의 하나 앞을, rear는 마지막 요소를 가리킨다.',146,'첫 번째 요소의 하나 앞','5.3 원형큐'),
'ainit':a('A의 원형큐는 front와 rear를 모두 0으로 초기화한다.',146,'front, rear는 모두 0','5.3 원형큐'),
'insert':a('A의 원형큐 삽입은 rear를 먼저 증가시키고 그 위치에 데이터를 저장한다.',146,'rear가 먼저 증가','5.3 원형큐'),
'delete':a('A의 원형큐 삭제는 front를 먼저 증가시키고 그 위치의 데이터를 삭제한다.',146,'front가 먼저 증가','5.3 원형큐'),
'reserve':a('원형큐는 포화 상태와 공백 상태를 구분하기 위해 한 자리를 항상 비워 둔다.',147,'하나의 자리는 항상 비워둔다','5.3 원형큐'),
'count':a('요소 개수를 저장하는 추가 변수 count를 사용하면 한 자리를 비워 두지 않아도 된다.',147,'count 변수를 사용할 수 있다면','5.3 원형큐'),
'bfront':b('B의 순환 큐에서 Front는 제거할 전단의 위치를, Rear는 실제 후단 위치에 1을 더한 값을 나타낸다.',[132,133],'실제 후단의 위치 값에 1','3.2.2 순환 큐의 기본 연산'),
'bcapacity':b('B는 공백·포화 구별을 위해 실제 용량보다 1만큼 더 큰 큐 배열을 만든다.',128,'실제 용량보다 1만큼 더 크게','3.2.1 공백 상태와 포화 상태'),
'buffer':a('큐는 서로 다른 속도로 실행되는 두 프로세스의 상호 작용을 조화시키는 버퍼 역할을 담당한다.',152,'버퍼 역할을 담당','5.4 큐의 응용: 버퍼'),
'deque':a('덱(deque)은 double-ended queue의 줄임말이며 전단과 후단에서 모두 삽입·삭제가 가능한 큐이다.',154,'double-ended queue','5.5 덱이란?'),
'middle':a('덱에서도 중간에 삽입하거나 삭제하는 것은 허용하지 않는다.',154,'중간에 삽입하거나 삭제','5.5 덱이란?'),
'stacklike':a('덱의 전단 관련 연산만 사용하면 스택으로 동작한다.',155,'전단과 관련된 연산들만','5.5 덱의 추상 자료형'),
'queuelike':a('덱에서 후단 삽입과 전단 삭제만 사용하면 큐로 동작한다.',155,'삽입은 후단, 삭제는 전단','5.5 덱의 추상 자료형'),
'dpeek':a('get_front와 get_rear는 각각 앞·뒤의 요소를 삭제하지 않고 반환한다.',155,'삭제하지 않고','5.5 ADT 5.2 Deque'),
'linked':a('연결된 큐(linked queue)는 연결 리스트로 만든 큐이며 front는 맨 앞 요소, rear는 맨 뒤 요소를 가리킨다.',235,'연결된 큐(linked queue)','7.5 연결 리스트로 구현한 큐'),
'lempty':a('연결된 큐에 요소가 없으면 front와 rear는 NULL이다.',235,'front와 rear는 NULL','7.5 연결 리스트로 구현한 큐'),
'lcost':a('연결된 큐는 크기가 제한되지 않는 장점이 있지만 코드가 더 복잡하고 링크 필드의 메모리가 필요하다.',235,'링크 필드 때문에 메모리 공간','7.5 연결 리스트로 구현한 큐'),
'bcount':b('B의 LinkedQueue 구조체는 Front, Rear, 노드 개수를 나타내는 Count를 갖는다.',140,'노드 개수를 나타내는 Count','3.3.1 링크드 큐의 기본 연산'),
'model':a('큐잉모델은 서비스를 수행하는 서버와 고객으로 구성되며 대기 행렬을 큐로 구현한다.',160,'이 대기 행렬이 큐로 구현','5.6 큐의 응용: 시뮬레이션'),
'sim':a('원문의 은행 시뮬레이션은 행원 한 사람을 가정하고 고객 도착 간격과 서비스 시간을 랜덤하게 정한다.',160,'행원은 한사람이라고 가정','5.6 큐의 응용: 시뮬레이션'),
}
u['learning']=[fs['fifo'],fs['deque']]
u['concepts']=[group('큐 ADT',*[fs[k] for k in ['fifo','ends','adt','enqueue','dequeue','peek']]),group('선형큐와 원형큐',*[fs[k] for k in ['linear','move','circular','afront','ainit','insert','delete','reserve','count']]),group('B의 순환 큐 구현',fs['bfront'],fs['bcapacity']),group('덱',*[fs[k] for k in ['deque','middle','stacklike','queuelike','dpeek']]),group('연결 큐·버퍼·시뮬레이션',*[fs[k] for k in ['linked','lempty','lcost','bcount','buffer','model','sim']])]
u['procedures']=[{'title':'A의 은행 서비스 시뮬레이션 루프','steps':[a('현재 시각을 나타내는 clock을 증가시킨다.',160,'clock이라는 변수를 하나 증가','5.6 시뮬레이션 반복 루프'),a('새 고객이 들어오면 아이디·도착시간·서비스 시간을 구조체에 저장하여 enqueue한다.',160,'구조체를 enqueue()','5.6 시뮬레이션 반복 루프'),a('service_time이 0이 아니면 하나 감소시키고, 0이면 큐에서 고객을 꺼내 서비스를 시작한다.',[160,161],'service_time이 0이면','5.6 시뮬레이션 반복 루프'),a('60분이 지나면 고객들이 기다린 시간을 모두 합하여 출력한다.',161,'60분의 시간이 지나면','5.6 시뮬레이션 반복 루프')]}]
u['syntax']=[code('원형큐 공백·포화 검출 함수','int is_empty(QueueType *q)\n{\n    return (q->front == q->rear);\n}\nint is_full(QueueType *q)\n{\n    return ((q->rear + 1) % MAX_QUEUE_SIZE == q->front);\n}','A','5.3 프로그램 5.2',150,'int is_empty(QueueType *q)')]
u['formulas']=[formula('A의 원형 회전','front ← (front+1) % MAX_QUEUE_SIZE; rear ← (rear+1) % MAX_QUEUE_SIZE;','A','5.3 원형큐의 삽입, 삭제 알고리즘',148,'나머지 연산자 %','배열 끝 다음 인덱스는 0이 된다.'),formula('A의 공백·포화 조건','공백: front == rear; 포화: (rear+1) % MAX_QUEUE_SIZE == front','A','5.3 프로그램 5.2',150,'(q->rear + 1) % MAX_QUEUE_SIZE == q->front','한 자리를 비워 두는 원문 구현이다.')]
rows=[[a('A 원형큐',146,'원형큐','5.3 원형큐'),fs['afront']],[b('B 순환 큐',132,'순환 큐','3.2.2 순환 큐의 기본 연산'),fs['bfront']],[a('연결된 큐',235,'연결된 큐','7.5 연결 리스트로 구현한 큐'),fs['linked']]]
u['comparisons']=[{'title':'전단·후단의 구현별 의미','headers':['원문 구현','포인터·인덱스 의미'],'rows':rows}]
u['terms']=[term(k,fs[v]) for k,v in [('큐','fifo'),('전단·후단','ends'),('enqueue','enqueue'),('dequeue','dequeue'),('원형큐','circular'),('덱','deque'),('연결된 큐','linked'),('큐잉모델','model')]]
u['summary']=[fs['fifo'],fs['reserve'],fs['deque'],fs['model']]
u['review']=[{'question':q,'answer':fs[k]} for q,k in [('큐의 삽입과 삭제는 각각 어디서 일어나는가?','ends'),('원형큐에서 한 자리를 비워 두는 이유는 무엇인가?','reserve'),('덱에서 스택으로 동작하려면 어떤 연산을 사용하는가?','stacklike'),('공백인 연결된 큐의 front와 rear 값은 무엇인가?','lempty')]]
u['cheat'].update({'definitions':[term('큐',fs['fifo']),term('덱',fs['deque']),term('연결된 큐',fs['lempty'])],'comparison_title':'A·B 원형 구현의 차이','comparison_rows':rows[:2],'formulas':[u['formulas'][1]]})
u['editor_notes']=['A의 front·rear와 B의 Front·Rear는 같은 인덱스 의미가 아니므로 각 구현을 구분하였다.','A의 은행 모델 설명과 프로그램은 일부 수치 표기가 달라 난수 범위·확률의 임의 보정을 하지 않았다.']
save(u)

u=base(8,'트리·순회·트리 응용',[{'source':'A','start':245,'end':285},{'source':'B','start':149,'end':194}])
a=lambda t,p,e=None,s='8장 트리':F(t,'A',s,p,e)
b=lambda t,p,e=None,s='4장 트리':F(t,'B',s,p,e)
fs={
'tree':a('트리는 한 개 이상의 노드로 이루어진 유한 집합이다.',247,'한 개 이상의 노드로 이루어진 유한 집합','8.1 트리의 용어들'),
'root':a('루트(root)는 계층적인 구조에서 가장 높은 곳에 있는 노드이다.',247,'가장 높은 곳에 있는 노드','8.1 트리의 용어들'),
'edge':a('트리에서 루트와 서브트리를 연결하는 선을 간선(edge)이라고 한다.',247,'이 연결선을 간선(edge)','8.1 트리의 용어들'),
'leaf':a('자식 노드가 없는 노드를 단말노드(terminal node, 또는 leaf node)라고 한다.',248,'자식 노드가 없는 노드','8.1 트리의 용어들'),
'desc':a('후손 노드는 임의의 노드 하위에 연결된 모든 노드를 의미한다.',248,'임의의 노드 하위에 연결된 모든 노드','8.1 트리의 용어들'),
'degree':a('노드의 차수(degree)는 자식 노드의 개수이며 트리의 차수는 노드 차수 중 가장 큰 값이다.',248,'자식 노드의 개수','8.1 트리의 용어들'),
'alevel':a('A에서 루트의 레벨은 1이고 한 층씩 내려갈수록 1씩 증가한다.',248,'루트의 레벨은 1','8.1 트리의 용어들'),
'aheight':a('A에서 트리의 높이(height)는 최대 레벨이다.',248,'최대 레벨','8.1 트리의 용어들'),
'forest':a('포리스트(forest)는 트리들의 집합이다.',248,'트리들의 집합','8.1 트리의 용어들'),
'bdepth':b('B에서 뿌리 노드의 깊이는 0이다.',154,'뿌리 노드의 깊이','4.1.2 트리의 구성 요소'),
'blevel':b('B에서 레벨은 깊이가 같은 노드의 집합이며, 높이는 가장 깊은 잎 노드까지의 깊이이다.',154,'깊이가 같은 노드의 집합','4.1.2 트리의 구성 요소'),
'binary':a('이진트리는 공집합이거나 루트와 왼쪽·오른쪽 서브 트리로 구성된 유한 집합이며 서브 트리들도 이진트리여야 한다.',250,'공집합이거나','8.2 정의 8.1 이진트리'),
'order':a('이진트리에는 서브 트리 간 순서가 있어 왼쪽과 오른쪽 서브 트리가 구별된다.',250,'왼쪽 서브 트리와 오른쪽 서브 트리는 서로 구별','8.2 이진 트리의 정의'),
'full':a('포화 이진 트리(full binary tree)는 각 레벨에 노드가 꽉 차 있는 이진트리이다.',253,'각 레벨에 노드가 꽉 차있는','8.2 이진트리의 분류'),
'complete':a('완전 이진 트리(complete binary tree)는 마지막 전 레벨까지 모두 채워지고 마지막 레벨은 왼쪽부터 순서대로 채워진다.',254,'왼쪽부터 오른쪽으로 노드가 순서대로','8.2 이진트리의 분류'),
'fullcomplete':a('포화 이진트리는 항상 완전 이진트리이지만 그 역은 항상 성립하지 않는다.',254,'그 역은 항상 성립하지 않는다','8.2 이진트리의 분류'),
'link':a('링크 표현법의 이진트리 노드는 데이터 필드와 왼쪽·오른쪽 자식을 가리키는 2개의 포인터 필드를 갖는다.',256,'2개의 포인터 필드','8.3 링크 표현법'),
'rootptr':a('링크 표현의 이진트리는 루트 노드를 가리키는 포인터로 모든 노드에 접근할 수 있다.',257,'루트 노드를 가리키는 포인터만','8.3 링크 표현법'),
'nlink':b('N-링크 표현법은 차수가 N인 노드에 N개의 자식 링크를 두며, 노드마다 차수가 다른 트리에는 적용하기 힘들다.',157,'노드가 N개의 링크','4.1.4 노드 표현 방법'),
'lcrs':b('왼쪽 자식-오른쪽 형제 표현법은 왼쪽 자식과 오른쪽 형제에 대한 2개의 포인터로 노드를 구성한다.',157,'왼쪽 자식과 오른쪽 형제','4.1.4 노드 표현 방법'),
'traverse':a('이진트리 순회(traversal)는 모든 노드를 한 번씩 방문하여 데이터를 목적에 맞게 처리하는 것이다.',259,'모든 노드를 한 번씩 방문','8.4 이진 트리의 순회'),
'pre':a('전위순회(preorder traversal)의 방문 순서는 VLR이다.',260,'전위순회(preorder traversal) : VLR','8.4 이진트리 순회방법'),
'in':a('중위순회(inorder traversal)의 방문 순서는 LVR이다.',260,'중위순회(inorder traversal) : LVR','8.4 이진트리 순회방법'),
'post':a('후위순회(postorder traversal)의 방문 순서는 LRV이다.',260,'후위순회(postorder traversal) : LRV','8.4 이진트리 순회방법'),
'sub':a('각 서브 트리에도 전체 이진트리와 같은 순회 방법을 적용한다.',260,'똑같은 방법을 적용','8.4 이진트리 순회방법'),
'iter':a('반복적 트리 순회는 별도의 스택에 자식 노드를 저장하고 꺼내면서 순환 호출을 흉내 낼 수 있다.',269,'별도의 스택을 사용하면','8.5 반복적 순회'),
'level':a('레벨 순회(level order)는 레벨 순으로 방문하고 같은 레벨에서는 좌에서 우로 방문하며 큐를 사용한다.',271,'레벨 순회는 큐를 사용','8.6 레벨 순회'),
'expression':a('수식 트리에서 피연산자는 단말노드, 연산자는 비단말 노드가 된다.',275,'피연산자들은 단말노드','8.7 트리의 응용: 수식 트리 처리'),
'notations':a('수식 트리를 전위·중위·후위로 읽으면 각각 전위·중위·후위 표기 수식이 된다.',275,'각각 전위 표기 수식','8.7 트리의 응용: 수식 트리 처리'),
'eval':a('수식 트리의 값을 계산하려면 자식 노드를 루트보다 먼저 방문하는 후위 순회를 사용한다.',275,'후위 순회','8.7 트리의 응용: 수식 트리 처리'),
'exprcondition':b('B의 수식 트리는 하나의 연산자가 2개의 피연산자를 취한다고 가정한다.',183,'2개의 피연산자를 취한다는 가정','4.3 수식 트리'),
'dircondition':a('A의 이진트리 디렉토리 용량 계산에서는 한 디렉토리 안의 다른 디렉토리가 2개를 초과하면 안 된다.',278,'2개를 초과하면 안 된다','8.8 트리의 응용: 디렉토리 용량 계산'),
'dir':a('디렉토리 용량은 서브 디렉토리부터 계산하여 반환하는 후위 순회로 구한다.',278,'따라서 후위 순회','8.8 트리의 응용: 디렉토리 용량 계산'),
'nodecount':a('노드 개수는 왼쪽·오른쪽 서브트리의 노드 개수에 현재 노드 1개를 더하여 구한다.',280,'반환되는 값에 1을 더하여','8.9 노드의 개수'),
'leafcount':a('단말노드 개수는 양쪽 자식이 NULL인 노드에서 1을 반환하고, 비단말 노드에서 양쪽 서브트리의 결과를 더한다.',280,'반환되는 값을 서로 더하면','8.9 단말 노드 개수 구하기'),
'heightcalc':a('높이 계산은 각 서브트리의 높이를 구한 뒤 그 최댓값에 1을 더한다.',281,'return 1 + max','8.9 알고리즘 8.8'),
'thread':a('스레드 이진 트리는 NULL 링크에 중위 선행자나 중위 후속자를 저장하여 순회 순서대로 연결한 트리이다.',282,'중위 선행자','8.10 스레드 이진 트리'),
'tag':a('스레드 이진트리에서는 링크가 자식 포인터인지 스레드인지 구별하는 태그 필드가 필요하다.',283,'구별해주는 태그 필드','8.10 스레드 이진 트리'),
}
u['learning']=[fs['binary'],fs['traverse']]
u['concepts']=[group('트리의 용어와 책별 높이 정의',*[fs[k] for k in ['tree','root','edge','leaf','desc','degree','alevel','aheight','forest','bdepth','blevel']]),group('이진트리의 정의와 종류',*[fs[k] for k in ['binary','order','full','complete','fullcomplete']]),group('노드 표현',*[fs[k] for k in ['link','rootptr','nlink','lcrs']]),group('순회',*[fs[k] for k in ['traverse','pre','in','post','sub','iter','level']]),group('수식·디렉토리 응용',*[fs[k] for k in ['expression','notations','eval','exprcondition','dircondition','dir']]),group('추가 연산·스레드 이진트리',*[fs[k] for k in ['nodecount','leafcount','heightcalc','thread','tag']])]
u['procedures']=[{'title':'레벨 순회의 반복','steps':[a('루트를 큐에 입력한 상태에서 시작한다.',271,'루트 노드인 +가 큐에 입력','8.6 레벨 순회'),a('큐의 노드를 꺼내어 방문한 뒤 그 노드의 자식 노드를 큐에 삽입한다.',271,'그 노드의 자식 노드를 큐에 삽입','8.6 레벨 순회'),a('큐에 노드가 더 이상 없을 때까지 반복한다.',271,'더 이상의 노드가 없을 때까지','8.6 레벨 순회')]},{'title':'B의 후위 표기식 기반 수식 트리 구축','steps':[b('수식을 뒤에서 앞쪽으로 읽으며 토큰을 취하고 마지막 토큰으로 뿌리 노드를 생성한다.',184,'뒤에서부터 앞쪽으로 읽어나가며','4.3.1 수식 트리 구축 방법'),b('연산자 토큰이면 가지 노드를 생성하고 오른쪽 자식과 왼쪽 자식을 구성하며, 다음 토큰도 연산자이면 그 하위 트리를 먼저 완성한다.',184,'하위 트리가 완성된 이후','4.3.1 수식 트리 구축 방법'),b('숫자 토큰이면 잎 노드를 생성한다.',185,'숫자인 경우 잎 노드를 생성','4.3.1 수식 트리 구축 방법')]}]
u['syntax']=[code('이진트리 노드의 링크 표현','typedef struct TreeNode {\n    int data;\n    struct TreeNode *left, *right;\n} TreeNode;','A','8.3 링크 표현법',257,'typedef struct TreeNode')]
u['formulas']=[formula('노드 수와 간선 수','간선의 개수 = n-1','A','8.2 이진트리의 성질',251,'n-1의 간선','노드가 n개인 이진트리.'),formula('A의 노드 수·높이 범위','최소 노드 수 h; 최대 노드 수 2^h-1; 최소 높이 ⌈log₂(n+1)⌉; 최대 높이 n','A','8.2 이진트리의 성질',252,'최대 2','h는 A의 높이 정의(루트 레벨 1), n은 노드 수.'),formula('A의 배열 표현 인덱스','부모: i/2; 왼쪽 자식: 2i; 오른쪽 자식: 2i+1','A','8.3 배열 표현법',256,'부모 노드 인덱스 = i/2','루트 인덱스 1인 원문 배열 표현.')]
rows=[[a('전위순회',260,'전위순회','8.4 이진트리 순회방법'),fs['pre']],[a('중위순회',260,'중위순회','8.4 이진트리 순회방법'),fs['in']],[a('후위순회',260,'후위순회','8.4 이진트리 순회방법'),fs['post']]]
u['comparisons']=[{'title':'표준 순회 순서: V=루트, L=왼쪽, R=오른쪽','headers':['순회','방문 순서'],'rows':rows},{'title':'원문별 레벨·높이 정의','headers':['출처','책에 나온 정의'],'rows':[[a('A',248,'레벨','8.1 트리의 용어들'),fs['alevel']],[a('A',248,'높이','8.1 트리의 용어들'),fs['aheight']],[b('B',154,'레벨','4.1.2 트리의 구성 요소'),fs['blevel']]]}]
u['terms']=[term(k,fs[v]) for k,v in [('루트','root'),('단말노드','leaf'),('차수','degree'),('포리스트','forest'),('이진트리','binary'),('포화 이진 트리','full'),('완전 이진 트리','complete'),('순회','traverse'),('스레드 이진 트리','thread')]]
u['summary']=[fs['binary'],fs['traverse'],fs['level'],fs['thread']]
u['review']=[{'question':q,'answer':fs[k]} for q,k in [('단말노드와 차수의 관계에서 단말노드는 어떤 노드인가?','leaf'),('전위순회의 방문 순서는 무엇인가?','pre'),('레벨 순회는 어떤 자료구조를 사용하는가?','level'),('A의 디렉토리 용량 계산 예제에는 어떤 이진트리 조건이 있는가?','dircondition')]]
u['cheat'].update({'definitions':[term('이진트리',fs['binary']),term('포화 이진 트리',fs['full']),term('완전 이진 트리',fs['complete'])],'comparison_title':'V=루트, L=왼쪽, R=오른쪽','comparison_rows':rows,'formulas':[u['formulas'][2]]})
u['editor_notes']=['A의 높이는 루트 레벨 1을 기준으로 하고, B의 높이는 루트 깊이 0을 기준으로 한다. 두 정의를 통합하여 하나로 고치지 않았다.','B의 순회 소개 문장 중 후위 순서 표기가 상세 설명과 달라, 일관된 A의 VLR/LVR/LRV 표와 B 상세 수식 트리 설명을 사용하였다.']
save(u)

u=base(10,'우선순위 큐·힙·허프만',[{'source':'A','start':313,'end':350},{'source':'B','start':308,'end':334}])
a=lambda text,p,e=None,s='9장 우선순위 큐':F(text,'A',s,p,e)
b=lambda text,p,e=None,s='7장 우선순위 큐와 힙':F(text,'B',s,p,e)
fs={
'priority':b('우선순위 큐는 우선순위 속성을 갖는 데이터의 삽입(Enqueue)과 제거(Dequeue) 연산을 지원하는 ADT이다.',310,'삽입과 제거 연산을 지원하는 ADT','7.1 우선순위 큐'),
'remove':b('우선순위 큐는 가장 높은 우선순위를 가진 요소부터 빠져나오게 한다.',310,'가장 높은 우선순위를 가진 요소부터','7.1 우선순위 큐'),
'criterion':b('우선순위의 기준은 프로그래머가 결정한다.',310,'전적으로 프로그래머에게 달렸습니다','7.1 우선순위의 기준'),
'bcriterion':b('B에서는 데이터의 값이 작을수록 우선순위가 높은 것으로 간주한다.',310,'데이터의 값이 작을수록 높은','7.1 우선순위의 기준'),
'apps':a('우선순위 큐는 시뮬레이션 시스템, 네트워크 트래픽 제어, 운영 체제의 작업 스케줄링, 수치 해석적인 계산에 사용된다.',315,'네트워크 트래픽 제어','9.1 우선순위 큐'),
'heap':a('히프(heap)는 여러 개의 값 중에서 가장 큰 값이나 가장 작은 값을 빠르게 찾아내도록 만들어진 자료구조이다.',319,'가장 큰 값이나 가장 작은 값','9.3 히프란?'),
'complete':a('히프는 완전 이진트리이다.',319,'완전 이진트리','9.3 히프란?'),
'loose':a('히프는 부모 노드의 키 값이 자식 노드의 키 값보다 큰 느슨한 정렬 상태를 유지한다.',319,'느슨한 정렬 상태','9.3 히프란?'),
'duplicate':a('히프 트리에서는 중복된 값을 허용한다.',319,'중복된 값을 허용','9.3 히프란?'),
'max':a('최대 히프(max heap)는 부모 노드의 키 값이 자식 노드의 키 값보다 크거나 같은 완전 이진트리이다.',320,'크거나 같은 완전 이진트리','9.3 최대 히프'),
'min':a('최소 히프(min heap)는 부모 노드의 키 값이 자식 노드의 키 값보다 작거나 같은 완전 이진트리이다.',320,'작거나 같은 완전 이진트리','9.3 최소 히프'),
'abase':a('A의 배열 표현은 인덱스 0을 사용하지 않고 루트 노드를 인덱스 1에 저장한다.',320,'인덱스는 0이 아닌 1부터','9.3 히프의 구현 방법'),
'bbase':b('B의 배열 표현은 깊이 0의 뿌리 노드를 배열의 0번 요소에 저장한다.',317,'배열의 0번 요소에 저장','7.2.3 힙의 구현'),
'nosearch':b('B의 힙은 이진 탐색을 할 수 없으며 어떤 노드를 찾으려면 모든 노드를 순회해야 한다.',312,'모든 노드를 순회','7.2 힙'),
'minroot':b('B의 힙에서 가장 작은 데이터를 갖는 노드는 뿌리 노드이다.',315,'가장 작은 데이터를 갖는 노드는 뿌리','7.2.2 힙의 최솟값 삭제 연산'),
'insert':a('최대 히프 삽입에서는 마지막 노드에 새 노드를 추가한 뒤 부모 노드와 비교하여 교환하며 올라간다.',325,'PARENT(i)','9.4 알고리즘 9.1'),
'delete':a('최대 히프 삭제에서는 루트를 삭제하고 마지막 노드를 루트로 옮긴 뒤 자식과 비교하여 교환하며 내려간다.',327,'마지막 노드를 루트 노드로','9.4 삭제 알고리즘'),
'cost':a('히프의 삽입과 삭제 연산은 최악의 경우 히프의 높이만큼 비교하므로 O(log₂n)이다.',332,'O(log','9.4 삽입과 삭제 연산의 복잡도 분석'),
'sort':a('히프 정렬은 히프의 삽입과 삭제 연산을 이용하여 정렬하며 전체 시간 복잡도는 O(nlog₂n)이다.',334,'O(nlog','9.5 히프 정렬'),
'partial':a('히프 정렬은 전체 자료를 정렬하지 않고 가장 큰 값 몇 개만 필요할 때 유용하다.',334,'가장 큰 값 몇 개만 필요','9.5 히프 정렬'),
'machine':a('기계 스케줄링 문제는 동일한 기계 m개에 서로 다른 작업 시간의 작업 n개를 할당하여 전체 작업을 가장 빨리 끝내도록 하는 문제이다.',335,'동일한 기계 m개','9.6 히프의 응용: 기계 스케줄링'),
'lpt':a('LPT(longest processing time first)는 작업 시간이 가장 긴 작업을 먼저 할당하는 근사해 방법이다.',335,'근사해','9.6 히프의 응용: 기계 스케줄링'),
'earliest':a('LPT에서는 기계가 사용 가능해질 때마다 남은 작업 중 시간이 가장 긴 작업을 할당한다.',335,'기계가 사용 가능하게 될 때마다','9.6 히프의 응용: 기계 스케줄링'),
'finishheap':a('기계의 종료 시간을 최소 히프에 저장하여 가장 먼저 사용 가능해지는 기계를 선택한다.',336,'종료 시간을 최소 히프에 저장','9.6 히프의 응용: 기계 스케줄링'),
'frequency':a('빈도수(frequencies)는 영문 텍스트에서 해당 글자가 나타나는 횟수이다.',340,'해당 글자가 나타나는 횟수','9.7 히프의 응용: 허프만 코드'),
'variable':a('빈도수에 따라 자주 등장하는 글자에는 짧은 비트열을, 잘 나오지 않는 글자에는 긴 비트열을 사용하는 가변 길이 코드로 전체 크기를 줄인다.',340,'가변 길이의 코드를 사용','9.7 히프의 응용: 허프만 코드'),
'prefix':a('허프만 코드(Huffman codes)에서는 모든 코드가 다른 코드의 첫 부분이 아니므로 왼쪽에서 오른쪽으로 조사하면 정확히 하나의 코드만 일치한다.',341,'모든 코드가 다른 코드의 첫 부분이 아니라는','9.7 히프의 응용: 허프만 코드'),
'bits':a('A의 허프만 트리에서 왼쪽 간선은 비트 1을, 오른쪽 간선은 비트 0을 나타낸다.',342,'왼쪽 간선은 비트 1','9.7 히프의 응용: 허프만 코드'),
'capacity':b('B의 Heap 구조체에서 Capacity는 Nodes 배열의 크기, UsedSize는 실제 배열에 들어 있는 큐 요소의 수이다.',318,'Capacity 필드는 힙의 용량','7.2.3 자료구조 선언'),
'expand':b('B의 HEAP_Insert()는 UsedSize가 Capacity에 도달하면 Capacity를 2배로 늘리고 realloc()으로 배열을 다시 할당한다.',319,'Capacity *= 2','7.2.3 삽입 연산 구현'),
'shrink':b('B의 최솟값 삭제 구현은 UsedSize가 Capacity/2보다 작으면 Capacity를 반으로 줄이고 realloc()을 호출한다.',321,'H->Capacity /= 2','7.2.3 최솟값 삭제 연산 구현'),
'pqnode':b('B의 힙 기반 우선순위 큐는 노드 구조체에 Priority 필드를 추가하고 Data 필드를 void*로 바꾸어 다양한 자료형을 담는다.',327,'Priority 필드 추가','7.3 힙 기반 우선순위 큐의 구현'),
}
u['learning']=[fs['priority'],fs['heap']]
u['concepts']=[group('우선순위 큐와 우선순위의 기준',*[fs[k] for k in ['priority','remove','criterion','bcriterion','apps']]),group('히프의 정의와 종류',*[fs[k] for k in ['heap','complete','loose','duplicate','max','min','minroot','nosearch']]),group('배열 표현과 B의 구현',*[fs[k] for k in ['abase','bbase','capacity','expand','shrink','pqnode']]),group('삽입·삭제·히프 정렬',*[fs[k] for k in ['insert','delete','cost','sort','partial']]),group('기계 스케줄링',*[fs[k] for k in ['machine','lpt','earliest','finishheap']]),group('허프만 코드',*[fs[k] for k in ['frequency','variable','prefix','bits']])]
u['procedures']=[{'title':'A의 최대 히프 삽입','steps':[a('히프의 크기를 1 증가시키고 새 원소를 마지막 위치에 둔다.',325,'heap_size','9.4 알고리즘 9.1'),a('새 원소가 루트가 아니며 부모의 키보다 크면 부모와 교환한다.',325,'A[i] > A[PARENT(i)]','9.4 알고리즘 9.1'),a('비교 위치를 부모 위치로 옮겨 같은 과정을 반복한다.',325,'i ← PARENT(i)','9.4 알고리즘 9.1')]},{'title':'B의 힙 최솟값 삭제','steps':[b('뿌리 노드를 삭제한 후 최고 깊이의 가장 우측 노드를 뿌리로 옮긴다.',315,'최고 깊이 가장 우측','7.2.2 힙의 최솟값 삭제 연산'),b('옮겨온 노드의 양쪽 자식을 비교하여 작은 쪽 자식과 위치를 교환한다.',315,'작은 쪽 자식과 위치를 교환','7.2.2 힙의 최솟값 삭제 연산'),b('옮겨온 노드가 잎 노드가 되거나 양쪽 자식보다 작으면 종료하고, 그렇지 않으면 교환을 반복한다.',315,'그렇지 않으면 단계','7.2.2 힙의 최솟값 삭제 연산')]},{'title':'A의 허프만 트리 구성','steps':[a('빈도수에 따라 글자를 나열하고 가장 작은 빈도수의 글자 2개를 추출한다.',341,'가장 작은 빈도수를 가지는 글자 2개','9.7 히프의 응용: 허프만 코드'),a('두 글자를 단말노드로 하는 이진트리를 만들고 루트에 두 자식의 값의 합을 저장한다.',341,'루트의 값은 각 자식노드의 값을 합한 값','9.7 히프의 응용: 허프만 코드'),a('합친 값을 글자들의 정렬된 리스트에 다시 삽입하고 가장 작은 값 2개를 합치는 과정을 최종 트리가 될 때까지 반복한다.',342,'합쳐진 값을 글자들의 리스트에 삽입','9.7 히프의 응용: 허프만 코드')]}]
u['syntax']=[code('B의 Heap 구조체','typedef struct tagHeap {\n    HeapNode* Nodes;\n    int Capacity;\n    int UsedSize;\n} Heap;','B','7.2.3 자료구조 선언',318,'typedef struct tagHeap')]
u['formulas']=[formula('최대·최소 히프의 키 관계','최대 히프: key(부모노드) ≥ key(자식노드); 최소 히프: key(부모노드) ≤ key(자식노드)','A','9.3 히프란?',320,'key(부모노드)','두 히프 모두 완전 이진트리.'),formula('A의 배열 인덱스 관계','왼쪽 자식 = 부모 인덱스*2; 오른쪽 자식 = 부모 인덱스*2+1; 부모 = 자식 인덱스/2','A','9.3 히프의 구현 방법',321,'부모 노드의 인덱스','루트 인덱스 1을 사용하는 배열 표현.'),formula('B의 배열 인덱스 관계','왼쪽 자식: 2k+1; 오른쪽 자식: 2k+2; 부모: (k-1)÷2의 몫','B','7.2.3 힙의 구현',318,'(k-1)÷2의 몫','k는 노드의 인덱스이며, 루트 인덱스는 0.')]
rows=[]
for label,ins,dele in [('순서 없는 배열','O(1)','O(n)'),('순서 없는 연결 리스트','O(1)','O(n)'),('정렬된 배열','O(n)','O(1)'),('정렬된 연결 리스트','O(n)','O(1)'),('히프','O(logn)','O(logn)')]:
    rows.append([a(label,318,label,'9.2 표 9-2 우선순위 큐의 구현 방법 비교'),a(ins,318,ins,'9.2 표 9-2 우선순위 큐의 구현 방법 비교'),a(dele,318,dele,'9.2 표 9-2 우선순위 큐의 구현 방법 비교')])
u['comparisons']=[{'title':'우선순위 큐의 구현 방법별 복잡도','headers':['표현 방법','삽입','삭제'],'rows':rows}]
u['terms']=[term(k,fs[v]) for k,v in [('우선순위 큐','priority'),('히프(heap)','heap'),('최대 히프(max heap)','max'),('최소 히프(min heap)','min'),('LPT','lpt'),('빈도수(frequencies)','frequency'),('허프만 코드(Huffman codes)','prefix'),('Capacity·UsedSize','capacity')]]
u['summary']=[fs['remove'],fs['cost'],fs['lpt'],fs['prefix']]
u['review']=[{'question':q,'answer':fs[k]} for q,k in [('B에서는 어떤 데이터가 더 높은 우선순위를 갖는가?','bcriterion'),('최대 히프에서 부모와 자식의 키 관계는 무엇인가?','max'),('히프 삽입·삭제의 최악 시간 복잡도는 무엇인가?','cost'),('A의 허프만 트리에서 왼쪽과 오른쪽 간선의 비트는 각각 무엇인가?','bits')]]
u['cheat'].update({'definitions':[term('우선순위 큐',fs['priority']),term('최대 히프',fs['max']),term('최소 히프',fs['min'])],'comparison_title':'두 책의 배열 시작 위치','comparison_rows':[[a('A',320,'인덱스','9.3 히프의 구현 방법'),fs['abase']],[b('B',317,'0번 요소','7.2.3 힙의 구현'),fs['bbase']]],'formulas':[u['formulas'][1],u['formulas'][2]]})
u['editor_notes']=['A의 본문 표기인 히프와 B의 힙을 각 출처에 맞추어 사용하였다.','A는 배열 루트 인덱스 1, B는 0을 사용하므로 두 인덱스 공식을 각각 제시하였다.','허프만 코드의 숫자 합계 예시는 발췌하지 않았으며, 간선의 비트는 A의 왼쪽 1·오른쪽 0 표기를 보존하였다.','기계 스케줄링의 LPT는 원문이 근사해라고 명시한 조건을 보존하였다.']
save(u)
