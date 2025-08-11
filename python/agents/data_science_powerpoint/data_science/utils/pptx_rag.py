def retrieve_info_from_pptx_text(query: str, pptx_text: str) -> str:
    """
    A simple RAG-like function to retrieve information from extracted PowerPoint text.
    For demonstration, this performs a basic keyword search.
    In a real RAG system, this would involve embeddings and vector similarity search.
    """
    relevant_sections = []
    # Split the text into lines or paragraphs for simpler processing
    paragraphs = pptx_text.split('\n')

    # Simple keyword matching
    query_keywords = query.lower().split()
    for paragraph in paragraphs:
        if any(keyword in paragraph.lower() for keyword in query_keywords):
            relevant_sections.append(paragraph)

    if relevant_sections:
        return "\n".join(relevant_sections)
    else:
        return "No relevant information found in the PowerPoint content for your query."
