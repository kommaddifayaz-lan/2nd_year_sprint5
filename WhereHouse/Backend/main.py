from fastapi import FastAPI, HTTPException , Header 
from fastapi.middleware.cors import CORSMiddleware
import functions
from pydantic import BaseModel, Field

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

#Pydantic Models
class LoginData(BaseModel):
    username: str
    password: str

class RegisterData(BaseModel):
    user_name: str
    password: str


class PackageData(BaseModel):
    package_name: str
    destination: str
    weight: float = Field(gt=0)


class PackageUpdate(BaseModel):
    package_name: str = None
    destination: str = None
    weight: float = Field(default=None, gt=0)
    status: str = None


class DispatchBatchData(BaseModel):
    destination: str
    vehicle_number: str
    package_ids: list[int]




@app.post("/login")
def login(data: LoginData):
    token = functions.verify_login(username=data.username,password=data.password)
    if not token:
         raise HTTPException(status_code=401, detail="Invalid credentials")
    return token

@app.post("/refresh")
def refresh(refresh_token = Header(None)):
    username = functions.verify_token(token=refresh_token, token_type="refresh")
    if not username:
         raise HTTPException(status_code=401, detail="Invalid or Expired refresh token")

    access_token=functions.create_token(username=username, token_type="access")
    return {"access_token": access_token}

@app.post("/register")
def register_user(data: RegisterData):
    if functions.register_user(user_name=data.user_name, password=data.password):
        return {"message": "user registered successfully"}
    raise HTTPException(status_code=400, detail="user already exists")

@app.get("/Packages")
def get_packages(token: str = Header(None)):
    username = functions.verify_token(token=token,token_type="access")
    if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    return functions.get_packages()
     
# 1.

@app.post("/Packages")
def register_package(data: PackageData, token: str  = Header(None)):
    username = functions.verify_token(token=token,token_type="access")  
    if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    if not data.package_name or not data.destination:
        raise HTTPException(status_code=422, detail="Package name and destination cannot be empty.")
    return functions.register_package(data.package_name, data.destination, data.weight)

# 2.

@app.get("/Packages/{package_id}")
def get_package(package_id: int,token: str  = Header(None)):
    username = functions.verify_token(token=token,token_type="access")
    if not username:
         raise HTTPException(status_code=401, detail="Invalid token")
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Invalid package ID. It must be a positive integer.")
    package = functions.get_package(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found.")
    return package

# 3.

@app.patch("/Packages/{package_id}")
def update_package(package_id: int,data: PackageUpdate, token: str  = Header(None)):
    username = functions.verify_token(token=token,token_type="access")
    if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Invalid package ID. It must be a positive integer.")
    if data.status is not None and data.status not in ["pending", "dispatched"]:
        raise HTTPException(status_code=422, detail="Invalid status")
    response = functions.update_package(package_id, data.package_name, data.destination, data.weight, data.status)
    if response is None:    
        raise HTTPException(status_code=404, detail="Package not found.")       
    return response

# 4.

@app.delete("/Packages/{package_id}")
def delete_package(package_id: int,token: str = Header(None)):
    username = functions.verify_token(token=token,token_type="access")
    if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    if package_id <= 0:
            raise HTTPException(status_code=422, detail="Invalid package ID. It must be a positive integer.")
    response = functions.delete_package(package_id)
    if response is None:
            raise HTTPException(status_code=404, detail="Package not found.") 
    return response

# 5. 

@app.get("/Packages/search")
def get_search_packages(destination: str=None, status:str=None, arrival_date:str=None,token: str = Header(None)):
    username = functions.verify_token(token=token,token_type="access")
    if not username:
            raise HTTPException(status_code=401, detail="Invalid token") 
    return functions.get_search_packages(destination=destination,status=status,arrival_date=arrival_date)

# 6.

@app.get("/DispatchBatches")
def get_dispatch_batches(destination: str = None,vehicle_number: str = None,dispatch_status: str = None,token: str = Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    if dispatch_status is not None:
        if dispatch_status.upper() not in ["PENDING", "DISPATCHED"]:
            raise HTTPException(status_code=422, detail="Invalid dispatch status")
    return functions.get_dispatch_batches(destination=destination,vehicle_number=vehicle_number,dispatch_status=dispatch_status)
    

# 7. 

@app.get("/Wharehouse/Statistics")
def warehouse_statistics(token: str = Header(None)):

    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return functions.get_warehouse_statistics()

# 8. 

@app.post("/DispatchBatches")
def create_dispatch_batch(data: DispatchBatchData,token: str = Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not data.destination or not data.vehicle_number:
        raise HTTPException(status_code=422, detail="Destination and vehicle number cannot be empty.")
    if not data.package_ids:
        raise HTTPException(status_code=422, detail="Please provide package IDs.")

    return functions.create_dispatch_batch(data.destination,data.vehicle_number,data.package_ids)
    