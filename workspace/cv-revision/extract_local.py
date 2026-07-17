import zipfile
import xml.etree.ElementTree as ET
import os

def extract_all_text_from_docx(docx_path):
    texts = []
    if not os.path.exists(docx_path):
        return f"Error: {docx_path} does not exist."
        
    try:
        with zipfile.ZipFile(docx_path) as z:
            namelist = z.namelist()
            # Parse main document and headers/footers
            xml_files = [f for f in namelist if f.endswith('.xml')]
            
            for xml_file in xml_files:
                if not ('document' in xml_file or 'header' in xml_file or 'footer' in xml_file):
                    continue
                    
                xml_content = z.read(xml_file)
                root = ET.fromstring(xml_content)
                
                file_texts = []
                for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    if t.text:
                        file_texts.append(t.text)
                        
                if file_texts:
                    texts.append(f"=== {xml_file} ===")
                    texts.append(" ".join(file_texts))
                    
        return "\n\n".join(texts)
    except Exception as e:
        return f"Error reading XML from DOCX: {e}"

if __name__ == "__main__":
    docx_file = "/home/Projects/NH-Mini/workspace/cv-revision/Curriculum_per_impiegati.docx"
    output_file = "/home/Projects/NH-Mini/workspace/cv-revision/extracted_cv_text.txt"
    
    print(f"Extracting text from {docx_file}...")
    extracted_text = extract_all_text_from_docx(docx_file)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)
        
    print(f"Text successfully saved to {output_file}.")
