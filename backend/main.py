# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# import os
# import hashlib
# from plagiarism_engine import check_plagiarism

# app = FastAPI(title="Plagiarism Detection Platform")

# BASE_BUCKET = "assignment_bucket"
# ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


# # ---------- Utility: File Hash ----------
# def calculate_file_hash(file_path: str) -> str:
#     sha256 = hashlib.sha256()
#     with open(file_path, "rb") as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             sha256.update(chunk)
#     return sha256.hexdigest()


# @app.get("/")
# def root():
#     return {"status": "Plagiarism API running"}


# @app.post("/submit")
# async def submit_assignment(
#     file: UploadFile = File(...),
#     assignment_id: str = Form(...)
# ):
#     # ---------- Validate file extension ----------
#     ext = os.path.splitext(file.filename)[1].lower()
#     if ext not in ALLOWED_EXTENSIONS:
#         raise HTTPException(
#             status_code=400,
#             detail="Unsupported file type. Only PDF, DOCX, TXT allowed."
#         )

#     # ---------- Assignment directory ----------
#     assignment_path = os.path.join(BASE_BUCKET, assignment_id)
#     os.makedirs(assignment_path, exist_ok=True)

#     file_path = os.path.join(assignment_path, file.filename)
#     hash_file_path = os.path.join(assignment_path, "hashes.txt")

#     # ---------- Save uploaded file ----------
#     try:
#         with open(file_path, "wb") as f:
#             f.write(await file.read())
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to save file")

#     # ---------- Duplicate content check ----------
#     current_hash = calculate_file_hash(file_path)

#     if os.path.exists(hash_file_path):
#         with open(hash_file_path, "r") as hf:
#             existing_hashes = set(hf.read().splitlines())

#         if current_hash in existing_hashes:
#             os.remove(file_path)
#             raise HTTPException(
#                 status_code=409,
#                 detail="Duplicate submission detected (same content already uploaded)."
#             )

#     # ---------- Run plagiarism engine ----------
#     try:
#         result = check_plagiarism(
#             new_file=file_path,
#             assignment_dir=assignment_path,
#             new_filename=file.filename
#         )
#     except Exception as e:
#         os.remove(file_path)
#         raise HTTPException(status_code=500, detail=str(e))

#     # ---------- Reject if plagiarized ----------
#     if not result["accepted"]:
#         os.remove(file_path)
#         return result

#     # ---------- Save hash (only if accepted) ----------
#     with open(hash_file_path, "a") as hf:
#         hf.write(current_hash + "\n")

#     from fastapi.middleware.cors import CORSMiddleware

#     app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
#     )


#     return result
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from plagiarism_engine import check_plagiarism
from routes import auth


app = FastAPI(title="Plagiarism Detection Platform")
app.include_router(auth.router)

# ---------- CORS (MUST be here) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # adjust in production
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_BUCKET = "assignment_bucket"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@app.get("/")
def root():
    return {"status": "Plagiarism API running"}


@app.post("/submit")
async def submit_assignment(
    file: UploadFile = File(...),
    assignment_id: str = Form(...)
):
    # ---------- Validate file type ----------
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return {
            "accepted": False,
            "document_similarity": 0,
            "matched_with": None,
            "sentence_matches": [],
            "total_sentence_matches": 0,
            "message": "Unsupported file type"
        }

    # ---------- Assignment folder ----------
    assignment_path = os.path.join(BASE_BUCKET, assignment_id)
    os.makedirs(assignment_path, exist_ok=True)

    file_path = os.path.join(assignment_path, file.filename)

    # ---------- Duplicate filename protection ----------
    if os.path.exists(file_path):
        return {
            "accepted": False,
            "document_similarity": 100,
            "matched_with": file.filename,
            "sentence_matches": [],
            "total_sentence_matches": 0,
            "message": "Same file already submitted"
        }

    # ---------- Save file ----------
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception:
        return {
            "accepted": False,
            "document_similarity": 0,
            "matched_with": None,
            "sentence_matches": [],
            "total_sentence_matches": 0,
            "message": "File save failed"
        }

    # ---------- Run plagiarism check ----------
    try:
        result = check_plagiarism(
            new_file=file_path,
            assignment_dir=assignment_path,
            new_filename=file.filename
        )
    except Exception as e:
        os.remove(file_path)
        return {
            "accepted": False,
            "document_similarity": 0,
            "matched_with": None,
            "sentence_matches": [],
            "total_sentence_matches": 0,
            "message": str(e)
        }

    # ---------- Reject if plagiarized ----------
    if not result["accepted"]:
        os.remove(file_path)

    return result
