"""Source-grounded manuscript for assigned chapters, using supplied-page map."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP = json.loads((HERE / 'source_map.json').read_text(encoding='utf-8'))
PAGES = {p['printed_page']: p['pdf_page'] for p in MAP['pages'] if p.get('printed_page')}

def src(a, b=None):
    ps = [p for p in range(a, (b or a)+1) if p in PAGES]
    return {'pdf':[PAGES[p] for p in ps], 'printed':ps}

def p(text, a=None, b=None):
    d={'type':'p','text':text}
    if a is not None: d['source']=src(a,b)
    return d

def ul(items, a=None,b=None):
    d={'type':'bullets','items':items}
    if a is not None:d['source']=src(a,b)
    return d

def table(headers, rows, a=None,b=None):
    d={'type':'table','headers':headers,'rows':rows}
    if a is not None:d['source']=src(a,b)
    return d

def ref(cid):return {'type':'code_ref','id':cid}

def section(number,title,a,b,*blocks):
    return {'number':number,'title':title,'source':src(a,b),'blocks':list(blocks)}

def code(cid,title,a,b,text,meaning,process=None,output=None,cautions=None,excerpt=False,note=''):
    return {'id':cid,'title':title,'source':src(a,b),'code':text,'meaning':meaning,
      'process':process or [],'output':output or '[원문에 실행 결과 미제시]',
      'cautions':cautions or [],'excerpt':excerpt,'excerpt_note':note}

def finish(n,title,a,b,overview,flow,sections,codes,key,comparisons,review,index,limitations=None):
    obj={'id':f'C{n:02d}','order':n,'title':f'제{n}장. {title}','source':src(a,b),
      'overview':overview,'flow':flow,'sections':sections,'codes':codes,'key_points':key,
      'comparisons':comparisons,'review':review,'index_terms':[{'term':t,'section':s} for t,s in index],
      'coverage':[{'number':s['number'],'title':s['title'],'source':s['source'],
         'topics':[bl.get('text','')[:130] for bl in s['blocks'] if bl['type']=='p']} for s in sections],
      'limitations':limitations or []}
    (HERE/'chapters').mkdir(exist_ok=True)
    (HERE/'chapters'/f'{n:02d}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')


def chapter11():
    sections=[
      section('11.1','소개',234,234,
        p('**컨테이너**는 객체를 저장하는 일이 주목적인 클래스다. 작업에 적합한 컨테이너와 기본 연산을 선택하는 일은 프로그램 구성의 중요한 단계다. 이 장은 이름과 전화번호를 담는 Entry의 전화번호부로 표준 컨테이너를 비교한다. 예제에서는 불필요한 복잡성을 피하려고 전화번호를 int로 표현한다.')),
      section('11.2','vector',234,238,
        p('**vector<T>**는 T 타입 요소가 메모리에 연속적으로 저장되는 시퀀스다. 전형적인 구현은 첫 요소, 사용 중인 요소의 끝, 할당 공간의 끝을 가리키는 정보와 할당자로 구성된다. 기본 할당자는 new와 delete로 메모리를 관리한다.',234,235),
        p('인덱스는 0에서 시작하며 size()는 실제 요소 수를 알려준다. 요소 목록을 주는 {} 초기화와 초기 크기를 지정하는 () 초기화를 구별한다. 크기만 지정하면 요소는 타입의 기본 값으로 초기화되고, 두 번째 인자로 별도의 초기 값을 지정할 수 있다. 구간 for는 vector가 제공하는 요소 구간 전체를 순회한다.',235,236),
        ref('C11-E01'),
        p('**size와 capacity**는 다르다. size는 실제 요소 수, capacity는 재할당 없이 저장할 수 있는 슬롯 수다. reserve()는 요소를 위한 공간을 확보하며, 새 공간을 할당하면 기존 요소를 그곳으로 이동시킨다. push_back()은 끝에 요소를 추가하고 size를 1 늘린다. 원문의 간략한 Vector 구현은 공간이 부족할 때 용량을 늘려 매번 재할당하는 일을 피한다.',236,237),
        ref('C11-E02'),
        p('성능 향상을 기대한다는 이유만으로 reserve()를 호출할 필요는 없다. 원문은 vector의 증가 전략을 신뢰하고, 요소 포인터나 반복자의 유효성을 위해 재할당을 막아야 할 때 명시적으로 reserve()를 사용하도록 권한다. 대입과 초기화로 vector를 복사하면 각 요소도 복사되어 독립된 복사본이 생긴다. 요소가 많으면 비용이 클 수 있으므로 복사가 바람직하지 않을 때 참조·포인터 또는 이동 연산을 사용한다.',237,238)),
      section('11.2.1','요소',238,239,
        p('표준 컨테이너에는 내장 타입, 사용자 정의 타입, 포인터 등 거의 모든 타입을 요소로 사용할 수 있다. 요소를 삽입하면 값이 컨테이너 안으로 복사된다. 정수 7을 넣으면 요소 자체가 7의 값을 가지며, 다른 곳의 7을 가리키는 참조나 포인터를 저장하는 것이 아니다. 이 방식은 간결하고 빠르게 접근할 수 있는 저장 구조를 만든다.'),
        p('가상 함수에 의존하는 클래스 계층의 **다형적인 동작**을 유지하려면 객체 자체 대신 포인터나 스마트 포인터를 요소로 저장한다. 원문은 vector<Shape>로 Circle이나 Smiley를 저장하려는 방식을 피하고, vector<unique_ptr<Shape>>를 사용하는 형태를 제시한다.')),
      section('11.2.2','구간 검사',239,241,
        p('표준 vector의 operator[]는 구간 검사를 보장하지 않는다. book[book.size()]처럼 마지막 요소 다음을 참조하는 코드는 유효한 접근이 아니다. at()은 구간 밖 인덱스에 out_of_range를 던진다. 원문의 Vec는 vector의 생성자를 상속하고 operator[]를 at()에 연결한다.',239,240),
        ref('C11-E03'),
        p('Vec의 구간 밖 접근은 예외를 발생시켜 호출자가 잡을 수 있게 한다. 잡지 않은 예외가 있으면 프로그램은 잘 정의된 방식으로 종료된다. 원문은 main()의 try 블록과 기본 예외 핸들러에서 cerr로 진단을 출력하는 예도 제시한다. 구간 검사의 비용은 하드웨어·최적화·접근 방식에 따라 다르므로, 표준은 모든 인덱싱에 검사를 강제하지 않는다. 일부 구현은 디버그 검사 기능을 제공한다.',240,241),
        p('구간 for나 begin()/end() 범위를 이용한 순회는 추가적인 구간 검사 비용 없이 구간 밖 접근을 피한다. 코드에서 at()을 직접 사용할 수 있다면 Vec를 따로 만들 필요가 없다.',241,241)),
      section('11.3','list',241,244,
        p('**list**는 이중 연결 리스트다. 다른 요소를 이동시키지 않고 시퀀스 중간에 삽입·삭제할 때 사용한다. vector처럼 인덱스로 접근하는 대신 처음부터 원하는 요소를 찾는다. begin()은 첫 요소를, end()는 마지막 요소 다음을 가리키는 반복자를 반환한다.',241,242),
        ref('C11-E04'),
        p('반복자 p에 대해 *p는 요소를 참조하고 ++p는 다음 요소로 진행한다. p->m은 (*p).m과 같다. insert(p,elem)은 elem을 복사한 요소를 p 앞에 넣으며, p가 end()여도 된다. erase(p)는 p의 요소를 제거하고 소멸시킨다. 원문의 전화번호부 예제는 vector로도 작성할 수 있고, 짧은 시퀀스에서는 삽입·삭제까지 vector 쪽이 더 효율적일 수 있으므로 직관만으로 list를 선택하지 않는다.',243,243),
        p('**forward_list**는 순방향 순회만 제공하는 단일 연결 리스트다. 이전 요소 포인터가 없어 공간을 아끼며 빈 객체의 크기는 포인터 하나다. 요소 개수도 저장하지 않으므로 개수를 알려면 직접 세어야 한다. 원문은 이 특성이 필요할 때 선택하도록 한다.',243,244)),
      section('11.4','map',244,245,
        p('**map**은 키와 값의 쌍을 담고 조회에 최적화된 연관 컨테이너다. 원문은 일반적인 구현을 균형 이진 탐색 트리, 특히 레드-블랙 트리로 설명한다. 연관 배열 또는 딕셔너리라고도 한다. 키 타입의 값으로 인덱싱하면 대응하는 매핑된 타입의 값을 얻는다.'),
        ref('C11-E05'),
        p('**없는 키에 대한 []는 조회만 하는 연산이 아니다.** 키를 못 찾으면 값 타입의 기본 값을 가진 항목이 삽입된다. 전화번호부에서는 int의 기본 값 0이 유효하지 않은 번호를 나타낸다. 이런 항목이 들어가는 것을 원치 않으면 [] 대신 find()와 insert()를 사용한다.',245,245)),
      section('11.5','unordered_map',245,248,
        p('map의 조회 비용은 요소 수 n에 대해 O(log(n))이다. **unordered_map**은 해시 테이블을 이용하며 순서 비교 함수를 요구하지 않는다. map과 비슷하게 초기화하고 인덱싱할 수 있지만 요소 사이의 순서를 유지하지 않는다. 표준 라이브러리는 string·내장 타입·여러 라이브러리 타입의 기본 해시 함수를 제공한다.',245,246),
        p('사용자 정의 타입에는 해시 함수 객체를 전달하거나 std::hash를 특수화할 수 있다. 원문의 Record 예제는 이름과 product_code의 표준 해시를 배타적 논리합(^)으로 결합한다. 좋은 해시 함수에는 데이터에 대한 지식과 실험이 필요할 수 있다. 좋은 함수를 쓸 때 큰 unordered_map은 map보다 훨씬 빠를 수 있지만, 잘못된 해시 함수에서는 최악의 경우가 map보다 훨씬 느릴 수 있다.',246,248)),
      section('11.6','컨테이너 개요',248,250,
        table(['표준 컨테이너','원문에서 정리한 역할'],[
          ['vector<T> / list<T> / forward_list<T>','가변 크기 벡터 / 이중 연결 리스트 / 단일 연결 리스트'],
          ['deque<T>','양방향 큐'],['set<T> / multiset<T>','값만 가진 집합 / 값의 중복을 허용하는 집합'],
          ['map<K,V> / multimap<K,V>','키와 값의 연관 배열 / 키의 중복을 허용하는 map'],
          ['unordered_map / unordered_multimap','해시 조회를 사용하는 map / multimap'],
          ['unordered_set / unordered_multiset','해시 조회를 사용하는 set / multiset']],248,248),
        p('컨테이너는 std에 정의되고 <vector>, <list>, <map> 등에서 제공된다. queue·stack·priority_queue는 컨테이너 어댑터이며 array와 bitset은 고정 크기 구조다. 여러 컨테이너는 일관된 표기와 의미를 갖도록 설계되어, 알고리즘을 개별 컨테이너 타입과 독립적으로 기술할 수 있다.',249,250),
        table(['연산','의미와 주의'],[['value_type','요소 타입'],['begin()/end(), cbegin()/cend()','첫 요소 / 마지막 요소 다음; const 반복자도 제공'],['size()/empty()','요소 수 / 비어 있는지 검사'],['capacity()/reserve(k)','새 할당 없는 저장 용량 / 용량 확보'],['resize(k)','요소 수 변경; 추가 요소는 value_type{}'],['[k] / at(k)','구간 검사 없는 접근 / 구간 밖에서 예외'],['push_back(x) / emplace_back(a)','끝에 x 추가 / 인자로 새 요소를 직접 생성'],['insert(p,x) / erase(p)','p 앞에 삽입 / p 요소 제거'],['= / == / <','대입 / 요소의 상등성 / 사전 순 비교']],249,250),
        p('각 컨테이너에 맞는 연산을 선택해야 한다. vector는 연속 저장에 따른 저렴한 인덱싱·순회를 제공하지만 중간 삽입·삭제 때 요소 이동이 필요하다. list는 그 반대의 성격을 갖는다. 빈 경우가 많다면 한 워드만 필요한 forward_list를 고려할 수 있다. 배치 연산은 객체를 먼저 만들어 복사하는 대신, 전달한 생성자 인자로 컨테이너의 새 저장 공간에 요소를 직접 만든다.',250,250)),
      section('11.7','조언',251,252,
        ul(['표준 컨테이너를 익히고 기본 선택으로 vector를 고려한다. 성능은 직관이 아니라 측정으로 확인한다.',
          '순회에는 구간 for나 시작/끝 반복자를 사용한다. 구간 검사가 필요하면 at()을 사용하며 []가 검사한다고 가정하지 않는다.',
          'vector의 크기 변경 후 반복자를 그대로 사용하지 않는다. 포인터·반복자 유효성을 위한 재할당 방지와 단순 성능 추측을 구별한다.',
          '컨테이너 요소는 값이다. 다형적인 동작이 필요하면 포인터를 저장한다. 컨테이너 전달은 참조로, 반환은 값으로 한다.',
          '많은 데이터의 빠른 조회에는 순서 없는 컨테이너, 순서 있는 순회에는 map·set 같은 순서 있는 연관 컨테이너를 고려한다.',
          '크기로 생성할 때 ()와 요소 목록으로 생성할 때 {}를 구별한다. 해시 함수의 적절성은 실험으로 확인한다.']))
    ]
    codes=[
      code('C11-E01','vector의 구간 for 순회',235,235,r'''void print_book(const vector<Entry>& book)
{
    for (const auto& x : book) // "auto"에 대해서는 1.4절 참고
        cout << x << '\n';
}''','각 Entry를 복사하지 않고 const 참조로 받아 순서대로 출력하는 원문 함수다. Entry의 << 연산이 정의되어 있다는 전제가 있다.',
        ['book의 구간에서 각 요소 x를 참조한다.','각 요소를 cout으로 전달하고 줄바꿈 문자를 출력한다.']),
      code('C11-E02','용량을 확보한 뒤 요소를 생성하는 push_back',237,237,r'''template<typename T>
void Vector<T>::push_back(const T& t)
{
    if (capacity()<size()+1)        // t를 저장할 공간이 있는지 확인
        reserve(size()==0?8:2*size()); // 용량을 2배로 증가
    new(space) T{t}; // *space 를 t로 초기화
    ++space;
}''','원문의 간략한 Vector 클래스에서 공간 부족 시 reserve()를 호출하고 사용하지 않던 첫 슬롯에 T를 생성한다. 클래스 선언은 앞선 원문에 있으며 여기서는 함수 정의를 발췌했다.',
        ['현재 용량이 새 요소 하나를 담기에 충분한지 검사한다.','필요하면 빈 경우 8, 그 외에는 size의 두 배를 요청한다.','space에 t로 요소를 생성한 후 space를 증가시킨다.'],excerpt=True,note='Vector 클래스 선언은 생략하고, 원문의 push_back 함수 정의 전체를 발췌했습니다.'),
      code('C11-E03','at()에 연결하여 구간 검사하는 Vec',239,239,r'''template<typename T>
class Vec : public std::vector<T> {
public:
    using vector<T>::vector; // (Vec라는 이름으로) vector의 생성자를 사용

    T& operator[](int i) // 구간 검사
        { return vector<T>::at(i); }

    const T& operator[](int i) const // const 객체용 구간 검사; 4.2.1절
        { return vector<T>::at(i); }
};''','vector에서 다른 기능을 상속하고 const 여부에 맞춘 두 인덱싱 연산을 at() 호출로 재정의한다.',cautions=['at()은 인덱스가 구간을 벗어나면 out_of_range를 던진다.']),
      code('C11-E04','반복자로 전화번호부 선형 탐색',243,243,r'''int get_number(const string& s)
{
    for (auto p = phone_book.begin(); p!=phone_book.end(); ++p)
        if (p->name==s)
            return p->number;
    return 0; // 0 은 "수를 찾지 못함"을 의미
}''','list의 begin()부터 end()까지 이름을 비교해 일치하는 항목의 number를 반환한다. 0은 찾지 못했음을 표시한다.',
        ['p가 각 요소를 가리키게 이동한다.','name이 s와 같으면 number를 반환한다.','끝에 이르면 0을 반환한다.']),
      code('C11-E05','map의 키로 전화번호 조회',245,245,r'''int get_number(const string& s)
{
    return phone_book[s];
}''','원문의 map<string,int> 전화번호부에서 이름 s로 번호를 조회한다. 같은 페이지의 map 초기화 코드는 생략했다.',cautions=['s가 없으면 기본 값 0인 항목이 삽입된다. 삽입을 원치 않으면 find()와 insert()를 사용한다.'],excerpt=True,note='동일 페이지의 map 초기화는 생략하고 get_number 함수 정의 전체를 발췌했습니다.')
    ]
    comparison=[{'title':'map과 unordered_map','source':src(245,248),'headers':['비교 기준','map','unordered_map'],'rows':[
      ['조회 구조','균형 이진 탐색 트리','해시 테이블'],['필요한 함수','순서 비교 함수; 기본적으로 <','해시 함수'],
      ['요소 순서','순서 있는 시퀀스','순서 유지 안 함'],['성능 조건','조회 O(log(n))','좋은 해시는 큰 데이터에서 빠름; 나쁜 해시는 최악의 경우 훨씬 느림']]}]
    finish(11,'컨테이너',233,252,
      ['컨테이너는 객체를 저장하는 자원 핸들이며 시퀀스를 정의한다.','vector의 크기·용량·요소 값 의미와 구간 검사를 이해한다.','list·map·unordered_map을 저장 구조와 조회 조건으로 구분한다.'],
      ['연속 저장 vector와 성장 방식','요소·다형성·구간 검사','연결 구조와 연관 컨테이너','공통 연산과 선택 기준'],sections,codes,
      ['기본 컨테이너는 vector로 고려하되 성능은 측정한다.','size는 요소 수, capacity는 저장 가능한 슬롯 수다.','[]의 구간 검사와 없는 키 삽입 동작은 컨테이너에 따라 다르다.','컨테이너의 값 저장과 다형적인 객체 포인터 저장을 구분한다.'],comparison,
      ['vector의 연속 저장·복사·성장·reserve와 반복자 유효성의 관계를 복습한다.','구간 밖 접근을 at()·구간 for·시작/끝 반복자로 다루는 방식을 정리한다.','list의 삽입·삭제와 vector의 짧은 시퀀스 효율을 함께 고려한다.','map의 []는 없는 키를 삽입하며 unordered_map은 해시 품질과 순서 유무를 고려해야 한다.'],
      [('컨테이너','11.1'),('vector','11.2'),('capacity / reserve','11.2'),('컨테이너 요소','11.2.1'),('구간 검사 / at','11.2.2'),('list','11.3'),('forward_list','11.3'),('map','11.4'),('unordered_map','11.5'),('배치 연산 / emplace_back','11.6')])


def chapter12():
    sections=[
      section('12.1','소개',254,255,
        p('표준 라이브러리 알고리즘은 컨테이너에 저장한 요소의 정렬·출력·검색·부분집합 추출 같은 공통 작업을 제공한다. 입력 시퀀스는 첫 요소를 포함하고 끝 위치는 포함하지 않는 **반개구간 [begin:end)**이며, 첫 요소와 마지막 요소 다음을 가리키는 반복자 쌍으로 나타낸다.'),
        p('sort는 비교 연산으로 입력 구간을 정렬하고 unique_copy는 이웃한 중복을 복사하지 않는다. 기존 출력 위치를 지정하면 그 뒤 요소를 덮어쓰므로 충분한 출력 공간이 있어야 한다. back_inserter는 컨테이너 뒤에 삽입하는 반복자를 만들어 필요에 따라 컨테이너를 확장한다. 이 방식은 미리 크기를 정하거나 C 스타일 realloc()으로 직접 관리할 필요를 줄인다.'),ref('C12-E01')),
      section('12.2','반복자의 사용',255,259,
        p('begin()과 end()는 컨테이너에서 반복자를 얻는 대표적인 함수다. find는 찾은 요소의 반복자를 반환하고, 찾지 못하면 입력 구간의 end()를 반환한다. 그러므로 반환값을 끝 반복자와 비교하여 검색 성공을 판정한다.',255,256),
        p('원문의 find_all은 일치하는 값 자체 대신 그 위치를 가리키는 반복자들의 vector를 반환한다. 이 반복자로 원래 요소를 바꿀 수도 있으므로, 변경할 문자열이나 컨테이너는 const가 아닌 참조로 받는다. 처음에는 string 전용으로 작성하고 이후 컨테이너 C와 값 V의 템플릿으로 일반화한다.',256,258),
        ref('C12-E02'),
        p('typename C::iterator의 typename은 iterator가 값이 아닌 타입임을 컴파일러에 알려준다. 타입 별칭 Iterator<T>는 이 세부사항을 숨긴다. 알고리즘은 반복자로 데이터에 적용되므로 저장 컨테이너를 알 필요가 없고, 컨테이너 역시 어떤 알고리즘이 쓰이는지 알 필요 없이 반복자를 제공한다. 이 분리가 일반적이고 유연한 소프트웨어의 바탕이다.',258,259)),
      section('12.3','반복자 타입',259,260,
        p('반복자는 특정 타입의 객체이며 저장 구조에 맞는 정보를 가진다. vector에서는 단순 포인터가 합리적인 구현일 수 있고, vector 포인터와 인덱스를 함께 저장하면 구간 검사를 할 수 있다. list에서는 다음 링크를 따라가야 하므로 단순 요소 포인터가 아니라 링크를 가리키는 정보가 필요하다.'),
        p('구현은 달라도 ++로 다음 요소를 가리키고 *로 요소를 참조하는 공통 의미와 명명 규칙을 따른다. 이러한 요구를 표현한 것이 Iterator 컨셉이다. 사용자에게 내부 구현 전체가 필요한 것은 아니며 각 컨테이너의 iterator·const_iterator라는 관례적인 이름을 이용하면 된다.')),
      section('12.4','스트림 반복자',261,263,
        p('요소 시퀀스는 컨테이너에만 있는 것이 아니다. 입력 스트림도 값의 시퀀스를 만들고 출력 스트림도 시퀀스를 받는다. ostream_iterator는 스트림과 출력 타입을 지정해 만들며, 역참조 위치에 대입하면 스트림으로 출력한다. ++는 배열 포인터와 같은 사용 방식을 흉내 낸다. istream_iterator는 입력 스트림을 읽기 전용 컨테이너처럼 다루게 한다.',261,261),
        ref('C12-E03'),
        p('기본 생성한 istream_iterator는 입력 끝의 보초 값으로 쓰인다. ostream_iterator의 두 번째 인자는 출력 값 사이의 구분자다. 예제는 파일의 단어를 vector로 읽고 정렬한 뒤 unique_copy로 중복을 제거해 출력한다. 원문은 set을 사용해 입력 단계에서 중복을 없애고 순서를 유지하면 sort·unique_copy 대신 copy만 쓸 수 있다는 대안도 제시한다. 코드 길이를 줄이는 선택은 취향과 가독성을 함께 고려한다.',262,263)),
      section('12.5','술어',263,264,
        p('**술어**는 알고리즘이 각 요소에 적용할 조건을 전달하는 수단이다. find가 지정 값과 같은 요소를 찾는 데 비해 find_if는 전달된 술어가 참이 되는 첫 요소를 찾는다. 원문의 map 예제는 값 부분이 42보다 큰 쌍을 찾는다. 비교 기준을 저장한 함수 객체와 람다 표현식 모두 사용할 수 있다.'),ref('C12-E04'),
        p('**술어는 적용 대상 요소를 변경하면 안 된다.** 원문의 Greater_than은 비교값을 val에 저장하고 pair의 second를 이 값과 비교한다. 람다 버전도 같은 비교를 직접 표현한다.',264,264)),
      section('12.6','알고리즘 요약',264,266,
        p('이 책에서 표준 알고리즘은 요소 시퀀스에 적용되는 함수 템플릿 연산이다. std에 정의되고 <algorithm>에서 제공된다. 컨테이너뿐 아니라 string과 내장 배열에도 적용할 수 있다.',264,266),
        table(['알고리즘','구간에 대한 역할'],[
          ['for_each','모든 요소에 함수 적용'],['find / find_if','지정 값 / 술어를 만족하는 첫 위치'],
          ['count / count_if','지정 값 / 술어에 맞는 요소 개수'],['replace / replace_if','지정 값 / 술어에 맞는 요소를 새 값으로 대체'],
          ['copy / copy_if / move','전체 복사 / 조건에 맞는 요소 복사 / 이동'],['unique_copy','이웃한 중복을 제외하고 복사'],
          ['sort','기본 < 또는 주어진 비교 연산으로 정렬'],['equal_range','정렬된 구간에서 같은 값의 부분 구간을 찾음; 기본적으로 이진 탐색'],
          ['merge','정렬된 두 구간을 기본 또는 지정 비교 연산으로 병합']],265,265),
        p('일부 알고리즘은 요소 값을 변경하지만 입력 시퀀스 자체에 요소를 추가하거나 제거하지는 않는다. 반복자만으로는 소유 컨테이너를 알 수 없기 때문이다. 크기를 바꾸려면 back_inserter처럼 컨테이너를 아는 수단이나 push_back·erase 같은 컨테이너 연산이 필요하다. 원문은 직접 루프를 만들기 전에 잘 설계된 표준 알고리즘으로 표현할 수 있는지 살피도록 권한다.',266,266)),
      section('12.7','컨셉(C++20)',266,272,
        p('**이 절은 원문 집필 시점의 Ranges Technical Specification과 C++20에 대한 전망을 설명한다.** 원문은 <experimental/ranges>의 컨셉을 소개하며 비슷한 기능이 C++20의 std에 들어가기를 기대한다고 쓴다. 이 노트는 그 시점의 명칭과 조건을 그대로 다룬다.',266,266),
        p('Range는 begin/end 시퀀스의 일반화다. {begin,end}, {begin,n} 또는 {begin,pred}로 구간을 정의할 수 있다. n은 요소 수, pred는 반복자가 끝에 도달했는지 판정하는 술어다. 마지막 방식은 동적으로 정의되거나 무한한 시퀀스도 표현한다. 이 구간을 받는 알고리즘은 sort(v)와 같은 호출을 가능하게 한다.',266,267),
        table(['핵심 컨셉','원문에서 요구하는 성질'],[
          ['Same / DerivedFrom / ConvertibleTo','같은 타입 / 파생 관계 / 변환 가능'],['CommonReference / Common','공통 참조 타입 / 공통 타입을 가짐'],
          ['Integral / SignedIntegral / UnsignedIntegral','정수 / 부호 있는 정수 / 부호 없는 정수'],
          ['Assignable / SwappableWith / Swappable','대입 가능 / 두 타입 값의 교환 가능 / 같은 타입 사이의 교환 가능']],267,268),
        p('Common은 여러 타입을 공통 타입 c로 변환한 뒤에도 비교가 합리적이어야 하는 알고리즘을 기술하는 데 쓰인다. 원문은 string과 char*, int와 double의 비교를 들고 string과 int는 비교하지 않는다고 구별한다. 라이브러리가 적당한 정의를 제공하지 않는 경우가 아니라면 common_type_t를 직접 특수화할 필요가 없다.',268,268),
        table(['비교·객체 컨셉','핵심 관계'],[
          ['Boolean','불리언 값으로 사용 가능'],['WeaklyEqualityComparableWith / WeaklyEqualityComparable','서로 다른 타입 / 같은 타입 값의 ==·!= 비교'],
          ['EqualityComparableWith / EqualityComparable','상등성 비교; 같은 타입 버전은 T,T 관계'],['StrictTotallyOrderedWith / StrictTotallyOrdered','<·<=·>·>=를 이용한 완전 순서; 같은 타입 버전은 T,T 관계'],
          ['Destructible / Constructible / DefaultConstructible','소멸 및 주소 연산 / 주어진 인자로 생성 / 기본 생성'],['MoveConstructible / CopyConstructible','이동 생성 / 복사와 이동 생성'],
          ['Movable / Copyable','이동 생성·대입·교환 / 복사 생성 및 복사 대입을 포함'],['Semiregular / Regular','Copyable와 기본 생성 / 여기에 상등성 비교를 포함']],268,269),
        p('원문은 WeaklyEqualityComparableWith와 WeaklyEqualityComparable를 혼용하면 오버로드 기회가 줄 수 있다고 경고한다. Regular 타입은 int처럼 동작해 사용이 단순해지는 이상적인 성격으로 설명하며, ==가 없는 기본적인 클래스는 Semiregular로 구분한다.',269,269),
        table(['호출 가능 컨셉','원문에서 설명한 의미'],[
          ['Invocable<F,Args>','Args 인자 목록으로 F 호출'],['InvocableRegular<F,Args>','호출 가능하고 상등성을 보존'],
          ['Predicate<F,Args>','호출하여 bool 반환'],['Relation<F,T,U>','Predicate<F,T,U>'],
          ['StrictWeakOrder<F,T,U>','Relation이 엄격하고 약한 순서를 제공']],270,270),
        p('상등성 보존은 x==y일 때 f(x)==f(y)가 되는 성질이다. 비교 연산에는 일반적으로 엄격하고 약한 순서를 가정한다. 원문은 Relation과 StrictWeakOrder의 차이가 의미론적인 것이며, 이 차이를 이름으로 의도에 드러낸다고 설명한다.',270,270),
        table(['반복자·구간 컨셉','원문에서의 조건과 관계'],[
          ['Iterator / Sentinel / SizedSentinel','증가·역참조 / 구간 끝의 보초 / 차이 연산이 가능한 보초'],['InputIterator / OutputIterator','입력의 읽기 / 출력의 쓰기'],
          ['ForwardIterator / BidirectionalIterator','여러 번 순방향 순회 / 여기에 -- 지원'],['RandomAccessIterator','양방향 반복자에 원문 표의 산술·인덱싱 연산을 추가'],
          ['Permutable / Mergeable / Sortable','이동·교환 / 정렬 구간 병합 / 지정 관계로 정렬 가능'],['Range / SizedRange','시작 반복자와 보초 / 크기를 상수 시간에 알 수 있음'],
          ['View / BoundedRange','상수 시간 복사·이동·대입 / 반복자와 보초의 타입이 같음'],
          ['InputRange / OutputRange / ForwardRange / BidirectionalRange / RandomAccessRange','각 이름에 대응하는 반복자 컨셉을 만족하는 구간']],270,271),
        p('보초는 주어진 반복자에서 시작해 종료 술어를 만족할 때까지 순회하게 하는 개념이다. 원문은 C 스타일 문자열에서 *p==0을 끝 조건으로 삼는 예를 든다. 반복자의 종류는 알고리즘을 더 적절하게 선택하는 데 활용한다.',271,272)),
      section('12.8','컨테이너 알고리즘',272,272,
        p('원문은 Ranges를 기다리지 않고도 컨테이너를 받아 내부에서 begin()/end() 버전을 호출하는 간단한 sort 래퍼를 작성할 수 있다고 설명한다. 기본 비교 버전과 술어 버전을 별도 Estd 네임스페이스에 두면 std 사용 시 충돌을 피하고 나중에 Range로 교체하기도 쉽다.')),
      section('12.9','병렬 알고리즘',273,274,
        p('각 데이터 항목의 계산이 서로 독립적이면 같은 작업을 병렬로 수행할 수 있다. **병렬 실행**은 여러 스레드에서 작업하고 **벡터화된 실행(SIMD)**은 한 스레드에서 벡터화로 작업한다. <execution>은 seq·par·par_unseq 실행 정책을 제공한다.'),ref('C12-E05'),
        p('정책은 실행에 대한 힌트이며 실제 병렬성은 컴파일러와 런타임 스케줄러가 정한다. 효과는 알고리즘·요소 수·하드웨어·사용률에 따라 달라지므로 반드시 실험으로 확인한다. 원문은 12.6절 표의 알고리즘 가운데 equal_range를 병렬 정책 대상에서 제외해 설명한다. 병렬 실행을 요청할 때 데이터 경합과 데드락을 피해야 한다.')),
      section('12.10','조언',274,274,
        ul(['알고리즘의 입력은 반복자로 정의한 반개구간이며, 검색 실패는 일반적으로 입력 끝으로 표시한다.',
          '알고리즘은 전달된 시퀀스 자체에 요소를 추가·제거하지 않는다.',
          '직접 루프를 만들기 전에 표준 제네릭 알고리즘을 고려한다. 함수 객체와 술어로 동작을 확장하되 술어가 인자를 바꾸지 않게 한다.',
          '반복자 쌍 방식이 번거로우면 컨테이너/구간 알고리즘을 사용한다.']))]
    codes=[
      code('C12-E01','정렬 후 중복 없이 새 list에 삽입',255,255,r'''list<Entry> f(vector<Entry>& vec)
{
    list<Entry> res;
    sort(vec.begin(),vec.end());
    unique_copy(vec.begin(),vec.end(),back_inserter(res)); // res 뒤에 붙이기
    return res;
}''','vec를 정렬하고 이웃한 중복을 제외한 요소를 res 뒤에 넣는다. Entry에는 순서 비교와 상등성 비교가 정의되어 있어야 한다.',
        ['sort가 vec의 요소를 정렬한다.','unique_copy가 연속 중복을 제외한다.','back_inserter가 res를 확장하며 요소를 추가하고 res를 값으로 반환한다.']),
      code('C12-E02','반복자 타입 별칭을 사용한 제네릭 find_all',258,258,r'''template<typename T>
using Iterator = typename T::iterator; // T의 반복자

template<typename C, typename V>
vector<Iterator<C>> find_all(C& c, V v) // c에서 v가 나타나는 곳을 모두 찾기
{
    vector<Iterator<C>> res;
    for (auto p = c.begin(); p!=c.end(); ++p)
        if (*p==v)
            res.push_back(p);
    return res;
}''','일치하는 요소를 가리키는 컨테이너 C의 반복자들을 반환한다. 원문의 string·list<double>·vector<string>에 공통으로 쓰는 알고리즘이다.'),
      code('C12-E03','파일 단어를 정렬하고 중복 없이 출력',262,262,r'''int main()
{
    string from, to;
    cin >> from >> to; // 원본과 출력 파일 이름 가져오기

    ifstream is {from}; // 파일 "from"의 입력 스트림
    istream_iterator<string> ii {is}; // 스트림에 사용할 입력 반복자
    istream_iterator<string> eos {}; // 입력(의 끝을 나타내는) 보초 값

    ofstream os {to}; // 파일 "to"의 출력 스트림
    ostream_iterator<string> oo {os,"\n"}; // 스트림의 출력 반복자

    vector<string> b {ii,eos}; // b는 입력으로부터 초기화된 벡터
    sort(b.begin(),b.end()); // 버퍼를 정렬

    unique_copy(b.begin(),b.end(),oo); // 버퍼를 출력에 복사, 중복된 값은 버림

    return !is.eof() || !os; // 에러 상태 반환(1.2.1절, 10.4절)
}''','입력·출력 파일 이름을 읽어 단어를 vector에 저장하고 정렬한 뒤 중복을 제외해 출력하는 원문 프로그램이다.',
        ['입력 반복자 ii와 끝 보초 eos로 vector를 초기화한다.','정렬한 버퍼에 unique_copy를 적용한다.','oo를 통해 단어마다 줄바꿈을 붙여 출력하고 스트림 상태로 반환값을 정한다.']),
      code('C12-E04','람다 술어를 전달한 find_if',264,264,r'''auto p = find_if(m.begin(), m.end(), [](const pair<string,int>& r) {
    return r.second>42;
});''','원문의 map<string,int>에서 값 부분이 42보다 큰 첫 항목을 찾는 람다 버전이다. m의 정의 및 함수 객체 버전은 같은 설명에서 발췌하지 않았다.',cautions=['술어는 적용 대상 요소를 변경하지 않는다.'],excerpt=True,note='원문 map 검색 설명 중 람다 호출 블록 전체를 발췌했습니다. m의 정의와 Greater_than 대안은 생략했습니다.'),
      code('C12-E05','정렬의 실행 정책',273,273,r'''sort(v.begin(),v.end()); // 순차
sort(seq,v.begin(),v.end()); // 순차(기본과 동일)
sort(par,v.begin(),v.end()); // 병렬
sort(par_unseq,v.begin(),v.end()); // 병렬 혹은 벡터화''','같은 정렬 작업에 순차·병렬·병렬 또는 벡터화 실행 정책을 요청하는 원문 비교다.',cautions=['병렬 정책은 가능한 경우에 적용하는 힌트다. 효과는 실험으로 확인하며 데이터 경합과 데드락을 피해야 한다.'])]
    comparisons=[{'title':'병렬 실행과 벡터화된 실행','source':src(273,273),'headers':['기준','병렬 실행','벡터화된 실행'],'rows':[
      ['실행 수단','여러 스레드; 여러 코어일 수도 있음','한 스레드에서 벡터화(SIMD)'],['정책 요청','par','par_unseq가 병렬 또는 벡터화를 허용'],['보장 조건','가능한 경우; 정책은 힌트','가능한 경우; 정책은 힌트']]}]
    finish(12,'알고리즘',253,274,
      ['반복자로 표현한 구간에 공통 알고리즘을 적용한다.','컨테이너·알고리즘 분리, 검색 실패, 출력 공간 조건을 확인한다.','술어·스트림 반복자·컨셉·실행 정책으로 알고리즘 사용을 확장한다.'],
      ['반개구간과 출력 삽입 반복자','반복자 사용과 구현 타입','입출력 및 술어','알고리즘 표·원문 시점의 Ranges 컨셉','컨테이너 래퍼와 병렬 정책'],sections,codes,
      ['입력 끝은 마지막 요소 다음이며 검색 실패 표시에 사용한다.','출력 알고리즘에 충분한 공간을 제공하거나 back_inserter로 확장한다.','알고리즘의 요소 값 변경과 컨테이너 크기 변경은 다르다.','원문의 Ranges 명칭과 C++20 전망은 집필 시점의 설명이다.','병렬 정책은 실제 병렬 실행이나 성능 향상을 보장하지 않는다.'],comparisons,
      ['반복자가 컨테이너 저장 구조와 알고리즘을 연결하는 공통 인터페이스임을 정리한다.','find와 find_if, 일반 출력 반복자와 back_inserter의 조건을 구분한다.','입력·출력·순방향·양방향·임의 접근 반복자의 요구와 Range 계열을 연결한다.','술어의 비변경 조건과 병렬 계산의 독립성·경합 방지 조건을 복습한다.'],
      [('알고리즘 / 반개구간','12.1'),('back_inserter','12.1'),('find / find_all','12.2'),('반복자 타입','12.3'),('스트림 반복자','12.4'),('술어 / find_if','12.5'),('표준 알고리즘','12.6'),('Ranges TS / 컨셉','12.7'),('Regular','12.7'),('보초 / Sentinel','12.7'),('컨테이너 알고리즘','12.8'),('병렬 알고리즘 / 실행 정책','12.9')],
      ['[원문 확인 필요] 책 270쪽 RandomAccessIterator 표의 일부 산술 기호는 제공 이미지에서 물음표 모양으로 보인다. 해당 기호를 임의로 복원하지 않고 연산 범주만 요약했다.'])


def chapter13():
    sections=[
      section('13.1','소개',276,276,
        p('이 장은 컨테이너·입출력 같은 큰 분류에 딱 들어맞지 않지만 널리 쓰이는 표준 라이브러리 유틸리티를 다룬다. 설계와 프로그램을 표현하는 일반적인 용어로 쓰이는 타입과, 다른 라이브러리 기능을 구현하는 재료가 포함된다. 유틸리티는 지나치게 복잡하거나 다른 기능에 의존하지 않아야 한다.')),
      section('13.2','자원 관리',276,277,
        p('**자원**은 획득한 후 언젠가 해제해야 하는 것으로 메모리·소켓·스레드 핸들·파일 핸들이 예다. 누수는 장시간 프로그램의 성능 저하나 충돌뿐 아니라 짧은 프로그램의 자원 부족도 일으킬 수 있다. 표준 라이브러리는 자원을 책임지는 객체의 생성·소멸과 자원의 생애주기를 연결해 누수를 막는다.'),
        p('**RAII**는 생성자에서 자원을 획득하고 소멸자에서 해제하는 관례적 관리 방식이다. 원문의 scoped_lock은 생성 시 mutex를 얻고, return·함수 끝·예외 등 어떤 방식으로 스코프를 벗어나도 소멸자로 해제한다. vector·map·string·iostream의 저장 공간이나 파일 핸들도 같은 원리에 따라 관리된다.')),
      section('13.2.1','unique_ptr과 shared_ptr',277,281,
        p('<memory>의 **unique_ptr**은 유일한 소유권을, **shared_ptr**은 공유된 소유권을 표현한다. 자유 저장소의 객체를 스마트 포인터에 맡기면 예외나 이른 반환에서 해제를 빠뜨리는 일을 막을 수 있다. 다만 지역 객체나 컨테이너 같은 더 높은 수준의 자원 핸들로 표현할 수 있다면 그것을 먼저 사용한다.',277,278),ref('C13-E01'),
        p('unique_ptr은 개별 객체나 배열의 핸들이며 소유권 전달에 이동을 사용한다. shared_ptr은 복사하여 소유권을 나누고 마지막 소유자가 소멸할 때 자원을 해제한다. 함수에 shared_ptr를 넘기면 함수가 종료된 뒤에도 복사본이 남을 수 있으므로, 자원 소멸 시점을 단순히 호출 함수의 끝으로 예상하면 안 된다. 공유에는 추가 비용과 생애주기 예측의 어려움이 있어 꼭 공유해야 할 때만 사용한다.',278,279),
        p('make_unique와 make_shared는 객체 생성과 포인터 인계를 함께 처리해 잘못된 포인터 전달이나 인계 누락을 줄인다. 원문은 make_shared가 소유자 수를 세기 위한 별도 할당을 줄일 수 있다는 이점도 설명한다. 포인터가 필요한 대표적인 경우는 다형적인 객체를 참조하거나 객체를 공유하는 경우다. 객체 컬렉션 반환은 컨테이너로 처리할 수 있다.',280,281),
        p('스마트 포인터는 여전히 포인터다. 특히 shared_ptr 자체는 소유자들의 읽기·쓰기 규칙을 명시하지 않으므로, 수명 관리만으로 자원 경합 같은 문제까지 해결되지는 않는다.',280,280)),
      section('13.2.2','move()와 forward()',281,283,
        p('이동과 복사의 선택은 대부분 암묵적이지만, 복사할 수 없는 unique_ptr을 다른 소유자로 넘길 때처럼 명시적인 이동이 필요할 수 있다. **std::move() 자체가 자원을 이동시키는 것은 아니다.** 전달한 객체를 rvalue 참조로 변환해 이동 생성자나 이동 대입 연산이 선택되게 유도한다.',281,282),ref('C13-E02'),
        p('이동 후에도 원본 객체는 남는다. 원문은 move한 문자열을 나중에 다시 인덱싱하는 위험을 들어, 확실하고 큰 성능 개선이 있을 때만 명시적으로 move를 사용하도록 한다. 이동 후 상태는 일반적으로 정해지지 않지만 표준 라이브러리 타입은 소멸·대입 가능한 상태로 남는다고 설명한다. 이 원문은 vector·string 같은 컨테이너를 이동 후 비어 있는 상태로 설명한다.',282,283),
        p('**완벽한 포워딩**은 인자의 성격을 바꾸지 않고 다른 함수로 넘기는 것이다. std::forward()는 lvalue와 rvalue의 차이를 처리한다는 점에서 move와 구별된다. 포워딩할 때는 std::forward를 사용하고 같은 객체를 두 번 포워딩하지 않는다. 포워딩 뒤에 그 객체를 다시 사용하지 않도록 주의한다.',283,283)),
      section('13.3','구간 검사: gsl::span',284,286,
        p('포인터와 요소 수를 따로 전달하는 인터페이스는 두 값이 실제 배열과 일치한다는 관례에 의존해 구간 에러를 일으키기 쉽다. **gsl::span**은 요소 시퀀스의 포인터와 길이를 함께 표현하는 구간 참조다. vector나 내장 배열 등의 연속 요소를 가리키며, 그 요소를 소유하지 않는다. string_view나 반복자 쌍과 유사하지만 문자 읽기 전용에 한정되지 않는다.',284,285),
        p('배열에서 span을 직접 만들면 컴파일러가 요소 수를 세므로 간단하고 안전하다. 별도로 포인터·길이로 span을 만들 때는 그 선택이 명시적으로 드러난다. 함수끼리 span을 넘기면 포인터와 개수를 각각 넘기는 것보다 단순하다. 인덱싱의 구간 검사는 에러 시 gsl::fail_fast를 던진다고 원문이 설명하며, 성능이 중요한 코드에서는 검사를 막을 수 있다고 한다.',285,286),
        p('이 절의 span은 원문 시점에 표준으로 제안된 GSL 타입이다. 원문은 향후 std::span의 구간 에러 처리에 계약을 사용하기를 기대한다고 쓴다. 이 전망을 현재의 표준 사실로 바꾸어 보충하지 않는다. 문자 구간에는 gsl::string_span을 제시한다.',284,286)),
      section('13.4','특수한 컨테이너',287,287,
        table(['유사 컨테이너','원문에서 정리한 역할'],[
          ['T[N] / array<T,N>','연속 저장된 T 요소 N개의 고정 크기 시퀀스; array는 내장 배열의 여러 문제를 줄임'],
          ['bitset<N> / vector<bool>','N비트의 고정 시퀀스 / vector 특수화로 저장한 비트 시퀀스'],
          ['pair<T,U> / tuple<T...>','두 요소 / 임의의 여러 타입을 가진 요소 시퀀스'],
          ['basic_string<C> / valarray<T>','문자열 연산이 있는 문자 시퀀스 / 수치 연산을 제공하는 수치 배열']]),
        p('여러 컨테이너는 서로 다르거나 겹치는 요구를 만족한다. pair와 tuple은 이형이며, 다른 컨테이너는 같은 타입의 요소를 담는 동형이다. array·vector·tuple의 요소는 연속 할당되고 forward_list·map은 연결 구조다.')),
      section('13.4.1','array',287,290,
        p('**정리 범위 제한:** 제공 자료에는 책 288~289쪽이 없다. array 설명의 앞부분을 확인할 수 없으므로 287쪽 표, 290쪽의 이어지는 설명, 313쪽 조언에서 확인되는 내용만 정리한다.',287,290),
        p('array는 크기를 알고 있어 표준 알고리즘과 함께 쓸 수 있고 =로 복사할 수 있다. 원문이 강조하는 장점은 내장 배열에서 생길 수 있는 예기치 않은 포인터 변환을 막는다는 것이다. Circle 배열을 Shape*로 받아 인덱싱하면 sizeof(Shape)<sizeof(Circle)이라는 원문의 전제하에 잘못된 오프셋이 생기지만 array는 그 포인터 변환을 허용하지 않는다. 290쪽의 이어지는 문장은 스택이 제한된 자원이며 스택 오버플로우가 생길 수 있다는 주의도 포함한다.',290,290)),
      section('13.4.2','bitset',290,292,
        p('**bitset<N>**은 컴파일 시간에 정한 N비트의 구간에 연산을 제공한다. 참/거짓·켜짐/꺼짐 등의 플래그 집합을 나타내며, 내장 정수에 담기 어려운 비트 집합을 다루는 데 편리하다. 비트에 번호 대신 이름을 붙여야 한다면 원문은 set이나 열거형을 권한다.',290,291),
        p('정수나 문자열로 초기화할 수 있고 비트별 연산과 시프트를 제공한다. 시프트는 0을 밀어 넣는다. to_ullong()과 to_string()은 생성자의 반대 방향으로 변환한다. 출력은 높은 자릿수의 비트가 왼쪽에 오며 bitset 자체의 출력 연산자도 사용할 수 있다.',291,292),ref('C13-E03')),
      section('13.4.3','pair와 tuple',292,295,
        p('값들의 모음 자체가 필요하면 간단한 struct 또는 pair·tuple을 사용할 수 있다. **pair**는 first와 second라는 일관된 멤버 이름을 가진 두 값의 묶음이다. equal_range는 정렬된 입력에서 같은 값에 해당하는 부분 구간을 두 반복자의 pair로 반환한다. 요소가 연산을 지원하면 pair의 대입·비교도 가능하다.',292,293),
        p('타입 추론이나 make_pair로 중복된 타입 명시를 줄일 수 있다. 둘보다 많거나 적은 요소에는 **tuple**을 사용한다. 원문은 생성자 인자에서의 타입 추론이 C++17부터 제공되며 이전 코드에서는 make_tuple을 사용할 수 있다고 설명한다.',293,294),ref('C13-E04'),
        p('get<0>()처럼 0부터 시작하는 상수 인덱스로 tuple 요소에 접근한다. 그 타입이 tuple 안에서 유일할 때는 get<string>()처럼 타입으로도 지정할 수 있고 쓰기에도 get을 사용한다. pair도 get으로 접근 가능하고 pair·tuple 모두 구조화된 바인딩을 사용할 수 있다. 제네릭할 필요가 없다면 이름 있는 멤버를 둔 struct가 더 읽기 쉽고 유지보수하기 좋을 수 있다.',294,295)),
      section('13.5','선택지',295,295,
        p('표준 라이브러리는 지정한 선택지 중 하나를 담는 variant, 특정 타입의 값 또는 값 없음을 표현하는 optional, 타입 집합에 제한이 없는 any를 제공한다. 각각 <variant>·<optional>·<any>에 정의되며, 관련 기능을 표현하지만 인터페이스가 통일되어 있지는 않다.')),
      section('13.5.1','variant',295,298,
        p('**variant<A,B,C>**는 union을 직접 사용하는 것보다 안전하고 편리한 선택지다. 대입·초기화한 값의 타입을 기억하며 사용자는 어떤 선택지가 저장되었는지 질의하고 값을 추출한다. 원문은 문자열 또는 에러 코드를 반환하는 경우와, 컴파일러 노드의 Expression·Statement·Declaration·Type을 구분하는 경우를 든다.',295,296),
        p('저장 타입별로 여러 번 검사하는 대신 visit과 오버로드된 함수 집합으로 행동을 선택할 수 있다. 원문의 overloaded는 람다 등으로부터 오버로드 집합을 만드는 보조 타입이며 표준 기능 자체는 아니라고 명시한다. 추론 가이드도 이 구현에 사용된다. visit 이후 오버로드 규칙으로 가장 적절한 람다가 호출된다. 잘못된 타입으로 접근하면 bad_variant_access를 던진다. 가상 호출보다 빠를 가능성은 실측해야 한다.',297,298)),
      section('13.5.2','optional',298,299,
        p('**optional<A>**는 A 또는 아무것도 없음을 나타낸다. 객체를 반환하거나 반환하지 않는 함수에 유용하며 빈 {}가 값 없음에 해당한다. 조건 검사로 값 유무를 살피고 *로 저장 값에 접근하므로 포인터와 비슷한 사용 형태를 가진다.'),ref('C13-E05'),
        p('원문은 값이 없는 optional에 접근하면 동작을 예측할 수 없고 예외도 던지지 않으므로, 이 접근 방식에서 타입 안전성을 보장하지 않는다고 경고한다. 따라서 예제처럼 먼저 존재 여부를 검사하는 조건을 유지한다.',299,299)),
      section('13.5.3','any',299,300,
        p('**any**는 임의의 타입을 저장하며 저장된 객체가 있으면 그 타입을 기억한다. 제약을 제거한 variant처럼 설명할 수 있다. any_cast로 타입을 지정하여 값을 추출한다. 원문은 저장된 타입과 다른 타입으로 접근하면 bad_any_access를 던진다고 표기하고, 예외에 의존하지 않는 접근 방법도 있다고 언급한다.'),
        p('[원문 확인 필요] 여기서 예외 이름 bad_any_access는 제공된 책 300쪽의 표기다. 이 노트에서는 의심되는 명칭을 다른 이름으로 조용히 바꾸지 않았다.',300,300)),
      section('13.6','할당자',300,302,
        p('컨테이너의 기본 할당은 new·delete를 사용하지만, 특별한 성능·보안·스레드별 할당·메모리 구조 요구가 있으면 **할당자**를 지정할 수 있다. 원문은 고급 할당자 전반 대신 이벤트 큐에서 풀 할당자로 단편화를 줄인 실제 사례를 제시한다.',300,300),
        p('원래 시스템은 vector를 가진 이벤트를 shared_ptr로 전달하여 마지막 사용자가 자동 소멸시키는 단순한 구조였지만 단편화로 많은 메모리를 소비했다. 풀 할당자는 같은 크기의 여러 객체를 한꺼번에 할당해 관리한다. C++17의 pmr 하위 네임스페이스에는 다형성 메모리 자원과 synchronized_pool_resource가 있어 컨테이너를 전면 교체하지 않고 할당자를 바꿀 수 있다.',301,302),
        p('원문 사례에서 프로듀서 16개와 컨슈머 4개가 이벤트 100,000개를 전달한 뒤 사용 메모리가 6GB에서 3MB 미만으로 줄었다. 이는 단편화 낭비를 줄인 결과이며 실제로 필요했던 메모리양이 바뀐 것은 아니다. 이 수치는 해당 사례의 관측값으로만 이해한다.',301,302)),
      section('13.7','시간',302,303,
        p('<chrono>의 clock::now()는 시각인 time_point를 반환하고 두 시각의 차이는 시간 구간인 duration이 된다. 시계별로 단위가 다르므로 duration_cast로 적절한 단위에 맞춰 표현한다. 성능을 판단할 때는 추측 대신 실제 시간을 측정한다.'),ref('C13-E06'),
        p('시간 단위 접미사는 std::chrono_literals에 정의되어 10ms·33us 같은 표현을 가능하게 한다. 원문은 년·월·달력·시간대·윤초를 다루는 확장 기능을 C++20 표준에 추가 중이라고 소개한다. 이는 원문 시점의 상태이며 현재 상황으로 보충하지 않는다.',303,303)),
      section('13.8','함수 어댑션',303,304,
        p('함수를 다른 함수의 인자로 넘길 때 호출 형태나 타입이 정확히 맞지 않으면 람다, mem_fn, function을 이용하는 세 방법을 고려한다.')),
      section('13.8.1','람다를 어댑터로 사용',304,304,
        p('표준 알고리즘은 f(x) 형태로 인자를 호출하지만 멤버 함수는 x->f() 형태를 사용한다. 람다는 이 호출 방식의 차이를 연결할 수 있다.'),ref('C13-E07')),
      section('13.8.2','mem_fn()',304,305,
        p('**mem_fn(mf)**는 멤버 함수 mf를 비멤버 함수처럼 호출할 수 있는 함수 객체로 바꾼다. 원문은 mem_fn(&Shape::draw)를 for_each에 넘겨 람다와 같은 연결을 수행한다. 람다 도입 이전에 객체지향 호출과 함수 스타일 호출을 연결하던 대표 수단이다.')),
      section('13.8.3','function()',305,305,
        p('**function** 객체는 ()로 호출할 수 있는 대상을 저장한다. 함수·람다를 넣고 그 호출 타입을 명시하거나 초기 값에서 추론할 수 있다. 콜백이나 연산을 인자로 전달하는 데 유용하지만 직접 함수 호출보다 실행 비용이 있고, function은 객체이므로 자체에 오버로딩을 적용할 수 없다. 함수 객체의 오버로딩에는 앞선 overloaded를 고려한다.')),
      section('13.9','타입 함수',306,306,
        p('**타입 함수**는 타입 자체를 인자로 받거나 타입을 반환하며 컴파일 시간에 평가된다. numeric_limits는 수치 타입 정보를, sizeof는 객체의 바이트 수를 알려준다. 이런 기능은 컴파일 시간 계산을 통한 타입 검사와 성능 향상의 재료다. 관련 기법을 메타프로그래밍, 템플릿과 관련되면 템플릿 메타프로그래밍이라고 한다. 원문은 아직 컨셉이 범용 표준이 아닌 시점이어서 타입 함수가 널리 쓰인다고 설명한다.')),
      section('13.9.1','iterator_traits',306,310,
        p('표준 sort는 임의 접근 반복자를 요구하지만 forward_list는 순방향 반복자만 제공한다. 원문은 임의 접근 구간에는 바로 sort를, 순방향 구간에는 vector로 복사·정렬·원래 구간으로 재복사를 선택하는 sort_helper 두 버전을 제시한다. 반복자 종류를 나타내는 태그로 적절한 오버로드를 컴파일 시간에 선택하는 기법이 **태그 디스패치**다.',306,309),ref('C13-E08'),
        p('컨테이너의 iterator·value_type 멤버는 타입 별칭으로 표현할 수 있다. 포인터처럼 이런 멤버 타입이 없는 경우에는 <iterator>의 iterator_traits 특수화를 통해 값 타입·참조·포인터·반복자 종류를 얻는다. 따라서 int*도 random_access_iterator_tag를 가진 반복자로 다룰 수 있다. 원문은 같은 구분이 컨셉으로 더 직접 표현될 수 있고 표준화가 진행 중이라고 설명한다.',308,310)),
      section('13.9.2','타입 술어',310,311,
        p('<type_traits>는 is_arithmetic·is_class·is_pod·is_literal_type·has_virtual_destructor·is_base_of 같은 **타입 술어**를 제공한다. 템플릿은 이 값으로 타입의 성질을 검사할 수 있다. 원문은 산술 타입만 받는 complex의 static_assert를 예로 들고, std::is_arithmetic<T>::value를 반환하는 Is_arithmetic() 래퍼로 표기를 간단히 한다.'),ref('C13-E09')),
      section('13.9.3','enable_if',311,312,
        p('타입 술어는 static_assert·컴파일 시간 if·enable_if의 조건으로 사용된다. **enable_if**는 조건에 따라 정의를 선택하는 데 널리 쓰인다. 원문의 스마트 포인터 설명은 T가 클래스일 때에만 화살표 연산을 제공하려는 의도를 든다. 함수 바깥에서는 컴파일 시간 if를 쓸 수 없다는 문맥에서 enable_if를 소개한다.'),
        p('enable_if는 표기가 낯설고 많은 경우 컨셉으로 대체될 수 있지만, 원문 시점의 템플릿 메타프로그래밍과 여러 표준 라이브러리 구성 요소의 기반이다. 이 기법은 **SFINAE(Substitution Failure Is Not An Error)** 언어 기능에 의존한다.',312,312)),
      section('13.10','조언',312,314,
        ul(['자원에는 RAII 자원 핸들을 사용한다. 포인터가 필요하면 unique_ptr를 우선하고, 소유권을 공유해야 할 때만 shared_ptr를 쓴다. 생성에는 make_unique·make_shared를 사용한다.',
          'move를 남용하지 않으며 forward는 포워딩에만 사용한다. 이동·포워딩한 객체를 나중에 읽지 않는다.',
          '포인터와 개수를 별도로 전달하기보다 span을 사용한다. 고정 크기에는 array, N비트에는 bitset을 고려한다.',
          'pair·tuple보다 이름 있는 struct가 읽기 쉬운 경우를 구별한다. union을 직접 쓰기보다 variant를 고려한다.',
          '단편화에는 할당자를 고려하고, 효율성은 실제 시간 측정으로 판단한다. duration은 단위를 명시하고 필요하면 duration_cast로 바꾼다.',
          '호출을 연결할 때 람다·mem_fn을, 호출 대상을 저장할 때 function을 쓴다. 타입 특성·enable_if·컨셉과 타입 별칭의 역할을 구분한다.']))]
    codes=[
      code('C13-E01','내장 포인터와 unique_ptr의 해제 비교',278,278,r'''void f(int i, int j) // X* vs. unique_ptr<X>
{
    X* p = new X; // 새로운 X 할당
    unique_ptr<X> sp {new X}; // 새로운 X를 할당하고, 그 포인터를 unique_ptr에 넘겨줌
    // ...

    if (i<99) throw Z{}; // 여기서 예외를 던지거나
    if (j<77) return; // "일찍" 반환될 수 있음
    // ... p와 sp 사용 ..
    delete p; // *p 소멸
}''','원문의 조기 종료·예외 사례다. p의 delete까지 도달하지 않는 경로와 달리 sp는 스코프를 떠날 때 자원을 해제한다. 원문에 포함된 생략 주석을 그대로 유지했다.',cautions=['원문 자체가 X·Z의 정의와 실제 사용 부분을 생략한 예다.']),
      code('C13-E02','이동을 이용한 swap',282,282,r'''template <typename T>
void swap(T& a, T& b)
{
    T tmp {move(a)}; // T의 생성자에는 rvalue로 전달되므로 이동을 수행
    a = move(b); // T의 대입 연산에는 rvalue로 전달되므로 이동을 수행
    b = move(tmp); // T의 대입 연산에는 rvalue로 전달되므로 이동을 수행
}''','복사를 계속 수행하지 않고 임시 객체와 두 대입을 이동으로 유도하는 원문 사례다. move 자체의 역할과 실제 이동 연산 선택을 구분한다.'),
      code('C13-E03','정수를 bitset 문자열로 출력',291,291,r'''void binary(int i)
{
    bitset<8*sizeof(int)> b = i; // 8비트 바이트를 가정(14.7절 참고)
    cout << b.to_string() << '\n'; // i를 비트로 출력
}''','정수의 비트를 가장 높은 자리부터 문자열로 출력한다. 바이트가 8비트라는 원문의 전제를 유지한다.',output='원문은 인자 123에 대해 00000000000000000000000001111011을 제시한다.'),
      code('C13-E04','tuple 생성과 타입 추론',294,294,r'''tuple<string,int,double> t1 {"Shark",123,3.14}; // 타입을 명시적으로 지정
auto t2 = make_tuple(string{"Herring"},10,1.23); // 타입을
    // tuple<string,int,double>로 추론
tuple t3 {"Cod"s,20,9.99}; // 타입을 tuple<string,int,double>로 추론''','명시한 타입, make_tuple, 생성자 인자에서 타입을 추론하는 세 방식을 비교하는 원문 선언이다.'),
      code('C13-E05','값이 있는 optional만 합산',299,299,r'''int cat(optional<int> a, optional<int> b)
{
    int res = 0;
    if (a) res+=*a;
    if (b) res+=*b;
    return res;
}

int x = cat(17,19);
int y = cat(17,{});
int z = cat({},{});''','조건으로 존재를 검사한 뒤 *a·*b를 사용한다. {}는 빈 optional을 나타낸다. 원문에 각 호출의 출력은 별도로 제시되지 않는다.',cautions=['값이 없는 optional을 바로 역참조하지 않는다.']),
      code('C13-E06','chrono로 작업 시간 측정',302,302,r'''using namespace std::chrono; // 하위 네임스페이스 std::chrono; 3.4절 참고

auto t0 = high_resolution_clock::now();
do_work();
auto t1 = high_resolution_clock::now();
cout << duration_cast<milliseconds>(t1-t0).count() << "msec\n";''','작업 전후의 time_point 차이를 milliseconds로 변환한 뒤 count()를 출력한다. 실제 소요 시간은 원문에서 특정하지 않는다.'),
      code('C13-E07','람다로 멤버 함수 호출 연결',304,304,r'''void draw_all(vector<Shape*>& v)
{
    for_each(v.begin(),v.end(),[](Shape* p) { p->draw(); });
}''','for_each의 함수 호출 형식을 각 Shape 포인터의 draw() 멤버 호출로 연결한다.'),
      code('C13-E08','포인터용 iterator_traits',309,309,r'''template<class T>
struct iterator_traits<T*> {
    using difference_type = ptrdiff_t;
    using value_type = T;
    using pointer = T*;
    using reference = T&;
    using iterator_category = random_access_iterator_tag;
};''','멤버 타입이 없는 포인터에 반복자 관련 타입 정보를 제공하는 원문 특수화다. 포인터의 종류를 임의 접근으로 분류하는 정보가 태그 디스패치에 쓰인다.',excerpt=True,note='원문의 iterator_traits<T*> 특수화 블록 전체를 발췌했습니다. 앞뒤 sort_helper와 타입 별칭 코드는 생략했습니다.'),
      code('C13-E09','타입 술어의 표기를 단순화한 래퍼',311,311,r'''template<typename T>
constexpr bool Is_arithmetic()
{
    return std::is_arithmetic<T>::value;
}''','표준 타입 특성의 value를 함수 호출 표기로 감싼 원문 래퍼다. 같은 절의 complex에서 static_assert 조건으로 활용한다.')]
    comparisons=[{'title':'스마트 포인터의 소유권','source':src(277,281),'headers':['기준','unique_ptr','shared_ptr'],'rows':[
      ['소유권','유일한 소유자','여러 소유자가 공유'],['전달','이동; 복사할 수 없음','복사하여 공유'],['자원 해제','소유 핸들의 수명에 연결','마지막 소유자가 소멸할 때'],['선택','포인터가 필요하고 소유자가 하나일 때 우선','공유 소유권이 실제로 필요할 때']]},
      {'title':'세 가지 선택지 타입','source':src(295,300),'headers':['타입','표현하는 선택지','원문의 접근 방식'],'rows':[
        ['variant','미리 지정한 여러 타입 중 하나','타입 질의·get·visit'],['optional','한 타입의 값 또는 없음','존재 검사 후 *'],['any','미리 제한하지 않은 타입','any_cast로 지정 타입 추출']]}]
    finish(13,'유틸리티',275,314,
      ['RAII·스마트 포인터·이동·포워딩으로 자원과 소유권을 표현한다.','비소유 구간·유사 컨테이너·선택지 타입을 구별한다.','할당자·시간·함수 어댑션·타입 함수의 역할과 원문 조건을 익힌다.'],
      ['자원 수명과 소유권','이동·포워딩과 구간 참조','특수 컨테이너와 선택지','할당·시간·호출 연결','컴파일 시간의 타입 정보와 선택'],sections,codes,
      ['RAII의 획득·해제 쌍은 예외와 이른 반환에도 연결된다.','shared_ptr는 동시 접근 규칙까지 보장하는 수단이 아니다.','move는 rvalue 변환이며 이동·포워딩 뒤 원본 재사용을 주의한다.','span은 요소를 소유하지 않는 구간 참조다.','variant·optional·any는 선택지 범위와 접근 방식이 다르다.','타입 특성과 태그는 컴파일 시간에 적절한 구현을 선택하는 재료다.'],comparisons,
      ['지역 객체·컨테이너·unique_ptr·shared_ptr 가운데 필요한 자원 관리 수준과 소유권을 구분한다.','구간의 길이와 포인터를 함께 다루는 span, 고정 크기 array, 비트 집합 bitset의 목적을 복습한다.','pair·tuple의 위치·타입 접근과 이름 있는 struct의 가독성 차이를 정리한다.','할당자의 단편화 개선 사례와 chrono의 실제 성능 측정을 연결한다.','람다·mem_fn·function의 호출 연결과 iterator_traits·타입 술어·enable_if의 컴파일 시간 역할을 구분한다.'],
      [('RAII / 자원','13.2'),('unique_ptr / shared_ptr','13.2.1'),('make_unique / make_shared','13.2.1'),('move / forward','13.2.2'),('gsl::span','13.3'),('array','13.4.1'),('bitset','13.4.2'),('pair / tuple','13.4.3'),('variant / visit','13.5.1'),('optional','13.5.2'),('any','13.5.3'),('할당자 / pmr','13.6'),('chrono / duration_cast','13.7'),('람다 어댑터','13.8.1'),('mem_fn','13.8.2'),('function','13.8.3'),('iterator_traits / 태그 디스패치','13.9.1'),('타입 술어','13.9.2'),('enable_if / SFINAE','13.9.3')],
      ['책 288~289쪽이 제공되지 않아 13.4.1 array의 앞부분은 확인할 수 없다. 확인된 앞뒤 페이지·표·조언만 정리했다.',
       '[원문 확인 필요] 책 300쪽의 any 예외 이름 bad_any_access를 원문대로 보존했다. 의심되는 표기를 외부 지식으로 수정하지 않았다.'])


if __name__=='__main__':
    chapter11()
    chapter12()
    chapter13()
