from core.release_endpoints import include_in_release_gate, release_urls

def test_fixture_tag_is_excluded_from_release_gate_urls():
    fixture={"enabled":True,"method":"GET","path":"/api/xss","definition_json":{"tags":["preflight-test-fixture"]}}
    real={"enabled":True,"method":"GET","path":"/health","definition_json":{"tags":["health"]}}
    assert not include_in_release_gate(fixture)
    assert release_urls("http://api.test",[fixture,real]) == ["http://api.test/health"]

def test_security_fixture_tag_is_also_excluded():
    fixture={"enabled":True,"method":"GET","path":"/api/file","definition_json":{"tags":["preflight-security-fixture"]}}
    assert not include_in_release_gate(fixture)

def test_non_get_and_unresolved_paths_are_not_used():
    post={"enabled":True,"method":"POST","path":"/tasks","definition_json":{}}
    unresolved={"enabled":True,"method":"GET","path":"/tasks/{id}","definition_json":{"parameters":[{"name":"id","in":"path","schema":{"type":"integer"}}]}}
    assert release_urls("http://api.test",[post,unresolved]) == []
