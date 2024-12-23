import os
import sys

import uvicorn
from fastapi import FastAPI

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from app.auth.router import router as auth_router

app = FastAPI(
    title="WALK Profile"
)

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", reload=True,
    )
