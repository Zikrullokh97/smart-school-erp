from fastapi import APIRouter

from smart_school.api.routers import auth, schools, users
from smart_school.api.routers.ai_reviews import router as ai_reviews_router
from smart_school.api.routers.attendance import router as attendance_router
from smart_school.api.routers.gamification import router as gamification_router
from smart_school.api.routers.parents import router as parents_router
from smart_school.api.routers.students import router as students_router
from smart_school.api.routers.sync import router as sync_router
from smart_school.api.routers.teachers import router as teachers_router

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(schools.router)
api_router.include_router(attendance_router)
api_router.include_router(students_router)
api_router.include_router(teachers_router)
api_router.include_router(parents_router)
api_router.include_router(gamification_router)
api_router.include_router(ai_reviews_router)
api_router.include_router(sync_router)
