from promptflow import tool

@tool
def replace_phrases(chat_input: str) -> str:
    
    REPLACE_PHRASES = {
        "install nuke" : "install the software Nuke", 
        "optimal cut" : "optimal graph cut" 
    }

    original_input = chat_input  # Save the original case
    lowercase_input = chat_input.lower()  # Make lowercase version for matching

    for key, value in REPLACE_PHRASES.items():
        if key.lower() in lowercase_input:
            # Find where the lowercase text is in the original string
            start = lowercase_input.find(key.lower())
            # Get the actual case version from the original string
            original_case_version = original_input[start:start + len(key)]
            # Replace while preserving the original case
            chat_input = chat_input.replace(original_case_version, value)
    
    return chat_input