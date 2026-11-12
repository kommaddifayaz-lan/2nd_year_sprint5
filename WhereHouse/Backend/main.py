from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import functions
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/Packages")
def register_package(package_name: str, destination: str, weight: float):
    if weight <= 0:
        raise HTTPException(status_code=422, detail="Weight must be a positive number.")
    if not package_name or not destination:
        raise HTTPException(status_code=422, detail="Package name and destination cannot be empty.")
    return functions.register_package(package_name, destination, weight)

@app.get("/Packages/{package_id}")
def get_package(package_id: int):
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Invalid package ID. It must be a positive integer.")
    package = functions.get_package(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found.")
    return package

@app.patch("/Packages/{package_id}")
def update_package(package_id: int, package_name: str = None, destination: str = None, weight: float = None, arrival_date: str = None, status: str = None):
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Invalid package ID. It must be a positive integer.")
    if weight is not None and weight <= 0:
        raise HTTPException(status_code=422, detail="Weight must be a positive number.")
    if status is not None and status not in ["pending", "dispatched"]:
        raise HTTPException(status_code=422, detail="Invalid status")
    response = functions.update_package(package_id, package_name, destination, weight, arrival_date, status)
    if response is None:    
        raise HTTPException(status_code=404, detail="Package not found.")       
    return response

@app.delete("/Packages/{package_id}")
def delete_package(package_id: int):
  if package_id <= 0:
        raise HTTPException(status_code=422, detail="Invalid package ID. It must be a positive integer.")
  response = functions.delete_package(package_id)
  if response is None:
        raise HTTPException(status_code=404, detail="Package not found.") 
  return response