import os
import io
import json
from fpdf.enums import XPos, YPos
import traceback
from typing import Annotated
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pdfminer.high_level import extract_text
from fpdf import FPDF, enums
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

client = genai.Client()

# ---------------------------------------------------------------------------
# Helper: clean Unicode → Latin-1 safe (Times font in fpdf)
# ---------------------------------------------------------------------------
UNICODE_MAP = {
    '\u2013': '-', '\u2014': '-',
    '\u2018': "'", '\u2019': "'",
    '\u201c': '"', '\u201d': '"',
    '\u2026': '...',
    '\u2022': '-', '\u25cf': '-', '\u25c6': '-',
    '\u00b0': ' degrees',
    '\u00e9': 'e', '\u00e1': 'a', '\u00ed': 'i',
    '\u00f3': 'o', '\u00fa': 'u', '\u00f1': 'n',
    '\u00c9': 'E', '\u00c1': 'A', '\u00cd': 'I',
    '\u00d3': 'O', '\u00da': 'U', '\u00d1': 'N',
    '\u00fc': 'u', '\u00e4': 'a', '\u00f6': 'o',
    '\u2019': "'",
}

def safe_str(value, default='') -> str:
    if isinstance(value, dict):
        parts = [str(v) for v in value.values() if v]
        result = ' | '.join(parts) if parts else default
    elif isinstance(value, list):
        result = ', '.join(str(i) for i in value)
    elif value is None:
        result = default
    else:
        result = str(value)
    for uc, ac in UNICODE_MAP.items():
        result = result.replace(uc, ac)
    # Final pass: replace any remaining non-latin1 chars
    result = result.encode('latin-1', errors='replace').decode('latin-1')
    return result


# ---------------------------------------------------------------------------
# Harvard PDF Builder
# ---------------------------------------------------------------------------
class HarvardCV(FPDF):
    PAGE_W = 210  # A4 width mm
    MARGIN = 20   # left/right margin mm

    def header(self):
        pass  # custom header inside body

    def footer(self):
        self.set_y(-13)
        self.set_font('Times', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f'Page {self.page_no()}', 0, 0, 'C')
        self.set_text_color(0, 0, 0)

    # ---- Utility ----
    def _hr(self, thickness=0.3):
        """Draw a horizontal rule across the content area."""
        self.set_draw_color(0, 0, 0)
        self.set_line_width(thickness)
        x = self.MARGIN
        w = self.PAGE_W - 2 * self.MARGIN
        self.line(x, self.get_y(), x + w, self.get_y())

    def section_title(self, title: str):
        self.ln(4)
        self.set_font('Times', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, safe_str(title).upper(), 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._hr(thickness=0.5)
        self.ln(3)

    def entry_header(self, left: str, right: str = ''):
        """Bold left, italic right (for dates), same line."""
        self.set_font('Times', 'B', 11)
        content_w = self.PAGE_W - 2 * self.MARGIN
        left_w = content_w - 55
        self.cell(left_w, 5, safe_str(left), 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
        self.set_font('Times', 'I', 10)
        self.cell(55, 5, safe_str(right), 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')

    def entry_sub(self, text: str):
        self.set_font('Times', 'I', 11)
        self.cell(0, 5, safe_str(text), 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    def bullet(self, text: str):
        self.set_font('Times', '', 10.5)
        x_orig = self.get_x()
        y_orig = self.get_y()
        indent = self.MARGIN + 6
        bullet_x = self.MARGIN + 1
        # draw diamond bullet manually
        self.set_xy(bullet_x, y_orig + 1.5)
        self.cell(5, 4, '-', 0, 0)
        self.set_xy(indent, y_orig)
        content_w = self.PAGE_W - indent - self.MARGIN
        self.multi_cell(content_w, 4.5, safe_str(text))

    def normal_text(self, text: str, size: float = 10.5):
        self.set_font('Times', '', size)
        content_w = self.PAGE_W - 2 * self.MARGIN
        self.multi_cell(content_w, 5, safe_str(text))


def generate_harvard_pdf(data: dict) -> bytes:
    pdf = HarvardCV()
    pdf.set_margins(HarvardCV.MARGIN, 20, HarvardCV.MARGIN)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    content_w = HarvardCV.PAGE_W - 2 * HarvardCV.MARGIN

    # ── NAME ──────────────────────────────────────────────────────────────────
    pdf.set_font('Times', 'B', 22)
    pdf.cell(0, 10, safe_str(data.get('name', 'Your Name')), 0, 1, 'C')

    # ── JOB TITLE ─────────────────────────────────────────────────────────────
    if data.get('job_title'):
        pdf.set_font('Times', '', 12)
        pdf.cell(0, 5, safe_str(data['job_title']), 0, 1, 'C')

    # ── CONTACT INFO ──────────────────────────────────────────────────────────
    pdf.ln(2)
    pdf.set_font('Times', '', 9.5)
    contact = safe_str(data.get('contact_info', ''))
    if contact:
        pdf.cell(0, 5, contact, 0, 1, 'C')
    pdf.ln(3)
    pdf._hr(0.6)
    pdf.ln(4)

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    if data.get('summary'):
        pdf.section_title('Summary')
        pdf.normal_text(data['summary'])
        pdf.ln(3)

    # ── EDUCATION ─────────────────────────────────────────────────────────────
    if data.get('education'):
        pdf.section_title('Education')
        for edu in data['education']:
            pdf.entry_header(edu.get('institution', ''), edu.get('year', ''))
            pdf.entry_sub(edu.get('degree', ''))
            if edu.get('location'):
                pdf.set_font('Times', '', 10)
                pdf.cell(0, 4, safe_str(edu['location']), 0, 1)
            for detail in edu.get('details', []):
                pdf.bullet(detail)
            pdf.ln(3)

    # ── SKILLS ───────────────────────────────────────────────────────────────
    if data.get('skills'):
        pdf.section_title('Skills')
        skills = data['skills']
        col_w = content_w / 2 - 3
        if isinstance(skills, dict):
            items = list(skills.items())
            for i in range(0, len(items), 2):
                y = pdf.get_y()
                # Left column
                cat, vals = items[i]
                pdf.set_xy(HarvardCV.MARGIN, y)
                pdf.set_font('Times', 'B', 10)
                pdf.cell(col_w, 4.5, safe_str(cat) + ':', 0, 0)
                pdf.ln(4.5)
                pdf.set_xy(HarvardCV.MARGIN, pdf.get_y())
                pdf.set_font('Times', '', 10)
                pdf.multi_cell(col_w, 4.5, safe_str(vals))
                y_after_left = pdf.get_y()
                # Right column (if exists)
                if i + 1 < len(items):
                    cat2, vals2 = items[i + 1]
                    pdf.set_xy(HarvardCV.MARGIN + col_w + 6, y)
                    pdf.set_font('Times', 'B', 10)
                    pdf.cell(col_w, 4.5, safe_str(cat2) + ':', 0, 0)
                    pdf.set_xy(HarvardCV.MARGIN + col_w + 6, y + 4.5)
                    pdf.set_font('Times', '', 10)
                    pdf.multi_cell(col_w, 4.5, safe_str(vals2))
                    y_after_right = pdf.get_y()
                    pdf.set_y(max(y_after_left, y_after_right))
                else:
                    pdf.set_y(y_after_left)
                pdf.ln(2)
        else:
            # Flat list of skills
            skills_list = skills if isinstance(skills, list) else [skills]
            for i in range(0, len(skills_list), 2):
                y = pdf.get_y()
                pdf.set_xy(HarvardCV.MARGIN, y)
                pdf.set_font('Times', '', 10)
                pdf.cell(col_w, 4.5, safe_str(skills_list[i]), 0, 0)
                if i + 1 < len(skills_list):
                    pdf.set_xy(HarvardCV.MARGIN + col_w + 6, y)
                    pdf.cell(col_w, 4.5, safe_str(skills_list[i + 1]), 0, 0)
                pdf.ln(5)
        pdf.ln(2)

    # ── EXPERIENCE ────────────────────────────────────────────────────────────
    if data.get('experience'):
        pdf.section_title('Experience')
        for exp in data['experience']:
            pdf.entry_header(exp.get('role', ''), exp.get('dates', ''))
            sub = safe_str(exp.get('company', ''))
            if exp.get('location'):
                sub += ', ' + safe_str(exp['location'])
            pdf.entry_sub(sub)
            for resp in exp.get('responsibilities', []):
                pdf.bullet(resp)
            pdf.ln(4)

    # ── COVER LETTER ──────────────────────────────────────────────────────────
    if data.get('cover_letter'):
        pdf.add_page()
        pdf.set_font('Times', 'B', 22)
        pdf.cell(0, 10, safe_str(data.get('name', '')), 0, 1, 'C')
        if data.get('job_title'):
            pdf.set_font('Times', '', 12)
            pdf.cell(0, 5, safe_str(data['job_title']), 0, 1, 'C')
        pdf.ln(2)
        pdf._hr(0.6)
        pdf.ln(4)

        pdf.section_title('Cover Letter')
        cl = data['cover_letter']
        if isinstance(cl, dict):
            if cl.get('hiring_manager'):
                pdf.set_font('Times', '', 10.5)
                pdf.cell(0, 5, safe_str(cl['hiring_manager']), 0, 1)
            if cl.get('company'):
                pdf.cell(0, 5, safe_str(cl['company']), 0, 1)
            if cl.get('address'):
                pdf.multi_cell(0, 5, safe_str(cl['address']))
            pdf.ln(3)
            for para in cl.get('paragraphs', []):
                pdf.normal_text(para)
                pdf.ln(3)
            if cl.get('closing'):
                pdf.normal_text(cl['closing'])
                pdf.ln(5)
            if cl.get('signature'):
                pdf.normal_text(cl['signature'])
        else:
            pdf.normal_text(str(cl))

    # ── REFERENCES ────────────────────────────────────────────────────────────
    if data.get('references'):
        if not data.get('cover_letter'):
            pdf.add_page()
        else:
            pdf.ln(6)
        pdf.section_title('References')
        refs = data['references']
        col_w = content_w / 2 - 3

        left_refs = refs[::2]
        right_refs = refs[1::2]
        max_rows = max(len(left_refs), len(right_refs))

        for i in range(max_rows):
            y = pdf.get_y()
            # Left
            if i < len(left_refs):
                ref = left_refs[i]
                pdf.set_xy(HarvardCV.MARGIN, y)
                pdf.set_font('Times', 'B', 10.5)
                pdf.cell(col_w, 5, safe_str(ref.get('name', '')), 0, 1)
                pdf.set_x(HarvardCV.MARGIN)
                pdf.set_font('Times', 'I', 10)
                pdf.cell(col_w, 4.5, safe_str(ref.get('title', '')), 0, 1)
                pdf.set_x(HarvardCV.MARGIN)
                pdf.set_font('Times', '', 10)
                for line in ['company', 'phone', 'email']:
                    if ref.get(line):
                        pdf.cell(col_w, 4.5, safe_str(ref[line]), 0, 1)
                        pdf.set_x(HarvardCV.MARGIN)
            y_after_left = pdf.get_y()

            # Right
            if i < len(right_refs):
                ref = right_refs[i]
                pdf.set_xy(HarvardCV.MARGIN + col_w + 6, y)
                pdf.set_font('Times', 'B', 10.5)
                pdf.cell(col_w, 5, safe_str(ref.get('name', '')), 0, 0)
                pdf.set_xy(HarvardCV.MARGIN + col_w + 6, y + 5)
                pdf.set_font('Times', 'I', 10)
                pdf.cell(col_w, 4.5, safe_str(ref.get('title', '')), 0, 0)
                base_y = y + 9.5
                pdf.set_font('Times', '', 10)
                for line in ['company', 'phone', 'email']:
                    if ref.get(line):
                        pdf.set_xy(HarvardCV.MARGIN + col_w + 6, base_y)
                        pdf.cell(col_w, 4.5, safe_str(ref[line]), 0, 0)
                        base_y += 4.5
            y_after_right = base_y if i < len(right_refs) else y_after_left
            pdf.set_y(max(y_after_left, y_after_right) + 5)

    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# AI Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a world-class professional CV writer and ATS optimization expert.

Your task:
1. Read the candidate's CV carefully.
2. Rewrite and optimize every section using powerful, action-oriented language and keywords that match the target job posting.
3. Output ONLY a valid JSON object (no markdown, no commentary).

The JSON must have EXACTLY these keys:
{
  "name": "Full Name",
  "job_title": "Target Position Title (concise, e.g. Senior Software Engineer)",
  "contact_info": "Email: x@x.com  |  Phone: +1 555 123 4567  |  LinkedIn: linkedin.com/in/x  |  Portfolio: x.com",
  "summary": "3-4 sentence professional summary tailored to the target job, packed with ATS keywords.",
  "education": [
    {
      "institution": "University Name",
      "degree": "Degree, Field of Study",
      "year": "Graduated: Month YYYY",
      "location": "City, State",
      "details": ["Thesis or relevant coursework bullet", "Honor or award"]
    }
  ],
  "skills": {
    "Category 1 (e.g. Programming)": "Skill A, Skill B, Skill C",
    "Category 2 (e.g. Frameworks)": "Skill D, Skill E",
    "Category 3": "...",
    "Category 4": "..."
  },
  "experience": [
    {
      "role": "Job Title",
      "company": "Company Name",
      "location": "City, State",
      "dates": "Month YYYY - Present",
      "responsibilities": [
        "Started with strong action verb; quantified achievement aligned with target role.",
        "Second bullet with ATS keyword from job description."
      ]
    }
  ],
  "cover_letter": {
    "hiring_manager": "Hiring Manager",
    "company": "Target Company Name",
    "address": "Company Address (if known)",
    "paragraphs": [
      "Opening paragraph: express enthusiasm and mention the specific role.",
      "Body paragraph 1: highlight most relevant experience + key achievement.",
      "Body paragraph 2: connect skills to company needs, show cultural fit.",
      "Closing paragraph: call to action, thank the reader."
    ],
    "closing": "Sincerely,",
    "signature": "Full Name"
  },
  "references": [
    {
      "name": "Reference Full Name",
      "title": "Their Job Title",
      "company": "Their Company",
      "phone": "Phone: +1 555 000 0000",
      "email": "Email: ref@company.com"
    }
  ]
}

Rules:
- Keep all actual facts from the candidate's CV. Do NOT invent new companies, degrees, or credentials.
- References: use only those provided in the CV; if none, output an empty array [].
- Skills must be grouped into categories (4-6 categories maximum), displayed two categories per row.
- Every experience bullet must start with a strong past or present action verb.
- The summary and bullets should naturally embed keywords from the target job description for ATS scoring.
- Output STRICTLY valid JSON, nothing else.
"""


@app.post("/api/optimize")
async def optimize_cv(
    file: UploadFile = File(...),
    job_description: Annotated[str, Form()] = ""
):
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key missing")

    # 1. Extract text from PDF
    try:
        content = await file.read()
        pdf_file = io.BytesIO(content)
        raw_text = extract_text(pdf_file)
        print(f"Extracted {len(raw_text)} chars from PDF.")
        if not raw_text.strip():
            raise ValueError("PDF appears to be empty or unreadable.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {e}")

    # 2. AI Optimization
    user_prompt = f"""Target Job / Position: "{job_description}"

Candidate's CV:
\"\"\"
{raw_text[:14000]}
\"\"\"

Rewrite and return the optimized CV as a JSON object following the schema defined in your instructions."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config={"system_instruction": SYSTEM_PROMPT}
        )
        raw_response = response.text
        # Strip markdown code fences if present
        clean = raw_response.strip()
        if clean.startswith("```"):
            clean = clean.split("```", 2)[1]
            if clean.startswith("json"):
                clean = clean[4:]
            clean = clean.rsplit("```", 1)[0].strip()

        optimized_data = json.loads(clean)
        print("AI generation successful.")
    except json.JSONDecodeError as e:
        print("RAW AI RESPONSE:", raw_response[:2000])
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"AI returned invalid JSON: {e}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"AI generation failed: {e}")

    # 3. Generate PDF
    try:
        pdf_bytes = generate_harvard_pdf(optimized_data)
        print(f"PDF generated: {len(pdf_bytes)} bytes.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

    return Response(content=pdf_bytes, media_type="application/pdf")
