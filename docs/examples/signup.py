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
