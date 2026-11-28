#its a format converting file. basically it takes the retrieved documents from the retriever module and formats them in a way that can be used by the generator module.
def format_context(documents):

    context_parts = []

    for index, document in enumerate(documents, start=1):

        source = document.metadata.get(
            "source",
            "Unknown source",
        )

        page = document.metadata.get(
            "page",
            "Unknown page",
        )

        context_parts.append(
            f"""
            [Source {index}]
            Document: {source}
            Page: {page}

            Content:
            {document.page_content}
            """
        )

    return "\n\n".join(context_parts)