import pytest
import pipen
from pathlib import Path
from pipen.utils import (
    brief_list,
    desc_from_docstring,
    get_logger,
    get_mtime,
    get_plugin_context,
    get_shebang,
    ignore_firstline_dedent,
    strsplit,
    truncate_text,
    update_dict,
    mark,
    get_marked,
    _get_obj_from_spec,
    load_pipeline,
)
from pipen.proc import Proc
from pipen.procgroup import ProcGroup
from pipen.exceptions import ConfigurationError
from pipen.pluginmgr import plugin

HERE = Path(__file__).parent.resolve()


def test_get_logger(caplog):
    logger = get_logger("test", "info")
    logger.debug("debug message")
    assert "debug message" not in caplog.text


def test_plugin_context():
    with pytest.raises(ConfigurationError):
        get_plugin_context(["a", "no:b"])

    plugin.get_plugin("core").enable()
    context = get_plugin_context(["no:core"])

    with context:
        assert plugin.get_plugin("core").enabled is False

    assert plugin.get_plugin("core").enabled is True


def test_brief_list():
    assert brief_list([1]) == "1"
    assert brief_list([1, 2, 3]) == "1-3"


def test_get_mtime_dir():
    package_dir = Path(pipen.__file__).parent
    mtime = get_mtime(package_dir, 2)
    assert mtime > 0


def test_desc_from_docstring():
    class Base:
        ...

    class Obj1(Base):
        """

        abc
        def

        """

    desc = desc_from_docstring(Obj1, Base)
    assert desc == "abc def"


def test_update_dict():
    assert update_dict(None, None) is None
    assert update_dict({}, None) == {}
    assert update_dict(None, {}) == {}


def test_strsplit():
    assert strsplit("a ,b ", ",", trim=None) == ["a ", "b "]
    assert strsplit("a , b", ",", trim="left") == ["a ", "b"]
    assert strsplit("a , b", ",", trim="right") == ["a", " b"]


def test_get_shebang():
    assert get_shebang("") is None
    assert get_shebang("#!bash") == "bash"
    assert get_shebang("#!bash \n") == "bash"


def test_ignore_firstline_dedent():
    text = """

    a
    """
    assert ignore_firstline_dedent(text) == "a\n"


def test_truncate_text():
    assert truncate_text("abcd", 2) == "a…"


def test_mark():
    @mark(a=1)
    class P1(pipen.Proc):
        ...

    assert get_marked(P1, "a") == 1

    class P2(P1):
        ...

    assert get_marked(P2, "a", None) is None

    P3 = pipen.Proc.from_proc(P1)
    assert get_marked(P3, "a") is None

    class X:
        ...

    assert get_marked(X, "a", None) is None

    @mark(a=1)
    class Y:
        ...

    assert get_marked(Y, "a") == 1

    class Z(Y):
        ...

    # Marks inherited, as Y/Z are not Proc nor ProcGroup
    assert get_marked(Z, "a", None) == 1


def test_get_obj_from_spec():
    with pytest.raises(ValueError):
        _get_obj_from_spec("a.b.c")

    obj = _get_obj_from_spec(f"{HERE}/helpers.py:SimpleProc")
    assert obj.name == "SimpleProc"

    obj = _get_obj_from_spec(f"pipen:Pipen")
    assert obj is pipen.Pipen


@pytest.mark.asyncio
async def test_load_pipeline(tmp_path):
    with pytest.raises(TypeError):
        await load_pipeline(f"{HERE}/helpers.py:create_dead_link")
    with pytest.raises(TypeError):
        await load_pipeline(ConfigurationError)

    # Proc
    pipeline = await load_pipeline(f"{HERE}/helpers.py:SimpleProc")
    assert pipeline.name == "SimpleProcPipeline"

    # ProcGroup
    class PG(ProcGroup):
        ...

    pg = PG()

    @pg.add_proc()
    class P1(Proc):
        pass

    pipeline = await load_pipeline(PG)
    assert pipeline.name == "PG"

    # Pipen
    obj = _get_obj_from_spec(f"{HERE}/helpers.py:pipen")
    proc = _get_obj_from_spec(f"{HERE}/helpers.py:SimpleProc")
    # Use the original function instead of fixture
    p = obj.__wrapped__(tmp_path).__class__
    p.starts = [proc]
    pipeline = await load_pipeline(p, name="LoadedPipeline")
    assert pipeline.name == "LoadedPipeline"
    assert pipeline.starts[0].name == "SimpleProc"
    assert len(pipeline.procs) == 1
