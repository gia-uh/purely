# Validating a signup

A visitor fills in the signup form: an email and a birth year. The shop sells
some books only to adults, so the year matters. When something is wrong, the
form must say what, next to the field.

`Option` cannot do this job. An empty box says that something is missing, but
not why. The plain-Python answer is to raise:

```{python}
def signup(form):
    email = form.get("email", "")
    if "@" not in email:
        raise ValueError("the email needs an @")
    year = form.get("year", "")
    if not year.isdigit():
        raise ValueError("the birth year must be a number")
    return {"email": email, "adult": 2026 - int(year) >= 18}


try:
    print(signup({"email": "ada@example.com", "year": "1990"}))
    print(signup({"email": "grace", "year": "1990"}))
except ValueError as e:
    print("form error:", e)
```

The reason survives, but only as long as every caller remembers the `try`.
Forget it once, and a typo in a form becomes a crashed request. The signature
`signup(form)` does not warn anyone that it can fail.

## Returning the failure

Return the outcome instead of raising it. `Ok(value)` holds a success and
`Err(error)` holds a failure. `Result[T, E]` is the type of either, so the
signature now says that the function can fail and what it returns when it
does.

`then` runs the next step on the value of an `Ok`. On an `Err` it does
nothing, so the first failure travels untouched to the end. If the step
raises, `then` turns the exception into an `Err`. The checks can therefore
stay small functions that raise, and the chain collects their reasons.

```{python export=examples/signup.py}
"""Validate a signup form and say what is wrong with it."""

from purely import Err, Ok, Result


def check_email(form):
    if "@" not in form.get("email", ""):
        raise ValueError("the email needs an @")
    return form


def check_year(form):
    if not form.get("year", "").isdigit():
        raise ValueError("the birth year must be a number")
    return form


def to_account(form):
    return {"email": form["email"], "adult": 2026 - int(form["year"]) >= 18}


def signup(form: dict) -> Result[dict, Exception]:
    return Ok(form).then(check_email).then(check_year).then(to_account)
```

The caller receives a value and has to look at it. `Ok` and `Err` work with
`match`:

```{python continue export=examples/signup.py}


def form_message(form):
    match signup(form):
        case Ok(account):
            return f"welcome, {account['email']} (adult: {account['adult']})"
        case Err(reason):
            return f"please fix: {reason}"


if __name__ == "__main__":
    print(form_message({"email": "ada@example.com", "year": "1990"}))
    print(form_message({"email": "grace", "year": "1990"}))
    print(form_message({"email": "alan@example.com", "year": "next year"}))
```

`is_ok` and `is_err` answer the question without `match`, and `unwrap` takes
the value out of an `Ok`. On an `Err`, `unwrap` raises the error, or returns
a default you pass. In purely 1.2 that default must not be `None`, which is
read as "no default".

```{python continue}
result = signup({"email": "grace", "year": "1990"})
print(result.is_ok(), result.is_err())
print(signup({"email": "ada@example.com", "year": "1990"}).unwrap())
print(result.unwrap({"email": None, "adult": False}))
```

A step does not have to raise to fail: it can return an `Err` itself, as in
`Err("this email already has an account")`. When you need to turn a failure
back into a success, for example to let a visitor in as a guest, `catch` runs
a function on the error and returns `Ok` with its result. On an `Ok`, `catch`
does nothing.

```{python continue}
as_guest = signup({"email": "grace", "year": "1990"}).catch(
    lambda reason: {"email": "guest", "adult": False}
)
print(as_guest)
```

`then` turns every exception into an `Err`, including a `NameError` from a
typo in your own step. When a chain fails for a reason you did not expect,
print the error before you look anywhere else.
