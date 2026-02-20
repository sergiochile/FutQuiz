"""
Sistema de Autenticación - El Crack Quiz v2.0
Preparado para Google OAuth en el futuro
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import hashlib
import secrets

# ═══════════════════════════════════════════════════════════════════════════════
# MODELOS DE AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    google_token: str
    id_token: str

class AuthResponse(BaseModel):
    success: bool
    user_id: int
    username: str
    email: str
    auth_token: str
    created_at: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# ═══════════════════════════════════════════════════════════════════════════════
# GESTOR DE AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class AuthManager:
    """Gestiona autenticación local y futura con Google OAuth"""
    
    def __init__(self):
        self.active_sessions = {}
        self.token_timeout = 86400  # 24 horas
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash seguro de contraseña con salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        return f"{salt}${password_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verifica contraseña contra su hash"""
        try:
            salt, stored_hash = password_hash.split('$')
            password_check = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            )
            return password_check.hex() == stored_hash
        except:
            return False
    
    @staticmethod
    def generate_token() -> str:
        """Genera token único de sesión"""
        return secrets.token_urlsafe(32)
    
    def validate_username(self, username: str) -> tuple[bool, str]:
        """Valida nombre de usuario"""
        if not username or len(username) < 3:
            return False, "Username debe tener al menos 3 caracteres"
        if len(username) > 20:
            return False, "Username máximo 20 caracteres"
        if not all(c.isalnum() or c in '-_' for c in username):
            return False, "Solo alfanuméricos, guiones y guiones bajos"
        return True, "✅ Username válido"
    
    def validate_email(self, email: str) -> tuple[bool, str]:
        """Valida formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Email inválido"
        return True, "✅ Email válido"
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Valida fortaleza de contraseña"""
        if len(password) < 8:
            return False, "Contraseña mínimo 8 caracteres"
        if not any(c.isupper() for c in password):
            return False, "Debe tener al menos una mayúscula"
        if not any(c.isdigit() for c in password):
            return False, "Debe tener al menos un número"
        return True, "✅ Contraseña segura"
    
    def create_session(self, user_id: int, username: str, email: str) -> dict:
        """Crea nueva sesión de autenticación"""
        token = self.generate_token()
        session = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "token": token,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=self.token_timeout),
            "ip": None,
            "user_agent": None
        }
        self.active_sessions[token] = session
        return session
    
    def verify_token(self, token: str) -> tuple[bool, dict]:
        """Verifica que un token sea válido"""
        if token not in self.active_sessions:
            return False, {}
        
        session = self.active_sessions[token]
        
        if datetime.now() > session["expires_at"]:
            del self.active_sessions[token]
            return False, {}
        
        return True, session
    
    def revoke_token(self, token: str) -> bool:
        """Revoca un token (logout)"""
        if token in self.active_sessions:
            del self.active_sessions[token]
            return True
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRACIÓN CON GOOGLE OAUTH (PLANTILLA LISTA)
# ═══════════════════════════════════════════════════════════════════════════════

class GoogleOAuthManager:
    """Preparado para integración con Google OAuth 2.0"""
    
    def __init__(self):
        # Estos valores se configurarían desde variables de entorno
        self.client_id = None  # "xxx.apps.googleusercontent.com"
        self.client_secret = None  # "secret_xxx"
        self.redirect_uri = None  # "http://127.0.0.1:3000/auth/google/callback"
    
    def verify_google_token(self, id_token: str) -> dict:
        """
        Verifica token de Google y retorna datos del usuario
        
        En producción, usar google-auth-oauthlib
        
        from google.auth.transport import requests
        from google.oauth2 import id_token
        
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token,
                requests.Request(),
                self.client_id
            )
            return {
                "email": idinfo.get('email'),
                "name": idinfo.get('name'),
                "picture": idinfo.get('picture'),
                "sub": idinfo.get('sub')  # Google unique ID
            }
        except ValueError:
            return None
        """
        # PLACEHOLDER: Implementar verificación real en producción
        return None
    
    def get_auth_url(self) -> str:
        """Genera URL de autenticación de Google"""
        # PLACEHOLDER: Implementar en producción
        pass
    
    def exchange_code_for_token(self, code: str) -> dict:
        """Intercambia código por token"""
        # PLACEHOLDER: Implementar en producción
        pass

# ═══════════════════════════════════════════════════════════════════════════════
# INSTANCIAS GLOBALES
# ═══════════════════════════════════════════════════════════════════════════════

auth_manager = AuthManager()
google_oauth = GoogleOAuthManager()
