"""Read-only MPS resource data adapter. No web crawling or search implementation."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().with_name('mps_resources.json')


def load_resources():
    """Return the complete list of MPS resource dictionaries."""
    with DATA_PATH.open(encoding='utf-8') as handle:
        return json.load(handle)


def get_resource(resource_id):
    """Return a resource by its stable ID, or None."""
    return next((r for r in load_resources() if r['resource_id'] == resource_id), None)


def get_categories():
    """Return sorted top-level categories for an information tree."""
    return sorted({r['category'] for r in load_resources()})


def as_search_pages():
    """Convert the curated resources to the page schema expected by search.py.

    Each resource is represented as a page with title, URL, searchable text,
    and a direct resource link. The underlying source is a curated catalog,
    not crawled page content.
    """
    pages = []
    for resource in load_resources():
        url = resource['source_url']
        pages.append({
            'title': resource['resource_name'],
            'url': url,
            'text': ' '.join(filter(None, [
                resource['category'], resource['subcategory'],
                resource['description'], resource['keywords'],
                resource['staff_intent'], resource['resource_type'],
            ])),
            'links': [{'text': resource['resource_name'], 'url': url}],
        })
    return pages


def export_search_pages(destination='mps_pages.json'):
    """Write a pages.json-compatible file without replacing existing pages.json."""
    path = Path(destination)
    path.write_text(json.dumps(as_search_pages(), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return path


if __name__ == '__main__':
    output = export_search_pages()
    print(f'Exported {len(load_resources())} MPS records to {output}')
