from sqlalchemy.orm import Session
import models
import auth


DEMO_STORES = [
    {
        "name": "Coffee Boom",
        "address": "Алматы, Абай даңғылы 15",
        "phone": "+7 727 250 11 22",
        "working_hours": "08:00 - 22:00",
        "category": "Кофехана",
        "rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1501339845178-abc20adc896a?w=800",
    },
    {
        "name": "Navat",
        "address": "Алматы, Достық даңғылы 52",
        "phone": "+7 727 261 33 44",
        "working_hours": "10:00 - 23:00",
        "category": "Мейрамхана",
        "rating": 4.7,
        "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",
    },
    {
        "name": "Gagarin Bakery",
        "address": "Алматы, Гагарин даңғылы 92",
        "phone": "+7 777 101 20 30",
        "working_hours": "07:00 - 21:00",
        "category": "Наубайхана",
        "rating": 4.6,
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
    },
    {
        "name": "Piala Tea House",
        "address": "Алматы, Қонаев көшесі 12",
        "phone": "+7 701 555 66 77",
        "working_hours": "09:00 - 22:00",
        "category": "Кафе",
        "rating": 4.5,
        "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800",
    },
    {
        "name": "Bahandi Burger",
        "address": "Алматы, Сәтбаев көшесі 30",
        "phone": "+7 747 888 99 00",
        "working_hours": "11:00 - 23:00",
        "category": "Кафе",
        "rating": 4.4,
        "image_url": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=800",
    },
    {
        "name": "Fresh Bowl",
        "address": "Алматы, Тимирязев көшесі 42",
        "phone": "+7 705 321 45 67",
        "working_hours": "09:00 - 21:00",
        "category": "Асхана",
        "rating": 4.9,
        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800",
    },
    {
        "name": "Green Table",
        "address": "Демо мекенжайы, Алматы",
        "phone": "+7 700 000 00 07",
        "working_hours": "09:00 - 21:00",
        "category": "Кафе",
        "rating": 4.7,
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
    },
    {
        "name": "Marmelad Bakery",
        "address": "Демо мекенжайы, Алматы",
        "phone": "+7 700 000 00 08",
        "working_hours": "07:00 - 20:00",
        "category": "Наубайхана",
        "rating": 4.6,
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
    },
    {
        "name": "Nomad Kitchen",
        "address": "Демо мекенжайы, Алматы",
        "phone": "+7 700 000 00 09",
        "working_hours": "10:00 - 22:00",
        "category": "Асхана",
        "rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
    },
]


def seed_if_empty(db: Session):
    if db.query(models.Store).count() > 0:
        # Existing installations can safely pick up newly added demo venues.
        new_stores = []
        for data in DEMO_STORES:
            if not db.query(models.Store).filter(models.Store.name == data["name"]).first():
                store = models.Store(**data)
                db.add(store)
                new_stores.append(store)
        if new_stores:
            db.flush()
            for store in new_stores:
                db.add(models.Bag(
                    store_id=store.id,
                    title=f"{store.name} Surprise Pack",
                    description="Күн соңындағы дәмді өнімдерден құралған демо пакет.",
                    original_price=2400,
                    discounted_price=890,
                    pickup_start="18:00",
                    pickup_end="21:00",
                    quantity_available=5,
                    image_url=store.image_url,
                ))
            db.commit()
        _ensure_demo_merchants(db)
        return

    stores = []
    for data in DEMO_STORES:
        store = models.Store(**data)
        db.add(store)
        stores.append(store)
    db.flush()

    bags = [
        models.Bag(
            store_id=stores[0].id,
            title="Coffee & Cake Box",
            description="Эспрессо, круассан және тәттінің сюрприз жиынтығы.",
            original_price=2800,
            discounted_price=990,
            pickup_start="18:00",
            pickup_end="21:00",
            quantity_available=6,
            image_url="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800",
        ),
        models.Bag(
            store_id=stores[1].id,
            title="Navat Evening Plov",
            description="Күріш, ет және салаттан тұратын кешкі порция.",
            original_price=3500,
            discounted_price=1290,
            pickup_start="19:00",
            pickup_end="22:00",
            quantity_available=4,
            image_url="https://images.unsplash.com/photo-1512058564366-18510be2db19?w=800",
        ),
        models.Bag(
            store_id=stores[2].id,
            title="Bakery Surprise",
            description="Наубайхананың күн соңындағы нан мен тәттілері.",
            original_price=2200,
            discounted_price=790,
            pickup_start="17:30",
            pickup_end="20:00",
            quantity_available=8,
            image_url="https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=800",
        ),
        models.Bag(
            store_id=stores[3].id,
            title="Tea & Pastry Pack",
            description="Шайға арналған печенье мен тәтті ассорти.",
            original_price=1900,
            discounted_price=690,
            pickup_start="18:00",
            pickup_end="21:30",
            quantity_available=5,
            image_url="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800",
        ),
        models.Bag(
            store_id=stores[4].id,
            title="Burger Combo Box",
            description="Бургер, картоп және соус. Студентке арналған жиынтық.",
            original_price=3200,
            discounted_price=1190,
            pickup_start="20:00",
            pickup_end="22:30",
            quantity_available=5,
            image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800",
        ),
        models.Bag(
            store_id=stores[5].id,
            title="Healthy Bowl Mix",
            description="Салат, гранола және жеміс толы эко-пакет.",
            original_price=2600,
            discounted_price=890,
            pickup_start="18:30",
            pickup_end="21:00",
            quantity_available=7,
            image_url="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800",
        ),
        models.Bag(
            store_id=stores[0].id,
            title="Morning leftover latte",
            description="Салқын кофе мен сэндвич. Таңғы қалдықтар — жаңа бағамен.",
            original_price=2100,
            discounted_price=750,
            pickup_start="16:00",
            pickup_end="19:00",
            quantity_available=3,
            image_url="https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=800",
        ),
        models.Bag(
            store_id=stores[2].id,
            title="Student Bread Box",
            description="3-4 нан өнімі. Арзан әрі тоқ.",
            original_price=1600,
            discounted_price=490,
            pickup_start="19:00",
            pickup_end="21:00",
            quantity_available=10,
            image_url="https://images.unsplash.com/photo-1549931319-a545dcf3b7b4?w=800",
        ),
        models.Bag(
            store_id=stores[6].id,
            title="Green Table Harvest Box",
            description="Маусымдық көкөністер мен дайын салаттардан демо жиынтық.",
            original_price=2500,
            discounted_price=990,
            pickup_start="18:00",
            pickup_end="21:00",
            quantity_available=5,
            image_url=stores[6].image_url,
        ),
        models.Bag(
            store_id=stores[7].id,
            title="Marmelad Bakery Box",
            description="Күн соңындағы жаңа піскен нан-тоқаштар.",
            original_price=2200,
            discounted_price=790,
            pickup_start="17:00",
            pickup_end="20:00",
            quantity_available=6,
            image_url=stores[7].image_url,
        ),
        models.Bag(
            store_id=stores[8].id,
            title="Nomad Kitchen Dinner Pack",
            description="Үй тағамдарының кешкі демо жиынтығы.",
            original_price=3000,
            discounted_price=1190,
            pickup_start="19:00",
            pickup_end="21:30",
            quantity_available=4,
            image_url=stores[8].image_url,
        ),
    ]
    db.add_all(bags)

    if not db.query(models.User).filter(models.User.email == "demo@qadam.food").first():
        db.add(
            models.User(
                email="demo@qadam.food",
                hashed_password=auth.get_password_hash("qadam123"),
                full_name="Demo Student",
                points=120,
            )
        )

    db.commit()
    _ensure_demo_merchants(db)
    print("🌱 Demo stores and bags seeded")


def _ensure_demo_merchants(db: Session):
    """Create isolated demo-only merchant accounts for the sample venues."""
    for store in db.query(models.Store).order_by(models.Store.id).all():
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
        if store.owner_user_id is None:
            store.owner_user_id = user.id
    db.commit()
