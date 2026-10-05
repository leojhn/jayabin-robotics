from excel_loader import db
from billing_manager import BillingManager

print("CONSULTANT COLUMNS")
print(db.consultants.columns.tolist())

print("\nFIRST CONSULTANT")
print(db.consultants.iloc[0])

bm = BillingManager()

print("\n==============================")
print("CONSULTANT BILL")
print("==============================")

print(
    bm.get_consultant_bill("PAT-014")
)

print("\n==============================")
print("SERVICE BILL")
print("==============================")

print(
    bm.get_service_bill("PAT-014")
)

print("\n==============================")
print("PAYMENT HISTORY")
print("==============================")

for item in bm.get_payment_history("PAT-014"):
    print(item)