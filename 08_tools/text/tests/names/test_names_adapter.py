from pathlib import Path

from names_adapter import NamesAdapter


NAMES_FILE = Path(__file__).parent / "test_names.txt"


def show(label: str, result: dict | None) -> None:
    print(f"\n{label}")
    print(result)


adapter = NamesAdapter(NAMES_FILE)

show("AUTHORIZED: Miguel Caló", adapter.lookup("Miguel Caló"))
show("AUTHORIZED: D'Arienzo", adapter.lookup("D'Arienzo"))
show("PROVISIONAL: Carlos Di Sarli", adapter.lookup("Carlos Di Sarli"))
show("NOT FOUND: José María Contursi", adapter.lookup("José María Contursi"))

show(
    "VERIFY/CREATE: José María Contursi",
    adapter.verify_or_create("José María Contursi"),
)

show(
    "VERIFY AGAIN: José María Contursi",
    adapter.verify_or_create("José María Contursi"),
)
print("\nPROVISIONAL → AUTHORIZED")

provisional = adapter.verify_or_create("José María Contursi")
print("before:", provisional)

authorized = adapter.authorize(
    provisional["name_ref"],
    "José María Contursi",
    "TEST-AUTHORITY",
)
print("after:", authorized)

print("\nREFERENCE PRESERVED")
print(
    "same ref:",
    provisional["name_ref"] == authorized["name_ref"],
)