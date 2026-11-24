"""Prints truth tables for the system's rules and checks each row against the real app.

    python truth_table.py

It uses a throwaway database, so your real plv-laf.db is never touched.
"""
import os
import tempfile
from itertools import product

from app import create_app
from database.connection import get_db
from models import claim_model, item_model, user_model

app = create_app({"DATABASE": os.path.join(tempfile.mkdtemp(), "demo.db"), "TESTING": True})

PROOF = "A valid proof of ownership text"     # long enough to pass the proof check


def tf(value):
    return "T" if value else "F"


def user_id(email):
    return get_db().execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]


def login(client, email, password):
    return client.post("/login", data={"email": email, "password": password})


with app.app_context():
    user_model.create("Demo Admin", "admin@demo.test", "admin1234", "Admin")
    user_model.create("Demo Student", "student@demo.test", "student1234", "Student")
    user_model.create("Demo Finder", "finder@demo.test", "finder1234", "Student")


# ================================================================ TABLE 1
# Rule in routes/utils.py:  admin_required  ->  logged_in AND role == "Admin"
#   p = the visitor is logged in
#   q = the visitor's role is Admin

def visit_admin_page(p, q):
    """Creates the situation for (p, q), then opens /admin/ and returns the result."""
    client = app.test_client()
    if p and q:
        login(client, "admin@demo.test", "admin1234")
    elif p:
        login(client, "student@demo.test", "student1234")
    elif q:
        # Not logged in, but "Admin" is sitting in the session. This can't happen
        # through the website; we force it to prove the rule still blocks it.
        with client.session_transaction() as s:
            s["role"] = "Admin"
    status = client.get("/admin/").status_code
    return {200: "page shown", 403: "403 Forbidden", 302: "redirect to login"}[status]


print("TABLE 1: access to an admin-only page")
print("p = logged in, q = role is Admin\n")
print(f"{'p':<3}{'q':<3}{'p AND q':<9}{'NOT(p AND q)':<14}{'(NOT p) OR (NOT q)':<20}real result")
for p, q in product([True, False], repeat=2):
    conj = p and q
    print(f"{tf(p):<3}{tf(q):<3}{tf(conj):<9}{tf(not conj):<14}{tf((not p) or (not q)):<20}{visit_admin_page(p, q)}")
print("\nThe NOT(p AND q) and (NOT p) OR (NOT q) columns are identical in every row: De Morgan's law.\n")


# ================================================================ TABLE 2
# Rule in models/user_model.py:  authenticate  ->  user exists AND password matches
#   u = an account with that email exists
#   m = the typed password matches that account's hash

def try_login(email, password):
    status = login(app.test_client(), email, password).status_code
    return "logged in" if status == 302 else "error shown"


print("TABLE 2: the login check")
print("u = the email has an account, m = the password matches\n")
print(f"{'u':<3}{'m':<3}{'u AND m':<9}real result")
cases = {
    (True, True): try_login("admin@demo.test", "admin1234"),
    (True, False): try_login("admin@demo.test", "wrong-password"),
    (False, False): try_login("nobody@demo.test", "wrong-password"),
    (False, True): "n/a (with no account there is no password to match)",
}
for (u, m), result in cases.items():
    print(f"{tf(u):<3}{tf(m):<3}{tf(u and m):<9}{result}")
print()


# ================================================================ TABLE 3
# Rule in routes/auth_routes.py:  an account is created only if ALL five checks pass
#   n = full name valid, e = email valid, r = role valid,
#   w = password valid,  c = confirm password matches
# Every one of the 2^5 = 32 rows is run through the real signup form.

GOOD = {"n": "Juan Dela Cruz", "r": "Student", "w": "password1"}
BAD = {"n": "J0hn 123", "e": "not-an-email", "r": "Admin", "w": "short"}

print("TABLE 3: signup, five conditions joined with AND")
print("n = name valid, e = email valid, r = role valid, w = password valid, c = confirm matches\n")
print(f"{'n':<3}{'e':<3}{'r':<3}{'w':<3}{'c':<3}{'n AND e AND r AND w AND c':<27}real result")

mismatches = 0
created_rows = 0
for number, (n, e, r, w, c) in enumerate(product([True, False], repeat=5)):
    email = f"row{number}@demo.test" if e else BAD["e"]
    password = GOOD["w"] if w else BAD["w"]
    confirm = password if c else password + "x"          # c False -> the two passwords differ
    app.test_client().post("/signup", data={
        "full_name": GOOD["n"] if n else BAD["n"],
        "email": email,
        "role": GOOD["r"] if r else BAD["r"],
        "password": password,
        "confirm": confirm,
    })
    with app.app_context():
        created = user_model.email_taken(email) if e else False
    expected = n and e and r and w and c
    mismatches += created != expected
    created_rows += created
    print(f"{tf(n):<3}{tf(e):<3}{tf(r):<3}{tf(w):<3}{tf(c):<3}{tf(expected):<27}"
          f"{'account created' if created else 'rejected'}")
print(f"\n32 rows, account created in {created_rows} (all five True). "
      f"Rows where the real app disagreed with the AND column: {mismatches}\n")


# ================================================================ TABLE 4
# Rule in routes/user_routes.py:  validate_claim  ->  a claim is saved only if
#   p = the item exists
#   q = the item is a Found report
#   r = the item is still Active
#   s = the item was NOT reported by the person claiming it
#   t = the person has NO pending claim on it already
# (and the proof text is valid, which every row below provides)

print("TABLE 4: claim eligibility, five conditions joined with AND")
print("p = item exists, q = is Found, r = is Active, s = not your own, t = no pending claim of yours\n")
print(f"{'p':<3}{'q':<3}{'r':<3}{'s':<3}{'t':<3}{'p AND q AND r AND s AND t':<27}claim saved?")
for p, q, r, s, t in product([True, False], repeat=5):
    ok = p and q and r and s and t
    print(f"{tf(p):<3}{tf(q):<3}{tf(r):<3}{tf(s):<3}{tf(t):<3}{tf(ok):<27}{'yes' if ok else 'no'}")
print("\nOnly 1 of the 32 rows is True. Now the real app, one case per condition:\n")

with app.app_context():
    finder, claimant = user_id("finder@demo.test"), user_id("student@demo.test")
    item_ok = item_model.create(finder, "Black wallet", "Wallet / Bag", "", "Library", "Found")
    item_lost = item_model.create(finder, "Blue umbrella", "Other", "", "Gate", "Lost")
    item_removed = item_model.create(finder, "Old keys", "Keys", "", "Gate", "Found")
    item_model.set_status(item_removed, "Removed")
    item_own = item_model.create(claimant, "My own bag", "Wallet / Bag", "", "Hall", "Found")
    item_pending = item_model.create(finder, "Red scarf", "Clothing", "", "Gate", "Found")
    claim_model.create(item_pending, claimant, PROOF)         # makes t False for this item

scenarios = [
    ("all five True", item_ok),
    ("p False: no such item", 9999),
    ("q False: item is Lost", item_lost),
    ("r False: item is Removed", item_removed),
    ("s False: your own item", item_own),
    ("t False: already pending", item_pending),
]
print(f"{'case':<28}{'p AND q AND r AND s AND t':<27}real result")
client = app.test_client()
login(client, "student@demo.test", "student1234")
for label, item_id in scenarios:
    with app.app_context():
        before = len(claim_model.by_user(claimant))
    client.post("/claims", data={"item_id": str(item_id), "proof_description": PROOF})
    with app.app_context():
        saved = len(claim_model.by_user(claimant)) > before
    print(f"{label:<28}{tf(label.startswith('all')):<27}{'claim saved' if saved else 'rejected'}")