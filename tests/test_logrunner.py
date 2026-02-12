import logrunner
import pytest

def test():
    (ret, out, err) = logrunner.run(["echo", "hello"])
    assert ret == 0
    assert out.strip() == "hello"
    assert err == ""

def test_error():
    (ret, out, err) = logrunner.run(["ls", "/nonexistentpath"])
    assert ret != 0
    assert out == ""
    assert "No such file or directory" in err

if __name__ == "__main__":
    pytest.main()
