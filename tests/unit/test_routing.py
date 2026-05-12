# Run all:  pytest tests/unit/test_routing.py -v
# Run one:  pytest tests/unit/test_routing.py::test_detect_git -v

import yaml
import pytest
from unittest.mock import patch
from gitwrap.__main__ import detect_service, main


def test_detect_git():
    with patch("sys.argv", ["gitwrap"]):
        assert detect_service() == "git"


def test_detect_docker():
    with patch("sys.argv", ["dockerwrap"]):
        assert detect_service() == "docker"


def test_detect_kubectl():
    with patch("sys.argv", ["kubewrap"]):
        assert detect_service() == "kubectl"


def test_dockerwrap_outputs_coming_soon(capsys):
    with patch("sys.argv", ["dockerwrap"]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0
    out = yaml.safe_load(capsys.readouterr().out)
    assert out["service"] == "docker"
    assert out["status"] == "coming_soon"


def test_kubewrap_outputs_coming_soon(capsys):
    with patch("sys.argv", ["kubewrap"]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0
    out = yaml.safe_load(capsys.readouterr().out)
    assert out["service"] == "kubectl"
    assert out["status"] == "coming_soon"
