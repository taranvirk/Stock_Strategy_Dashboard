from app.database import seed
from app.database.base import Base
from app.database.models import User
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


def test_seed_renames_existing_demo_account_without_recreating_it(monkeypatch) -> None:
    monkeypatch.setattr(seed, "seed_market_catalog", lambda db: None)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    try:
        with Session(engine) as db:
            demo = User(
                email=seed.DEMO_EMAIL,
                password_hash="existing-password-hash",
                first_name="TradeIQ",
                last_name="Demo",
                full_name="TradeIQ Demo",
                is_demo=True,
            )
            db.add(demo)
            db.commit()
            original_id = demo.id

            seed.seed_demo_database(db)
            seed.seed_demo_database(db)
            db.expire_all()

            updated_demo = db.scalars(select(User)).one()
            assert updated_demo.id == original_id
            assert updated_demo.first_name == "Stock Strategy"
            assert updated_demo.full_name == "Stock Strategy Demo"
            assert updated_demo.password_hash == "existing-password-hash"
    finally:
        engine.dispose()
