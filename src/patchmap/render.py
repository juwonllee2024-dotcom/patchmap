import json
def render_json(graph): return json.dumps(graph,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
def _esc(s): return s.replace('\\','\\\\').replace('`','\\`').replace('|','\\|').replace('\n',' ')
def render_markdown(graph):
 lines=['# PatchMap Report','',f"Commit: `{_esc(graph['commit'])}`",'','## Requirements','','| Requirement | Status | Text |','|---|---|---|']
 for r in graph['requirements']: lines.append(f"| `{_esc(r['key'])}` | **{r['status']}** | {_esc(r['text'])} |")
 lines += ['','## Changed hunks','','| File | Status | Hunk |','|---|---|---|']
 for h in graph['hunks']: lines.append(f"| `{_esc(h['path'])}` | **{h['status']}** | `{_esc(h['id'])}` |")
 lines += ['','## Evidence','']
 if not graph['evidence']: lines.append('_No valid evidence._')
 else:
  for e in graph['evidence']: lines.append(f"- `{_esc(e['requirement_key'])}` <- `{_esc(e['test_id'])}` @ `{_esc(e['hunk_id'])}`")
 return '\n'.join(lines)+'\n'
