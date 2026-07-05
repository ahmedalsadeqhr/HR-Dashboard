"""
51Talk Egypt Employee Handbook — Bilingual PDF Generator
Generates a professional bilingual (English + Arabic) PDF from handbook content.
"""

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
import os
import urllib.request

# ---------------------------------------------------------------------------
# Font Setup — Download a free Arabic-supporting font if not present
# ---------------------------------------------------------------------------
ARABIC_FONT_PATH = "C:/Windows/Fonts/trado.ttf"
ARABIC_BOLD_FONT_PATH = "C:/Windows/Fonts/tradbdo.ttf"

pdfmetrics.registerFont(TTFont("Amiri", ARABIC_FONT_PATH))
pdfmetrics.registerFont(TTFont("Amiri-Bold", ARABIC_BOLD_FONT_PATH))

# ---------------------------------------------------------------------------
# Arabic text helper
# ---------------------------------------------------------------------------
def ar(text):
    """Reshape and apply BiDi to Arabic text for correct rendering."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = A4
BRAND_BLUE = colors.HexColor("#1a3c6e")
BRAND_GOLD = colors.HexColor("#c9a84c")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
MID_GRAY = colors.HexColor("#cccccc")

styles = getSampleStyleSheet()

EN_TITLE = ParagraphStyle("en_title", fontName="Helvetica-Bold", fontSize=22,
                           textColor=BRAND_BLUE, leading=28, alignment=TA_CENTER)
EN_SECTION = ParagraphStyle("en_section", fontName="Helvetica-Bold", fontSize=13,
                              textColor=BRAND_BLUE, leading=18, spaceAfter=4)
EN_BODY = ParagraphStyle("en_body", fontName="Helvetica", fontSize=10,
                          leading=15, spaceAfter=4)
EN_BULLET = ParagraphStyle("en_bullet", fontName="Helvetica", fontSize=10,
                            leading=14, leftIndent=14, spaceAfter=2,
                            bulletIndent=6)
EN_SMALL = ParagraphStyle("en_small", fontName="Helvetica-Oblique", fontSize=9,
                           textColor=colors.grey, leading=13)

AR_TITLE = ParagraphStyle("ar_title", fontName="Amiri-Bold", fontSize=22,
                           textColor=BRAND_BLUE, leading=32, alignment=TA_CENTER)
AR_SECTION = ParagraphStyle("ar_section", fontName="Amiri-Bold", fontSize=13,
                              textColor=BRAND_BLUE, leading=20, spaceAfter=4,
                              alignment=TA_RIGHT)
AR_BODY = ParagraphStyle("ar_body", fontName="Amiri", fontSize=11,
                          leading=18, spaceAfter=4, alignment=TA_RIGHT)
AR_BULLET = ParagraphStyle("ar_bullet", fontName="Amiri", fontSize=11,
                            leading=17, rightIndent=14, spaceAfter=2,
                            alignment=TA_RIGHT)

# ---------------------------------------------------------------------------
# Handbook content
# ---------------------------------------------------------------------------
SECTIONS = [
    {
        "en_title": "1. Welcome & Introduction",
        "ar_title": "١. مرحباً بك",
        "en_body": (
            "This handbook is your comprehensive reference for company policies, "
            "benefits, and employment standards at 51Talk Egypt. It forms an integral "
            "part of your employment relationship and supplements your individual contract. "
            "We are committed to providing a safe, respectful, and inclusive workplace for everyone."
        ),
        "ar_body": (
            "يُعدّ هذا الدليل مرجعك الشامل لسياسات الشركة والمزايا ومعايير التوظيف في 51Talk Egypt. "
            "وهو جزء لا يتجزأ من علاقة العمل ويكمّل عقدك الفردي. "
            "نحن ملتزمون بتوفير بيئة عمل آمنة ومحترِمة وشاملة للجميع."
        ),
    },
    {
        "en_title": "2. Company Identity & Core Values",
        "ar_title": "٢. هوية الشركة والقيم الأساسية",
        "en_body": None,
        "ar_body": None,
        "table_en": [
            ["Element", "Detail"],
            ["Vision", "To be recognized as a highly respectable online education platform for centuries."],
            ["Mission", "To enable every student to speak up, stand out, and succeed in life."],
            ["Customer Focus", "Fulfilling duties and responding swiftly to customer needs."],
            ["Game Changer", "Proactively adapting, driving initiatives, and learning through change."],
            ["Passion", "Taking responsibility, striving for higher goals, facing difficulties head-on."],
            ["Team Work", "Fostering mutual trust, open communication, and cross-cultural integration."],
        ],
        "table_ar": [
            [ar("العنصر"), ar("التفاصيل")],
            [ar("الرؤية"), ar("أن نكون منصة تعليم إلكتروني موقّرة على مدى قرون.")],
            [ar("الرسالة"), ar("تمكين كل طالب من التحدث والتميز والنجاح في الحياة.")],
            [ar("التركيز على العميل"), ar("أداء الواجبات والاستجابة السريعة لاحتياجات العملاء.")],
            [ar("صانع التغيير"), ar("التكيف الاستباقي وقيادة المبادرات والتعلم من التغيير.")],
            [ar("الشغف"), ar("تحمّل المسؤولية والسعي نحو أهداف أعلى ومواجهة الصعوبات.")],
            [ar("العمل الجماعي"), ar("تعزيز الثقة المتبادلة والتواصل المفتوح والتكامل الثقافي.")],
        ],
    },
    {
        "en_title": "3. Work Schedule & Attendance",
        "ar_title": "٣. جدول العمل والحضور",
        "en_body": (
            "Official Working Week: Six days (Saturday–Thursday)\n"
            "• Sunday–Thursday: 12:00 PM – 9:00 PM\n"
            "• Saturday: 12:00 PM – 4:00 PM\n"
            "Break Times (Sun–Thu): 2:45–3:00 PM and 5:00–6:00 PM\n"
            "Break Time (Sat): 1:45–2:00 PM\n\n"
            "Attendance is recorded via fingerprint system. Missing daily records "
            "without approved leave count as unauthorized absence."
        ),
        "ar_body": (
            "أسبوع العمل الرسمي: ستة أيام (السبت–الخميس)\n"
            "• الأحد–الخميس: من الساعة 12:00 ظهراً حتى 9:00 مساءً\n"
            "• السبت: من 12:00 ظهراً حتى 4:00 مساءً\n"
            "فترات الراحة (الأحد–الخميس): 2:45–3:00 مساءً و5:00–6:00 مساءً\n"
            "فترة الراحة (السبت): 1:45–2:00 مساءً\n\n"
            "يُسجَّل الحضور عبر نظام بصمة الأصابع. يُعدّ الغياب دون إجازة معتمدة "
            "غياباً غير مبرر."
        ),
    },
    {
        "en_title": "4. Leave Policies",
        "ar_title": "٤. سياسات الإجازات",
        "en_body": None,
        "ar_body": None,
        "table_en": [
            ["Leave Type", "Entitlement", "Pay", "Key Conditions"],
            ["Annual Leave", "15 days (<1yr) / 21 days (≥1yr)", "Full", "Must be used within same year"],
            ["Casual Leave", "7 days/year (max 2 days/request)", "Full", "Counts toward annual leave"],
            ["Sick Leave", "As needed", "75%", "Stamped medical certificate required"],
            ["Maternity Leave", "120 days", "Full", "After 1 year of service; birth certificate required"],
            ["Paternity Leave", "1 day/occurrence (max 3×/year)", "Full", "Proof required"],
            ["Marriage Leave", "3 days", "Full", "Extra days from annual balance or unpaid"],
            ["Bereavement Leave", "3 days", "Full", "Parents, spouse, children only; proof required"],
            ["Unpaid Leave", "As approved", "0%", "Manager + HR approval required"],
        ],
        "table_ar": [
            [ar("نوع الإجازة"), ar("الاستحقاق"), ar("الأجر"), ar("الشروط الأساسية")],
            [ar("الإجازة السنوية"), ar("15 يوم (<سنة) / 21 يوم (≥سنة)"), ar("كامل"), ar("تُستخدم خلال نفس العام")],
            [ar("إجازة عارضة"), ar("7 أيام/سنة (2 أيام كحد أقصى/طلب)"), ar("كامل"), ar("تُحسب ضمن الإجازة السنوية")],
            [ar("إجازة مرضية"), ar("حسب الحاجة"), ar("75%"), ar("يلزم تقرير طبي مختوم")],
            [ar("إجازة أمومة"), ar("120 يوم"), ar("كامل"), ar("بعد سنة خدمة كاملة؛ يلزم شهادة الميلاد")],
            [ar("إجازة أبوة"), ar("يوم/حادثة (3 مرات كحد أقصى/سنة)"), ar("كامل"), ar("يلزم إثبات")],
            [ar("إجازة زواج"), ar("3 أيام"), ar("كامل"), ar("الأيام الإضافية من الرصيد السنوي أو بدون أجر")],
            [ar("إجازة وفاة"), ar("3 أيام"), ar("كامل"), ar("للوالدين والزوج/الزوجة والأبناء فقط")],
            [ar("إجازة بدون أجر"), ar("حسب الموافقة"), ar("0%"), ar("تتطلب موافقة المدير والـ HR")],
        ],
    },
    {
        "en_title": "5. Attendance Violations & Penalties",
        "ar_title": "٥. مخالفات الحضور والعقوبات",
        "en_body": None,
        "ar_body": None,
        "table_en": [
            ["Violation", "Penalty"],
            ["Late arrival — 1st time", "100 EGP deduction"],
            ["Late arrival — 2nd time", "200 EGP deduction"],
            ["Late arrival — 3rd time", "500 EGP deduction"],
            ["Late arrival — 4th time+", "500 EGP + Warning letter"],
            ["Missing punch (3 occurrences)", "Half-day salary deduction"],
            ["Missing punch (6 occurrences)", "Warning letter"],
            ["Early departure (no approval)", "Half-day salary deduction"],
            ["Unapproved absence", "Two-day salary deduction + Warning letter"],
        ],
        "table_ar": [
            [ar("المخالفة"), ar("العقوبة")],
            [ar("التأخر — المرة الأولى"), ar("خصم 100 جنيه")],
            [ar("التأخر — المرة الثانية"), ar("خصم 200 جنيه")],
            [ar("التأخر — المرة الثالثة"), ar("خصم 500 جنيه")],
            [ar("التأخر — المرة الرابعة فأكثر"), ar("خصم 500 جنيه + إنذار")],
            [ar("نسيان البصمة (3 مرات)"), ar("خصم نصف يوم")],
            [ar("نسيان البصمة (6 مرات)"), ar("إنذار رسمي")],
            [ar("المغادرة المبكرة بدون إذن"), ar("خصم نصف يوم")],
            [ar("الغياب بدون إذن"), ar("خصم يومين + إنذار رسمي")],
        ],
    },
    {
        "en_title": "6. Workplace Conduct Standards",
        "ar_title": "٦. معايير السلوك في بيئة العمل",
        "en_body": (
            "All employees are expected to:\n"
            "• Communicate respectfully — no insults or demeaning language\n"
            "• Protect confidential company and student information\n"
            "• Disclose any conflicts of interest\n"
            "• Follow health, safety, and security procedures\n"
            "• Report misconduct through available channels\n\n"
            "Strictly Prohibited:\n"
            "• Harassment or discrimination based on race, religion, gender, age, or disability\n"
            "• Smoking indoors or in vehicles (designated outdoor areas only)\n"
            "• Possession or consumption of drugs or alcohol during work hours\n"
            "• Fraud, falsification of documents, theft, or embezzlement\n"
            "• Physical violence, threats, or intimidation\n"
            "• Unauthorized sharing of confidential data or credentials"
        ),
        "ar_body": (
            "يُتوقع من جميع الموظفين:\n"
            "• التواصل باحترام — لا إهانات ولا لغة مسيئة\n"
            "• حماية المعلومات السرية للشركة والطلاب\n"
            "• الإفصاح عن أي تضارب في المصالح\n"
            "• اتباع إجراءات الصحة والسلامة والأمن\n"
            "• الإبلاغ عن المخالفات عبر القنوات المتاحة\n\n"
            "محظور تماماً:\n"
            "• التحرش أو التمييز على أساس العرق أو الدين أو الجنس أو السن أو الإعاقة\n"
            "• التدخين داخل المبنى أو في السيارات (في الأماكن المخصصة خارجياً فقط)\n"
            "• حيازة أو تناول المخدرات أو الكحول أثناء ساعات العمل\n"
            "• الاحتيال أو تزوير المستندات أو السرقة أو الاختلاس\n"
            "• العنف الجسدي أو التهديد أو التخويف\n"
            "• مشاركة البيانات السرية أو بيانات الدخول بدون تصريح"
        ),
    },
    {
        "en_title": "7. Professional Dress Code",
        "ar_title": "٧. قواعد اللباس المهني",
        "en_body": (
            "Standard: Business casual, clean, neat, and professional.\n\n"
            "Acceptable:\n"
            "• Collared shirts, blouses, polo shirts\n"
            "• Slacks, modest dresses or skirts\n"
            "• Closed-toe shoes\n\n"
            "Not Acceptable:\n"
            "• Short skirts or shorts\n"
            "• Off-shoulder tops, crop tops, exposed midriff or cleavage\n"
            "• Clothing with offensive slogans or ripped/torn items\n\n"
            "Clothing should provide appropriate coverage from neck to knees. "
            "Cultural and religious dress is respected and accommodated."
        ),
        "ar_body": (
            "المعيار: كاجوال رسمي، نظيف وأنيق ومهني.\n\n"
            "مقبول:\n"
            "• القمصان ذات الياقة، البلوزات، قمصان البولو\n"
            "• البناطيل، الفساتين المحتشمة أو التنانير\n"
            "• الأحذية المغلقة\n\n"
            "غير مقبول:\n"
            "• التنانير القصيرة أو الشورت\n"
            "• الملابس الكاشفة للكتفين أو المعدة أو منطقة الصدر\n"
            "• الملابس ذات الشعارات المسيئة أو الممزقة\n\n"
            "يجب أن تغطي الملابس المناطق من الرقبة إلى الركبة. "
            "يُحترم اللباس الثقافي والديني ويُؤخذ بعين الاعتبار."
        ),
    },
    {
        "en_title": "8. Probation & Employment Structure",
        "ar_title": "٨. فترة الاختبار وهيكل التوظيف",
        "en_body": (
            "Probationary Period: 3 months with monthly KPI evaluations.\n"
            "• A low rating in any month deems probation unsuccessful\n"
            "• Termination during probation carries no severance compensation\n\n"
            "Resignation:\n"
            "• 30-day notice period required\n"
            "• Submit resignation email to Team Leader, CC hr.egy@51talk.com\n"
            "• Early departure without department head approval results in withheld salary\n\n"
            "Off-Boarding Process:\n"
            "1. Submit resignation email\n"
            "2. Obtain Chinese Manager approval (if required)\n"
            "3. HR confirms internal clearance and vendor off-boarding\n"
            "4. Complete exit meeting on final day\n"
            "5. Return all company assets to Admin/IT\n"
            "6. Vendor & labor office finalization within 2–5 working days\n"
            "7. Final salary processed in next cycle after clearance"
        ),
        "ar_body": (
            "فترة الاختبار: 3 أشهر مع تقييمات KPI شهرية.\n"
            "• أي تقييم منخفض في أي شهر يعني فشل فترة الاختبار\n"
            "• الإنهاء خلال فترة الاختبار لا يستحق تعويضاً\n\n"
            "الاستقالة:\n"
            "• مطلوب إشعار 30 يوماً مسبقاً\n"
            "• تقديم بريد إلكتروني للاستقالة للمدير المباشر مع نسخة لـ hr.egy@51talk.com\n"
            "• المغادرة المبكرة بدون موافقة رئيس القسم تؤدي لحجب الراتب\n\n"
            "إجراءات إنهاء الخدمة:\n"
            "١. تقديم بريد الاستقالة\n"
            "٢. الحصول على موافقة المدير الصيني (إن لزم)\n"
            "٣. تأكيد HR للإخلاء الداخلي وإنهاء تعاقد المورّد\n"
            "٤. إجراء مقابلة الخروج في اليوم الأخير\n"
            "٥. إعادة جميع أصول الشركة للإدارة/IT\n"
            "٦. استكمال إجراءات المورّد ومكتب العمل خلال 2–5 أيام عمل\n"
            "٧. صرف الراتب الأخير في الدورة التالية بعد إتمام الإخلاء"
        ),
    },
    {
        "en_title": "9. Compensation & Benefits",
        "ar_title": "٩. التعويضات والمزايا",
        "en_body": (
            "Payment Schedule:\n"
            "• Basic salary: paid on the 30th of each month\n"
            "• Commission: paid on the 20th of each month\n"
            "• Attendance variables calculated: 21st of previous month to 20th of current month\n\n"
            "Insurance:\n"
            "• Social Insurance: shared contribution between company and employee\n"
            "• Medical Insurance: company-provided; effective same month if hired by the 20th, "
            "following month if hired after the 20th\n\n"
            "KPI System:\n"
            "Performance targets tied to both salary and commission components. "
            "Errors in payment are corrected and paid in the next cycle."
        ),
        "ar_body": (
            "جدول الدفع:\n"
            "• الراتب الأساسي: يُصرف في الـ 30 من كل شهر\n"
            "• العمولة: تُصرف في الـ 20 من كل شهر\n"
            "• متغيرات الحضور تُحسب من الـ 21 من الشهر السابق حتى الـ 20 من الشهر الحالي\n\n"
            "التأمينات:\n"
            "• التأمينات الاجتماعية: اشتراك مشترك بين الشركة والموظف\n"
            "• التأمين الطبي: تتحمله الشركة؛ يسري من نفس الشهر إذا كان الالتحاق قبل الـ 20، "
            "ومن الشهر التالي إذا كان بعد الـ 20\n\n"
            "نظام KPI:\n"
            "أهداف أداء مرتبطة بمكونات الراتب والعمولة. "
            "تُصحَّح أخطاء الدفع وتُسوَّى في الدورة التالية."
        ),
    },
    {
        "en_title": "10. Communication & Escalation",
        "ar_title": "١٠. التواصل والتصعيد",
        "en_body": (
            "Escalation Matrix:\n"
            "1. Direct Manager — day-to-day concerns, performance issues, early-stage conflicts\n"
            "2. Director / 2nd Manager — repeated or severe issues\n"
            "3. HR (hr.egy@51talk.com) — workplace conduct, grievances, harassment, discrimination, "
            "policy clarification\n\n"
            "Confidentiality: The company makes reasonable efforts to protect reporter confidentiality.\n"
            "Non-Retaliation: Retaliation against anyone who reports a concern is strictly prohibited."
        ),
        "ar_body": (
            "مصفوفة التصعيد:\n"
            "١. المدير المباشر — المخاوف اليومية ومشكلات الأداء والنزاعات الأولية\n"
            "٢. المدير / المستوى الثاني — المشكلات المتكررة أو الجسيمة\n"
            "٣. HR (hr.egy@51talk.com) — سلوك مكان العمل والشكاوى والتحرش والتمييز وتوضيح السياسات\n\n"
            "السرية: تبذل الشركة جهوداً معقولة لحماية سرية هوية المُبلِّغ.\n"
            "عدم الانتقام: يُحظر تماماً اتخاذ أي إجراء انتقامي ضد أي شخص يُبلّغ عن مخاوفه."
        ),
    },
]

# ---------------------------------------------------------------------------
# Table helper
# ---------------------------------------------------------------------------
def make_table(data, col_widths=None, rtl=False):
    if col_widths is None:
        n = len(data[0])
        col_widths = [(PAGE_W - 4 * cm) / n] * n

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Amiri-Bold" if rtl else "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 1), (-1, -1), "Amiri" if rtl else "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT" if rtl else "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("WORDWRAP", (0, 0), (-1, -1), True),
    ]

    cell_data = []
    for row in data:
        cell_row = []
        for cell in row:
            if rtl:
                cell_row.append(Paragraph(str(cell), AR_BODY))
            else:
                cell_row.append(Paragraph(str(cell), EN_BODY))
        cell_data.append(cell_row)

    t = Table(cell_data, colWidths=col_widths)
    t.setStyle(TableStyle(style_cmds))
    return t


def multiline_para(text, style):
    """Convert \n in text to <br/> for Paragraph."""
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = escaped.replace("\n", "<br/>")
    return Paragraph(html, style)


# ---------------------------------------------------------------------------
# Build PDF
# ---------------------------------------------------------------------------
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "docs", "51Talk-Egypt-Employee-Handbook-Bilingual.pdf")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    rightMargin=2 * cm,
    leftMargin=2 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
)

story = []

# ---- Cover Page ----
story.append(Spacer(1, 3 * cm))
story.append(Paragraph("51Talk Egypt", EN_TITLE))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("Employee Handbook", EN_TITLE))
story.append(Spacer(1, 0.3 * cm))
story.append(HRFlowable(width="80%", thickness=2, color=BRAND_GOLD, hAlign="CENTER"))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph(ar("دليل الموظف"), AR_TITLE))
story.append(Paragraph(ar("51Talk Egypt"), AR_TITLE))
story.append(Spacer(1, 1.5 * cm))
story.append(Paragraph("Bilingual Edition — English & Arabic", ParagraphStyle(
    "cover_sub", fontName="Helvetica-Oblique", fontSize=12, textColor=colors.grey,
    alignment=TA_CENTER)))
story.append(Paragraph(ar("نسخة ثنائية اللغة — الإنجليزية والعربية"), ParagraphStyle(
    "cover_sub_ar", fontName="Amiri", fontSize=12, textColor=colors.grey,
    alignment=TA_CENTER, leading=20)))
story.append(Spacer(1, 0.5 * cm))
story.append(Paragraph("2026", ParagraphStyle(
    "cover_year", fontName="Helvetica-Bold", fontSize=14, textColor=BRAND_BLUE,
    alignment=TA_CENTER)))
story.append(Spacer(1, 1 * cm))
story.append(Paragraph("HR Contact: hr.egy@51talk.com", EN_SMALL))
story.append(PageBreak())

# ---- Sections ----
for sec in SECTIONS:
    block = []

    # English side
    block.append(Paragraph(sec["en_title"], EN_SECTION))
    block.append(HRFlowable(width="100%", thickness=1, color=BRAND_GOLD))
    block.append(Spacer(1, 0.2 * cm))

    if sec.get("en_body"):
        block.append(multiline_para(sec["en_body"], EN_BODY))

    if sec.get("table_en"):
        n_cols = len(sec["table_en"][0])
        col_w = (PAGE_W - 4 * cm) / n_cols
        block.append(make_table(sec["table_en"], [col_w] * n_cols, rtl=False))

    block.append(Spacer(1, 0.5 * cm))

    # Arabic side
    block.append(Paragraph(ar(sec["ar_title"]), AR_SECTION))
    block.append(HRFlowable(width="100%", thickness=1, color=BRAND_GOLD))
    block.append(Spacer(1, 0.2 * cm))

    if sec.get("ar_body"):
        block.append(multiline_para(ar(sec["ar_body"]), AR_BODY))

    if sec.get("table_ar"):
        n_cols = len(sec["table_ar"][0])
        col_w = (PAGE_W - 4 * cm) / n_cols
        block.append(make_table(sec["table_ar"], [col_w] * n_cols, rtl=True))

    block.append(Spacer(1, 0.8 * cm))
    block.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    block.append(PageBreak())

    story.append(KeepTogether(block[:6]))  # keep title + first few lines together
    story.extend(block[6:])

# ---- Build ----
doc.build(story)
print(f"\n✅ PDF generated successfully:\n   {OUTPUT_PATH}\n")
