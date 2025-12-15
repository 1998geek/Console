import os
import sys

# Add project root to sys.path to allow importing from other packages
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from prompt_template.biding_doc_review_template import review_key_points, review_batch_key_points

# --- Constants for File Paths ---
_PROMPT_DIR = os.path.dirname(__file__)
PROMPT_FILE = os.path.join(_PROMPT_DIR, 'biding_review_prompt.txt')
BATCH_PROMPT_FILE = os.path.join(_PROMPT_DIR, 'biding_review_batch_prompt.txt')

# --- Prompt Loading and Saving Functions ---
def load_prompt(is_batch=False):
    """
    Loads the system prompt.
    It first tries to load from the .txt file. If the file doesn't exist,
    it loads the default prompt from the template, saves it to the .txt file,
    and then returns it.

    Args:
        is_batch (bool): If True, loads the prompt for batch image processing.
                         Otherwise, loads the standard single-item prompt.

    Returns:
        str: The content of the loaded prompt.

    Raises:
        IOError: If there is an error reading or writing the file.
    """
    prompt_path = BATCH_PROMPT_FILE if is_batch else PROMPT_FILE
    default_prompt = review_batch_key_points if is_batch else review_key_points

    if not os.path.exists(prompt_path):
        try:
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(default_prompt)
            return default_prompt
        except Exception as e:
            raise IOError(f"Error writing default prompt to {prompt_path}: {e}")

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise IOError(f"Error reading prompt file {prompt_path}: {e}")

def save_prompt(content, is_batch=False):
    """
    Saves the system prompt to the appropriate .txt file.

    Args:
        content (str): The new prompt content to save.
        is_batch (bool): If True, saves the prompt for batch image processing.
                         Otherwise, saves the standard single-item prompt.

    Raises:
        IOError: If there is an error writing the file.
    """
    prompt_path = BATCH_PROMPT_FILE if is_batch else PROMPT_FILE
    try:
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"Error writing prompt file {prompt_path}: {e}")