from fastapi import APIRouter

from app.api.v1.endpoints import auth, blooms, curriculum, generate_paper, generated_papers, health, questions, subjects, units

router = APIRouter()
router.include_router(health.router, prefix="", tags=["Health"])
router.include_router(auth.router, prefix="", tags=["Auth"])
router.include_router(curriculum.router, prefix="", tags=["Curriculum"])
router.include_router(subjects.router, prefix="", tags=["Subjects"])
router.include_router(units.router, prefix="", tags=["Units"])
router.include_router(questions.router, prefix="", tags=["Questions"])
router.include_router(generate_paper.router, prefix="", tags=["Question Paper"])
router.include_router(generated_papers.router, prefix="", tags=["Generated Papers"])
router.include_router(blooms.router, prefix="", tags=["Bloom Levels"])


