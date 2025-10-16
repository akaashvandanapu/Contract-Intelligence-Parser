from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db.database


async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Create indexes on contracts collection
        contracts_collection = db.database.contracts
        
        # Index on contract ID for fast lookups
        await contracts_collection.create_index("id", unique=True)
        
        # Index on status for filtering
        await contracts_collection.create_index("status")
        
        # Index on uploaded_at for sorting
        await contracts_collection.create_index("uploaded_at")
        
        # Index on score for sorting
        await contracts_collection.create_index("score")
        
        # Compound index for common queries
        await contracts_collection.create_index([("status", 1), ("uploaded_at", -1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating database indexes: {str(e)}")
        raise
