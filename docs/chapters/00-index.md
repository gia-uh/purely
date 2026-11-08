Purely is a small, dependency-free library for the parts of everyday Python
that tend to fill up with `if x is None`, `try`/`except` and `isinstance`
checks. It needs Python 3.12 or later.

```bash
pip install purely
```

This guide follows one small project: the backend of an online bookshop.
Each chapter starts with a job the shop needs done, writes it first in plain
Python, looks at what goes wrong as it grows, and then fixes it with one or two
ideas from purely. Later chapters reuse what the earlier ones introduced, and
the last one puts everything together into a checkout.

1. **A customer's city.** Showing a value that may be missing, with `Option`.
2. **Reading the shop's settings.** Walking nested data with `safe`, and
   insisting on what is required with `ensure`.
3. **Validating a signup.** Reporting why something failed, with `Ok` and
   `Err`.
4. **Importing a batch of orders.** Running a list through several steps and
   stopping cleanly on the first broken row, with `Chain`.
5. **Pricing rules.** Composing small configurable steps, with `curry` and
   `pipe`.
6. **Sending notifications.** Choosing what to do by the kind of event, with
   `dispatcher`.
7. **Testing the checkout.** Swapping a real payment gateway for a fake one,
   with `Registry` and `depends`.
8. **The checkout, end to end.** All of the above in one program, with nothing
   new.

Every code block in this guide runs against the installed package when the
guide is built. The output under a block is what that run printed. Each
chapter's finished program is also saved in the repository under
`docs/examples/`.
