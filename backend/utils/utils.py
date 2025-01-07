from fpdf import FPDF
import re
from datetime import datetime


class TravelPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_left_margin(25)
        self.set_right_margin(25)
        self.set_auto_page_break(auto=True, margin=25)
        self._current_section = None

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'{self._current_section or ""}', 0, 0, 'L')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section(self, name):
        self._current_section = name


def sanitize_content(content):
    return content.encode('utf-8', 'ignore').decode('utf-8')


def replace_problematic_characters(content):
    replacements = {
        '\u2013': '-',  # en dash
        '\u2014': '--',  # em dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2026': '...',  # ellipsis
        '\u2022': '*',  # bullet
        '\u2122': 'TM',  # trademark
        '\u00a0': ' ',  # non-breaking space
        '\u20ac': 'EUR',  # euro
        '\u00a3': 'GBP',  # pound
        '\u00a5': 'JPY'  # yen
    }
    for char, replacement in replacements.items():
        content = content.replace(char, replacement)
    return content


def generate_travel_pdf(content, filename='itinerary.pdf'):
    try:
        pdf = TravelPDF()
        pdf.add_page()

        # Extract and process content sections
        sections = re.split(r'(?=# |\n## )', content)

        for section in sections:
            if not section.strip():
                continue

            # Process section heading
            if section.startswith('# '):
                # Main title
                pdf.set_font('Arial', 'B', 24)
                title = section.split('\n')[0].strip('# ')
                pdf.cell(0, 20, title, 0, 1, 'C')
                section = '\n'.join(section.split('\n')[1:])
            elif section.startswith('## '):
                # Section heading
                pdf.add_page()
                pdf.set_font('Arial', 'B', 16)
                title = section.split('\n')[0].strip('## ')
                pdf.section(title)
                pdf.cell(0, 15, title, 0, 1, 'L')
                section = '\n'.join(section.split('\n')[1:])

            # Process section content
            lines = section.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    pdf.ln(5)
                    continue

                # Process subsections (###)
                if line.startswith('### '):
                    pdf.set_font('Arial', 'B', 14)
                    pdf.ln(5)
                    pdf.cell(0, 10, line.strip('### '), 0, 1)
                    pdf.set_font('Arial', '', 12)
                    continue

                # Process lists
                if line.startswith('- ') or line.startswith('* '):
                    pdf.set_font('Arial', '', 12)
                    pdf.cell(10, 6, '•', 0, 0)
                    pdf.multi_cell(0, 6, line[2:])
                    continue

                # Process numbered lists
                if re.match(r'^\d+\. ', line):
                    pdf.set_font('Arial', '', 12)
                    number = line.split('.')[0]
                    text = line[len(number) + 2:]
                    pdf.cell(15, 6, f"{number}.", 0, 0)
                    pdf.multi_cell(0, 6, text)
                    continue

                # Process bold text
                if '**' in line:
                    parts = line.split('**')
                    for i, part in enumerate(parts):
                        if i % 2 == 0:
                            pdf.set_font('Arial', '', 12)
                            pdf.write(6, part)
                        else:
                            pdf.set_font('Arial', 'B', 12)
                            pdf.write(6, part)
                    pdf.ln()
                    continue

                # Regular text
                pdf.set_font('Arial', '', 12)
                pdf.multi_cell(0, 6, line)

        pdf.output(filename)
        return f"✓ PDF itinerary generated: {filename}"

    except Exception as e:
        return f"Error generating PDF: {str(e)}"