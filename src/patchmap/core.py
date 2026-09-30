from dataclasses import asdict, dataclass
import hashlib,json,posixpath,re

def stable_id(kind,payload):
 raw=json.dumps({'kind':kind,'payload':payload},sort_keys=True,separators=(',',':'),ensure_ascii=False); return hashlib.sha256(raw.encode()).hexdigest()[:16]
def safe_repo_path(path):
 path=path.replace('\\','/')
 if path.startswith('/') or re.match(r'^[A-Za-z]:/',path): raise ValueError('absolute paths are not allowed')
 norm=posixpath.normpath(path)
 if norm=='..' or norm.startswith('../') or norm in ('','.'): raise ValueError('unsafe repository path')
 return norm
@dataclass(frozen=True)
class AcceptanceCriterion:
 requirement_key:str; text:str
 @property
 def id(self): return stable_id('ac',asdict(self))
@dataclass(frozen=True)
class Requirement:
 key:str; text:str; criteria:tuple=()
 @property
 def id(self): return stable_id('requirement',{'key':self.key,'text':self.text,'criteria':[asdict(c) for c in self.criteria]})
@dataclass(frozen=True)
class ChangedHunk:
 path:str; old_start:int; new_start:int; header:str; body:str
 def __post_init__(self): object.__setattr__(self,'path',safe_repo_path(self.path))
 @property
 def id(self): return stable_id('hunk',asdict(self))
@dataclass(frozen=True)
class Evidence:
 requirement_key:str; hunk_id:str; test_id:str; passed:bool; commit:str
 @property
 def id(self): return stable_id('evidence',asdict(self))
_REQ=re.compile(r'^REQ-([A-Za-z0-9_-]+):\s+(.+)$'); _AC=re.compile(r'^\s+AC:\s+(.+)$')
def parse_spec(text):
 out=[]; key=None; desc=None; acs=[]
 def flush():
  if key is not None: out.append(Requirement(key,desc,tuple(acs)))
 for n,line in enumerate(text.splitlines(),1):
  if not line.strip(): continue
  m=_REQ.match(line)
  if m: flush(); key='REQ-'+m.group(1); desc=m.group(2).strip(); acs=[]
  else:
   a=_AC.match(line)
   if a and key: acs.append(AcceptanceCriterion(key,a.group(1).strip()))
   else: raise ValueError(f'malformed spec line {n}: {line}')
 flush()
 if not out: raise ValueError('spec contains no requirements')
 return tuple(out)
_DIFF_FILE=re.compile(r'^\+\+\+ b/(.+)$'); _HUNK=re.compile(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)$')
def parse_diff(text):
 lines=text.splitlines(); path=None; out=[]; i=0
 while i<len(lines):
  fm=_DIFF_FILE.match(lines[i])
  if fm: path=safe_repo_path(fm.group(1)); i+=1; continue
  hm=_HUNK.match(lines[i])
  if hm:
   if not path: raise ValueError('hunk before file path')
   header=lines[i]; body=[]; i+=1
   while i<len(lines) and not _HUNK.match(lines[i]) and not _DIFF_FILE.match(lines[i]): body.append(lines[i]); i+=1
   out.append(ChangedHunk(path,int(hm.group(1)),int(hm.group(2)),header,'\n'.join(body))); continue
  i+=1
 if not out: raise ValueError('diff contains no hunks')
 return tuple(out)
