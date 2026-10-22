import json,pathlib
ROOT=pathlib.Path(r"C:/Users/user/Desktop/Obsidian/git-study-sync/CS/CPP/tmp/pdfs/cpp_compilation")
def F(text,pages,evidence,section,source="B"):
 return {"text":text,"refs":[{"source":source,"section":section,"pages":pages if isinstance(pages,list) else [pages]}],"evidence":evidence}
def G(title,*facts):return {"title":title,"items":list(facts)}
def T(term,fact):return {"term":term,"definition":fact}
def C(label,code,pages,section,source="B"):return {"label":label,"code":code,"refs":[{"source":source,"section":section,"pages":pages if isinstance(pages,list) else [pages]}],"evidence":code,"note":None}
def Q(question,fact):return {"question":question,"answer":fact}
def P(title,*steps):return {"title":title,"steps":list(steps)}
def W(unit):
 (ROOT/f"unit_{unit['unit']:02}.json").write_text(json.dumps(unit,ensure_ascii=False,indent=2),encoding="utf-8")
 print(f"unit_{unit['unit']:02}.json saved")
