from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
import os
import uuid
import asyncio
from datetime import datetime
import aiofiles
from .models import Contract, ContractStatus, ContractData
from .parser import ContractParser
from .scoring import ScoringEngine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Contract Intelligence Parser", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
contract_parser = ContractParser()
scoring_engine = ScoringEngine()

@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup"""
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    app.mongodb = app.mongodb_client.contract_intelligence
    
    # Create indexes
    try:
        await app.mongodb.contracts.create_index("id", unique=True)
        await app.mongodb.contracts.create_index("status")
        await app.mongodb.contracts.create_index("uploaded_at")
        await app.mongodb.contracts.create_index("score")
        await app.mongodb.contracts.create_index([("status", 1), ("uploaded_at", -1)])
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating database indexes: {str(e)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    if hasattr(app, 'mongodb_client'):
        app.mongodb_client.close()

@app.post("/contracts/upload")
async def upload_contract(file: UploadFile = File(...)):
    """Upload a contract file and initiate background processing"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Generate unique contract ID
        contract_id = str(uuid.uuid4())
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(uploads_dir, f"{contract_id}.pdf")
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create contract record in database
        contract = Contract(
            id=contract_id,
            filename=file.filename,
            file_path=file_path,
            status=ContractStatus.PENDING,
            uploaded_at=datetime.utcnow(),
            file_size=len(content)
        )
        
        await app.mongodb.contracts.insert_one(contract.dict())
        
        # Start background processing
        asyncio.create_task(process_contract(contract_id))
        
        return {"contract_id": contract_id, "status": "uploaded", "message": "Contract uploaded successfully"}
    
    except Exception as e:
        logger.error(f"Error uploading contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading contract: {str(e)}")

@app.get("/contracts/{contract_id}/status")
async def get_contract_status(contract_id: str):
    """Get the processing status of a contract"""
    try:
        contract = await app.mongodb.contracts.find_one({"id": contract_id})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return {
            "contract_id": contract_id,
            "status": contract["status"],
            "progress": contract.get("progress", 0),
            "error": contract.get("error"),
            "updated_at": contract.get("updated_at")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting contract status: {str(e)}")

@app.get("/contracts/{contract_id}")
async def get_contract_data(contract_id: str):
    """Get parsed contract data"""
    try:
        contract = await app.mongodb.contracts.find_one({"id": contract_id})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        if contract["status"] != ContractStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Contract processing not completed")
        
        return contract.get("parsed_data", {})
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting contract data: {str(e)}")

@app.get("/contracts")
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    sort_by: str = Query("uploaded_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc")
):
    """Get paginated list of contracts with filtering and sorting"""
    try:
        # Build filter
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        
        # Build sort
        sort_direction = -1 if sort_order == "desc" else 1
        sort_dict = {sort_by: sort_direction}
        
        # Get contracts
        cursor = app.mongodb.contracts.find(filter_dict).sort(sort_dict).skip(skip).limit(limit)
        contracts = await cursor.to_list(length=limit)
        
        # Get total count
        total = await app.mongodb.contracts.count_documents(filter_dict)
        
        # Format response
        contract_list = []
        for contract in contracts:
            contract_list.append({
                "id": contract["id"],
                "filename": contract["filename"],
                "status": contract["status"],
                "uploaded_at": contract["uploaded_at"],
                "file_size": contract.get("file_size", 0),
                "score": contract.get("score", 0),
                "progress": contract.get("progress", 0)
            })
        
        return {
            "contracts": contract_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error listing contracts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing contracts: {str(e)}")

@app.get("/contracts/{contract_id}/download")
async def download_contract(contract_id: str):
    """Download the original contract file"""
    try:
        contract = await app.mongodb.contracts.find_one({"id": contract_id})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        file_path = contract["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Contract file not found")
        
        return FileResponse(
            path=file_path,
            filename=contract["filename"],
            media_type="application/pdf"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading contract: {str(e)}")

async def process_contract(contract_id: str):
    """Background task to process a contract"""
    try:
        # Update status to processing
        await app.mongodb.contracts.update_one(
            {"id": contract_id},
            {
                "$set": {
                    "status": ContractStatus.PROCESSING,
                    "progress": 10,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Get contract from database
        contract = await app.mongodb.contracts.find_one({"id": contract_id})
        if not contract:
            logger.error(f"Contract {contract_id} not found during processing")
            return
        
        # Parse contract
        await app.mongodb.contracts.update_one(
            {"id": contract_id},
            {"$set": {"progress": 50, "updated_at": datetime.utcnow()}}
        )
        
        parsed_data = await contract_parser.parse_contract(contract["file_path"])
        
        # Calculate score
        await app.mongodb.contracts.update_one(
            {"id": contract_id},
            {"$set": {"progress": 80, "updated_at": datetime.utcnow()}}
        )
        
        score, gaps = scoring_engine.calculate_score(parsed_data)
        
        # Update contract with results
        await app.mongodb.contracts.update_one(
            {"id": contract_id},
            {
                "$set": {
                    "status": ContractStatus.COMPLETED,
                    "progress": 100,
                    "parsed_data": parsed_data,
                    "score": score,
                    "gaps": gaps,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Successfully processed contract {contract_id}")
    
    except Exception as e:
        logger.error(f"Error processing contract {contract_id}: {str(e)}")
        # Update status to failed
        await app.mongodb.contracts.update_one(
            {"id": contract_id},
            {
                "$set": {
                    "status": ContractStatus.FAILED,
                    "error": str(e),
                    "updated_at": datetime.utcnow()
                }
            }
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Contract Intelligence Parser API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "upload": "POST /contracts/upload",
            "status": "GET /contracts/{contract_id}/status",
            "data": "GET /contracts/{contract_id}",
            "list": "GET /contracts",
            "download": "GET /contracts/{contract_id}/download"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
