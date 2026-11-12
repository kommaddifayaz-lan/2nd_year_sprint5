
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import Session, declarative_base
from datetime import date, datetime

DB_PATH = "wherehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()


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


Base.metadata.create_all(engine)

# Register a package
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

#Get the details of a specific package

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
   
#Partially update package details

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

#Delete a package (only if it has not been dispatched)
def delete_package(package_id):
    session = Session(engine)
    package = session.query(Packages).filter(Packages.id == package_id).first()
    if package is None:
        session.close()
        return None
    if package.status == "DISPATCHED":
        session.close()
        return {"error": "Cannot delete a dispatched package."}
    session.delete(package)
    session.commit()
    session.close()
    return {"message": "Package deleted successfully."}
   
