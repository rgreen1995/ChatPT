"""
Supabase database handler for ChatPT.
Provides cloud-based PostgreSQL database through Supabase.
Falls back to SQLite if Supabase is not configured.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import hashlib
import secrets
import streamlit as st
from supabase import create_client, Client

def get_secret(key: str, default: str = None) -> str:
    """Get secret from Streamlit secrets or environment variables."""
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (FileNotFoundError, KeyError):
        pass
    return os.getenv(key, default)


class SupabaseDB:
    """Supabase database handler."""

    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = get_secret("SUPABASE_URL")
        supabase_key = get_secret("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be configured")

        self.client: Client = create_client(supabase_url, supabase_key)

    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple[str, str]:
        """Hash a password with a salt using SHA-256."""
        if salt is None:
            salt = secrets.token_hex(16)

        password_salt = (password + salt).encode('utf-8')
        hashed = hashlib.sha256(password_salt).hexdigest()
        return hashed, salt

    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """Verify a password against a hash."""
        test_hash, _ = SupabaseDB.hash_password(password, salt)
        return test_hash == hashed_password

    def init_db(self):
        """Initialize database tables. Run this once to set up your Supabase database."""
        # Note: In Supabase, you'll create these tables via the Supabase dashboard or SQL editor
        # This method provides the SQL schema for reference
        schema = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            password_salt TEXT,
            auth_provider TEXT DEFAULT 'email',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Consultations table
        CREATE TABLE IF NOT EXISTS consultations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed BOOLEAN DEFAULT FALSE,
            workout_plan JSONB,
            consultation_type TEXT DEFAULT 'training'
        );

        -- Conversation history table
        CREATE TABLE IF NOT EXISTS conversation_history (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            consultation_id UUID NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Exercise progress table
        CREATE TABLE IF NOT EXISTS exercise_progress (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            consultation_id UUID NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
            exercise_name TEXT NOT NULL,
            day TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            notes TEXT,
            completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Exercise library table
        CREATE TABLE IF NOT EXISTS exercise_library (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            primary_muscles TEXT NOT NULL,
            secondary_muscles TEXT,
            equipment TEXT,
            difficulty TEXT,
            youtube_url TEXT,
            instructions TEXT,
            form_cues TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- User coaching profile table - shared across training and nutrition
        CREATE TABLE IF NOT EXISTS user_coaching_profile (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            profile_json JSONB NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- User coaching memory table - shared coaching memory summary
        CREATE TABLE IF NOT EXISTS user_coaching_memory (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            memory_json JSONB NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Nutrition plans table - separate storage for nutrition plans
        CREATE TABLE IF NOT EXISTS nutrition_plans (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            consultation_id UUID NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
            plan_json JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_consultations_user_id ON consultations(user_id);
        CREATE INDEX IF NOT EXISTS idx_consultations_type ON consultations(consultation_type);
        CREATE INDEX IF NOT EXISTS idx_consultations_user_created ON consultations(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_conversation_consultation_id ON conversation_history(consultation_id);
        CREATE INDEX IF NOT EXISTS idx_exercise_progress_user_id ON exercise_progress(user_id);
        CREATE INDEX IF NOT EXISTS idx_exercise_progress_exercise_name ON exercise_progress(exercise_name);
        CREATE INDEX IF NOT EXISTS idx_exercise_library_name ON exercise_library(name);
        CREATE INDEX IF NOT EXISTS idx_exercise_library_category ON exercise_library(category);
        CREATE INDEX IF NOT EXISTS idx_nutrition_plans_user ON nutrition_plans(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_nutrition_plans_consultation ON nutrition_plans(consultation_id);
        """
        return schema

    def create_user(self, name: str, email: str, password: str = None, auth_provider: str = 'email') -> str:
        """Create a new user and return their ID (UUID as string)."""
        data = {
            "name": name,
            "email": email,
            "auth_provider": auth_provider
        }

        if password:
            hashed_password, salt = self.hash_password(password)
            data["password_hash"] = hashed_password
            data["password_salt"] = salt

        result = self.client.table("users").insert(data).execute()
        return result.data[0]["id"]

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user by email and password."""
        result = self.client.table("users").select("*").eq("email", email).execute()

        if not result.data:
            return None

        user = result.data[0]

        if not user.get("password_hash") or not user.get("password_salt"):
            return None

        if self.verify_password(password, user["password_hash"], user["password_salt"]):
            return {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }

        return None

    def user_exists(self, email: str) -> bool:
        """Check if a user with this email already exists."""
        result = self.client.table("users").select("id").eq("email", email).execute()
        return len(result.data) > 0

    def get_or_create_user_by_email(self, email: str, name: str, auth_provider: str = 'google') -> str:
        """Get existing user by email or create a new one (for OAuth)."""
        result = self.client.table("users").select("id").eq("email", email).execute()

        if result.data:
            return result.data[0]["id"]
        else:
            return self.create_user(name, email, auth_provider=auth_provider)

    def create_consultation(self, user_id: str, consultation_type: str = 'training') -> str:
        """Create a new consultation for a user."""
        data = {
            "user_id": user_id,
            "consultation_type": consultation_type
        }
        result = self.client.table("consultations").insert(data).execute()
        return result.data[0]["id"]

    def save_message(self, consultation_id: str, role: str, content: str):
        """Save a message to conversation history."""
        data = {
            "consultation_id": consultation_id,
            "role": role,
            "content": content
        }
        self.client.table("conversation_history").insert(data).execute()

    def get_conversation_history(self, consultation_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a consultation."""
        result = self.client.table("conversation_history")\
            .select("role, content")\
            .eq("consultation_id", consultation_id)\
            .order("timestamp")\
            .execute()

        return [{"role": row["role"], "content": row["content"]} for row in result.data]

    def save_workout_plan(self, consultation_id: str, workout_plan: Dict[str, Any]):
        """Save the workout plan JSON to the consultation."""
        self.client.table("consultations")\
            .update({"workout_plan": workout_plan, "completed": True})\
            .eq("id", consultation_id)\
            .execute()

    def get_workout_plan(self, consultation_id: str) -> Optional[Dict[str, Any]]:
        """Get the workout plan for a consultation."""
        result = self.client.table("consultations")\
            .select("workout_plan")\
            .eq("id", consultation_id)\
            .execute()

        if result.data and result.data[0].get("workout_plan"):
            return result.data[0]["workout_plan"]
        return None

    def get_user_consultations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all consultations for a user."""
        result = self.client.table("consultations")\
            .select("id, created_at, completed")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()

        return [
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "completed": row["completed"]
            }
            for row in result.data
        ]

    def save_exercise_progress(
        self,
        user_id: str,
        consultation_id: str,
        exercise_name: str,
        day: str,
        sets: int,
        reps: int,
        weight: float,
        notes: str = ""
    ):
        """Save exercise progress for a user."""
        data = {
            "user_id": user_id,
            "consultation_id": consultation_id,
            "exercise_name": exercise_name,
            "day": day,
            "sets": sets,
            "reps": reps,
            "weight": weight,
            "notes": notes
        }
        self.client.table("exercise_progress").insert(data).execute()

    def get_exercise_progress(self, user_id: str, exercise_name: str) -> List[Dict[str, Any]]:
        """Get all progress records for a specific exercise."""
        result = self.client.table("exercise_progress")\
            .select("sets, reps, weight, notes, completed_at, day")\
            .eq("user_id", user_id)\
            .eq("exercise_name", exercise_name)\
            .order("completed_at", desc=True)\
            .execute()

        return [
            {
                "sets": row["sets"],
                "reps": row["reps"],
                "weight": row["weight"],
                "notes": row["notes"],
                "completed_at": row["completed_at"],
                "day": row["day"]
            }
            for row in result.data
        ]

    # ============================================================================
    # Nutrition Consultation Methods
    # ============================================================================

    def get_coaching_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's coaching profile (shared across training and nutrition)."""
        result = self.client.table("user_coaching_profile")\
            .select("profile_json")\
            .eq("user_id", user_id)\
            .execute()

        if result.data and result.data[0].get("profile_json"):
            return result.data[0]["profile_json"]
        return None

    def save_coaching_profile(self, user_id: str, profile: Dict[str, Any]):
        """Save/update user's coaching profile."""
        # Try to update existing profile first
        result = self.client.table("user_coaching_profile")\
            .select("id")\
            .eq("user_id", user_id)\
            .execute()

        if result.data:
            # Update existing
            self.client.table("user_coaching_profile")\
                .update({"profile_json": profile, "updated_at": "NOW()"})\
                .eq("user_id", user_id)\
                .execute()
        else:
            # Insert new
            self.client.table("user_coaching_profile")\
                .insert({"user_id": user_id, "profile_json": profile})\
                .execute()

    def get_coaching_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's coaching memory summary."""
        result = self.client.table("user_coaching_memory")\
            .select("memory_json")\
            .eq("user_id", user_id)\
            .execute()

        if result.data and result.data[0].get("memory_json"):
            return result.data[0]["memory_json"]
        return None

    def save_coaching_memory(self, user_id: str, memory: Dict[str, Any]):
        """Save/update user's coaching memory summary."""
        # Try to update existing memory first
        result = self.client.table("user_coaching_memory")\
            .select("id")\
            .eq("user_id", user_id)\
            .execute()

        if result.data:
            # Update existing
            self.client.table("user_coaching_memory")\
                .update({"memory_json": memory, "updated_at": "NOW()"})\
                .eq("user_id", user_id)\
                .execute()
        else:
            # Insert new
            self.client.table("user_coaching_memory")\
                .insert({"user_id": user_id, "memory_json": memory})\
                .execute()

    def save_nutrition_plan(self, user_id: str, consultation_id: str, plan: Dict[str, Any]):
        """Save nutrition plan for a consultation."""
        # Check if a plan already exists for this consultation
        result = self.client.table("nutrition_plans")\
            .select("id")\
            .eq("consultation_id", consultation_id)\
            .execute()

        if result.data:
            # Update existing plan
            self.client.table("nutrition_plans")\
                .update({"plan_json": plan, "updated_at": "NOW()"})\
                .eq("consultation_id", consultation_id)\
                .execute()
        else:
            # Deactivate all previous plans for this user
            self.client.table("nutrition_plans")\
                .update({"is_active": False})\
                .eq("user_id", user_id)\
                .execute()

            # Insert new plan
            self.client.table("nutrition_plans")\
                .insert({
                    "user_id": user_id,
                    "consultation_id": consultation_id,
                    "plan_json": plan,
                    "is_active": True
                })\
                .execute()

    def get_nutrition_plan(self, consultation_id: str) -> Optional[Dict[str, Any]]:
        """Get nutrition plan by consultation ID."""
        result = self.client.table("nutrition_plans")\
            .select("plan_json")\
            .eq("consultation_id", consultation_id)\
            .execute()

        if result.data and result.data[0].get("plan_json"):
            return result.data[0]["plan_json"]
        return None

    def get_latest_nutrition_plan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's latest active nutrition plan."""
        result = self.client.table("nutrition_plans")\
            .select("plan_json")\
            .eq("user_id", user_id)\
            .eq("is_active", True)\
            .order("updated_at", desc=True)\
            .limit(1)\
            .execute()

        if result.data and result.data[0].get("plan_json"):
            return result.data[0]["plan_json"]
        return None

    def get_consultation_type(self, consultation_id: str) -> str:
        """Get the type of a consultation (training or nutrition)."""
        result = self.client.table("consultations")\
            .select("consultation_type")\
            .eq("id", consultation_id)\
            .execute()

        if result.data and result.data[0].get("consultation_type"):
            return result.data[0]["consultation_type"]
        return 'training'  # Default to training if not found


def is_supabase_configured() -> bool:
    """Check if Supabase is configured."""
    supabase_url = get_secret("SUPABASE_URL")
    supabase_key = get_secret("SUPABASE_KEY")
    return bool(supabase_url and supabase_key)
