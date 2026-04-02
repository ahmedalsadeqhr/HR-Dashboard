# Probation Review Presentation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a professional 7-slide PowerPoint presentation for Ahmed Al-Sadeq's 3-month probation review at 51Talk Egypt.

**Architecture:** Single Python script using python-pptx to generate a clean, professional deck. Each slide is built programmatically with consistent styling — dark navy theme with accent colors. No template dependency.

**Tech Stack:** Python 3, python-pptx, saved to `docs/Probation-Review-Ahmed-AlSadeq.pptx`

**Output file:** `C:/Users/high tech/Desktop/HRBP/docs/Probation-Review-Ahmed-AlSadeq.pptx`

---

## Design System (51Talk Brand Refresh — March 2026)

- **Background:** Deep navy `#1B2A5C` (matches 51Talk brand)
- **Primary text:** White `#FFFFFF`
- **Accent / headings:** Bright yellow `#F5C430` (51Talk brand yellow)
- **Card background:** Dark navy card `#162044`
- **Subtext / secondary:** Light gray `#B0BEC5`
- **Value colors:** Red `#E53935`, Blue `#3D8EF0`, Amber `#F5C430`, Green `#43A047`
- **Font:** Calibri throughout
- **Slide size:** 13.33" × 7.5" (widescreen 16:9)

---

## Task 1: Script scaffold + helpers

**Files:**
- Create: `build_presentation.py`

**Step 1: Create the script with imports and helper functions**

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Color palette
NAVY       = RGBColor(0x1B, 0x2A, 0x5C)   # 51Talk deep navy
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
GOLD       = RGBColor(0xF5, 0xC4, 0x30)   # 51Talk brand yellow
LIGHT_GRAY = RGBColor(0xB0, 0xBE, 0xC5)
RED        = RGBColor(0xE5, 0x39, 0x35)
BLUE       = RGBColor(0x3D, 0x8E, 0xF0)
AMBER      = RGBColor(0xF5, 0xC4, 0x30)   # same as GOLD for brand consistency
GREEN      = RGBColor(0x43, 0xA0, 0x47)
DARK_CARD  = RGBColor(0x16, 0x20, 0x44)   # darker navy for cards

W = Inches(13.33)
H = Inches(7.5)

def new_prs():
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H
    return prs

def blank_slide(prs):
    layout = prs.slide_layouts[6]   # completely blank
    return prs.slides.add_slide(layout)

def bg(slide, color=NAVY):
    """Fill slide background."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def box(slide, left, top, width, height,
        bg_color=None, text='', font_size=18,
        bold=False, color=WHITE, align=PP_ALIGN.LEFT,
        wrap=True, line_color=None):
    """Add a text box with optional background fill and border."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    if bg_color:
        txBox.fill.solid()
        txBox.fill.fore_color.rgb = bg_color
    if line_color:
        txBox.line.color.rgb = line_color
        txBox.line.width = Pt(1)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(font_size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.name  = 'Calibri'
    return txBox

def add_para(tf, text, font_size=16, bold=False,
             color=WHITE, align=PP_ALIGN.LEFT, space_before=0):
    """Append a paragraph to an existing text frame."""
    from pptx.util import Pt as Pt2
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt2(space_before)
    run = p.add_run()
    run.text = text
    run.font.size  = Pt2(font_size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.name  = 'Calibri'
    return p

def accent_line(slide, top, color=GOLD,
                left=Inches(0.5), width=Inches(12.33), height=Pt(3)):
    """Thin horizontal accent line."""
    from pptx.util import Pt as Pt2
    line = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, Pt2(3)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = color
    line.line.fill.background()
    return line
```

**Step 2: Run to verify no import errors**

```bash
python3 -c "exec(open('build_presentation.py').read()); print('OK')"
```
Expected: `OK`

**Step 3: Commit**

```bash
git add build_presentation.py
git commit -m "feat: add presentation script scaffold and helpers"
```

---

## Task 2: Slide 1 — Cover

**Step 1: Add slide 1 function**

```python
def slide_01_cover(prs):
    s = blank_slide(prs)
    bg(s)

    # Left accent bar
    bar = s.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.08), H)
    bar.fill.solid(); bar.fill.fore_color.rgb = GOLD
    bar.line.fill.background()

    # Main title
    box(s, Inches(0.5), Inches(1.8), Inches(9), Inches(1.2),
        text='Work Review Report', font_size=44, bold=True,
        color=WHITE, align=PP_ALIGN.LEFT)

    # Subtitle
    box(s, Inches(0.5), Inches(3.0), Inches(9), Inches(0.6),
        text='Probation Period Review', font_size=22,
        color=GOLD, align=PP_ALIGN.LEFT)

    # Gold divider
    accent_line(s, Inches(3.8))

    # Details row
    box(s, Inches(0.5), Inches(4.1), Inches(4), Inches(0.5),
        text='Ahmed Al-Sadeq', font_size=18, bold=True,
        color=WHITE, align=PP_ALIGN.LEFT)

    box(s, Inches(0.5), Inches(4.6), Inches(6), Inches(0.5),
        text='HR Business Partner  |  51Talk Egypt', font_size=16,
        color=LIGHT_GRAY, align=PP_ALIGN.LEFT)

    box(s, Inches(0.5), Inches(5.1), Inches(6), Inches(0.5),
        text='December 9, 2025  –  March 9, 2026', font_size=15,
        color=LIGHT_GRAY, align=PP_ALIGN.LEFT)

    return s
```

---

## Task 3: Slide 2 — Self Introduction

**Step 1: Add slide 2 function**

```python
def slide_02_intro(prs):
    s = blank_slide(prs)
    bg(s)

    # Section label
    box(s, Inches(0.5), Inches(0.25), Inches(3), Inches(0.4),
        text='01  /  Self Introduction', font_size=12,
        color=GOLD, bold=True)

    # Title
    box(s, Inches(0.5), Inches(0.65), Inches(12), Inches(0.7),
        text='Who I Am', font_size=32, bold=True, color=WHITE)

    accent_line(s, Inches(1.45))

    # Left column — key facts cards
    cards = [
        ('Date of Joining',   'December 9, 2025'),
        ('Years of Experience', '10 Years'),
        ('Current Role',      'HR Business Partner'),
        ('Department',        'Human Resources — 51Talk Egypt'),
    ]
    y = Inches(1.65)
    for label, value in cards:
        card = s.shapes.add_shape(1, Inches(0.5), y, Inches(4.5), Inches(0.72))
        card.fill.solid(); card.fill.fore_color.rgb = DARK_CARD
        card.line.fill.background()
        box(s, Inches(0.62), y + Pt(6), Inches(4.3), Inches(0.28),
            text=label, font_size=10, color=GOLD, bold=True)
        box(s, Inches(0.62), y + Pt(22), Inches(4.3), Inches(0.35),
            text=value, font_size=14, color=WHITE, bold=False)
        y += Inches(0.82)

    # Right column — summary + responsibilities
    box(s, Inches(5.5), Inches(1.65), Inches(7.3), Inches(1.7),
        text=(
            'HR professional with 10 years of experience spanning all HR functions — '
            'from talent acquisition, onboarding, and employee relations to HR operations, '
            'legal compliance, and HR technology. Proven track record of managing '
            'high-volume HR operations, building systems that scale, and driving '
            'people-focused initiatives that create measurable business impact.'
        ),
        font_size=13, color=LIGHT_GRAY, wrap=True)

    box(s, Inches(5.5), Inches(3.5), Inches(3.5), Inches(0.4),
        text='Key Responsibilities', font_size=14, bold=True, color=GOLD)

    resp = [
        '▸  Employee lifecycle management (onboarding to offboarding)',
        '▸  Employee relations and case management',
        '▸  HR systems implementation and automation',
        '▸  Legal compliance (social insurance, labor law)',
        '▸  HR data, reporting, and dashboards',
    ]
    y2 = Inches(3.95)
    for r in resp:
        box(s, Inches(5.5), y2, Inches(7.3), Inches(0.37),
            text=r, font_size=13, color=WHITE)
        y2 += Inches(0.38)

    return s
```

---

## Task 4: Slide 3 — Performance Summary

**Step 1: Add slide 3 function**

```python
def slide_03_performance(prs):
    s = blank_slide(prs)
    bg(s)

    box(s, Inches(0.5), Inches(0.25), Inches(5), Inches(0.4),
        text='02  /  Performance Summary', font_size=12, color=GOLD, bold=True)

    box(s, Inches(0.5), Inches(0.65), Inches(12), Inches(0.7),
        text='Impact at a Glance', font_size=32, bold=True, color=WHITE)

    accent_line(s, Inches(1.45))

    # Top row — 3 stat cards
    stats = [
        ('100', 'New Hires Onboarded',
         'End-to-end onboarding for 100 employees\nwithin the first 3 months'),
        ('50',  'ER Cases Handled',
         'Managed and resolved 50 employee\nrelations cases'),
        ('3',   'Legal & Compliance Cases',
         '1 social insurance investigation\n2 re-hire violation cases resolved'),
    ]
    x = Inches(0.5)
    for num, title, desc in stats:
        card = s.shapes.add_shape(1, x, Inches(1.65), Inches(3.9), Inches(2.0))
        card.fill.solid(); card.fill.fore_color.rgb = DARK_CARD
        card.line.fill.background()
        box(s, x + Inches(0.15), Inches(1.75), Inches(3.6), Inches(0.9),
            text=num, font_size=52, bold=True, color=GOLD, align=PP_ALIGN.LEFT)
        box(s, x + Inches(0.15), Inches(2.55), Inches(3.6), Inches(0.35),
            text=title, font_size=13, bold=True, color=WHITE)
        box(s, x + Inches(0.15), Inches(2.9), Inches(3.6), Inches(0.6),
            text=desc, font_size=11, color=LIGHT_GRAY, wrap=True)
        x += Inches(4.1)

    # Bottom row — 2 initiative cards
    initiatives = [
        ('3', 'HR Systems Built & Automated',
         '• Leave Email Automation (Lark integration)\n'
         '• Attendance & HC Dashboard\n'
         '• Live Quiz System (600+ concurrent players)'),
        ('1', 'Major Initiative In Progress',
         'iTalent ESS Portal — transitioning leave management\n'
         'from email to fully digital self-service system'),
    ]
    x = Inches(0.5)
    for num, title, desc in initiatives:
        card = s.shapes.add_shape(1, x, Inches(3.9), Inches(6.1), Inches(2.9))
        card.fill.solid(); card.fill.fore_color.rgb = DARK_CARD
        card.line.fill.background()
        box(s, x + Inches(0.2), Inches(4.0), Inches(5.7), Inches(0.8),
            text=num, font_size=44, bold=True, color=GOLD)
        box(s, x + Inches(0.2), Inches(4.7), Inches(5.7), Inches(0.4),
            text=title, font_size=14, bold=True, color=WHITE)
        box(s, x + Inches(0.2), Inches(5.1), Inches(5.7), Inches(1.5),
            text=desc, font_size=12, color=LIGHT_GRAY, wrap=True)
        x += Inches(6.4)

    return s
```

---

## Task 5: Slide 4 — Value Practice (STAR)

**Step 1: Add slide 4 function**

```python
def slide_04_values(prs):
    s = blank_slide(prs)
    bg(s)

    box(s, Inches(0.5), Inches(0.25), Inches(5), Inches(0.4),
        text='03  /  Value Practice', font_size=12, color=GOLD, bold=True)

    box(s, Inches(0.5), Inches(0.65), Inches(12), Inches(0.7),
        text='Living the 51Talk Values — STAR Method', font_size=28, bold=True, color=WHITE)

    accent_line(s, Inches(1.45))

    values = [
        (RED,   'Game Changer',   '🔴',
         'Leave management was email-based — slow and error-prone.',
         'Find and implement digital HR solutions proactively.',
         'Built Leave Automation, Attendance Dashboard, and iTalent plan.',
         'Reduced manual effort and laid foundation for digital HR operations.'),
        (BLUE,  'Customer Focus', '🔵',
         '51Talk Egypt needed structured onboarding for rapid growth.',
         'Ensure every new hire has a smooth, consistent experience.',
         'Managed end-to-end onboarding for 100 employees.',
         '100 employees successfully integrated within 3 months.'),
        (AMBER, 'Passion',        '🟡',
         'ER cases require time, sensitivity, and deep expertise.',
         'Handle all cases professionally while maintaining trust.',
         'Managed 50 ER cases with full documentation and fair investigation.',
         'All cases resolved within policy guidelines.'),
        (GREEN, 'Teamwork',       '🟢',
         'Compliance cases required cross-functional coordination.',
         'Navigate legal matters in collaboration with other departments.',
         'Led 3 investigations, coordinated with legal and finance teams.',
         'All cases resolved in compliance with Egyptian labor law.'),
    ]

    positions = [
        (Inches(0.4),  Inches(1.6)),
        (Inches(6.7),  Inches(1.6)),
        (Inches(0.4),  Inches(4.3)),
        (Inches(6.7),  Inches(4.3)),
    ]

    star_labels = ['S', 'T', 'A', 'R']
    star_texts  = ['Situation', 'Task', 'Action', 'Result']

    for (color, value_name, emoji, s_txt, t_txt, a_txt, r_txt), (cx, cy) in zip(values, positions):
        # Card background
        card = s.shapes.add_shape(1, cx, cy, Inches(6.1), Inches(2.5))
        card.fill.solid(); card.fill.fore_color.rgb = DARK_CARD
        card.line.color.rgb = color; card.line.width = Pt(1.5)

        # Value name header bar
        hdr = s.shapes.add_shape(1, cx, cy, Inches(6.1), Inches(0.38))
        hdr.fill.solid(); hdr.fill.fore_color.rgb = color
        hdr.line.fill.background()
        box(s, cx + Inches(0.12), cy + Pt(4), Inches(5.8), Inches(0.3),
            text=value_name, font_size=13, bold=True, color=WHITE)

        # STAR rows
        star_data = [s_txt, t_txt, a_txt, r_txt]
        for i, (lbl, full, data) in enumerate(zip(star_labels, star_texts, star_data)):
            row_y = cy + Inches(0.45) + i * Inches(0.5)
            # Label badge
            badge = s.shapes.add_shape(1, cx + Inches(0.1), row_y, Inches(0.28), Inches(0.32))
            badge.fill.solid(); badge.fill.fore_color.rgb = color
            badge.line.fill.background()
            box(s, cx + Inches(0.1), row_y, Inches(0.28), Inches(0.32),
                text=lbl, font_size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
            # Text
            box(s, cx + Inches(0.45), row_y, Inches(5.5), Inches(0.42),
                text=data, font_size=10, color=WHITE if i < 3 else GOLD, wrap=True)

    return s
```

---

## Task 6: Slide 5 — Gains, Losses & Reflection

**Step 1: Add slide 5 function**

```python
def slide_05_reflection(prs):
    s = blank_slide(prs)
    bg(s)

    box(s, Inches(0.5), Inches(0.25), Inches(6), Inches(0.4),
        text='04  /  Gains, Losses & Reflection', font_size=12, color=GOLD, bold=True)

    box(s, Inches(0.5), Inches(0.65), Inches(12), Inches(0.7),
        text='Looking Back — Honest Self-Assessment', font_size=28, bold=True, color=WHITE)

    accent_line(s, Inches(1.45))

    # Left — Gains
    gain_card = s.shapes.add_shape(1, Inches(0.4), Inches(1.6), Inches(5.9), Inches(5.5))
    gain_card.fill.solid(); gain_card.fill.fore_color.rgb = DARK_CARD
    gain_card.line.color.rgb = GREEN; gain_card.line.width = Pt(1.5)

    hdr_g = s.shapes.add_shape(1, Inches(0.4), Inches(1.6), Inches(5.9), Inches(0.42))
    hdr_g.fill.solid(); hdr_g.fill.fore_color.rgb = GREEN
    hdr_g.line.fill.background()
    box(s, Inches(0.55), Inches(1.65), Inches(5.5), Inches(0.35),
        text='✓  What I Gained', font_size=14, bold=True, color=WHITE)

    gains = [
        ('Built team-scale solutions',
         'Focused on tools that support the entire HR team, not just individual tasks.'),
        ('Deepened industry expertise',
         'Gained strong understanding of EdTech HR operations and 51Talk\'s business model.'),
        ('Started learning Chinese',
         'Investing in language skills to connect with the broader 51Talk organization.'),
        ('Advanced AI & automation skills',
         'Leveraged AI tools to modernize HR workflows and build scalable systems.'),
    ]
    gy = Inches(2.15)
    for title, desc in gains:
        box(s, Inches(0.6), gy, Inches(5.5), Inches(0.3),
            text=f'▸  {title}', font_size=12, bold=True, color=GREEN)
        box(s, Inches(0.6), gy + Inches(0.3), Inches(5.5), Inches(0.4),
            text=f'   {desc}', font_size=11, color=LIGHT_GRAY, wrap=True)
        gy += Inches(0.85)

    # Right — Improvements
    imp_card = s.shapes.add_shape(1, Inches(6.7), Inches(1.6), Inches(6.2), Inches(5.5))
    imp_card.fill.solid(); imp_card.fill.fore_color.rgb = DARK_CARD
    imp_card.line.color.rgb = AMBER; imp_card.line.width = Pt(1.5)

    hdr_i = s.shapes.add_shape(1, Inches(6.7), Inches(1.6), Inches(6.2), Inches(0.42))
    hdr_i.fill.solid(); hdr_i.fill.fore_color.rgb = AMBER
    hdr_i.line.fill.background()
    box(s, Inches(6.85), Inches(1.65), Inches(5.8), Inches(0.35),
        text='⟳  What I\'d Do Differently', font_size=14, bold=True, color=WHITE)

    improvements = [
        ('Accelerate knowledge acquisition',
         'Getting up to speed on systems, processes, and people took time — '
         'I\'d compress this phase with a more structured onboarding approach.'),
        ('Build management trust earlier',
         'I\'d prioritize more frequent check-ins and proactive communication '
         'from day one to establish alignment faster.'),
        ('Implement systems sooner',
         'The automation and iTalent projects showed clear value. Earlier '
         'implementation would have delivered earlier impact.'),
        ('Continue learning Chinese',
         'Language learning is a priority I want to invest in more consistently '
         'going forward.'),
    ]
    iy = Inches(2.15)
    for title, desc in improvements:
        box(s, Inches(6.85), iy, Inches(5.8), Inches(0.3),
            text=f'▸  {title}', font_size=12, bold=True, color=AMBER)
        box(s, Inches(6.85), iy + Inches(0.3), Inches(5.8), Inches(0.5),
            text=f'   {desc}', font_size=11, color=LIGHT_GRAY, wrap=True)
        iy += Inches(0.95)

    return s
```

---

## Task 7: Slide 6 — Next Stage Plan & Support Needed

**Step 1: Add slide 6 function**

```python
def slide_06_next(prs):
    s = blank_slide(prs)
    bg(s)

    box(s, Inches(0.5), Inches(0.25), Inches(6), Inches(0.4),
        text='05  /  Next Stage Plan', font_size=12, color=GOLD, bold=True)

    box(s, Inches(0.5), Inches(0.65), Inches(12), Inches(0.7),
        text='Looking Forward — Priorities & Support Needed', font_size=28, bold=True, color=WHITE)

    accent_line(s, Inches(1.45))

    # Priorities section
    box(s, Inches(0.5), Inches(1.6), Inches(4.5), Inches(0.4),
        text='Next Stage Priorities', font_size=15, bold=True, color=GOLD)

    priorities = [
        ('Complete iTalent ESS Portal Rollout',
         'Finalize configuration, run CC Team pilot, and transition the full '
         'company to digital leave management.'),
        ('HR Analytics',
         'Build comprehensive HR analytics reporting covering turnover, '
         'headcount, attendance, and performance trends.'),
        ('AI & Data Projects for HR',
         'Expand automation — smarter leave processing, predictive analytics, '
         'automated reporting, and intelligent HR workflows.'),
        ('Continue Learning Chinese',
         'Invest consistently in language learning to strengthen collaboration '
         'with the broader 51Talk organization.'),
    ]

    py = Inches(2.1)
    for i, (title, desc) in enumerate(priorities):
        num_box = s.shapes.add_shape(1, Inches(0.5), py, Inches(0.38), Inches(0.38))
        num_box.fill.solid(); num_box.fill.fore_color.rgb = GOLD
        num_box.line.fill.background()
        box(s, Inches(0.5), py, Inches(0.38), Inches(0.38),
            text=str(i + 1), font_size=13, bold=True,
            color=NAVY, align=PP_ALIGN.CENTER)
        box(s, Inches(1.05), py, Inches(6.5), Inches(0.3),
            text=title, font_size=13, bold=True, color=WHITE)
        box(s, Inches(1.05), py + Inches(0.32), Inches(6.5), Inches(0.38),
            text=desc, font_size=11, color=LIGHT_GRAY, wrap=True)
        py += Inches(0.85)

    # Support needed section (right panel)
    sup_card = s.shapes.add_shape(1, Inches(8.2), Inches(1.55), Inches(4.7), Inches(5.6))
    sup_card.fill.solid(); sup_card.fill.fore_color.rgb = DARK_CARD
    sup_card.line.color.rgb = GOLD; sup_card.line.width = Pt(1.5)

    hdr_s = s.shapes.add_shape(1, Inches(8.2), Inches(1.55), Inches(4.7), Inches(0.42))
    hdr_s.fill.solid(); hdr_s.fill.fore_color.rgb = GOLD
    hdr_s.line.fill.background()
    box(s, Inches(8.35), Inches(1.6), Inches(4.4), Inches(0.35),
        text='Support Needed', font_size=14, bold=True, color=NAVY)

    supports = [
        ('Claude AI — Max Subscription',
         'Required to continue building and scaling HR automation and AI projects '
         'that benefit the entire department.'),
        ('Broader System Access',
         'Access to relevant HR and operational systems to enable deeper analytics '
         'and automation capabilities.'),
    ]
    sy = Inches(2.1)
    for title, desc in supports:
        box(s, Inches(8.4), sy, Inches(4.3), Inches(0.35),
            text=f'▸  {title}', font_size=12, bold=True, color=GOLD)
        box(s, Inches(8.4), sy + Inches(0.35), Inches(4.3), Inches(0.7),
            text=desc, font_size=11, color=LIGHT_GRAY, wrap=True)
        sy += Inches(1.3)

    return s
```

---

## Task 8: Slide 7 — Thank You

**Step 1: Add slide 7 function**

```python
def slide_07_thanks(prs):
    s = blank_slide(prs)
    bg(s)

    # Left accent bar
    bar = s.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.08), H)
    bar.fill.solid(); bar.fill.fore_color.rgb = GOLD
    bar.line.fill.background()

    # Gold circle decoration
    circle = s.shapes.add_shape(9, Inches(9.5), Inches(1.0), Inches(3.5), Inches(3.5))
    circle.fill.solid(); circle.fill.fore_color.rgb = DARK_CARD
    circle.line.color.rgb = GOLD; circle.line.width = Pt(2)

    box(s, Inches(0.5), Inches(2.3), Inches(8.5), Inches(1.4),
        text='Thank You', font_size=60, bold=True,
        color=WHITE, align=PP_ALIGN.LEFT)

    accent_line(s, Inches(3.85), width=Inches(5))

    box(s, Inches(0.5), Inches(4.1), Inches(8), Inches(0.6),
        text='Ahmed Al-Sadeq  |  HR Business Partner  |  51Talk Egypt',
        font_size=16, color=LIGHT_GRAY, align=PP_ALIGN.LEFT)

    box(s, Inches(0.5), Inches(4.75), Inches(8), Inches(0.5),
        text='Open for questions & discussion',
        font_size=14, color=GOLD, align=PP_ALIGN.LEFT)

    return s
```

---

## Task 9: Main build function + save

**Step 1: Add main() and call it**

```python
def main():
    prs = new_prs()
    slide_01_cover(prs)
    slide_02_intro(prs)
    slide_03_performance(prs)
    slide_04_values(prs)
    slide_05_reflection(prs)
    slide_06_next(prs)
    slide_07_thanks(prs)

    out = 'docs/Probation-Review-Ahmed-AlSadeq.pptx'
    prs.save(out)
    print(f'Saved: {out}')

if __name__ == '__main__':
    main()
```

**Step 2: Run the full script**

```bash
cd "C:/Users/high tech/Desktop/HRBP" && python3 build_presentation.py
```
Expected: `Saved: docs/Probation-Review-Ahmed-AlSadeq.pptx`

**Step 3: Verify file exists and has reasonable size**

```bash
ls -lh docs/Probation-Review-Ahmed-AlSadeq.pptx
```
Expected: file exists, size > 30KB

**Step 4: Commit**

```bash
git add build_presentation.py docs/Probation-Review-Ahmed-AlSadeq.pptx
git commit -m "feat: add probation review presentation for Ahmed Al-Sadeq"
```

---

## Success Criteria

- [ ] Script runs without errors
- [ ] Output file `docs/Probation-Review-Ahmed-AlSadeq.pptx` generated
- [ ] All 7 slides present with correct content
- [ ] Consistent dark navy theme with gold accents throughout
- [ ] File size > 30KB (confirms all slides rendered)
