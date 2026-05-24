"""
Regression suite for the 2026-05-24 audit (see vault/Atlas/Architecture/
2026-05-24-purely-audit-fix-spec.md). Each test pins a known defect at the
behavior level. All are xfail(strict=True): a passing test means the fix
landed and the xfail marker should be removed.
"""

from __future__ import annotations

import pytest

from purely import Chain, Err, Ok, Option
from purely.curry import curry
from purely.di import Registry
from purely.dispatch import AmbiguityError, dispatcher


# =============================================================================
# Bug #1 — Option.__setitem__ raises AttributeError when value is None
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #1: pass should be return; core.py:107")
def test_option_setitem_on_none_is_noop():
    opt: Option = Option(None)
    opt["k"] = "v"  # must not raise


def test_option_setitem_on_dict_still_writes():
    d: dict = {}
    Option(d)["k"] = "v"
    assert d == {"k": "v"}


# =============================================================================
# Bug #2 — Err.unwrap(default=None) raises instead of returning None
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #2: literal None cannot be a recovery value; result.py:54")
def test_err_unwrap_default_none_returns_none():
    assert Err("boom").unwrap(default=None) is None


def test_err_unwrap_default_nonzero_falsy_returns_value():
    assert Err("boom").unwrap(default=0) == 0
    assert Err("boom").unwrap(default="") == ""
    assert Err("boom").unwrap(default=False) is False


# =============================================================================
# Bug #3 — Registry.register(BareClass) crashes
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #3: bare class hits provider=lambda branch; di.py:42")
def test_registry_register_bare_class_resolves_to_instance():
    class Service:
        pass

    reg = Registry()
    reg.register(Service)
    assert isinstance(reg.resolve(Service), Service)


# =============================================================================
# Bug #4 — Registry.register(callable_instance) misclassified as factory
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #4: any __call__ instance treated as factory; di.py:42")
def test_registry_register_callable_instance_preserves_instance():
    class Bus:
        def __call__(self):
            return "side-effect"

        def publish(self, msg):
            return msg

    bus = Bus()
    reg = Registry()
    reg.register(bus)
    resolved = reg.resolve(Bus)
    assert resolved is bus
    assert resolved.publish("hi") == "hi"


# =============================================================================
# Bug #5 — Factory side effects fire an extra time during MRO discovery
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #5: provider() called once for MRO discovery at register; di.py:53")
def test_registry_factory_side_effects_do_not_fire_at_registration():
    calls = {"n": 0}

    class Conn:
        pass

    def factory():
        calls["n"] += 1
        return Conn()

    reg = Registry()
    reg.register(factory)  # no explicit interface → MRO discovery path
    assert calls["n"] == 0  # bug: this currently equals 1
    reg.resolve(Conn)
    assert calls["n"] == 1


# =============================================================================
# Bug #6 — Chain.then / Chain.tap / Ok.then swallow programmer errors
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #6: NameError captured at .then(); should propagate immediately; core.py:227")
def test_chain_then_propagates_nameerror():
    # The NameError should escape .then() at the call site, not be stored as
    # a domain error to be re-raised at .unwrap() time.
    with pytest.raises(NameError):
        Chain(5).then(lambda x: undefined_name)  # noqa: F821


@pytest.mark.xfail(strict=True, reason="bug #6: AttributeError captured at .then(); should propagate immediately; core.py:227")
def test_chain_then_propagates_attributeerror_on_typo():
    class User:
        address = "1 Main St"

    with pytest.raises(AttributeError):
        Chain(User()).then(lambda u: u.adress)


@pytest.mark.xfail(strict=True, reason="bug #6: tap captures programmer errors; should propagate; core.py:237")
def test_chain_tap_propagates_nameerror():
    with pytest.raises(NameError):
        Chain(5).tap(lambda x: undefined_name)  # noqa: F821


@pytest.mark.xfail(strict=True, reason="bug #6: Ok.then captures AttributeError; should propagate; result.py:24")
def test_ok_then_propagates_attributeerror():
    class User:
        address = "1 Main St"

    with pytest.raises(AttributeError):
        Ok(User()).then(lambda u: u.adress)


# =============================================================================
# Bug #7 — Dispatcher silently swallows predicate exceptions
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #7: predicate exception swallowed; dispatch.py:48")
def test_dispatcher_predicate_exception_propagates():
    @dispatcher
    def proc(x):
        return "default"

    @proc.when(lambda x: x.nonexistent_attr)  # raises AttributeError
    def _(x):
        return "predicate"

    with pytest.raises(AttributeError):
        proc(object())


# =============================================================================
# Bug #8 — Chain.__eq__ raises stored exception instead of comparing
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #8: __eq__ must be a total relation; core.py:339")
def test_failed_chain_eq_is_total_relation():
    c = Chain.fail(ValueError("x"))
    # equal to itself
    assert c == c
    # unequal to anything that isn't an equivalent failed chain
    assert (c == 5) is False
    assert (c == "anything") is False


@pytest.mark.xfail(strict=True, reason="bug #8: two failed chains with same exception should compare equal")
def test_two_failed_chains_with_equal_errors_compare_equal():
    e1 = ValueError("x")
    e2 = ValueError("x")
    assert Chain.fail(e1) == Chain.fail(e2)


# =============================================================================
# Bug #9 — Option, Chain, Ok, Err are all unhashable
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #9: Option missing __hash__; core.py:118")
def test_option_is_hashable():
    {Option(5): "x"}


@pytest.mark.xfail(strict=True, reason="bug #9: Chain missing __hash__; core.py:339")
def test_chain_is_hashable():
    {Chain(5): "x"}


@pytest.mark.xfail(strict=True, reason="bug #9: Ok missing __hash__; result.py:36")
def test_ok_is_hashable():
    {Ok(5), Ok(5)}


@pytest.mark.xfail(strict=True, reason="bug #9: Err missing __hash__; result.py:75")
def test_err_is_hashable():
    {Err("x"), Err("x")}


# =============================================================================
# Bug #10 — Option.unwrap default error is a shared mutable instance
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #10: mutable default exception; core.py:42")
def test_option_unwrap_default_error_is_fresh_each_call():
    e1 = None
    e2 = None
    try:
        Option(None).unwrap()
    except ValueError as e:
        e1 = e
    try:
        Option(None).unwrap()
    except ValueError as e:
        e2 = e
    assert e1 is not e2


# =============================================================================
# Bug #11 — Dispatcher ignores kwargs for type dispatch
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #11: kwargs ignored in dispatch loop; dispatch.py:59")
def test_dispatcher_dispatches_on_kwargs():
    # Two overloads — only one matches by type. With positional args this works.
    # With keyword-only args the dispatcher currently cannot disambiguate
    # because the filtering loop only inspects positional args.
    @dispatcher
    def proc(a, b):
        return "default"

    @proc.dispatch
    def _(a: int, b: str):
        return "int+str"

    @proc.dispatch
    def _(a: str, b: int):
        return "str+int"

    assert proc(1, "hi") == "int+str"
    assert proc(a=1, b="hi") == "int+str"


# =============================================================================
# Bug #12 — Dispatcher zero-arg dispatch always raises AmbiguityError
# =============================================================================


@pytest.mark.xfail(strict=True, reason="bug #12: zero-arg dispatch leaves all candidates in pool; dispatch.py:46")
def test_dispatcher_zero_arg_multiple_overloads_does_not_raise_ambiguity():
    # With ≥2 zero-arg overloads, the candidate-filtering loop never runs and
    # every implementation remains a candidate → AmbiguityError. The expected
    # behavior (per audit recommendation) is to fall back to the default or to
    # the first registration, not raise.
    @dispatcher
    def f():
        return "default"

    @f.dispatch
    def _():
        return "a"

    @f.dispatch
    def _():
        return "b"

    # Either "default", "a", or "b" — anything but AmbiguityError.
    result = f()
    assert result in {"default", "a", "b"}


# =============================================================================
# Footgun F1 — curry: unrecognized kwargs counted toward arity
# =============================================================================


@pytest.mark.xfail(strict=True, reason="footgun F1: bogus kwarg silently retained as partial state; curry.py:104")
def test_curry_rejects_unknown_kwargs_at_application_time():
    @curry
    def f(a, b):
        return a + b

    # Currently: f(bogus_kwarg=99) silently returns a partial that carries the
    # bogus kwarg forward, only blowing up much later when arity threshold is
    # crossed and Python's binder rejects it. After fix: curry validates kwarg
    # names against signature(func).parameters and raises here.
    with pytest.raises(TypeError):
        f(bogus_kwarg=99)


# =============================================================================
# Footgun F2 — curry over *args-only function bypasses currying
# =============================================================================


@pytest.mark.xfail(strict=True, reason="footgun F2: VAR_POSITIONAL excluded from arity; curry.py:90")
def test_curry_variadic_function_is_not_silently_no_op():
    # We want curry to either reject variadic functions outright, or treat them
    # in a way that doesn't make `f(1)` execute the body before all args arrive.
    @curry
    def f(*args):
        return sum(args)

    partial = f(1)
    # If currying worked, `partial` is callable awaiting more args, not the result.
    assert callable(partial) and not isinstance(partial, int)


# =============================================================================
# Footgun F3 — Chain.map on a dict silently iterates keys
# =============================================================================


@pytest.mark.xfail(strict=True, reason="footgun F3: dict accepted as Iterable; core.py:262")
def test_chain_map_on_dict_is_explicit_not_silent():
    # Either reject dicts (TypeError) or map over (k, v) pairs. Silently
    # iterating keys is the surprise.
    result = Chain({"a": 1, "b": 2}).map(lambda kv: kv)
    if result.is_ok:
        # If we accept dicts, the mapped value should be pairs, not bare keys.
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result.unwrap())
    else:
        assert isinstance(result.error(), TypeError)


# =============================================================================
# Footgun F4 — Registry: overlapping-MRO re-registration silently ignored
# =============================================================================


@pytest.mark.xfail(strict=True, reason="footgun F4: 'if cls not in providers' blocks override; di.py:60")
def test_registry_overlapping_mro_registration_is_explicit():
    class Base:
        pass

    class A(Base):
        pass

    class B(Base):
        pass

    reg = Registry()
    reg.register(A())
    # Either raise on conflict, or last-write-wins. Silent first-write-wins is
    # the footgun.
    with pytest.raises(Exception):
        reg.register(B())


# =============================================================================
# Footgun F5 — Dispatcher: predicate always shadows type dispatch
# =============================================================================


@pytest.mark.xfail(strict=True, reason="footgun F5: no way to scope predicate; dispatch.py:48")
def test_dispatcher_type_dispatch_survives_unrelated_predicate():
    # An over-broad predicate registered for one type should not shadow type
    # dispatches on unrelated types.
    @dispatcher
    def proc(x):
        return "default"

    @proc.when(lambda x: isinstance(x, str))
    def _(x):
        return "string-predicate"

    @proc.dispatch
    def _(x: int):
        return "int-type"

    assert proc(42) == "int-type"
    assert proc("hi") == "string-predicate"
