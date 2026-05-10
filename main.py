from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.operations import router as operations_router
from app.api.v1.wallets import router as wallets_router
from app.api.v1.users import router as users_router
from app.database import Base, engine


app = FastAPI()

app.include_router(wallets_router, prefix="/api/v1", tags=["wallets"])
app.include_router(operations_router, prefix="/api/v1", tags=["operations"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")


Base.metadata.create_all(bind=engine)

# @app.get("/balance")
# def get_balance(wallet_name: str | None = None):
#     # if the wallet_name is not specified - calculate total balance
#     if wallet_name is None:
#         return {"total_balance": sum(BALANCE.values())}
#     # check if wallet_name exists
#     if wallet_name not in BALANCE:
#         raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
#     # return the balance of the specified wallet_name
#     return {"wallet": wallet_name, "balance": BALANCE[wallet_name]}


# @app.get("/wallets")
# def list_wallets():
#     return {"wallets": dict(BALANCE)}


# @app.post("/wallets")
# def create_wallet(wallet: CreateWalletRequest):
#     if wallet.name in BALANCE:
#         raise HTTPException(
#             status_code=400, detail=f"Wallet '{wallet.name}'already exists "
#         )

#     BALANCE[wallet.name] = wallet.initial_balance

#     return {
#         "message": f"Wallet {wallet.name} created'",
#         "wallet": wallet.name,
#         "balance": BALANCE[wallet.name],
#     }


# @app.post("/operations/expense")
# def add_expense(operation: OperationRequest):
#     if operation.wallet_name not in BALANCE:
#         raise HTTPException(
#             status_code=400, detail=f"Wallet '{operation.wallet_name}' not found"
#         )

#     if operation.amount > BALANCE[operation.wallet_name]:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Isufficient funds. Available: {BALANCE[operation.wallet_name]}",
#         )

#     BALANCE[operation.wallet_name] -= operation.amount

#     return {
#         "message": "Expense added",
#         "wallet": operation.wallet_name,
#         "amount": operation.amount,
#         "description": operation.description,
#         "new_balance": BALANCE[operation.wallet_name],
#     }


# @app.post("/operations/income")
# def add_income(operation: OperationRequest):
#     if operation.wallet_name not in BALANCE:
#         raise HTTPException(
#             status_code=400, detail=f"Wallet '{operation.wallet_name}' not found"
#         )

#     BALANCE[operation.wallet_name] += operation.amount

#     return {
#         "message": "Income added",
#         "wallet": operation.wallet_name,
#         "amount": operation.amount,
#         "description": operation.description,
#         "new_balance": BALANCE[operation.wallet_name],
#     }
