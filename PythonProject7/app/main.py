import logging
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.schemas import SubmitIn, SubmitResponse
from app.repository import FSTRRepository

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fstr")


# Создаем таблицы при старте (в т.ч. ENUM pereval_status)
def init_models():
    Base.metadata.create_all(bind=engine)
    logger.info("DB tables ensured")


app = FastAPI(title="FSTR submitData API", version="1.0.0")


@app.on_event("startup")
def on_startup():
    init_models()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/submitData", response_model=SubmitResponse)
def submit_data(payload: SubmitIn, db: Session = Depends(get_db)):
    repo = FSTRRepository(db)
    try:
        new_id = repo.create_pereval(payload)
        return SubmitResponse(status=200, message="success", id=new_id)
    except IntegrityError as e:
        db.rollback()
        logger.exception("Integrity error on submitData")
        return JSONResponse(
            status_code=409,
            content=SubmitResponse(status=409, message="integrity error", id=None).model_dump()
        )
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error on submitData")
        return JSONResponse(
            status_code=500,
            content=SubmitResponse(status=500, message="internal error", id=None).model_dump()
        )
