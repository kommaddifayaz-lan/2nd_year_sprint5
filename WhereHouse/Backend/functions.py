
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import Session, declarative_base
from datetime import date, datetime,timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

DB_PATH = "wherehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

USERNAME = "12345"
PASSWORD = "pass"

ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7*24*60
SECRET_KEY = "screte123"
ALGORITHM = "HS256"


class Packages(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    arrival_date = Column(Date, default=date.today)
    status = Column(String, default="RECEIVED")
    dispatch_batch_id = Column(Integer, ForeignKey("dispatch_batches.id"), nullable=True)


class DispatchBatches(Base):
    __tablename__ = "dispatch_batches"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, nullable=False)
    vehicle_number = Column(String, nullable=False)
    dispatch_status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.now)
    dispatched_at = Column(DateTime, nullable=True)

class Users(Base):
    __tablename__="users"

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)

    

Base.metadata.create_all(engine)

# verification

def verify_login(username,password):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name = username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False
    session.close()
    access_token = create_token(username=username, token_type="access")
    refresh_token = create_token(username=username, token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token}


    
    # if username == USERNAME and password == PASSWORD:
    #     access_token = create_token(username=username, token_type="access")
    #     refresh_token = create_token(username=username, token_type="refresh")
    #     return {"access_token": access_token, "refresh_token": refresh_token}
    # return None

def create_token(username, token_type):
    time = None
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    
    payload = {
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token,token_type):
    try:
        payload = jwt.decode(jwt=token,key=SECRET_KEY,algorithms=[ALGORITHM])
    except:
        return False
    
    if payload["token_type"] == token_type:
        return payload["username"]
    return False

# Users

def register_user(user_name:str, password:str):
    session = Session(engine)
    user_exists = session.query(Users).filter_by(user_name=user_name).first()
    if user_exists is not None:
        session.close()
        return False
    session.add(Users(user_name=user_name,password=ph.hash(password)))
    session.commit()
    session.close()
    return True

    
    
def get_packages():
    session =Session(engine)
    packages = session.query(Packages).all()
    response = []
    for package in packages:
        temp_package= {
            "id" : package.id,
            "package_name" : package.package_name,
            "destination" : package.destination,
            "weight" : package.weight,
            "arrival_date" : package.arrival_date,
            "status" : package.status,
            "dispatch_batch_id" : package.dispatch_batch_id,
        }
        response.append(temp_package)
    session.close()
    return response
     


# 1) Register a package

def register_package(package_name, destination, weight):
    session = Session(engine)
    new_package = Packages(package_name=package_name, destination=destination, weight=weight)
    session.add(new_package)
    session.commit()
    response = {
        "id": new_package.id,
        "package_name": new_package.package_name,
        "destination": new_package.destination,
        "weight": new_package.weight,
        "arrival_date": new_package.arrival_date,
        "status": new_package.status,
        "dispatch_batch_id": new_package.dispatch_batch_id
    }
    
    session.close()
    return response

#2) Get the details of a specific package

def get_package(package_id):    
    
    session = Session(engine)
    package = session.query(Packages).filter(Packages.id == package_id).first()
    if package is None:
        session.close()
        return None
    if package:
        response = {
            "id": package.id,
            "package_name": package.package_name,
            "destination": package.destination,
            "weight": package.weight,
            "arrival_date": package.arrival_date,
            "status": package.status,
            "dispatch_batch_id": package.dispatch_batch_id
        }
    session.close()
    return response
   
#3) Partially update package details

def update_package(package_id, package_name=None, destination=None, weight=None,arrival_date=None, status=None):
    session = Session(engine)
    package = session.query(Packages).filter(Packages.id == package_id).first()
    if package is None:
        session.close()
        return None
    if package_name is not None:
        package.package_name = package_name
    if destination is not None:
        package.destination = destination
    if weight is not None:
        package.weight = weight
    if arrival_date is not None:
        package.arrival_date = arrival_date
    if status is not None:
        package.status = status
    session.commit()
    response = {
                "id": package.id,
                "package_name": package.package_name,
                "destination": package.destination,
                "weight": package.weight,
                "arrival_date": package.arrival_date,
                "status": package.status
    }
    session.close()
    return response

#4) Delete a package (only if it has not been dispatched)

def delete_package(package_id):
    session = Session(engine)
    package = session.query(Packages).filter(Packages.id == package_id).first()
    if package is None:
        session.close()
        return None
    if package.status == "DISPATCHED":
        session.close()
        return {"error": "Cannot delete a dispatched package."}

    if package.dispatch_batch_id is not None:
        session.close()
        return {"error": "Package is already assigned to a dispatch batch."}


    session.delete(package)
    session.commit()
    session.close()
    return {"message": "Package deleted successfully."}

#5) Search and filter packages (by destination, status, arrival date)

def get_search_packages(destination=None, status=None, arrival_date=None):
    session = Session(engine)
    query = session.query(Packages)

    if destination is not None:
        query = query.filter(Packages.destination == destination)
    if status is not None:
        query = query.filter(Packages.status == status)
    if arrival_date is not None:
        query = query.filter(Packages.arrival_date == arrival_date)

    packages = query.all()

    response = []
    for package in packages:
        temp_package = {
            "id": package.id,
            "package_name": package.package_name,
            "destination": package.destination,
            "weight": package.weight,
            "arrival_date": package.arrival_date,
            "status": package.status,
            "dispatch_batch_id": package.dispatch_batch_id
        }
        response.append(temp_package)

    session.close()
    return response

#6 View dispatch batches (filter by destination, vehicle, dispatch status)
    
def get_dispatch_batches(destination = None, vehicle_number = None,dispatch_status = None):
    session=Session(engine)
    query = session.query(DispatchBatches)

    if destination is not None:
            query = query.filter(DispatchBatches.destination == destination)
    if dispatch_status is not None:
        query = query.filter(DispatchBatches.dispatch_status == dispatch_status)
    if vehicle_number is not None:
        query = query.filter(DispatchBatches.vehicle_number == vehicle_number)

    dispatch_batches=  query.all()
    response=[]
    for dispatch_batch in dispatch_batches:

        # Get all packages assigned to this dispatch batch
        packages = session.query(Packages).filter(Packages.dispatch_batch_id == dispatch_batch.id).all()

        package_ids = []

        for package in packages:
            package_ids.append(package.id)

        temp_dispatch_batch = {
            "id": dispatch_batch.id,
            "destination": dispatch_batch.destination,
            "vehicle_number": dispatch_batch.vehicle_number,
            "dispatch_status": dispatch_batch.dispatch_status,
            "package_ids": package_ids,
            "created_at": dispatch_batch.created_at,
            "dispatched_at": dispatch_batch.dispatched_at
        }

        response.append(temp_dispatch_batch)

    session.close()
    return response

#7 Get warehouse statistics (dispatch summary)

def get_warehouse_statistics():
    session = Session(engine)

    total_packages = session.query(Packages).count()
    pending_packages = session.query(Packages).filter(Packages.status == "PENDING").count()
    dispatched_packages = session.query(Packages).filter(Packages.status == "DISPATCHED").count()
    destination_wise = {}

    packages = session.query(Packages).all()

    for package in packages:
        if package.destination in destination_wise:
            destination_wise[package.destination] = destination_wise[package.destination] + 1
        else:
            destination_wise[package.destination] = 1

    response = {
        "total_packages": total_packages,
        "pending_packages": pending_packages,
        "dispatched_packages": dispatched_packages,
        "destination_wise": destination_wise
    }

    session.close()
    return response

#8 Add data manually (e.g. create a dispatch batch and assign packages)

def create_dispatch_batch(destination, vehicle_number, package_ids):
    session = Session(engine)
    if not package_ids:
        session.close()
        return {"error": "Please provide package IDs."}

    packages = []

    for package_id in package_ids:
        package = session.query(Packages).filter(Packages.id == package_id).first()
        if package is None:
            session.close()
            return {"error": "Package not found."}
        if package.dispatch_batch_id is not None:
            session.close()
            return {"error": "Package is already assigned to a batch."}
        if package.status == "DISPATCHED":
            session.close()
            return {"error": "Package is already dispatched."}
        if package.destination != destination:
            session.close()
            return {"error": "Package destination does not match batch destination."}

        packages.append(package)

    new_batch = DispatchBatches(destination=destination,vehicle_number=vehicle_number)

    session.add(new_batch)
    session.commit()

    for package in packages:
        package.dispatch_batch_id = new_batch.id
        package.status = "PENDING"

    session.commit()

    response = {
        "message": "Dispatch batch created successfully.",
        "batch_id": new_batch.id,
        "destination": new_batch.destination,
        "vehicle_number": new_batch.vehicle_number,
        "dispatch_status": new_batch.dispatch_status,
        "package_ids": package_ids
    }

    session.close()
    return response