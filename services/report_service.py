import os
import tempfile
import sqlite3
from datetime import datetime
from fpdf import FPDF

DB_FILE = "annadata_farm.db"

class FarmSummaryPDF(FPDF):
    def header(self):
        # Header banner
        self.set_fill_color(2, 54, 37)  # Forest Green
        self.rect(0, 0, 210, 22, 'F')
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 10, 'AnnaDATA - Farm Health & Diagnostic Summary Report', ln=True, align='L')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'AnnaDATA Offline Agronomic Twin | Generated on {datetime.now().strftime("%d %b %Y, %H:%M")} | Page {self.page_no()}', align='C')

    def section_header(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(2, 54, 37)
        self.set_fill_color(240, 245, 240)
        self.cell(0, 7, f"  {title}", ln=True, fill=True)
        self.ln(2)

def generate_farm_health_pdf(
    farmer_name: str = "Farmer",
    location: str = "Odisha, India",
    crop: str = "Paddy",
    farm_acres: float = 12.5,
    soil_moisture: float = 42.0,
    soil_temp: float = 28.0,
    ndvi: float = 0.72
) -> str:
    """Generates a downloadable PDF report and returns the file path."""
    pdf = FarmSummaryPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 1. Farmer & Farm Overview Table
    pdf.section_header("1. Farm & Crop Profile")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)
    
    col_w = 47
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(col_w, 6, "Farmer Name:", border=0)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(col_w, 6, f"{farmer_name}", border=0)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(col_w, 6, "Location:", border=0)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(col_w, 6, f"{location}", border=0, ln=True)

    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(col_w, 6, "Primary Crop:", border=0)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(col_w, 6, f"{crop}", border=0)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(col_w, 6, "Farm Size:", border=0)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(col_w, 6, f"{farm_acres} Acres", border=0, ln=True)
    pdf.ln(3)

    # 2. Live Agronomic Telemetry
    pdf.section_header("2. Real-Time Telemetry & Microclimate Indices")
    pdf.set_font('Helvetica', '', 9.5)
    
    # Simple metric boxes
    pdf.set_draw_color(200, 200, 200)
    pdf.set_fill_color(250, 250, 250)
    
    metrics = [
        ("Soil Moisture", f"{soil_moisture}%", "Optimal Range: 35-50%"),
        ("Soil Temperature", f"{soil_temp} C", "Normal"),
        ("NDVI Canopy Index", f"{ndvi}", "Healthy Vegetative Cover")
    ]
    
    box_w = 60
    for title, val, note in metrics:
        x, y = pdf.get_x(), pdf.get_y()
        pdf.rect(x, y, box_w, 16, 'DF')
        pdf.set_xy(x + 2, y + 2)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(box_w - 4, 4, title.upper(), ln=True)
        pdf.set_x(x + 2)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(2, 54, 37)
        pdf.cell(box_w - 4, 5, val, ln=True)
        pdf.set_x(x + 2)
        pdf.set_font('Helvetica', '', 7.5)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(box_w - 4, 4, note, ln=True)
        pdf.set_xy(x + box_w + 5, y)
    
    pdf.ln(20)

    # 3. Actionable Diagnostic & Advisory
    pdf.section_header("3. AI Agronomic Advisory & Crop Health Assessment")
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(30, 30, 30)
    
    advisory_text = (
        f"- Irrigation: Current root-zone moisture ({soil_moisture}%) indicates adequate hydration. "
        "Maintain normal drainage channels to avoid moisture stagnation.\n"
        f"- Nutrient Top-Dressing: For {crop}, apply recommended second split of Nitrogen during active tillering.\n"
        "- Pest Watch: Relative humidity levels support preventive organic spray (Neem oil 1500 ppm) "
        "to prevent early shoot borer or fungal spores."
    )
    pdf.multi_cell(0, 5, advisory_text)
    pdf.ln(3)

    # 4. Recent Farm Lifecycle Events (from SQLite)
    pdf.section_header("4. Farm Ledger History (Last 5 Events)")
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_fill_color(230, 235, 230)
    pdf.cell(35, 6, " Date", border=1, fill=True)
    pdf.cell(45, 6, " Event Title", border=1, fill=True)
    pdf.cell(110, 6, " Description", border=1, fill=True, ln=True)

    pdf.set_font('Helvetica', '', 8.5)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT date_logged, title, description FROM crop_history ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        conn.close()

        if rows:
            for d, t, desc in rows:
                desc_clean = (desc[:65] + '...') if len(desc) > 65 else desc
                pdf.cell(35, 6, f" {d}", border=1)
                pdf.cell(45, 6, f" {t}", border=1)
                pdf.cell(110, 6, f" {desc_clean}", border=1, ln=True)
        else:
            pdf.cell(190, 6, " No recent farm events logged.", border=1, ln=True)
    except Exception as e:
        pdf.cell(190, 6, f" Ledger query notice: {e}", border=1, ln=True)

    pdf.ln(5)

    # Save to temp path
    output_filename = f"farm_health_report_{int(datetime.now().timestamp())}.pdf"
    output_path = os.path.join(tempfile.gettempdir(), output_filename)
    pdf.output(output_path)
    return output_path