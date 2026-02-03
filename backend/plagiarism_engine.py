# import os
# from text_extractors import extract_text
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from nltk.tokenize import sent_tokenize

# DOC_SIM_THRESHOLD = 0.30
# SENTENCE_SIM_THRESHOLD = 0.80


# def sentence_level_check(new_text, existing_texts, filenames):
#     matches = []

#     new_sentences = sent_tokenize(new_text)

#     for idx, old_text in enumerate(existing_texts):
#         old_sentences = sent_tokenize(old_text)

#         if not old_sentences:
#             continue

#         corpus = new_sentences + old_sentences
#         tfidf = TfidfVectorizer(stop_words="english").fit_transform(corpus)

#         sim_matrix = cosine_similarity(
#             tfidf[:len(new_sentences)],
#             tfidf[len(new_sentences):]
#         )

#         for i, row in enumerate(sim_matrix):
#             max_sim = row.max()
#             if max_sim >= SENTENCE_SIM_THRESHOLD:
#                 j = row.argmax()
#                 matches.append({
#                     "source_file": filenames[idx],
#                     "new_sentence": new_sentences[i],
#                     "matched_sentence": old_sentences[j],
#                     "similarity": round(float(max_sim * 100), 2)
#                 })

#     return matches


# def check_plagiarism(new_file, assignment_dir,new_file_name):
#     new_text = extract_text(new_file)

#     existing_texts = []
#     filenames = []

#     for file in os.listdir(assignment_dir):
#         if file == new_filename:
#             continue


#         try:
#             text = extract_text(path)
#             if text.strip():
#                 existing_texts.append(text)
#                 filenames.append(file)
#         except:
#             continue

#     # First submission
#     if not existing_texts:
#         return {
#             "accepted": True,
#             "document_similarity": 0,
#             "matched_with": None,
#             "sentence_matches": [],
#             "message": "First submission for this assignment"
#         }

#     # -------- Document-level similarity --------
#     vectorizer = TfidfVectorizer(stop_words="english")
#     vectors = vectorizer.fit_transform([new_text] + existing_texts)

#     similarity_scores = cosine_similarity(vectors[0:1], vectors[1:])[0]
#     max_score = similarity_scores.max()
#     matched_file = filenames[similarity_scores.argmax()]

#     # -------- Sentence-level explainability --------
#     sentence_matches = sentence_level_check(
#         new_text, existing_texts, filenames
#     )

#     plagiarized = (
#         max_score >= DOC_SIM_THRESHOLD or
#         len(sentence_matches) >= 3
#     )

#     return {
#         "accepted": not plagiarized,
#         "document_similarity": round(float(max_score * 100), 2),
#         "matched_with": matched_file,
#         "sentence_matches": sentence_matches,
#         "total_sentence_matches": len(sentence_matches),
#         "message": "Plagiarism detected" if plagiarized else "Submission accepted"
#     }
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from text_extractors import extract_text
import nltk
from nltk.tokenize import sent_tokenize

# Download once at startup
nltk.download("punkt", quiet=True)

DOC_SIM_THRESHOLD = 0.3
SENTENCE_SIM_THRESHOLD = 0.8


# def check_plagiarism(new_file, assignment_dir, new_filename):
#     new_text = extract_text(new_file)

#     existing_texts = []
#     filenames = []

#     for file in os.listdir(assignment_dir):
#         if file == new_filename:
#             continue

#         path = os.path.join(assignment_dir, file)

#         try:
#             text = extract_text(path)
#             existing_texts.append(text)
#             filenames.append(file)
#         except Exception:
#             continue

#     if not existing_texts:
#         return {
#             "accepted": True,
#             "document_similarity": 0,
#             "matched_with": None,
#             "sentence_matches": [],
#             "total_sentence_matches": 0,
#             "message": "First submission for this assignment"
#         }

#     # ---------- Document-level similarity ----------
#     vectorizer = TfidfVectorizer(stop_words="english")
#     vectors = vectorizer.fit_transform([new_text] + existing_texts)

#     similarity_scores = cosine_similarity(vectors[0:1], vectors[1:])[0]
#     max_score = similarity_scores.max()
#     matched_idx = similarity_scores.argmax()
#     matched_file = filenames[matched_idx]

#     # ---------- Sentence-level similarity ----------
#     sentence_matches = []

#     if max_score >= DOC_SIM_THRESHOLD:
#         new_sentences = sent_tokenize(new_text)
#         matched_text = existing_texts[matched_idx]
#         matched_sentences = sent_tokenize(matched_text)

#         for s1 in new_sentences:
#             for s2 in matched_sentences:
#                 sent_vectorizer = TfidfVectorizer(stop_words="english")
#                 sent_vec = sent_vectorizer.fit_transform([s1, s2])
#                 score = cosine_similarity(sent_vec[0:1], sent_vec[1:])[0][0]

#                 if score >= SENTENCE_SIM_THRESHOLD:
#                     sentence_matches.append({
#                         "source_sentence": s1,
#                         "matched_sentence": s2,
#                         "similarity": round(score * 100, 2)
#                     })

#     if max_score >= DOC_SIM_THRESHOLD:
#         return {
#             "accepted": False,
#             "document_similarity": round(max_score * 100, 2),
#             "matched_with": matched_file,
#             "sentence_matches": sentence_matches,
#             "total_sentence_matches": len(sentence_matches),
#             "message": "Plagiarism detected"
#         }

#     return {
#         "accepted": True,
#         "document_similarity": round(max_score * 100, 2),
#         "matched_with": matched_file,
#         "sentence_matches": sentence_matches,
#         "total_sentence_matches": len(sentence_matches),
#         "message": "Submission accepted"
#     }
def check_plagiarism(new_file, assignment_dir, new_filename):
    new_text = extract_text(new_file)

    existing_texts = []
    filenames = []

    for file in os.listdir(assignment_dir):
        if file == new_filename:
            continue

        path = os.path.join(assignment_dir, file)
        try:
            existing_texts.append(extract_text(path))
            filenames.append(file)
        except Exception:
            continue

    # ---------- First submission ----------
    if not existing_texts:
        return {
            "accepted": True,
            "document_similarity": 0,
            "matched_with": None,
            "sentence_matches": [],
            "total_sentence_matches": 0,
            "message": "First submission for this assignment"
        }

    # ---------- Document-level similarity ----------
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([new_text] + existing_texts)

    similarity_scores = cosine_similarity(vectors[0:1], vectors[1:])[0]
    max_score = float(similarity_scores.max())

    # ---------- NO similarity at all ----------
    if max_score == 0:
        return {
            "accepted": True,
            "document_similarity": 0,
            "matched_with": None,
            "sentence_matches": [],
            "total_sentence_matches": 0,
            "message": "Submission accepted"
        }

    matched_idx = similarity_scores.argmax()
    matched_file = filenames[matched_idx]

    # ---------- Sentence-level similarity ----------
    sentence_matches = []

    if max_score >= DOC_SIM_THRESHOLD:
        new_sentences = sent_tokenize(new_text)
        matched_text = existing_texts[matched_idx]
        matched_sentences = sent_tokenize(matched_text)

        for s1 in new_sentences:
            for s2 in matched_sentences:
                sent_vectorizer = TfidfVectorizer(stop_words="english")
                sent_vec = sent_vectorizer.fit_transform([s1, s2])
                score = cosine_similarity(sent_vec[0:1], sent_vec[1:])[0][0]

                if score >= SENTENCE_SIM_THRESHOLD:
                    sentence_matches.append({
                        "source_sentence": s1,
                        "matched_sentence": s2,
                        "similarity": round(score * 100, 2)
                    })

    # ---------- Plagiarism detected ----------
    if max_score >= DOC_SIM_THRESHOLD:
        return {
            "accepted": False,
            "document_similarity": round(max_score * 100, 2),
            "matched_with": matched_file,
            "sentence_matches": sentence_matches,
            "total_sentence_matches": len(sentence_matches),
            "message": "Plagiarism detected"
        }

    # ---------- Accepted but similarity exists ----------
    return {
        "accepted": True,
        "document_similarity": round(max_score * 100, 2),
        "matched_with": None,  # ✅ FIX
        "sentence_matches": [],
        "total_sentence_matches": 0,
        "message": "Submission accepted"
    }
