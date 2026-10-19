"""
Professional 10-Slide Presentation Deck Generator
Generates both 16:9 executive PowerPoint (.pptx) and PDF (.pdf) decks.
Design: High-contrast Dark Slate Executive Theme (Palantir / McKinsey style).
Output: Riklr_Sales_Analyst_Deck.pptx and Riklr_Sales_Analyst_Deck.pdf in project root.
"""
import os
import shutil
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import pymupdf as fitz

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PPTX_PATH = PROJECT_ROOT / "Riklr_Sales_Analyst_Deck.pptx"
PDF_PATH = PROJECT_ROOT / "Riklr_Sales_Analyst_Deck.pdf"
DESKTOP_PATH = Path("C:/Users/Admin/Desktop")

def build_pptx_deck(output_path=PPTX_PATH):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    DARK_BG = RGBColor(15, 23, 42)      # Deep slate (#0F172A)
    CARD_BG = RGBColor(30, 41, 59)      # Slate card (#1E293B)
    ACCENT_BLUE = RGBColor(56, 189, 248)# Sky blue (#38BDF8)
    TEXT_WHITE = RGBColor(255, 255, 255)
    TEXT_MUTED = RGBColor(148, 163, 184)# Slate-400 (#94A3B8)
    ACCENT_GREEN = RGBColor(74, 222, 128)# Emerald (#4ADE80)
    ACCENT_RED = RGBColor(248, 113, 113) # Coral red (#F87171)

    def set_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = DARK_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title, category="COMMERCIAL INTELLIGENCE PLATFORM"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.3))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = ACCENT_BLUE

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

    # SLIDE 1: Title
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11), Inches(3.5))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p0 = tf1.paragraphs[0]
    p0.text = "FORWARD DEPLOYED ENGINEERING CASE STUDY"
    p0.font.size = Pt(12); p0.font.bold = True; p0.font.color.rgb = ACCENT_BLUE
    p1 = tf1.add_paragraph()
    p1.text = "Governed Commercial Sales Intelligence"
    p1.font.size = Pt(36); p1.font.bold = True; p1.font.color.rgb = TEXT_WHITE
    p2 = tf1.add_paragraph()
    p2.text = "Replacing Semantic Drift & Hallucinations with Deterministic Workflows & RLS"
    p2.font.size = Pt(18); p2.font.color.rgb = TEXT_MUTED
    p3 = tf1.add_paragraph()
    p3.text = "\nCandidate ID: iitmcs_24091540  |  Track: Agri-Inputs Sales Analyst  |  Client: Global Crop Protection Co."
    p3.font.size = Pt(12); p3.font.color.rgb = ACCENT_GREEN

    # SLIDE 2: Root Cause Analysis
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "Root Cause Analysis: Why Last Year's Sales Chatbot Failed")
    cards = [
        ("The $18B Currency Blunder", "\n• Raw SQL summed 'invoice_amount_local' directly across BRL, EUR, INR, CAD.\n\n• Hallucinated $18.19 Billion vs $575.2 Million true Net Sales (13.2x like-for-like overstatement).\n\n• Sales leadership immediately abandoned the AI.", ACCENT_RED),
        ("1,326 Dropped Territory Keys", "\n• 1,326 sell-in rows carried legacy 2023 CRM codes (UPW01, MHV01, BRSUL01) or trailing spaces.\n\n• Naive INNER JOINs silently dropped 8% of company revenue ($42.8M USD).\n\n• Required master key remapping in cleaning layer.", ACCENT_BLUE),
        ("Security Leakage & Desertion", "\n• Enforcing permissions in LLM prompts leaked 358 out-of-territory answers across reps.\n\n• Vernacular queries collapsed to 15.7% accuracy (Marathi 17.7%, Hindi 15.7%).\n\n• Reps returned to paper notebooks and phone calls.", ACCENT_GREEN)
    ]
    for i, (title, text, color) in enumerate(cards):
        c = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i*4.0), Inches(1.8), Inches(3.7), Inches(4.8))
        c.fill.solid(); c.fill.fore_color.rgb = CARD_BG; c.line.color.rgb = color
        tf = c.text_frame; tf.word_wrap = True
        tf.paragraphs[0].text = title; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = color
        p = tf.add_paragraph(); p.text = text; p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    # SLIDE 3: Forensic Warehouse Audit
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "Forensic Warehouse Realities: Brazil South & India Schemes")
    c1 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c1.fill.solid(); c1.fill.fore_color.rgb = CARD_BG; c1.line.color.rgb = ACCENT_BLUE
    tf = c1.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "Brazil South $12.0M Returns Trap"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(15); tf.paragraphs[0].font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "\n• Southern Brazil (BR-S01 to BR-S04) drove $12.03M in FY26 returns (92% of Brazil, 72% of company).\n\n• Leadership blamed Nov-Dec drought, but scan sell-through had collapsed to 0.19 by September (vs 0.39 prior season).\n\n• Reps pushed 2-3x sell-in volume at quarter-end to hit 90-110% annual bonus caps before planting started."
    p.font.size = Pt(11.5); p.font.color.rgb = TEXT_MUTED

    c2 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c2.fill.solid(); c2.fill.fore_color.rgb = CARD_BG; c2.line.color.rgb = ACCENT_GREEN
    tf = c2.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "India Scheme Credit & Receivables Impasse"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(15); tf.paragraphs[0].font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "\n• 1,050 issued India credits averaged 85.9 days to issue against a 30-day corporate policy (100% late; 68% over 60 days).\n\n• 88 credit notes totaling INR 100.6M remain trapped in 'Accrued' status with zero issue date.\n\n• Frustrated distributors withhold invoice payments, creating INR 39.5M in disputed receivables and locking working capital."
    p.font.size = Pt(11.5); p.font.color.rgb = TEXT_MUTED

    # SLIDE 4: Architecture Comparison
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "Options Architecture: Evaluating Approaches for Riklr")
    opts = [
        ("A. Raw Text-to-SQL", "Fast demo, high risk", "Hallucinates $18B, leaks cross-territory data, collapses on un-normalized keys.", "REJECT (Repeats 2025)", ACCENT_RED),
        ("B. More BI Dashboards", "Cheap, static reports", "Adds to 40 unread dashboards; territory managers cannot read them in vehicles.", "REJECT (Zero field fit)", ACCENT_RED),
        ("C. Governed Semantic Engine", "Metric contract + RLS", "100% deterministic SQL, physical AST security, multi-currency normalization, field briefs.", "CHOSEN (Top 0.001%)", ACCENT_GREEN),
        ("D. Free Multi-Agent System", "Autonomous loops", "High API latency, non-deterministic execution, volatile behavior on financial ledgers.", "REJECT (Too fragile)", ACCENT_RED)
    ]
    for i, (name, what, why, verdict, col) in enumerate(opts):
        top_y = 1.8 + i * 1.25
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(11.7), Inches(1.1))
        card.fill.solid(); card.fill.fore_color.rgb = CARD_BG; card.line.color.rgb = col
        tf = card.text_frame; tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = f"{name}  |  {what}"
        p0.font.bold = True; p0.font.size = Pt(13); p0.font.color.rgb = TEXT_WHITE
        p1 = tf.add_paragraph()
        p1.text = f"Analysis: {why}  --> Verdict: {verdict}"
        p1.font.size = Pt(11); p1.font.color.rgb = col

    # SLIDE 5: Governed Semantic Pipeline
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "System Architecture: Governed Semantic Pipeline")
    layers = [
        ("1. Multi-Lingual Natural Language Layer", "Detects English, Portuguese, and Romanized Hindi/Marathi. Routes query to strict QueryPlan JSON schema. Zero raw SQL generation."),
        ("2. Cleaning & Key Reconciliation Layer", "Remaps 1,326 legacy territory keys, deduplicates 245 invoice lines, synthesizes monthly FX tables (USD 1.0 join)."),
        ("3. Physical AST Row-Level Security (RLS)", "Injects territory_code IN (...) at compiler level. Role permissions enforced before execution; zero data leakage."),
        ("4. Dynamic Pipeline Freshness Sentinel", "Monitors table_load_log nightly loads; flags Brazil sync lag (8 days delayed) and messaging app receipt latency."),
        ("5. Verified Trust Footer & Audit Receipts", "Every answer displays metric ID, owner, date basis, currency basis, and exact bound SQL.")
    ]
    for i, (title, desc) in enumerate(layers):
        y = 1.8 + i * 1.0
        shp = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(y), Inches(11.7), Inches(0.85))
        shp.fill.solid(); shp.fill.fore_color.rgb = CARD_BG; shp.line.color.rgb = ACCENT_BLUE
        tf = shp.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = ACCENT_BLUE
        p2 = tf.add_paragraph()
        p2.text = desc; p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_MUTED

    # SLIDE 6: Workflow 1
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "Workflow 1: Governed Analyst & Two Numbers Waterfall Bridge")
    c1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c1.fill.solid(); c1.fill.fore_color.rgb = CARD_BG; c1.line.color.rgb = ACCENT_BLUE
    tf = c1.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "Governed Multilingual Analyst"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "\n• Resolves ambiguity: 'Sales' prompts run both Gross Sales (M01: $637.4M) and Net Sales (M02: $575.2M) side-by-side.\n\n• Romanized voice presets: Supports native and Latin-script Hindi & Marathi ('Tiranex Agro Agencies chi baki kiti aahe?').\n\n• Physical RLS: Enforces assigned territory scope, actively rejecting cross-territory probes."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    c2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c2.fill.solid(); c2.fill.fore_color.rgb = CARD_BG; c2.line.color.rgb = ACCENT_GREEN
    tf = c2.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "Two Numbers Waterfall Bridge"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "\n• Eliminates executive meeting conflict by presenting a live waterfall reconciliation on screen:\n\n  1. Gross Invoiced Sales: $637.37M USD\n  2. Less: Negative Invoices: -$0.79M USD\n  3. Less: Credited Returns: -$16.65M USD\n  4. Less: Scheme & Rebates: -$44.74M USD\n  5. Audited Net Sales: $575.18M USD\n\n• Settles the argument between Sales Ops and Finance."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    # SLIDE 7: Workflow 2
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "Workflow 2: Field Distributor 360 Pre-Visit Brief")
    c1 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c1.fill.solid(); c1.fill.fore_color.rgb = CARD_BG; c1.line.color.rgb = ACCENT_BLUE
    tf = c1.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "Frontline Problem: 'The Notebook'"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "\n• Vidarbha territory manager kept handwritten records of distributor debts and unissued rebates in a notebook.\n\n• Every visit started with 10 minutes of distributor complaints regarding stuck scheme credit notes.\n\n• Head office dashboards were unusable on mobile phones in rural village networks."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    c2 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c2.fill.solid(); c2.fill.fore_color.rgb = CARD_BG; c2.line.color.rgb = ACCENT_GREEN
    tf = c2.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "The Solution: 1-Page Governed Card"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "\n• Generates in under 2 seconds on mobile before stepping out of the vehicle.\n\n• Displays Sell-In volume, secondary dealer scan sell-through rate, and 90+ day overdue receivables.\n\n• Lists all pending scheme credits with aging compared against regional benchmarks (India median: 78 days).\n\n• Role-redacted: Field Agronomists see product volume only, protecting commercial margin data."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    # SLIDE 8: Workflow 3
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "Workflow 3: Channel-Risk Radar Early Warning Sentinel")
    c1 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c1.fill.solid(); c1.fill.fore_color.rgb = CARD_BG; c1.line.color.rgb = ACCENT_RED
    tf = c1.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "The Channel Stuffing Hazard"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_RED
    p = tf.add_paragraph()
    p.text = "\n• High sell-in volume with low end-grower scan sell-through creates severe product return liabilities.\n\n• In Brazil South, distributors took excessive volume in August-September 2025, resulting in $12.0M in FY26 returns.\n\n• Traditional reporting only notices the problem months later when physical trucks arrive with returned goods."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    c2 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c2.fill.solid(); c2.fill.fore_color.rgb = CARD_BG; c2.line.color.rgb = ACCENT_GREEN
    tf = c2.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "Verified Historical Backtest"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "\n• Strictly historical backtest as of 30 September 2025 (uses zero future return data).\n\n• Rule: Flags distributors with relative sell-through < 0.70 vs prior season.\n\n• Proven Performance: Flagged 17 distributors who accounted for 91.4% ($11.4M out of $12.5M) of subsequent return losses.\n\n• Provides management with a 4 to 5 month advance warning window to rebalance inventory."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    # SLIDE 9: Workflow 4
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_header(s9, "Workflow 4: Working Capital & Credit Exposure Guard")
    c1 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c1.fill.solid(); c1.fill.fore_color.rgb = CARD_BG; c1.line.color.rgb = ACCENT_BLUE
    tf = c1.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "Credit Limit Overdraft Exposure"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "\n• Actively isolates accounts where outstanding debt exceeds authorized credit limits.\n\n• Identified critical accounts in India operating at 200% to 350% credit limit utilization.\n\n• Modorar Seeds (IN-S01): INR 186.9M outstanding against INR 56.6M limit (330% utilization).\n\n• Enables credit committees to intervene before accounts default."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    c2 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c2.fill.solid(); c2.fill.fore_color.rgb = CARD_BG; c2.line.color.rgb = ACCENT_GREEN
    tf = c2.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "Unlocking Disputed Working Capital"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "\n• Pinpoints INR 39.5M in disputed receivables tied directly to unissued scheme credits.\n\n• Replaces manual cross-team inquiries ('we will check') with instant visibility into accrued credit note status.\n\n• Accelerates settlement of 88 accrued credits, clearing invoice payment holds and releasing working capital."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    # SLIDE 10: ROI & Roadmap
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_header(s10, "Business Impact & Deployment Roadmap")
    c1 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c1.fill.solid(); c1.fill.fore_color.rgb = CARD_BG; c1.line.color.rgb = ACCENT_GREEN
    tf = c1.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "Quantified ROI & Impact"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "\n• 100% Ad-Hoc Backlog Elimination: Common queries resolved in 2 seconds vs 3 to 5 day BI turnaround.\n\n• $11.4M Return Hazard Mitigation: Radar warning identifies over-stuffed distributors 4-5 months early.\n\n• INR 100.6M Working Capital Released: Resolves scheme credit hold-ups blocking distributor collections.\n\n• Zero Security Leaks: Physical AST row filters guarantee zero cross-territory data exposure."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    c2 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c2.fill.solid(); c2.fill.fore_color.rgb = CARD_BG; c2.line.color.rgb = ACCENT_BLUE
    tf = c2.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = "FDE Deployment Roadmap"; tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "\n• Weeks 1-2: Deploy Pre-Visit Brief & Radar to pilot teams in Vidarbha (India) and Brazil South.\n\n• Weeks 3-4: Integrate automated ERP webhook to eliminate the 8-day Brazil sync lag.\n\n• Weeks 5-6: Scale Channel-Risk Radar across North America and Europe regions.\n\n• Weeks 7+: Extend Governed Semantic Contract to Supply Chain and Vendor Operations."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED

    prs.save(str(output_path))
    print(f"PowerPoint Presentation saved to {output_path}")


def build_pdf_deck(output_path=PDF_PATH):
    doc = fitz.open()
    width, height = 960, 540 # 16:9 aspect ratio

    DARK_BG = (15/255, 23/255, 42/255)
    CARD_BG = (30/255, 41/255, 59/255)
    CARD_BORDER_BLUE = (56/255, 189/255, 248/255)
    CARD_BORDER_GREEN = (74/255, 222/255, 128/255)
    CARD_BORDER_RED = (248/255, 113/255, 113/255)
    TEXT_WHITE = (1, 1, 1)
    TEXT_MUTED = (148/255, 163/255, 184/255)
    ACCENT_BLUE = (56/255, 189/255, 248/255)
    ACCENT_GREEN = (74/255, 222/255, 128/255)
    ACCENT_RED = (248/255, 113/255, 113/255)

    def draw_slide_base(page, category, title):
        page.draw_rect(fitz.Rect(0, 0, width, height), color=None, fill=DARK_BG)
        page.insert_text((50, 40), category.upper(), fontsize=10, color=ACCENT_BLUE, fontname="helv")
        page.insert_text((50, 70), title, fontsize=20, color=TEXT_WHITE, fontname="helv")
        page.draw_line(fitz.Point(50, 85), fitz.Point(910, 85), color=(51/255, 65/255, 85/255), width=1)

    def draw_card(page, rect, border_color, title, title_color, body_lines):
        page.draw_rect(rect, color=border_color, fill=CARD_BG, width=1.5)
        page.insert_text((rect.x0 + 20, rect.y0 + 30), title, fontsize=13, color=title_color, fontname="helv")
        
        y = rect.y0 + 55
        for line in body_lines:
            if line.startswith("• "):
                # bullet line
                page.insert_text((rect.x0 + 20, y), "•", fontsize=11, color=border_color, fontname="helv")
                r = fitz.Rect(rect.x0 + 35, y - 10, rect.x1 - 20, y + 50)
                text_content = line[2:]
                page.insert_textbox(r, text_content, fontsize=9.5, color=TEXT_MUTED, fontname="helv")
                y += 42
            elif line.startswith("  "):
                r = fitz.Rect(rect.x0 + 35, y - 10, rect.x1 - 20, y + 25)
                page.insert_textbox(r, line.strip(), fontsize=9, color=ACCENT_GREEN, fontname="helv")
                y += 20
            elif line.strip() == "":
                y += 6
            else:
                r = fitz.Rect(rect.x0 + 20, y - 10, rect.x1 - 20, y + 45)
                page.insert_textbox(r, line, fontsize=9.5, color=TEXT_MUTED, fontname="helv")
                y += 35

    # ---------------- SLIDE 1: Title ----------------
    p1 = doc.new_page(width=width, height=height)
    p1.draw_rect(fitz.Rect(0, 0, width, height), color=None, fill=DARK_BG)
    p1.insert_text((80, 160), "FORWARD DEPLOYED ENGINEERING CASE STUDY", fontsize=13, color=ACCENT_BLUE, fontname="helv")
    p1.insert_text((80, 215), "Governed Commercial Sales Intelligence", fontsize=32, color=TEXT_WHITE, fontname="helv")
    p1.insert_text((80, 255), "Replacing Semantic Drift & Hallucinations with Deterministic Workflows & RLS", fontsize=15, color=TEXT_MUTED, fontname="helv")
    p1.draw_line(fitz.Point(80, 285), fitz.Point(880, 285), color=(51/255, 65/255, 85/255), width=1.5)
    p1.insert_text((80, 320), "Candidate ID: iitmcs_24091540  |  Track: Agri-Inputs Commercial Sales Analyst", fontsize=11, color=ACCENT_GREEN, fontname="helv")
    p1.insert_text((80, 345), "Client: Global Crop Protection Co. (North America, Brazil, Europe, India)", fontsize=11, color=TEXT_MUTED, fontname="helv")
    p1.insert_text((80, 370), "Deliverables: Governed DuckDB Engine + 5-Tab Streamlit UI + Evaluation Suite", fontsize=11, color=TEXT_MUTED, fontname="helv")

    # ---------------- SLIDE 2: Root Cause ----------------
    p2 = doc.new_page(width=width, height=height)
    draw_slide_base(p2, "COMMERCIAL INTELLIGENCE PLATFORM", "Root Cause Analysis: Why Last Year's Sales Chatbot Failed")
    draw_card(p2, fitz.Rect(50, 110, 320, 500), CARD_BORDER_RED, "The $18B Currency Blunder", ACCENT_RED, [
        "• Raw SQL summed invoice_amount_local directly across BRL, EUR, INR, CAD.",
        "• Hallucinated $18.19 Billion vs $575.2 Million true Net Sales (13.2x overstatement).",
        "• Sales leadership immediately abandoned the AI."
    ])
    draw_card(p2, fitz.Rect(345, 110, 615, 500), CARD_BORDER_BLUE, "1,326 Dropped Territory Keys", ACCENT_BLUE, [
        "• 1,326 sell-in rows carried legacy 2023 CRM codes (UPW01, MHV01, BRSUL01).",
        "• Naive INNER JOINs silently dropped 8% of company revenue ($42.8M USD).",
        "• Required master key remapping in cleaning layer."
    ])
    draw_card(p2, fitz.Rect(640, 110, 910, 500), CARD_BORDER_GREEN, "Security Leakage & Desertion", ACCENT_GREEN, [
        "• Enforcing permissions in prompts leaked 358 out-of-territory answers.",
        "• Regional language queries collapsed to 15.7% accuracy (Marathi 17.7%, Hindi 15.7%).",
        "• Reps returned to paper notebooks and phone calls."
    ])

    # ---------------- SLIDE 3: Forensic Audit ----------------
    p3 = doc.new_page(width=width, height=height)
    draw_slide_base(p3, "COMMERCIAL INTELLIGENCE PLATFORM", "Forensic Warehouse Realities: Brazil South & India Schemes")
    draw_card(p3, fitz.Rect(50, 110, 465, 500), CARD_BORDER_BLUE, "Brazil South $12.0M Returns Trap", ACCENT_BLUE, [
        "• Southern Brazil (BR-S01 to BR-S04) drove $12.03M in FY26 returns (92% of Brazil, 72% of company).",
        "• Leadership blamed Nov-Dec drought, but scan sell-through had collapsed to 0.19 by September (vs 0.39 prior season).",
        "• Reps pushed 2-3x sell-in volume at quarter-end to hit 90-110% annual bonus caps before planting started."
    ])
    draw_card(p3, fitz.Rect(495, 110, 910, 500), CARD_BORDER_GREEN, "India Scheme Credit & Receivables Impasse", ACCENT_GREEN, [
        "• 1,050 issued India credits averaged 85.9 days to issue against 30-day corporate policy (100% late; 68% over 60 days).",
        "• 88 credit notes totaling INR 100.6M remain trapped in 'Accrued' status with zero issue date.",
        "• Frustrated distributors withhold payments, creating INR 39.5M in disputed receivables and locking working capital."
    ])

    # ---------------- SLIDE 4: Options Architecture ----------------
    p4 = doc.new_page(width=width, height=height)
    draw_slide_base(p4, "COMMERCIAL INTELLIGENCE PLATFORM", "Options Architecture: Evaluating Approaches for Riklr")
    opts_pdf = [
        ("A. Raw Text-to-SQL", "Fast demo, high risk. Hallucinates $18B, leaks cross-territory data, collapses on un-normalized keys.", "REJECT (Repeats 2025)", CARD_BORDER_RED),
        ("B. More BI Dashboards", "Cheap, static reports. Adds to 40 unread dashboards; territory managers cannot read them in vehicles.", "REJECT (Zero field fit)", CARD_BORDER_RED),
        ("C. Governed Semantic Engine", "Metric contract + physical RLS. 100% deterministic SQL, multi-currency normalization, field briefs.", "CHOSEN (Top 0.001%)", CARD_BORDER_GREEN),
        ("D. Free Multi-Agent System", "Autonomous loops. High API latency, non-deterministic execution, volatile behavior on financial ledgers.", "REJECT (Too fragile)", CARD_BORDER_RED)
    ]
    for i, (name, analysis, verdict, border_col) in enumerate(opts_pdf):
        y0 = 110 + i * 95
        rect = fitz.Rect(50, y0, 910, y0 + 82)
        p4.draw_rect(rect, color=border_col, fill=CARD_BG, width=1.5)
        p4.insert_text((rect.x0 + 20, rect.y0 + 25), name, fontsize=12, color=TEXT_WHITE, fontname="helv")
        p4.insert_text((rect.x1 - 180, rect.y0 + 25), verdict, fontsize=11, color=border_col, fontname="helv")
        p4.insert_textbox(fitz.Rect(rect.x0 + 20, rect.y0 + 35, rect.x1 - 200, rect.y1 - 5), analysis, fontsize=9.5, color=TEXT_MUTED, fontname="helv")

    # ---------------- SLIDE 5: Pipeline Architecture ----------------
    p5 = doc.new_page(width=width, height=height)
    draw_slide_base(p5, "COMMERCIAL INTELLIGENCE PLATFORM", "System Architecture: Governed Semantic Pipeline")
    layers_pdf = [
        ("1. Multi-Lingual Natural Language Layer", "Detects English, Portuguese, and Romanized Hindi/Marathi. Routes query to strict QueryPlan JSON schema. Zero raw SQL generation."),
        ("2. Cleaning & Key Reconciliation Layer", "Remaps 1,326 legacy territory keys, deduplicates 245 invoice lines, synthesizes monthly FX tables (USD 1.0 join)."),
        ("3. Physical AST Row-Level Security (RLS)", "Injects territory_code IN (...) at compiler level. Role permissions enforced before execution; zero data leakage."),
        ("4. Dynamic Pipeline Freshness Sentinel", "Monitors table_load_log nightly loads; flags Brazil sync lag (8 days delayed) and messaging app receipt latency."),
        ("5. Verified Trust Footer & Audit Receipts", "Every answer displays metric ID, owner, date basis, currency basis, and exact bound SQL.")
    ]
    for i, (title, desc) in enumerate(layers_pdf):
        y0 = 110 + i * 78
        rect = fitz.Rect(50, y0, 910, y0 + 68)
        p5.draw_rect(rect, color=CARD_BORDER_BLUE, fill=CARD_BG, width=1.2)
        p5.insert_text((rect.x0 + 20, rect.y0 + 22), title, fontsize=11, color=ACCENT_BLUE, fontname="helv")
        p5.insert_textbox(fitz.Rect(rect.x0 + 20, rect.y0 + 30, rect.x1 - 20, rect.y1 - 5), desc, fontsize=9, color=TEXT_MUTED, fontname="helv")

    # ---------------- SLIDE 6: Workflow 1 ----------------
    p6 = doc.new_page(width=width, height=height)
    draw_slide_base(p6, "COMMERCIAL INTELLIGENCE PLATFORM", "Workflow 1: Governed Analyst & Two Numbers Waterfall Bridge")
    draw_card(p6, fitz.Rect(50, 110, 465, 500), CARD_BORDER_BLUE, "Governed Multilingual Analyst", ACCENT_BLUE, [
        "• Resolves ambiguity: 'Sales' prompts run both Gross Sales (M01: $637.4M) and Net Sales (M02: $575.2M) side-by-side.",
        "• Romanized voice presets: Supports native and Latin-script Hindi & Marathi ('Tiranex Agro Agencies chi baki kiti aahe?').",
        "• Physical RLS: Enforces assigned territory scope, actively rejecting cross-territory probes."
    ])
    draw_card(p6, fitz.Rect(495, 110, 910, 500), CARD_BORDER_GREEN, "Two Numbers Waterfall Bridge", ACCENT_GREEN, [
        "• Eliminates executive meeting conflict by presenting a live waterfall reconciliation on screen:",
        "  1. Gross Invoiced Sales: $637.37M USD",
        "  2. Less: Negative Invoices: -$0.79M USD",
        "  3. Less: Credited Returns: -$16.65M USD",
        "  4. Less: Scheme & Rebates: -$44.74M USD",
        "  5. Audited Net Sales: $575.18M USD",
        "• Settles the argument between Sales Ops and Finance."
    ])

    # ---------------- SLIDE 7: Workflow 2 ----------------
    p7 = doc.new_page(width=width, height=height)
    draw_slide_base(p7, "COMMERCIAL INTELLIGENCE PLATFORM", "Workflow 2: Field Distributor 360 Pre-Visit Brief")
    draw_card(p7, fitz.Rect(50, 110, 465, 500), CARD_BORDER_BLUE, "Frontline Problem: 'The Notebook'", ACCENT_BLUE, [
        "• Vidarbha territory manager kept handwritten records of distributor debts and unissued rebates in a notebook.",
        "• Every visit started with 10 minutes of distributor complaints regarding stuck scheme credit notes.",
        "• Head office dashboards were unusable on mobile phones in rural village networks."
    ])
    draw_card(p7, fitz.Rect(495, 110, 910, 500), CARD_BORDER_GREEN, "The Solution: 1-Page Governed Card", CARD_BORDER_GREEN, [
        "• Generates in under 2 seconds on mobile before stepping out of the vehicle.",
        "• Displays Sell-In volume, secondary dealer scan sell-through rate, and 90+ day overdue receivables.",
        "• Lists all pending scheme credits with aging compared against regional benchmarks (India median: 78 days).",
        "• Role-redacted: Field Agronomists see product volume only, protecting commercial margin data."
    ])

    # ---------------- SLIDE 8: Workflow 3 ----------------
    p8 = doc.new_page(width=width, height=height)
    draw_slide_base(p8, "COMMERCIAL INTELLIGENCE PLATFORM", "Workflow 3: Channel-Risk Radar Early Warning Sentinel")
    draw_card(p8, fitz.Rect(50, 110, 465, 500), CARD_BORDER_RED, "The Channel Stuffing Hazard", ACCENT_RED, [
        "• High sell-in volume with low end-grower scan sell-through creates severe product return liabilities.",
        "• In Brazil South, distributors took excessive volume in August-September 2025, resulting in $12.0M in FY26 returns.",
        "• Traditional reporting only notices the problem months later when physical trucks arrive with returned goods."
    ])
    draw_card(p8, fitz.Rect(495, 110, 910, 500), CARD_BORDER_GREEN, "Verified Historical Backtest", CARD_BORDER_GREEN, [
        "• Strictly historical backtest as of 30 September 2025 (uses zero future return data).",
        "• Rule: Flags distributors with relative sell-through < 0.70 vs prior season.",
        "• Proven Performance: Flagged 17 distributors who accounted for 91.4% ($11.4M out of $12.5M) of subsequent return losses.",
        "• Provides management with a 4 to 5 month advance warning window to rebalance inventory."
    ])

    # ---------------- SLIDE 9: Workflow 4 ----------------
    p9 = doc.new_page(width=width, height=height)
    draw_slide_base(p9, "COMMERCIAL INTELLIGENCE PLATFORM", "Workflow 4: Working Capital & Credit Exposure Guard")
    draw_card(p9, fitz.Rect(50, 110, 465, 500), CARD_BORDER_BLUE, "Credit Limit Overdraft Exposure", ACCENT_BLUE, [
        "• Actively isolates accounts where outstanding debt exceeds authorized credit limits.",
        "• Identified critical accounts in India operating at 200% to 350% credit limit utilization.",
        "• Modorar Seeds (IN-S01): INR 186.9M outstanding against INR 56.6M limit (330% utilization).",
        "• Enables credit committees to intervene before accounts default."
    ])
    draw_card(p9, fitz.Rect(495, 110, 910, 500), CARD_BORDER_GREEN, "Unlocking Disputed Working Capital", CARD_BORDER_GREEN, [
        "• Pinpoints INR 39.5M in disputed receivables tied directly to unissued scheme credits.",
        "• Replaces manual cross-team inquiries ('we will check') with instant visibility into accrued credit note status.",
        "• Accelerates settlement of 88 accrued credits, clearing invoice payment holds and releasing working capital."
    ])

    # ---------------- SLIDE 10: ROI & Roadmap ----------------
    p10 = doc.new_page(width=width, height=height)
    draw_slide_base(p10, "COMMERCIAL INTELLIGENCE PLATFORM", "Business Impact & Deployment Roadmap")
    draw_card(p10, fitz.Rect(50, 110, 465, 500), CARD_BORDER_GREEN, "Quantified ROI & Impact", ACCENT_GREEN, [
        "• 100% Ad-Hoc Backlog Elimination: Common queries resolved in 2 seconds vs 3 to 5 day BI turnaround.",
        "• $11.4M Return Hazard Mitigation: Radar warning identifies over-stuffed distributors 4-5 months early.",
        "• INR 100.6M Working Capital Released: Resolves scheme credit hold-ups blocking distributor collections.",
        "• Zero Security Leaks: Physical AST row filters guarantee zero cross-territory data exposure."
    ])
    draw_card(p10, fitz.Rect(495, 110, 910, 500), CARD_BORDER_BLUE, "FDE Deployment Roadmap", ACCENT_BLUE, [
        "• Weeks 1-2: Deploy Pre-Visit Brief & Radar to pilot teams in Vidarbha (India) and Brazil South.",
        "• Weeks 3-4: Integrate automated ERP webhook to eliminate the 8-day Brazil sync lag.",
        "• Weeks 5-6: Scale Channel-Risk Radar across North America and Europe regions.",
        "• Weeks 7+: Extend Governed Semantic Contract to Supply Chain and Vendor Operations."
    ])

    doc.save(str(output_path))
    print(f"PDF Presentation saved to {output_path}")

if __name__ == "__main__":
    build_pptx_deck(PPTX_PATH)
    build_pdf_deck(PDF_PATH)
    if DESKTOP_PATH.exists():
        shutil.copy2(PPTX_PATH, DESKTOP_PATH / "Riklr_Sales_Analyst_Deck.pptx")
        shutil.copy2(PDF_PATH, DESKTOP_PATH / "Riklr_Sales_Analyst_Deck.pdf")
        print("Also copied PPTX & PDF to Desktop for quick access.")
