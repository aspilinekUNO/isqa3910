import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_FILE = "pages.json"
NUMBER_OF_PAGE_RESULTS = 3
NUMBER_OF_LINK_RESULTS = 5


def load_pages():
    """Load the information collected by crawler.py."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_page_index(pages):
    """
    Create searchable text for every page.

    The title is repeated so that words appearing in the page title
    have more influence on the search results.
    """
    documents = []

    for page in pages:
        title = page.get("title", "")
        text = page.get("text", "")

        searchable_text = f"{title} {title} {title} {text}"
        documents.append(searchable_text)

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    page_vectors = vectorizer.fit_transform(documents)

    return vectorizer, page_vectors


def search_pages(query, pages, vectorizer, page_vectors):
    """Rank crawled pages according to their similarity to the query."""

    query_vector = vectorizer.transform([query])

    scores = cosine_similarity(
        query_vector,
        page_vectors
    )[0]

    ranked_indexes = scores.argsort()[::-1]

    results = []

    for index in ranked_indexes[:NUMBER_OF_PAGE_RESULTS]:
        results.append({
            "page": pages[index],
            "score": scores[index]
        })

    return results


def search_links(query, page):
    """
    Search the links found on a particular page.

    Link text is used because it often describes the actual
    resource the user wants.
    """

    links = page.get("links", [])

    # Remove links with no useful text
    useful_links = []

    for link in links:
        link_text = link.get("text", "").strip()
        url = link.get("url", "").strip()

        if link_text and url:
            useful_links.append(link)

    if not useful_links:
        return []

    link_texts = [
        link["text"]
        for link in useful_links
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:
        link_vectors = vectorizer.fit_transform(link_texts)
        query_vector = vectorizer.transform([query])

    except ValueError:
        return []

    scores = cosine_similarity(
        query_vector,
        link_vectors
    )[0]

    ranked_indexes = scores.argsort()[::-1]

    results = []

    for index in ranked_indexes[:NUMBER_OF_LINK_RESULTS]:

        # Ignore links that have absolutely no similarity
        if scores[index] <= 0:
            continue

        results.append({
            "link": useful_links[index],
            "score": scores[index]
        })

    return results


def display_results(query, page_results):

    print()
    print("=" * 70)
    print(f'Search results for: "{query}"')
    print("=" * 70)

    for number, result in enumerate(page_results, start=1):

        page = result["page"]
        page_score = result["score"]

        print()
        print(f"{number}. {page['title']}")
        print(f"   Page relevance: {page_score:.3f}")
        print(f"   Page: {page['url']}")

        link_results = search_links(query, page)

        if link_results:
            print()
            print("   Possible resources:")

            for link_number, link_result in enumerate(
                link_results,
                start=1
            ):
                link = link_result["link"]
                score = link_result["score"]

                print(
                    f"      {link_number}. "
                    f"{link['text']}"
                )

                print(
                    f"         Relevance: {score:.3f}"
                )

                print(
                    f"         {link['url']}"
                )


def main():

    print("=" * 70)
    print("School Website Information Retrieval Prototype")
    print("=" * 70)

    pages = load_pages()

    print(f"Loaded {len(pages)} crawled pages.")

    vectorizer, page_vectors = build_page_index(pages)

    while True:

        print()

        query = input(
            "What are you looking for? "
            "(type 'quit' to exit): "
        ).strip()

        if query.lower() == "quit":
            print("Goodbye.")
            break

        if not query:
            continue

        page_results = search_pages(
            query,
            pages,
            vectorizer,
            page_vectors
        )

        display_results(
            query,
            page_results
        )


if __name__ == "__main__":
    main()