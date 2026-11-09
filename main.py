from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas, auth, seed
from database import engine
import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Qadam Food API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db = auth.SessionLocal()
    try:
        seed.seed_if_empty(db)
    finally:
        db.close()


def serialize_bag(b: models.Bag):
    return {
        "id": b.id,
        "title": b.title,
        "description": b.description,
        "original_price": b.original_price,
        "discounted_price": b.discounted_price,
        "pickup_start": b.pickup_start,
        "pickup_end": b.pickup_end,
        "pickup_date": "today",
        "quantity_available": b.quantity_available,
        "image_url": b.image_url,
        "status": b.status,
        "store_id": b.store_id,
        "stores": {
            "id": b.store.id if b.store else None,
            "name": b.store.name if b.store else "Store",
            "rating": b.store.rating if b.store else 4.5,
            "address": b.store.address if b.store else "",
            "category": b.store.category if b.store else "Кафе",
            "image_url": b.store.image_url if b.store else None,
            "working_hours": b.store.working_hours if b.store else "",
        },
    }


def serialize_order(o: models.Order):
    return {
        "id": o.id,
        "qr_code": o.qr_code,
        "status": o.status,
        "created_at": o.created_at,
        "user_id": o.user_id,
        "bags": {
            "title": o.bag.title if o.bag else "Surprise Bag",
            "pickup_start": o.bag.pickup_start if o.bag else "",
            "pickup_end": o.bag.pickup_end if o.bag else "",
            "discounted_price": o.bag.discounted_price if o.bag else 0,
            "original_price": o.bag.original_price if o.bag else 0,
            "stores": {"name": o.bag.store.name if o.bag and o.bag.store else "Store"},
        },
        "user": {
            "full_name": o.user.full_name if o.user else "",
            "email": o.user.email if o.user else "",
        },
    }


@app.get("/")
def root():
    return {"status": "ok", "app": "Qadam Food API"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Бұл email тіркелген")

        hashed_pwd = auth.get_password_hash(user.password)
        new_user = models.User(
            email=user.email,
            hashed_password=hashed_pwd,
            full_name=user.full_name,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        token = auth.create_access_token(data={"sub": new_user.email})
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("🔥 SERVER ERROR:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(auth.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Email немесе құпиясөз қате")

    token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/me")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "points": current_user.points,
        "role": current_user.role,
    }


@app.get("/api/stores")
def get_stores(db: Session = Depends(auth.get_db)):
    return db.query(models.Store).all()


@app.get("/api/stores/{store_id}")
def get_store(store_id: int, db: Session = Depends(auth.get_db)):
    store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Кафе табылмады")
    bags = db.query(models.Bag).filter(models.Bag.store_id == store_id, models.Bag.status == "active").all()
    return {
        "id": store.id,
        "name": store.name,
        "address": store.address,
        "phone": store.phone,
        "working_hours": store.working_hours,
        "category": store.category,
        "rating": store.rating,
        "image_url": store.image_url,
        "bags": [serialize_bag(b) for b in bags],
    }


@app.post("/api/stores")
def create_store(store: schemas.StoreCreate, db: Session = Depends(auth.get_db)):
    new_store = models.Store(**store.dict())
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store


@app.get("/api/bags")
def get_bags(
    q: str = Query(default=""),
    category: str = Query(default=""),
    db: Session = Depends(auth.get_db),
):
    bags = db.query(models.Bag).filter(models.Bag.status == "active").all()
    result = []
    for b in bags:
        item = serialize_bag(b)
        hay = f"{item['title']} {item['stores']['name']} {item['stores']['category']}".lower()
        if q and q.lower() not in hay:
            continue
        if category and item["stores"]["category"] != category:
            continue
        result.append(item)
    return result


@app.post("/api/bags")
def create_bag(bag: schemas.BagCreate, db: Session = Depends(auth.get_db)):
    new_bag = models.Bag(**bag.dict())
    db.add(new_bag)
    db.commit()
    db.refresh(new_bag)
    return new_bag


@app.post("/api/orders")
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    bag = db.query(models.Bag).filter(models.Bag.id == order.bag_id).first()
    if not bag or bag.quantity_available <= 0:
        raise HTTPException(status_code=400, detail="Пакет таусылған")

    qr_code = f"QADAM-{str(uuid.uuid4())[:6].upper()}"

    new_order = models.Order(
        user_id=current_user.id,
        bag_id=bag.id,
        qr_code=qr_code,
    )

    bag.quantity_available -= 1
    if bag.quantity_available == 0:
        bag.status = "sold_out"

    current_user.points = (current_user.points or 0) + 50

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {"order_id": new_order.id, "qr_code": qr_code, "points": current_user.points}


@app.get("/api/orders")
def get_orders(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    orders = (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )
    return [serialize_order(o) for o in orders]


@app.get("/api/admin/orders")
def get_admin_orders(db: Session = Depends(auth.get_db)):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return [serialize_order(o) for o in orders]


@app.put("/api/orders/{order_id}/complete")
def complete_order(order_id: int, db: Session = Depends(auth.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ табылмады")
    order.status = "completed"
    db.commit()
    return {"message": "Order completed"}


@app.delete("/api/stores/{store_id}")
def delete_store(store_id: int, db: Session = Depends(auth.get_db)):
    store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if not store:
        return {"message": "Store not found"}
    bags = db.query(models.Bag).filter(models.Bag.store_id == store_id).all()
    bag_ids = [b.id for b in bags]
    if bag_ids:
        db.query(models.Order).filter(models.Order.bag_id.in_(bag_ids)).delete(synchronize_session=False)
        db.query(models.Bag).filter(models.Bag.store_id == store_id).delete(synchronize_session=False)
    db.delete(store)
    db.commit()
    return {"message": "Store deleted"}


@app.delete("/api/bags/{bag_id}")
def delete_bag(bag_id: int, db: Session = Depends(auth.get_db)):
    bag = db.query(models.Bag).filter(models.Bag.id == bag_id).first()
    if bag:
        db.query(models.Order).filter(models.Order.bag_id == bag_id).delete(synchronize_session=False)
        db.delete(bag)
        db.commit()
    return {"message": "Bag deleted"}


@app.get("/api/users")
def get_all_users(db: Session = Depends(auth.get_db)):
    users = db.query(models.User).order_by(models.User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "points": u.points,
            "created_at": u.created_at,
        }
        for u in users
    ]


@app.get("/api/stats")
def get_stats(db: Session = Depends(auth.get_db)):
    users_count = db.query(func.count(models.User.id)).scalar() or 0
    orders_count = db.query(func.count(models.Order.id)).scalar() or 0
    bags_count = db.query(func.count(models.Bag.id)).filter(models.Bag.status == "active").scalar() or 0
    stores_count = db.query(func.count(models.Store.id)).scalar() or 0
    meals_saved = max(orders_count, 12)
    kg_saved = round(meals_saved * 0.4, 1)
    co2 = round(kg_saved * 2.1, 1)
    return {
        "users": users_count,
        "orders": orders_count,
        "active_bags": bags_count,
        "stores": stores_count,
        "meals_saved": meals_saved,
        "kg_saved": kg_saved,
        "co2_prevented": co2,
    }
