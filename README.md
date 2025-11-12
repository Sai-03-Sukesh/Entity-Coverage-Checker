# Entity Matcher
This is the updated Entity Matcher project with several bug fixes and improvements:
- Robust column mapping and parsing in `core/database.py`
- Identifier indexes for O(1) lookups
- Cached normalized names for faster fuzzy matching
- Faster fuzzy matching using `rapidfuzz.process.extractOne`
- Fixed division-by-zero in results Excel generation
- Fixed variable naming/namespace issues in UI component
- Small UX and safety improvements

**Note:** `data/Entities.xlsx` is not included. Add your master database Excel at `data/Entities.xlsx`.
