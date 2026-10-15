import csv
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

DATASET_FOLDER = Path("data/MPS_Parsed_Content_2026-10-01")
MANIFEST_FILE = DATASET_FOLDER / "manifest.csv"

NUMBER_OF_RESULTS = 5


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


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("MPS Information Retrieval Prototype")
    print("=" * 70)

    documents = load_documents()

    if not documents:
        print()
        print("No documents were loaded.")
        print("Check DATASET_FOLDER at the top of search.py.")
        return

    vectorizer, document_vectors = build_search_index(
        documents
    )

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

        results = search(
            query,
            documents,
            vectorizer,
            document_vectors
        )

        display_results(
            query,
            results
        )


if __name__ == "__main__":
    main()