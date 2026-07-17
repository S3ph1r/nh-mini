import re

def clean_pdf_text(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    clean_lines = []
    
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # If the line contains mostly printable ascii / common characters and has a decent length
        # Let's clean up any weird spaces, backslashes, etc.
        # We want to exclude lines that contain a high density of non-word / binary symbols.
        non_alphanum = len(re.findall(r'[^a-zA-Z0-9\sÀ-ÿ.,:;@()/\-–—]', line))
        total_len = len(line)
        
        if total_len > 0:
            ratio = non_alphanum / total_len
            if ratio < 0.15 and total_len > 15: # Less than 15% junk characters
                # Format some common separators to look nice
                line = re.sub(r'\s+', ' ', line)
                # Clean up PDF artifacts
                line = line.replace(' con gurazione ', ' configurazione ')
                line = line.replace(' con gurare ', ' configurare ')
                line = line.replace(' con gurazioni ', ' configurazioni ')
                clean_lines.append(line)
                
    with open(output_path, 'w', encoding='utf-8') as f_out:
        f_out.write("\n\n".join(clean_lines))

if __name__ == "__main__":
    clean_pdf_text(
        "/home/Projects/NH-Mini/workspace/cv-revision/extracted_pdf_text.txt",
        "/home/Projects/NH-Mini/workspace/cv-revision/clean_cv.txt"
    )
    print("Cleaned text saved.")
