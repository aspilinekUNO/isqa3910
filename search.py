import csv
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from mps_data import load_resources


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

DATASET_FOLDER = Path("data/MPS_Parsed_Content_2026-10-01")
MANIFEST_FILE = DATASET_FOLDER / "manifest.csv"

NUMBER_OF_RESULTS = 5

MIN_RESOURCE_SCORE = 0.15
MIN_INTENT_SCORE = 0.10
MIN_SEMANTIC_SCORE = 0.40
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------------------------------------------------
# LOAD THE DATASET
# ---------------------------------------------------------

def load_documents():
    """
    Read manifest.csv and load the corresponding Markdown files.

    Each document keeps:
    - title
    - original source URL
    - source partition
    - source type
    - local path
    - document text
    """

    documents = []

    print("Loading MPS documents...")

    with open(MANIFEST_FILE, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:

            relative_path = row["path"]
            document_path = DATASET_FOLDER / relative_path

            if not document_path.exists():
                continue

            try:
                text = document_path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

            except OSError:
                continue

            documents.append({
                "title": row.get("title", ""),
                "source_url": row.get("source_url", ""),
                "source_partition": row.get(
                    "source_partition",
                    ""
                ),
                "source_type": row.get("source_type", ""),
                "path": relative_path,
                "text": text
            })

    print(f"Loaded {len(documents):,} documents.")

    return documents


# ---------------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------------

def clean_text(text):
    """
    Perform some very basic cleanup before indexing.
    """

    # Remove Markdown/YAML punctuation that isn't useful
    text = re.sub(r"[-#>*`]", " ", text)

    # Replace repeated whitespace with a single space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------
# BUILD SEARCH INDEX
# ---------------------------------------------------------

def build_search_index(documents):
    """
    Create one searchable string for each document.

    The title is repeated so that title matches receive
    more weight than ordinary body-text matches.
    """

    searchable_documents = []

    print("Building search index...")

    for document in documents:

        title = clean_text(document["title"])
        body = clean_text(document["text"])

        searchable_text = (
            f"{title} {title} {title} "
            f"{document['source_partition']} "
            f"{document['source_type']} "
            f"{body}"
        )

        searchable_documents.append(searchable_text)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=50000
    )

    document_vectors = vectorizer.fit_transform(
        searchable_documents
    )

    print("Search index ready.")

    return vectorizer, document_vectors


# ---------------------------------------------------------
# FIND A USEFUL EXCERPT
# ---------------------------------------------------------

def get_excerpt(text, query, length=350):
    """
    Try to show the part of the document containing
    one of the user's search terms.
    """

    cleaned = clean_text(text)

    query_words = [
        word.lower()
        for word in query.split()
        if len(word) > 2
    ]

    lower_text = cleaned.lower()

    position = -1

    for word in query_words:
        position = lower_text.find(word)

        if position != -1:
            break

    # If no query word is found, use the beginning
    if position == -1:
        position = 0

    start = max(0, position - 100)
    end = min(len(cleaned), start + length)

    excerpt = cleaned[start:end]

    if start > 0:
        excerpt = "..." + excerpt

    if end < len(cleaned):
        excerpt += "..."

    return excerpt


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------

def search(
    query,
    documents,
    vectorizer,
    document_vectors
):
    """
    Compare the user's query against every indexed document.
    """

    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(
        query_vector,
        document_vectors
    )[0]

    ranked_indexes = scores.argsort()[::-1]

    results = []

    for index in ranked_indexes[:NUMBER_OF_RESULTS]:

        results.append({
            "document": documents[index],
            "score": scores[index]
        })

    return results


def check_query_safety(query):
    """
    Check whether a query requests student images or
    private student information.

    Returns:
        (True, None) if the query may continue to retrieval.
        (False, reason) if the query should be blocked.
    """

    query = query.lower()

    # Requests for images/photos of students
    image_words = [
        "picture",
        "pictures",
        "photo",
        "photos",
        "image",
        "images"
    ]

    student_image_subjects = [
        "student",
        "students",
        "class",
        "cheerleader",
        "cheerleaders",
        "cheerleading",
        "wrestler",
        "wrestlers",
        "wrestling",
        "team"
    ]

    asks_for_image = any(
        word in query
        for word in image_words
    )

    mentions_student_subject = any(
        word in query
        for word in student_image_subjects
    )

    if asks_for_image and mentions_student_subject:
        return False, "student_images"

    # Requests for private student information
    private_info_terms = [
        "home address",
        "phone number",
        "personal email",
        "password",
        "passwords",
        "student id",
        "student ids",
        "student number",
        "date of birth",
        "birth date",
        "medical record",
        "medical records",
        "grades",
        "grade report",
        "disciplinary record",
        "disciplinary records"
    ]

    student_terms = [
        "student",
        "students",
        "child",
        "children"
    ]

    mentions_private_info = any(
        term in query
        for term in private_info_terms
    )

    mentions_student = any(
        term in query
        for term in student_terms
    )

    if mentions_private_info and mentions_student:
        return False, "student_private_information"

    return True, None

def handle_search(query, number_of_results=3):
    """
    Run safety validation followed by resource retrieval.
    """

    allowed, reason = check_query_safety(query)

    if not allowed:
        return {
            "blocked": True,
            "reason": reason,
            "results": []
        }

    results = search_resources(
        query,
        number_of_results
    )

    return {
        "blocked": False,
        "reason": None,
        "results": results
    }


# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------

def display_results(query, results):

    print()
    print("=" * 70)
    print(f'Search results for: "{query}"')
    print("=" * 70)

    for number, result in enumerate(results, start=1):

        document = result["document"]
        score = result["score"]

        print()
        print(f"{number}. {document['title']}")
        print(f"   Relevance: {score:.3f}")

        print(
            f"   Source group: "
            f"{document['source_partition']}"
        )

        print(
            f"   Document type: "
            f"{document['source_type']}"
        )

        print()
        print(
            "   "
            + get_excerpt(
                document["text"],
                query
            )
        )

        if document["source_url"]:
            print()
            print(
                f"   Source: "
                f"{document['source_url']}"
            )

def search_resources(query, number_of_results=3):
    """
    Search the curated MPS information tree.

    Returns the resources that best match the user's question.
    """

    resources = load_resources()
    '''
    intent_texts = [
        resource.get("staff_intent", "")
        for resource in resources
    ]
    '''
    semantic_texts = []

    for resource in resources:
        semantic_text = " ".join([
            resource.get("resource_name", ""),
            resource.get("description", ""),
            resource.get("staff_intent", "")
        ])

        semantic_texts.append(semantic_text)

    resource_embeddings = semantic_model.encode(
        semantic_texts,
        normalize_embeddings=True
    )

    query_embedding = semantic_model.encode(
        query,
        normalize_embeddings=True
    )

    semantic_scores = resource_embeddings @ query_embedding

    searchable_resources = []

    for resource in resources:
        searchable_text = " ".join([
            resource.get("resource_name", ""),
            resource.get("resource_name", ""),
            resource.get("resource_name", ""),
            resource.get("category", ""),
            resource.get("subcategory", ""),
            resource.get("description", ""),
            resource.get("keywords", ""),
            resource.get("staff_intent", ""),
            resource.get("resource_type", "")
        ])

        searchable_resources.append(searchable_text)

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    resource_vectors = vectorizer.fit_transform(
        searchable_resources
    )
    '''
    intent_vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    intent_vectors = intent_vectorizer.fit_transform(
        intent_texts
    )
    '''
    query_vector = vectorizer.transform([query])
    #intent_query_vector = intent_vectorizer.transform([query])

    scores = cosine_similarity(
        query_vector,
        resource_vectors
    )[0]
    '''
    intent_scores = cosine_similarity(
        intent_query_vector,
        intent_vectors
    )[0]
    '''
    ranked_indexes = scores.argsort()[::-1]

    results = []

    for index in ranked_indexes:

        score = float(scores[index])
        #intent_score = float(intent_scores[index])
        semantic_score = float(semantic_scores[index])

        # Do not return resources that are not relevant enough.
        if score < MIN_RESOURCE_SCORE:
            continue
        # Do not return resources when query intent is not strong enough.
        #if intent_score < MIN_INTENT_SCORE:
        #    continue
        if semantic_score < MIN_SEMANTIC_SCORE:
            continue

        resource = resources[index]

        results.append({
            "resource_id": resource["resource_id"],
            "resource_name": resource["resource_name"],
            "category": resource["category"],
            "subcategory": resource["subcategory"],
            "resource_type": resource["resource_type"],
            "description": resource["description"],
            "staff_intent": resource["staff_intent"],
            "source_url": resource["source_url"],
            "score": score,
            #"intent_score": intent_score,
            "semantic_score": semantic_score
        })

        # Return at most the requested number of relevant resources.
        if len(results) >= number_of_results:
            break

    return results


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("MPS Information Tree Search")
    print("=" * 70)

    while True:

        print()

        query = input(
            "What are you looking for? "
            "(type 'quit' to exit): "
        ).strip()

        if query.lower() == "quit":
            break

        if not query:
            continue

        results = search_resources(query)

        print()
        print(f'Results for: "{query}"')
        print("-" * 70)

        for number, result in enumerate(results, start=1):

            print()
            print(
                f"{number}. "
                f"{result['resource_name']}"
            )

            print(
                f"   Category: "
                f"{result['category']} > "
                f"{result['subcategory']}"
            )

            print(
                f"   Type: "
                f"{result['resource_type']}"
            )

            print(
                f"   Relevance: "
                f"{result['score']:.3f}"
            )

            print(
                f"   {result['description']}"
            )

            print(
                f"   Source: "
                f"{result['source_url']}"
            )


if __name__ == "__main__":
    main()