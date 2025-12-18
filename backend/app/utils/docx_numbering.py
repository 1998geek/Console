import io
import re
import logging
from collections import defaultdict
try:
    from docx import Document
    from docx.shared import Pt
except ImportError:
    Document = None

logger = logging.getLogger(__name__)

class DocxNumberingService:
    def process(self, file_stream: io.BytesIO) -> io.BytesIO:
        if not Document:
            raise ImportError("python-docx is not installed")
        
        doc = Document(file_stream)
        
        # 1. Analyze existing heading levels
        # We look for styles starting with 'Heading' or '标题'
        # and map them to a compressed range (1, 2, 3...)
        
        existing_levels = set()
        paragraphs_to_process = []
        
        for para in doc.paragraphs:
            style_name = para.style.name
            level = self._get_heading_level(style_name)
            if level is not None:
                existing_levels.add(level)
                paragraphs_to_process.append((para, level))
        
        if not existing_levels:
            logger.info("No headings found.")
            file_stream.seek(0)
            return file_stream

        # Map actual levels to compressed levels (1-based index)
        sorted_levels = sorted(list(existing_levels))
        level_map = {original: i+1 for i, original in enumerate(sorted_levels)}
        
        # 2. Apply numbering
        # current_counters[k] stores the current count for level k
        current_counters = defaultdict(int)
        
        for para, original_level in paragraphs_to_process:
            new_level = level_map[original_level]
            
            # Increment counter for this level
            current_counters[new_level] += 1
            
            # Reset counters for deeper levels
            keys_to_reset = [k for k in current_counters if k > new_level]
            for k in keys_to_reset:
                current_counters[k] = 0
            
            # Construct the number string (e.g., "1.1. ")
            number_parts = [str(current_counters[i]) for i in range(1, new_level + 1)]
            number_str = ".".join(number_parts)
            # Add trailing dot only if it's top level? Or always?
            # User example: "1, 1.1, 1.1.1" -> No trailing dot for sub-levels usually, 
            # but often "1." for top level. Let's follow standard "1.1" format.
            # If user wants "1.", "1.1", "1.1.1"
            
            # Clean existing numbering if present (simple heuristic)
            # e.g. "1. Introduction" -> "Introduction"
            clean_text = self._strip_existing_numbering(para.text)
            
            # Prepend new number
            full_text = f"{number_str} {clean_text}"
            
            # Update paragraph text while trying to preserve style
            # Simplest way: set para.text. This removes run-level formatting.
            # Better way: insert a run at the beginning or modify the first run.
            # Given "Preserve Format" requirement, we try to keep run styles.
            # But changing text requires shuffling runs.
            # A safe compromise: Clear text and add new run with same style as first run?
            # Or just prepend to the first run?
            if para.runs:
                # Check if first run contains the text we stripped
                # This is hard. Let's just update para.text for now as it's robust.
                # To preserve style, we can try to copy the style of the first run to the new text.
                # But headings usually have paragraph-level style.
                para.text = full_text
            else:
                para.add_run(full_text)

        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        return output

    def _get_heading_level(self, style_name: str) -> int | None:
        # Match "Heading 1", "Heading 2" ... or "标题 1", "标题 2"
        match = re.search(r'(?:Heading|标题)\s*(\d+)', style_name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def _strip_existing_numbering(self, text: str) -> str:
        # Regex to remove "1. ", "1.1 ", "1.1.1 " at start
        # strict pattern: numbers separated by dots, optional trailing dot, followed by space
        return re.sub(r'^\s*[\d.]+\s+', '', text).strip()
