import json
import re

json_file_path = "dataset/scraped_data.json"
output_file_path = "dataset/cleaned_data.json"

cleaning_patterns = [
    (r'hamburger-icon|close-icon|down-arrow|ratings-stars|qr-code', ''), 
    (r'\[.*?\]\s*\(https?://[^\s)]+\)|\[.*?\]\s*\(/[^)]*\)', ''), 
    (r'\[.*?\]', ''), 
    (r'\b\w+-icon\b', ''), 
    (r'By .*?\s*·\s*\w+\s+\d{1,2},\s*\d{4}', ''), 
    (r'By\s+\w+\s+', ''), 
    (r'Play\s*\S*', ''), 
    (r'Load More\s*\S*', ''), 
    (r'\s+', ' '), 
]


processed_data = []

with open(json_file_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

for i, entry in enumerate(raw_data):
    entry_number = i + 1
    print(f"Processing entry {entry_number} (URL: {entry.get('metadata', {}).get('url', 'N/A')})")

    original_text = entry['text']

    cleaned_text = original_text

    for pattern, replacement in cleaning_patterns:

        cleaned_text = re.sub(pattern, replacement, cleaned_text)

    cleaned_text_lines = [line.strip() for line in cleaned_text.split('\n')]

    cleaned_text = '\n'.join(cleaned_text_lines).strip()
    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)

    processed_entry = {
        "text": cleaned_text,
        "metadata": entry['metadata']
    }

    processed_data.append(processed_entry)
    print(f"Processed entry {entry_number} successfully.")



if processed_data:
    with open(output_file_path, "w", encoding="utf-8") as out:
        json.dump(processed_data, out, indent=4)
    print(f"Successfully saved cleaned data to {output_file_path}.")
else:  
    print("No data to save after processing. Output file not created.")
