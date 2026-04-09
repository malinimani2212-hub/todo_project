from fastapi import FastAPI,Depends,HTTPException
from schemas import Todo as TodoSchemas,TodoCreate
from sqlalchemy.orm import Session
from database import SessionLocal,Base,engine
from models import Todo
Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/todo", response_model=TodoSchemas)
def create(todo:TodoCreate,db:Session = Depends(get_db)):
    db_todo=Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.get("/todo",response_model=list[TodoSchemas])
def read_todos(db:Session=Depends(get_db)):
    return db.query(Todo).all()

@app.get("/todo/{todo_id}",response_model=TodoSchemas)
def readone(todo_id:int,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==todo_id).first()
    if not todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    return todo

@app.put("/todo/{todo_id}", response_model=TodoSchemas)
def update_todo(todo_id:int,  updated: TodoCreate, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in updated.dict().items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todo/{todo_id}")
def delete_todo(todo_id:int,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return{"message":"Todo delete successfully"}