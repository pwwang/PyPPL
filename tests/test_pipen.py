from re import template
import pytest
from pipen import Proc, Pipen
from pipen.exceptions import (
    PipenException,
    ProcDependencyError,
    PipenSetDataError,
)
from pipen.proc import PipenOrProcNameError

from .helpers import (
    ErrorProc,
    NormalProc,
    SimpleProc,
    RelPathScriptProc,
    pipen,
    SimplePlugin,
    pipen_with_plugin,
)


def test_init(pipen):
    assert isinstance(pipen, Pipen)


def test_name():
    p = Pipen()
    assert p.name == "p"
    [p] = [Pipen()]
    assert p.name.startswith("pipen-")


def test_run(pipen):
    ret = pipen.set_starts(SimpleProc).run()
    assert ret

    ret = pipen.set_starts([ErrorProc]).run()
    assert not ret


def test_no_start_procs(pipen):
    with pytest.raises(ProcDependencyError):
        pipen.run()


def test_cyclic_dependency(pipen):
    """
    proc1(start) --> proc2 --> proc3(start)
                           <--
    """
    proc1 = Proc.from_proc(NormalProc, input_data=[1])
    proc2 = Proc.from_proc(NormalProc)
    proc3 = Proc.from_proc(NormalProc, requires=proc2)
    proc2.requires = [proc1, proc3]

    with pytest.raises(ProcDependencyError, match="Cyclic dependency"):
        pipen.set_starts(proc1, proc3).run()


def test_not_cyclic_for_subclass_of_proc_in_pipeline(pipen):
    proc1 = Proc.from_proc(NormalProc, input_data=[1])
    proc2 = Proc.from_proc(NormalProc, requires=proc1)

    class proc3(proc1):
        requires = proc2

    pipen.set_starts(proc1).run()
    assert pipen.procs == [proc1, proc2, proc3]


def test_no_next_procs(pipen):
    """
    proc1 --> proc2 --> proc3
                    <--
    """
    proc1 = Proc.from_proc(NormalProc, input_data=[1])
    proc2 = Proc.from_proc(NormalProc)
    proc3 = Proc.from_proc(NormalProc, requires=proc2)
    proc2.requires = [proc1, proc3]
    # trigger requires/nexts computation
    proc2.__init_subclass__()

    with pytest.raises(
        ProcDependencyError,
        match="No available next processes",
    ):
        pipen.set_starts(proc1).run()


def test_plugins_are_pipeline_dependent(pipen, pipen_with_plugin, caplog):
    simproc = Proc.from_proc(SimpleProc)
    pipen_with_plugin.set_starts(simproc).run()
    assert "simpleplugin" in caplog.text

    caplog.clear()
    pipen.set_starts(simproc).run()  # No simple plugin enabled
    assert "simpleplugin" not in caplog.text


def test_set_starts_error(pipen):
    with pytest.raises(ProcDependencyError):
        pipen.set_starts(SimpleProc, SimpleProc)


def test_set_data(pipen):
    simproc = Proc.from_proc(SimpleProc, input_data=[1])
    pipen.set_starts(simproc).set_data(None)
    assert simproc.input_data == [1]

    with pytest.raises(PipenSetDataError):
        pipen.set_data([2])


def test_proc_order(pipen):
    proc1 = Proc.from_proc(NormalProc, input_data=[1])
    proc2 = Proc.from_proc(NormalProc, requires=proc1)
    proc3 = Proc.from_proc(NormalProc, requires=proc1, order=-1)

    pipen.set_starts(proc1).run()
    assert pipen.procs == [proc1, proc3, proc2]


def test_proc_inherited(pipen):
    proc1 = Proc.from_proc(RelPathScriptProc)
    proc2 = Proc.from_proc(proc1)
    pipen.set_starts(proc2).set_data([1]).run()
    assert proc2.__doc__ == RelPathScriptProc.__doc__


def test_subclass_pipen(tmp_path, caplog):
    class Proc1(Proc):
        input = "a"
        output = "b:var:{{in.a}}"

    class Proc2(Proc):
        requires = Proc1
        input = "b"
        output = "c:file:{{in.b}}"
        script = "touch {{out.c}}"

    class MyPipen(Pipen):
        name = "MyAwesomePipeline"
        starts = Proc1
        data = [1],
        outdir = tmp_path / "outdir"
        workdir = tmp_path
        loglevel = "DEBUG"
        plugin_opts = {"x": 1}
        scheduler_opts = {"n": 1}
        template_opts = {"a": 1}

    MyPipen(plugin_opts={"y": 2}).run()

    assert (tmp_path / "outdir" / "Proc2" / "1").is_file()
    assert "MYAWESOMEPIPELINE" in caplog.text
    assert "x=1" in caplog.text
    assert "y=2" in caplog.text

    class MyPipe2(Pipen):
        ...

    assert MyPipe2().name == "MyPipe2"


def test_invalid_name():
    class MyPipe3(Pipen):
        name = "a+"

    with pytest.raises(PipenOrProcNameError, match="Invalid pipeline name"):
        MyPipe3().run()


def test_duplicate_proc_name():
    class MyProc1(Proc):
        ...

    class MyProc2(Proc):
        requires = MyProc1
        name = "MyProc1"

    class MyPipe4(Pipen):
        starts = MyProc1

    with pytest.raises(PipenOrProcNameError, match="already used by another"):
        MyPipe4().run()
