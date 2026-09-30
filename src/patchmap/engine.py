from dataclasses import asdict
def build_graph(requirements,hunks,evidence,commit):
 req_keys={r.key for r in requirements}; hunk_ids={h.id for h in hunks}
 valid=[e for e in evidence if e.commit==commit and e.passed and e.requirement_key in req_keys and e.hunk_id in hunk_ids and e.test_id.strip()]
 proven={e.requirement_key for e in valid}; bound={e.hunk_id for e in valid}
 return {'schema_version':1,'commit':commit,'requirements':[{'key':r.key,'id':r.id,'text':r.text,'status':'PROVEN' if r.key in proven else 'UNPROVEN','criteria':[asdict(c)|{'id':c.id} for c in r.criteria]} for r in requirements],'hunks':[asdict(h)|{'id':h.id,'status':'BOUND' if h.id in bound else 'ORPHAN'} for h in hunks],'evidence':[asdict(e)|{'id':e.id} for e in valid]}
