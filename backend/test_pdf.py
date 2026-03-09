import sys
sys.path.insert(0, '.')
from main import generate_harvard_pdf

# Test data with skills as a dict (the problematic case)
test_data = {
    "name": "John Doe",
    "contact_info": "john@example.com",
    "education": [],
    "experience": [
        {
            "company": "Tech Corp",
            "dates": "2019-Present",
            "role": "Software Engineer",
            "responsibilities": ["Developed systems", "Led team"]
        }
    ],
    "skills": {"technical": "Python, JavaScript", "soft": "Leadership"}  # Dict instead of list/string
}

try:
    print("Testing PDF generation with skills as dict...")
    pdf_bytes = generate_harvard_pdf(test_data)
    print(f"SUCCESS! Generated PDF with {len(pdf_bytes)} bytes")
    
    with open("test_skills_dict.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("Saved to test_skills_dict.pdf")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
