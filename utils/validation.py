from fastapi import Form, HTTPException
from config import settings
import secrets
import re
from .logger import logger
import bcrypt

class SecurityConfig:
    MAX_MESSAGE_LENGTH = 5000
    # for blocking dangerous patterns
    SUSPICIOUS_PATTERNS = [
        r'javascript:',         # JavaScript protocol
        r'data:',               # Data URLs
        r'<script.*?>',         # Script tags
        r'<.*?on\w+\s*=',       # Event handlers
    ]

class InputValidator:

    @staticmethod
    def validate_username(username: str) -> bool:
        if not secrets.compare_digest(username, settings.GLOBAL_USERNAME):
            return False
        return True

    @staticmethod
    def validate_password(password: str) -> bool:
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                settings.GLOBAL_PASSWORD.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def validate_checkbox(value: str) -> bool:
        # Handle boolean first
        if isinstance(value, bool):
            return value
        # Then string, just in case
        if isinstance(value, str):
            value = value.lower()
            if value in ('true', '1', 'yes', 'on'):
                return True
            if value in ('false', '0', 'no', 'off', None, ''):
                error_text = "Checkbox was not checked"
                logger.error(error_text, event_type="aita")
                return False
        error_text = "Checkbox failed validation"
        logger.error(error_text, event_type="aita")
        return False
    
    async def validate_login_data(username: str = Form(...), password: str = Form(...), agreement_part_1: bool = Form(...), agreement_part_2: bool = Form(...)):
    
        username = InputValidator.validate_username(username)
        password = InputValidator.validate_password(password)
        if not (username and password):
            return {"check_code": False, "message": "Either username or password was invalid"}
        agreement_part_1 = InputValidator.validate_checkbox(agreement_part_1)
        agreement_part_2 = InputValidator.validate_checkbox(agreement_part_2)
        if not (agreement_part_1 and agreement_part_2):
            return {"check_code": False, "message": "Agreement to participate was not indicated"}
        return {"check_code": True, 
                "login_data" : {
                    "username": username,
                    "password": password,
                    "agreement_part_1": agreement_part_1,
                    "agreement_part_2": agreement_part_2
                }
            }

    async def validate_chat_message(message: str) -> str:
        # Check message is not empty
        if not message or not message.strip():
            error_text = "Message is empty"
            logger.error(error_text, event_type="aita")
            raise HTTPException(status_code=422, detail=error_text) 

        # Check message length
        if len(message) > SecurityConfig.MAX_MESSAGE_LENGTH:
            error_text = f"Message exceeds maximum length of {SecurityConfig.MAX_MESSAGE_LENGTH} characters"
            logger.error(error_text, event_type="aita")
            raise HTTPException(status_code=422, detail=error_text) 

        # Check message for suspicious patterns
        for pattern in SecurityConfig.SUSPICIOUS_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                error_text = "Message contins suspicious patterns"
                logger.error(error_text, event_type="aita")
                raise HTTPException(status_code=403, detail=error_text)

        return True


        