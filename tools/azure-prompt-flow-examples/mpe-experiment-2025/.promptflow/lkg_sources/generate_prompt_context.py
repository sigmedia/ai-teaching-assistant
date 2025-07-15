from typing import List
from promptflow import tool
from promptflow_vectordb.core.contracts import SearchResultEntity

@tool
def generate_prompt_context(search_result: List[dict]) -> str:
    def format_doc(doc: dict):
        if doc['Page'] is not "":
            return f"Content: {doc['Content']}\nSource: {doc['Source']}\nPage: {doc['Page']}"
        else:
            return f"Content: {doc['Content']}\nSource: {doc['Source']}"

    SOURCE_KEY = "source"
    URL_KEY = "url"
    PAGE_NUM_KEY = "page_number"

    retrieved_docs = []
    for item in search_result:

        entity = SearchResultEntity.from_dict(item)
        content = entity.text or ""

        source = ""
        page_number = ""
        if entity.metadata is not None:
            if SOURCE_KEY in entity.metadata:
                if URL_KEY in entity.metadata[SOURCE_KEY]:
                    source = entity.metadata[SOURCE_KEY][URL_KEY] or ""
                    if not source.endswith('.no-page.pdf'):
                        if PAGE_NUM_KEY in entity.metadata:
                            page_number = entity.metadata[PAGE_NUM_KEY]+1
                            page_number = str(page_number)
                    source = source.removesuffix('.txt')
                    source = source.removesuffix('.remove.pdf')
                    source = source.removesuffix('.no-page.pdf')

        retrieved_docs.append({
            "Content": content,
            "Source": source,
            "Page": page_number
        })
    doc_string = "\n\n".join([format_doc(doc) for doc in retrieved_docs])
    return doc_string
