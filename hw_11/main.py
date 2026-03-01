from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract
from datetime import date, timedelta
from typing import List

# Імпортуємо ваші налаштування бази та моделі
from database import engine, Base, get_db
import models
import schemas

# Створюємо таблиці в PostgreSQL автоматично при старті
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contact Management API")

# --- CRUD операції ---

@app.post("/contacts/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=List[schemas.ContactResponse])
def read_contacts(
    skip: int = 0, 
    limit: int = 100, 
    search: str = Query(None, description="Search by first name, last name or email"), 
    db: Session = Depends(get_db)
):
    query = db.query(models.Contact)
    if search:
        query = query.filter(
            or_(
                models.Contact.first_name.ilike(f"%{search}%"),
                models.Contact.last_name.ilike(f"%{search}%"),
                models.Contact.email.ilike(f"%{search}%")
            )
        )
    return query.offset(skip).limit(limit).all()

@app.get("/contacts/birthdays/", response_model=List[schemas.ContactResponse])
def get_upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    upcoming_date = today + timedelta(days=7)
    
    # Фільтрація за днем та місяцем (ігноруючи рік)
    contacts = db.query(models.Contact).all()
    result = []
    for contact in contacts:
        # Створюємо дату дня народження в поточному році
        try:
            bday_this_year = contact.birthday.replace(year=today.year)
        except ValueError: # Для високосних років (29 лютого)
            bday_this_year = contact.birthday.replace(year=today.year, day=28)
            
        if today <= bday_this_year <= upcoming_date:
            result.append(contact)
    return result

@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(contact_id: int, contact_update: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in contact_update.model_dump().items():
        setattr(db_contact, key, value)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return None