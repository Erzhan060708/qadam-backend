from sqlalchemy.orm import Session
import models
import auth


DEMO_STORES = [
    {
        "name": "Qazan Deli",
        "address": "Алматы, проспект Серкебаева, 5",
        "working_hours": "09:00 - 21:00",
        "category": "Кафе",
        "rating": 4.8,
        "image_url": "assets/stores/qazan_deli.png",
    },
    {
        "name": "The Hleb",
        "address": "Алматы, улица Егизбаева, 7/21",
        "working_hours": "08:00 - 21:00",
        "category": "Наубайхана",
        "rating": 4.8,
        "image_url": "assets/stores/the_hleb.png",
    },
    {
        "name": "Umai",
        "address": "Алматы, улица Абиша Кекилбайулы, 149",
        "working_hours": "09:00 - 22:00",
        "category": "Кафе",
        "rating": 4.7,
        "image_url": "assets/stores/umai.png",
    },
    {
        "name": "Восток",
        "address": "Алматы, проспект Серкебаева, 25",
        "working_hours": "08:00 - 21:00",
        "category": "Наубайхана",
        "rating": 4.7,
        "image_url": "assets/stores/vostok.png",
    },
    {
        "name": "Дәмді бауырсақ",
        "address": "Алматы, проспект Сейфуллина, 402/1а",
        "working_hours": "08:00 - 20:00",
        "category": "Наубайхана",
        "rating": 4.9,
        "image_url": "assets/stores/damdi_bauyrsak.png",
    },
    {
        "name": "Три Пирога",
        "address": "Алматы, улица Дуйсенова, 25",
        "working_hours": "08:00 - 21:00",
        "category": "Наубайхана",
        "rating": 4.8,
        "image_url": "assets/stores/tri_piroga.png",
    },
]

DEMO_BOXES = {
    "Qazan Deli": (2800, 1190),
    "The Hleb": (2400, 990),
    "Umai": (3000, 1290),
    "Восток": (2200, 890),
    "Дәмді бауырсақ": (1800, 790),
    "Три Пирога": (2600, 1090),
}


def seed_if_empty(db: Session):
    target_names = {store["name"] for store in DEMO_STORES}
    existing = db.query(models.Store).all()

    # Archive the former demo venues so prior orders keep their original references.
    for store in existing:
        if store.name not in target_names and store.is_active:
            store.is_active = False
            for bag in db.query(models.Bag).filter(models.Bag.store_id == store.id, models.Bag.status == "active").all():
                bag.status = "archived"

    by_name = {store.name: store for store in existing}
    newly_added = []
    for data in DEMO_STORES:
        store = by_name.get(data["name"])
        if store is None:
            store = models.Store(**data, is_active=True)
            db.add(store)
            newly_added.append(store)
        else:
            for key, value in data.items():
                setattr(store, key, value)
            store.is_active = True

    db.flush()

    # Each new venue starts with a flexible surprise box, never a fixed food list.
    for store in newly_added:
        original, discounted = DEMO_BOXES[store.name]
        db.add(models.Bag(
            store_id=store.id,
            title="Сюрприз-бокс",
            description="Демо ұсыныс. Ішіндегі тағамдар күн сайынғы артық өнімге қарай өзгереді; демо бағасы кафемен нақтыланады.",
            original_price=original,
            discounted_price=discounted,
            pickup_start="18:00",
            pickup_end="21:00",
            quantity_available=5,
            image_url=store.image_url,
        ))

    if not db.query(models.User).filter(models.User.email == "demo@qadam.food").first():
        db.add(models.User(
            email="demo@qadam.food",
            hashed_password=auth.get_password_hash("qadam123"),
            full_name="Demo Student",
            points=120,
        ))

    db.commit()
    _ensure_demo_merchants(db)


def _ensure_demo_merchants(db: Session):
    for store in db.query(models.Store).filter(models.Store.is_active.is_(True)).all():
        email = f"demo.cafe{store.id}@qadam.food"
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            user = models.User(
                email=email,
                hashed_password=auth.get_password_hash(f"QadamDemo!{store.id}"),
                full_name=f"{store.name} demo",
                role="merchant",
            )
            db.add(user)
            db.flush()
        store.owner_user_id = user.id
    db.commit()
