# Run all:      pytest tests/unit/test_output.py -v
# Run one:      pytest tests/unit/test_output.py::test_render_returns_valid_yaml -v

import yaml
from gitwrap.output import render


def test_render_returns_valid_yaml():
    result = render({"status": "ok", "files": []})
    parsed = yaml.safe_load(result)
    assert parsed["status"] == "ok"


def test_render_preserves_nested_structure():
    data = {"command": "status", "status": "ok", "files": [{"path": "foo.py", "state": "M"}]}
    parsed = yaml.safe_load(render(data))
    assert parsed["files"][0]["path"] == "foo.py"
    assert parsed["files"][0]["state"] == "M"
