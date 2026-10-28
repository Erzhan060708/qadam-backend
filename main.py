from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, auth
from database import engine
import uuid

# Кестелерді жасау
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Qadam Food API")

# CORS (Flutter Web-тан сұраныс қабылдау үшін МІНДЕТТІ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Кейін Vercel сілтемесін қоясыз
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== AUTH ==================
@app.post("/api/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Бұл email тіркелген")
    
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.User(
        email=user.email, 
        hashed_password=hashed_pwd, 
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = auth.create_access_token(data={"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

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
        "role": current_user.role
    }

# ================== STORES ==================
@app.get("/api/stores")
def get_stores(db: Session = Depends(auth.get_db)):
    return db.query(models.Store).all()

@app.post("/api/stores")
def create_store(store: schemas.StoreCreate, db: Session = Depends(auth.get_db)):
    new_store = models.Store(**store.dict())
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store

# ================== BAGS ==================
@app.get("/api/bags")
def get_bags(db: Session = Depends(auth.get_db)):
    bags = db.query(models.Bag).filter(models.Bag.status == "active").all()
    result = []
    for b in bags:
        result.append({
            "id": b.id,
            "title": b.title,
            "original_price": b.original_price,
            "discounted_price": b.discounted_price,
            "pickup_start": b.pickup_start,
            "pickup_end": b.pickup_end,
            "quantity_available": b.quantity_available,
            "image_url": b.image_url,
            "stores": {
                "name": b.store.name,
                "rating": b.store.rating
            }
        })
    return result

@app.post("/api/bags")
def create_bag(bag: schemas.BagCreate, db: Session = Depends(auth.get_db)):
    new_bag = models.Bag(**bag.dict())
    db.add(new_bag)
    db.commit()
    db.refresh(new_bag)
    return new_bag

# ================== ORDERS ==================
@app.post("/api/orders")
def create_order(
    order: schemas.OrderCreate, 
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bag = db.query(models.Bag).filter(models.Bag.id == order.bag_id).first()
    if not bag or bag.quantity_available <= 0:
        raise HTTPException(status_code=400, detail="Пакет таусылған")
    
    qr_code = f"QADAM-{str(uuid.uuid4())[:6].upper()}"
    
    new_order = models.Order(
        user_id=current_user.id,
        bag_id=bag.id,
        qr_code=qr_code
    )
    
    bag.quantity_available -= 1
    if bag.quantity_available == 0:
        bag.status = "sold_out"
        
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return {"order_id": new_order.id, "qr_code": qr_code}

# ================== MISSING ENDPOINTS ==================
@app.get("/api/orders")
def get_orders(db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    orders = db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "qr_code": o.qr_code,
            "status": o.status,
            "created_at": o.created_at,
            "bags": {
                "title": o.bag.title,
                "pickup_start": o.bag.pickup_start,
                "pickup_end": o.bag.pickup_end,
                "discounted_price": o.bag.discounted_price,
                "stores": {"name": o.bag.store.name}
            }
        })
    return result

@app.put("/api/orders/{order_id}/complete")
def complete_order(order_id: int, db: Session = Depends(auth.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        order.status = "completed"
        db.commit()
    return {"message": "Order completed"}



@app.delete("/api/stores/{store_id}")
def delete_store(store_id: int, db: Session = Depends(auth.get_db)):
    store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if store:
        db.delete(store)
        db.commit()
    return {"message": "Store deleted"}

@app.delete("/api/bags/{bag_id}")
def delete_bag(bag_id: int, db: Session = Depends(auth.get_db)):
    bag = db.query(models.Bag).filter(models.Bag.id == bag_id).first()
    if bag:
        db.delete(bag)
        db.commit()
    return {"message": "Bag deleted"}