import zipfile
import xml.etree.ElementTree as ET

def extract_all_text_from_docx(docx_path):
    # Namespace dictionary for Word XML
    ns = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    texts = []
    
    with zipfile.ZipFile(docx_path) as z:
        # Check files in the zip
        namelist = z.namelist()
        
        # We are interested in word/document.xml, but there could be headers/footers too
        xml_files = [f for f in namelist if f.endswith('.xml')]
        
        for xml_file in xml_files:
            # Let's focus on the main document and headers/footers/footnotes
            if not ('document' in xml_file or 'header' in xml_file or 'footer' in xml_file):
                continue
                
            xml_content = z.read(xml_file)
            root = ET.fromstring(xml_content)
            
            # Find all <w:t> elements (text elements)
            file_texts = []
            for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if t.text:
                    file_texts.append(t.text)
                    
            if file_texts:
                texts.append(f"=== {xml_file} ===")
                texts.append(" ".join(file_texts))
                
    return "\n\n".join(texts)

if __name__ == "__main__":
    content = extract_all_text_from_docx("/home/Projects/NH-Mini/scratch/Curriculum_per_impiegati.docx")
    print(content[:5000]) # print first 5000 characters
