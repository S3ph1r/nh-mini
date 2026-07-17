import re
import zlib
import os

def extract_text_from_raw_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        return f"Error: {pdf_path} does not exist."
        
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
            
        # Find all stream objects in the PDF
        stream_matches = re.finditer(b'stream\r?\n(.*?)\r?\nendstream', content, re.DOTALL)
        
        extracted_text = []
        
        for match in stream_matches:
            stream_data = match.group(1)
            
            # Try to decompress the stream data (usually FlateDecode/zlib)
            try:
                decompressed = zlib.decompress(stream_data)
                # Decode text from bytes
                text_content = decompressed.decode('utf-8', errors='ignore')
                
                # In PDF content streams, text is usually inside parentheses like (text)
                # Let's find all occurrences of (text)
                pdf_strings = re.findall(r'\(([^)]+)\)', text_content)
                if pdf_strings:
                    cleaned_strings = []
                    for s in pdf_strings:
                        # Unescape PDF octal codes if any, e.g. \300 or escaped characters
                        s_cleaned = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m.group(1), 8)), s)
                        s_cleaned = s_cleaned.replace('\\(', '(').replace('\\)', ')')
                        s_cleaned = s_cleaned.strip()
                        if s_cleaned:
                            cleaned_strings.append(s_cleaned)
                    if cleaned_strings:
                        extracted_text.append(" ".join(cleaned_strings))
            except Exception:
                # If decompression fails, it might be an image, font, or non-flate stream, skip it
                continue
                
        if not extracted_text:
            # Let's search for ASCII text anyway in case it's not compressed
            pdf_strings = re.findall(rb'\(([^)]+)\)', content)
            if pdf_strings:
                return "Non-compressed strings:\n" + "\n".join(s.decode('utf-8', errors='ignore') for s in pdf_strings)
            return "No text extracted from PDF."
            
        return "\n\n".join(extracted_text)
    except Exception as e:
        return f"Error parsing PDF: {e}"

if __name__ == "__main__":
    pdf_file = "/home/Projects/NH-Mini/workspace/cv-revision/CV_Roberto_Guareschi_2022.pdf"
    output_file = "/home/Projects/NH-Mini/workspace/cv-revision/extracted_pdf_text.txt"
    
    print(f"Extracting text from {pdf_file}...")
    text = extract_text_from_raw_pdf(pdf_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
        
    print(f"Extracted PDF text saved to {output_file}.")
