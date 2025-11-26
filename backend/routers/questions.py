"""
Questions Router
API endpoints for generating and managing level-wise module questions
"""
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys

router = APIRouter(tags=["Questions"])


class QuestionGenerateRequest(BaseModel):
    module: str
    difficulty_level: Optional[str] = "all"  # beginner, intermediate, advanced, or all
    tenant_id: Optional[str] = "default"


class QuestionsResponse(BaseModel):
    success: bool
    module: str
    questions: dict
    message: Optional[str] = None


class AllModulesQuestionsRequest(BaseModel):
    tenant_id: Optional[str] = "default"


@router.post("/generate", summary="Generate level-wise questions for a module")
async def generate_questions(request: QuestionGenerateRequest):
    """
    Generate level-wise questions for a specific module based on documentation.
    
    Returns questions categorized by difficulty: beginner, intermediate, advanced
    """
    try:
        from llm.question_generator import generate_module_questions, format_questions_for_display
        from llm.rag import search
        from database.db_manager import db_manager
        
        print(f"\n📚 Generating questions for module: {request.module}", flush=True)
        sys.stdout.flush()
        
        # Search for documentation about this module
        context_query = f"What is {request.module} module? What are the features, functions, and workflows?"
        print(f"   🔍 Searching for documentation...", flush=True)
        docs = search(context_query, request.tenant_id)
        context = "\n".join(docs[:3])  # Use top 3 documents
        
        if not context or "No relevant documents found" in context:
            return {
                "success": False,
                "module": request.module,
                "questions": {},
                "message": f"No documentation found for {request.module} module. Please upload documentation first."
            }
        
        # Generate questions
        print(f"   🤔 Generating {request.difficulty_level} level questions...", flush=True)
        questions = generate_module_questions(request.module, context, request.difficulty_level)
        
        # Save to database
        try:
            db_manager.save_generated_questions(request.module, questions, request.tenant_id)
            print(f"   💾 Questions saved to database", flush=True)
        except Exception as db_error:
            print(f"   ⚠️  Could not save questions to database: {db_error}", flush=True)
        
        # Format for display
        formatted = format_questions_for_display(questions, request.module)
        
        print(f"✅ Generated {sum(len(q) for q in questions.values())} questions", flush=True)
        sys.stdout.flush()
        
        return {
            "success": True,
            "module": request.module,
            "questions": questions,
            "formatted_questions": formatted,
            "message": f"Successfully generated questions for {request.module}"
        }
        
    except Exception as e:
        print(f"❌ Error generating questions: {e}", flush=True)
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-all", summary="Generate questions for all modules")
async def generate_all_questions(request: AllModulesQuestionsRequest):
    """
    Generate level-wise questions for all available modules.
    
    This may take some time depending on the number of modules.
    """
    try:
        from llm.question_generator import generate_questions_from_all_modules
        
        print(f"\n📚 Generating questions for ALL modules", flush=True)
        sys.stdout.flush()
        
        all_questions = generate_questions_from_all_modules(request.tenant_id)
        
        total_questions = sum(
            sum(len(questions[level]) for level in questions)
            for questions in all_questions.values()
        )
        
        print(f"✅ Generated {total_questions} questions across {len(all_questions)} modules", flush=True)
        sys.stdout.flush()
        
        return {
            "success": True,
            "modules_count": len(all_questions),
            "total_questions": total_questions,
            "questions": all_questions,
            "message": f"Successfully generated questions for {len(all_questions)} modules"
        }
        
    except Exception as e:
        print(f"❌ Error generating questions for all modules: {e}", flush=True)
        sys.stdout.flush()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{module}", summary="Get saved questions for a module")
async def get_questions(module: str, difficulty_level: Optional[str] = None, 
                       tenant_id: str = "default"):
    """
    Retrieve previously generated questions for a module from the database.
    """
    try:
        from database.db_manager import db_manager
        
        questions_data = db_manager.get_generated_questions(
            module_name=module,
            difficulty_level=difficulty_level,
            tenant_id=tenant_id,
            active_only=True
        )
        
        # Group by difficulty level
        questions = {"beginner": [], "intermediate": [], "advanced": []}
        
        for row in questions_data:
            level = row.get('difficulty_level')
            question = row.get('question')
            if level in questions:
                questions[level].append({
                    "id": row.get('id'),
                    "question": question,
                    "times_asked": row.get('times_asked', 0)
                })
        
        return {
            "success": True,
            "module": module,
            "questions": questions,
            "total": len(questions_data)
        }
        
    except Exception as e:
        print(f"❌ Error retrieving questions: {e}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/random/{module}", summary="Get random questions for a module")
async def get_random_questions(module: str, count: int = 3, 
                              difficulty_level: Optional[str] = None,
                              tenant_id: str = "default"):
    """
    Get random questions from a module to help users explore the documentation.
    """
    try:
        from database.db_manager import db_manager
        import random
        
        questions_data = db_manager.get_generated_questions(
            module_name=module,
            difficulty_level=difficulty_level,
            tenant_id=tenant_id,
            active_only=True
        )
        
        if not questions_data:
            return {
                "success": False,
                "module": module,
                "questions": [],
                "message": f"No questions available for {module}. Generate them first."
            }
        
        # Get random questions
        random_questions = random.sample(questions_data, min(count, len(questions_data)))
        
        formatted_questions = [
            {
                "id": q.get('id'),
                "question": q.get('question'),
                "difficulty": q.get('difficulty_level')
            }
            for q in random_questions
        ]
        
        return {
            "success": True,
            "module": module,
            "questions": formatted_questions,
            "count": len(formatted_questions)
        }
        
    except Exception as e:
        print(f"❌ Error getting random questions: {e}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-clarity", summary="Check query clarity")
async def check_query_clarity(query: str = Body(...), tenant_id: str = Body("default")):
    """
    Check if a user's query is clear or needs clarification.
    Returns clarity analysis and suggested clarifying questions if needed.
    """
    try:
        from llm.clarity_detector import analyze_query_clarity, format_clarification_response
        
        print(f"\n🔍 Analyzing query clarity: '{query}'", flush=True)
        
        analysis = analyze_query_clarity(query)
        
        response_data = {
            "success": True,
            "query": query,
            "is_clear": analysis["is_clear"],
            "clarity_score": analysis["clarity_score"],
            "issues": analysis["issues"],
            "clarifying_questions": analysis["suggestions"]
        }
        
        if not analysis["is_clear"]:
            response_data["formatted_clarification"] = format_clarification_response(
                query, analysis["suggestions"]
            )
        
        print(f"✅ Clarity analysis complete: {analysis['clarity_score']:.2f}", flush=True)
        
        return response_data
        
    except Exception as e:
        print(f"❌ Error checking query clarity: {e}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", summary="Get question generation statistics")
async def get_question_stats(tenant_id: str = "default"):
    """
    Get statistics about generated questions and their usage.
    """
    try:
        from database.db_manager import db_manager
        
        # Get all questions for this tenant
        all_questions = db_manager.get_generated_questions(tenant_id=tenant_id, active_only=True)
        
        # Calculate statistics
        stats = {
            "total_questions": len(all_questions),
            "by_module": {},
            "by_difficulty": {"beginner": 0, "intermediate": 0, "advanced": 0},
            "total_times_asked": 0,
            "most_popular": []
        }
        
        for q in all_questions:
            module = q.get('module_name')
            difficulty = q.get('difficulty_level')
            times_asked = q.get('times_asked', 0)
            
            # Count by module
            if module not in stats["by_module"]:
                stats["by_module"][module] = 0
            stats["by_module"][module] += 1
            
            # Count by difficulty
            if difficulty in stats["by_difficulty"]:
                stats["by_difficulty"][difficulty] += 1
            
            # Track times asked
            stats["total_times_asked"] += times_asked
            
            # Track popular questions
            if times_asked > 0:
                stats["most_popular"].append({
                    "question": q.get('question'),
                    "module": module,
                    "times_asked": times_asked
                })
        
        # Sort popular questions
        stats["most_popular"].sort(key=lambda x: x["times_asked"], reverse=True)
        stats["most_popular"] = stats["most_popular"][:10]  # Top 10
        
        # Get clarification stats
        clarification_stats = db_manager.get_clarification_stats(tenant_id)
        stats["clarifications"] = clarification_stats
        
        return {
            "success": True,
            "tenant_id": tenant_id,
            "stats": stats
        }
        
    except Exception as e:
        print(f"❌ Error getting question stats: {e}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))

