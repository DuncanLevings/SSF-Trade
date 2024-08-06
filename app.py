from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import database_name, get_league_name
import sys
from pathlib import Path

def create_database_session():
    DATABASE_URL = f"sqlite:///./{database_name}.db"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    return engine, SessionLocal, Base

engine, SessionLocal, Base = create_database_session()

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    item_type =  Column(String, index=True)
    item_class = Column(String, index=True)
    sub_class = Column(String, index=True)
    rarity = Column(String, index=True)
    ilev = Column(String, index=True)
    name = Column(String, index=True)
    obtained = Column(Integer, index=True)

    __table_args__ = (
        UniqueConstraint('item_type', 'item_class', 'sub_class', 'name', name='_item_unique'),
    )

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path

static_path = get_resource_path('static')
app.mount("/static", StaticFiles(directory=static_path), name="static")

templates_path = get_resource_path('templates')
templates = Jinja2Templates(directory=templates_path)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ItemDetails(BaseModel):
    id: int
    item_type: str
    item_class: str
    sub_class: Optional[str] = None
    rarity: Optional[str] = None
    ilev:  Optional[str] = None
    name: str
    obtained: int

class ItemClassResponse(BaseModel):
    item_class: str
    items: List[ItemDetails]

class ItemResponse(BaseModel):
    item_type: str
    items: List[ItemClassResponse]

class AddItemsRequest(BaseModel):
    names: List[str]
    item_type: str
    item_class: str
    sub_class: Optional[str] = None
    rarity: Optional[str] = None

class UpdateLeagueRequest(BaseModel):
    league_name: str

class DeleteItemsRequest(BaseModel):
    ids: List[int]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/items/", response_model=List[ItemResponse])
def read_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    response = {}
    for item in items:
        if item.item_type not in response:
            response[item.item_type] = {"item_type": item.item_type, "items": {}}

        if item.item_class not in response[item.item_type]["items"]:
            response[item.item_type]["items"][item.item_class] = {
                "item_class": item.item_class,
                "items": []
            }
        
        item_detail = ItemDetails(
            id=item.id,
            item_type=item.item_type,
            item_class=item.item_class,
            sub_class=item.sub_class,
            rarity=item.rarity,
            ilev=item.ilev,
            name=item.name,
            obtained=item.obtained
        )
        
        response[item.item_type]["items"][item.item_class]["items"].append(item_detail)

    final_response = []
    for item_type, type_data in response.items():
        class_items = [ItemClassResponse(**class_data) for class_data in type_data["items"].values()]
        final_response.append(ItemResponse(item_type=item_type, items=class_items))

    return final_response

@app.post("/add_items/")
def add_items(request: AddItemsRequest, db: Session = Depends(get_db)):
    for name in request.names:
        existing_item = db.query(Item).filter(
            Item.item_type == request.item_type,
            Item.item_class == request.item_class,
            Item.sub_class == request.sub_class,
            Item.name == name
        ).first()
        if existing_item is None:
            db_item = Item(item_type=request.item_type, item_class=request.item_class, sub_class=request.sub_class, rarity=request.rarity, ilev=0, name=name, obtained=False)
            db.add(db_item)
    db.commit()
    return {"message": "Items added successfully"}

@app.put("/reset_all/")
def reset_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    for item in items:
        item.obtained = False
        item.ilev = 0
    db.commit()
    return {"message": "Items added successfully"}

def add_item(item_data):
    if (item_data['name'] == 'Unknown'):
        return

    db = SessionLocal()
    existing_item = db.query(Item).filter(
        Item.item_type == item_data['item_type'],
        Item.item_class == item_data['item_class'],
        Item.sub_class == item_data['sub_class'],
        Item.name == item_data['name']
    ).first()
    if existing_item is None:
        db_item = Item(item_type=item_data['item_type'], 
                       item_class=item_data['item_class'], 
                       sub_class=item_data['sub_class'], 
                       rarity=item_data['rarity'], 
                       ilev=item_data['ilev'],
                       name=item_data['name'], 
                       obtained=True)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    else:
        existing_item.obtained = True
        existing_item.sub_class = item_data['sub_class']
        existing_item.rarity = item_data['rarity']

        if (existing_item.ilev is None):
            existing_item.ilev = item_data['ilev']
        elif (int(existing_item.ilev) < int(item_data['ilev'])):
            existing_item.ilev = item_data['ilev']

        db.commit()
        db.refresh(existing_item)
    db.close()

@app.delete("/delete_items/")
def delete_items(request: DeleteItemsRequest, db: Session = Depends(get_db)):
    items_to_delete = db.query(Item).filter(Item.id.in_(request.ids)).all()
    if not items_to_delete:
        raise HTTPException(status_code=404, detail="Items not found")

    for item in items_to_delete:
        db.delete(item)
    db.commit()
    return {"message": "Items deleted successfully"}

@app.get("/get_league_name/")
def get_current_league_name():
    try:
        league_name = get_league_name()
        return JSONResponse(status_code=200, content={"league_name": league_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))