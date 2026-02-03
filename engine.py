# =========================
# FINAL DEBUGGED PLAGIARISM ENGINE (COLAB + DEVICE UPLOAD)
# =========================

import os
import re
import shutil
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# CONFIG
# =========================
BUCKET_DIR = "assignment_bucket"
EXACT_JACCARD_THRESHOLD = 0.20
FULL_DOC_COSINE_THRESHOLD = 0.95
CHUNK_COSINE_THRESHOLD = 0.85
CHUNK_SIZE = 150

os.makedirs(BUCKET_DIR, exist_ok=True)

print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# =========================
# TEXT UTILS
# =========================
def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    return text.strip()



def chunk_text(text, size=150):
    words = text.split()
    if len(words) == 0:
        return []
    chunks = []
    for i in range(0, len(words), size):
        chunk = " ".join(words[i:i+size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

# =========================
# SHINGLES + SIMILARITY
# =========================
def get_shingles(text, k=3):
    words = text.split()
    if len(words) < k:
        return set()

def extract_text(file_path):
    ext = file_path.lower()

    # TXT
    if ext.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    # PDF
    elif ext.endswith(".pdf"):
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    # DOCX (CROSS-FILE SUPPORT)
    elif ext.endswith(".docx"):
        from docx import Document
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            if para.text:
                text.append(para.text)
        return "\n".join(text)

    # FALLBACK (TRY AS TEXT)
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except:
            raise ValueError(f"Unsupported file type: {file_path}")

    return set([" ".join(words[i:i+k]) for i in range(len(words)-k+1)])

def jaccard_similarity(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def full_doc_cosine_similarity(t1, t2):
    emb = model.encode([t1, t2], convert_to_numpy=True)
    v1, v2 = emb
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    return float(np.dot(v1, v2))

# =========================
# LOAD BUCKET FILES
# =========================
def load_bucket_texts():
    texts = {}
    print("\n[DEBUG] Loading bucket files...")
    files = os.listdir(BUCKET_DIR)
    print("[DEBUG] Bucket contains:", files)

    for fname in files:
        path = os.path.join(BUCKET_DIR, fname)
        if not os.path.isfile(path):
            continue
        try:
            raw = extract_text(path)
            norm = normalize_text(raw)
            print(f"[DEBUG] {fname}: {len(norm.split())} words")
            if norm.strip():
                texts[fname] = norm
            else:
                print(f"[DEBUG] {fname} has EMPTY normalized text")
        except Exception as e:
            print(f"[DEBUG] Skipped: {fname} Error:", e)

    if not texts:
        print("[DEBUG] Bucket is EMPTY after loading texts")
    return texts

# =========================
# EXACT + MIXED CHECKS
# =========================
def exact_copy_check(new_text, bucket_texts):
    new_shingles = get_shingles(new_text)
    results = []

    for fname, old_text in bucket_texts.items():
        old_shingles = get_shingles(old_text)
        jaccard = jaccard_similarity(new_shingles, old_shingles)
        cosine = full_doc_cosine_similarity(new_text, old_text)
        results.append((fname, jaccard, cosine))

    return results

def mixed_copy_check(new_chunks, bucket_texts):
    alerts = []

    for fname, old_text in bucket_texts.items():
        old_chunks = chunk_text(old_text, CHUNK_SIZE)

        if not old_chunks:
            print(f"[DEBUG] {fname} has 0 old chunks (SKIPPING)")
            continue

        emb_old = model.encode(old_chunks, convert_to_numpy=True)
        emb_new = model.encode(new_chunks, convert_to_numpy=True)

        sim_matrix = cosine_similarity(emb_new, emb_old)
        high_matches = (sim_matrix > CHUNK_COSINE_THRESHOLD).sum()

        alerts.append((fname, high_matches, sim_matrix.max()))

    return alerts

# =========================
# SAVE TO BUCKET
# =========================
def save_to_bucket(file_path):
    base = os.path.basename(file_path)
    dest = os.path.join(BUCKET_DIR, base)

    if os.path.exists(dest):
        name, ext = os.path.splitext(base)
        i = 1
        while os.path.exists(dest):
            dest = os.path.join(BUCKET_DIR, f"{name} ({i}){ext}")
            i += 1

    shutil.copy(file_path, dest)
    print(f"[DEBUG] Saved to bucket as: {os.path.basename(dest)}")

# =========================
# MAIN ENGINE
# =========================
def run_engine_colab(new_file_path):
    print("\n==============================")
    print("Plagiarism Engine Started")
    print("==============================")

    raw_new = extract_text(new_file_path)
    new_text = normalize_text(raw_new)

    print("[DEBUG] New file words:", len(new_text.split()))

    if not new_text.strip():
        print("❌ New file has EMPTY content after normalization")
        return False

    new_chunks = chunk_text(new_text, CHUNK_SIZE)
    print("[DEBUG] New file chunks:", len(new_chunks))

    bucket_texts = load_bucket_texts()

    # FIRST FILE
    if not bucket_texts:
        print("\nBucket empty -> First submission")
        save_to_bucket(new_file_path)
        print("✅ First submission accepted")
        return True

    # EXACT CHECK
    exact_results = exact_copy_check(new_text, bucket_texts)

    print("\n---- Exact Copy Report ----")
    for fname, jaccard, cosine in exact_results:
        print(f"{fname}: Jaccard = {jaccard:.2f} | Full-Doc Cosine = {cosine:.2f}")

    for fname, jaccard, cosine in exact_results:
        if jaccard >= EXACT_JACCARD_THRESHOLD or cosine >= FULL_DOC_COSINE_THRESHOLD:
            print(f"\n❌ EXACT / NEAR-EXACT COPYING DETECTED with {fname}")
            print("SUBMISSION REJECTED")
            return False

    # MIXED CHECK
    mixed_results = mixed_copy_check(new_chunks, bucket_texts)

    print("\n---- Mixed Copy Report ----")
    for fname, hits, max_sim in mixed_results:
        print(f"{fname}: High Similarity Chunks = {hits}, Max Chunk Sim = {max_sim:.2f}")

    for fname, hits, max_sim in mixed_results:
        if hits >= 2:
            print(f"\n❌ MIXED COPYING DETECTED across {fname}")
            print("SUBMISSION REJECTED")
            return False

    # ACCEPT
    save_to_bucket(new_file_path)
    print("\n✅ Submission accepted (unique enough)")
    return True
