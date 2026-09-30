import json,pytest
from patchmap.core import Evidence,parse_diff,parse_spec,safe_repo_path
from patchmap.engine import build_graph
from patchmap.render import render_json,render_markdown
from patchmap.cli import run
SPEC='REQ-A: login works\n  AC: accepts valid user\nREQ-B: audit exists\n'; DIFF='diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,1 +1,2 @@\n-old\n+new\n+line\n'
def base(): return parse_spec(SPEC),parse_diff(DIFF)
def test_golden_states():
 r,h=base(); g=build_graph(r,h,[Evidence('REQ-A',h[0].id,'test_login',True,'abc')],'abc'); assert [x['status'] for x in g['requirements']]==['PROVEN','UNPROVEN']; assert g['hunks'][0]['status']=='BOUND'
def test_wrong_commit_and_unrelated_green_do_not_prove():
 r,h=base(); g=build_graph(r,h,[Evidence('REQ-A',h[0].id,'t',True,'wrong'),Evidence('REQ-B','missing','green',True,'abc')],'abc'); assert all(x['status']=='UNPROVEN' for x in g['requirements'])
def test_failed_evidence_does_not_prove():
 r,h=base(); assert build_graph(r,h,[Evidence('REQ-A',h[0].id,'t',False,'abc')],'abc')['requirements'][0]['status']=='UNPROVEN'
def test_orphan_hunk():
 r,h=base(); assert build_graph(r,h,[],'abc')['hunks'][0]['status']=='ORPHAN'
def test_deterministic_bytes():
 r,h=base(); e=[Evidence('REQ-A',h[0].id,'t',True,'abc')]; assert render_json(build_graph(r,h,e,'abc')).encode()==render_json(build_graph(r,h,e,'abc')).encode()
def test_hostile_markdown_is_escaped():
 r,h=base(); assert 'x\\|\\`y' in render_markdown(build_graph(r,h,[Evidence('REQ-A',h[0].id,'x|`y',True,'abc')],'abc'))
@pytest.mark.parametrize('p',['../../secret','/etc/passwd','C:/Windows'])
def test_unsafe_paths_rejected(p):
 with pytest.raises(ValueError): safe_repo_path(p)
def test_malformed_inputs():
 with pytest.raises(ValueError): parse_spec('hello')
 with pytest.raises(ValueError): parse_diff('not a diff')
def test_unrelated_invalid_evidence_invariance():
 r,h=base(); good=Evidence('REQ-A',h[0].id,'t',True,'abc'); assert build_graph(r,h,[good],'abc')==build_graph(r,h,[good,Evidence('REQ-B','nope','other',True,'abc')],'abc')
def test_cli_outputs_and_collision(tmp_path):
 s=tmp_path/'s'; d=tmp_path/'d'; e=tmp_path/'e'; o=tmp_path/'o'; s.write_text(SPEC); d.write_text(DIFF); h=parse_diff(DIFF); e.write_text(json.dumps([{'requirement_key':'REQ-A','hunk_id':h[0].id,'test_id':'t','passed':True,'commit':'abc'}])); run(s,d,e,'abc',o); assert (o/'graph.json').exists() and (o/'report.md').exists()
 with pytest.raises(FileExistsError): run(s,d,e,'abc',o)
