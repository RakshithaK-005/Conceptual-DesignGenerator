"""
Contact form endpoint
Handles contact form submissions from the frontend
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from app.utils.logger import logger
import json
from datetime import datetime

router = APIRouter(prefix="/contact", tags=["contact"])


class ContactRequest(BaseModel):
    """Contact form request schema"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(default="", max_length=20)
    subject: str = Field(..., min_length=3, max_length=255)
    message: str = Field(..., min_length=10, max_length=5000)


class ContactResponse(BaseModel):
    """Contact form response schema"""
    success: bool
    message: str
    submission_id: str = None


@router.post("/", response_model=ContactResponse)
async def submit_contact(contact: ContactRequest):
    """
    Submit contact form
    
    Receives contact form submissions from the website and logs them.
    In a production environment, you would:
    - Store in database
    - Send email notification
    - Integrate with CRM
    """
    try:
        # Generate submission ID
        submission_id = f"contact_{datetime.utcnow().timestamp()}"
        
        # Log the contact submission
        contact_data = contact.dict()
        logger.info(f"📧 New contact submission (ID: {submission_id})")
        logger.info(f"   From: {contact.name} <{contact.email}>")
        logger.info(f"   Phone: {contact.phone if contact.phone else 'Not provided'}")
        logger.info(f"   Subject: {contact.subject}")
        logger.info(f"   Message: {contact.message[:100]}...")
        
        # In production, you would:
        # 1. Save to database
        # 2. Send email to admin
        # 3. Send confirmation email to user
        # 4. Integrate with CRM/ticketing system
        
        # For now, just log and return success
        return ContactResponse(
            success=True,
            message="Thank you for contacting us! We will get back to you soon.",
            submission_id=submission_id
        )
        
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process contact form. Please try again later."
        )


@router.get("/")
async def contact_info():
    """Get contact information"""
    return {
        "email": "info@archai.com",
        "support_email": "support@archai.com",
        "phone": "+1 (555) 123-4567",
        "office": "123 Architecture Drive, Design City, DC 12345",
        "hours": {
            "monday_friday": "9:00 AM - 6:00 PM",
            "saturday": "10:00 AM - 4:00 PM",
            "sunday": "Closed"
        }
    }
