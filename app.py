# -*- coding: utf-8 -*-
import streamlit as st
import re
from html import escape

st.set_page_config(page_title="일일 재고 현황표", layout="wide")

# -------------------------------
# 레이아웃 정의
# -------------------------------
CIRCLE_ROWS = [
    ["A101", "A102", "A103", "A104", "A105", "A106"],
    ["A301", "A302", "A303", "A304", "A305", "A306"],
    ["A501", "A502", "A503", "A504", "A505", "A506"],
]

BOX_ROWS = [
    ["A201", "A202", "A203", "A204", "A205", "A206", "A207"],
    ["A401", "A402", "A403", "A404", "A405", "A406", "A407"],
]

DEFAULT_TEXT = """장치장\t곡종\t재고량
A101\tWUR\t1,600.000
A102\tWCRS\t1,700.557
A103\tWASW\t1,360.392
A104\tWASWP\t1,403.039
A105\tWUR\t1,700.915
A106\tWNS\t1,637.684
A201\tWUSL9.0\t146.960
A202\tWUSH\t420.000
A203\tWUR\t420.679
A204\tWUR\t420.233
A205\tWUSH\t420.000
A206\tWUSL9.0\t419.860
A207\tWUR\t158.126
A301\tWUSH\t864.386
A302\tWUSH\t1,695.227
A303\tWUSH\t1,671.185
A304\tWUSH\t1,690.285
A305\tWNS\t1,697.176
A306\tWUR\t1,701.166
A401\tWCRS\t170.000
A402\tWUSH\t410.000
A403\tWUSH\t0.000
A404\tWNS\t419.287
A405\tWUSH\t0.000
A406\tWUSH\t0.000
A407\tWNS\t170.000
A501\tWUSH\t1,557.437
A502\tWNS\t1,703.834
A503\tWUSH\t1,645.290
A504\tWCRS\t956.294
A505\tWASWP\t1,696.740
A506\tWUR\t1,700.906
"""

# -------------------------------
# CSS: 가운데 정렬 + SVG 1/2 축소
# -------------------------------
st.markdown(
    """
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
.center-wrap{ max-width: 980px; margin: 0 auto; }
.center-title{ text-align:center; font-weight:900; font-size:28px; margin: 0.2rem 0 0.6rem 0; }

.svg-wrap{ display:flex; justify-content:center; align-items:flex-start; margin-top: 8px; }
.svg-scale{ transform: scale(0.5); transform-origin: top center; }
</style>
""",
    unsafe_allow_html=True
)

# -------------------------------
# 데이터 입력 UI (가운데)
# -------------------------------
if "raw_text" not in st.session_state:
    st.session_state["raw_text"] = DEFAULT_TEXT

st.markdown('<div class="center-wrap">', unsafe_allow_html=True)
st.markdown('<div class="center-title">데이터 입력 (엑셀 복사/붙여넣기)</div>', unsafe_allow_html=True)

raw = st.text_area(
    label="hidden",
    height=110,
    value=st.session_state["raw_text"],
    label_visibility="collapsed",
)

# ✅ 버튼을 "Streamlit 컬럼"으로 가운데 정렬 (가장 안정적)
left, center, right = st.columns([3, 1, 3])
with center:
    update_clicked = st.button("현황표 업데이트", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

if update_clicked:
    st.session_state["raw_text"] = raw

data_text = st.session_state["raw_text"]

# -------------------------------
# 파싱(헤더 자동 무시)
# -------------------------------
HEADER_WORDS = {"장치장", "곡종", "재고량", "device", "grain", "qty", "quantity"}

def is_header_line(parts):
    p = [x.strip().lower() for x in parts[:3]]
    return any(x in HEADER_WORDS for x in p)

def parse_rows(text: str):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if "\t" in line:
            parts = [p.strip() for p in line.split("\t") if p.strip() != ""]
        else:
            parts = [p.strip() for p in re.split(r"[,\s]+", line) if p.strip() != ""]

        if len(parts) < 3:
            continue

        if is_header_line(parts):
            continue

        device = parts[0].upper()
        grain = parts[1].upper()
        qty_raw = parts[2]
        rows.append((device, grain, qty_raw))
    return rows

def pretty_qty(q: str) -> str:
    cleaned = re.sub(r"[^0-9,\.]", "", q.strip())
    if cleaned == "":
        return ""
    if "." in cleaned:
        cleaned = cleaned.split(".")[0]
    cleaned = cleaned.replace(",,", ",").strip(",")
    return cleaned if cleaned != "" else "0"

rows = parse_rows(data_text)
by_device = {}
for device, grain, qty_raw in rows:
    by_device[device] = (grain, pretty_qty(qty_raw))

# -------------------------------
# SVG 생성 (정답지 스타일)
# -------------------------------
def build_svg():
    W, H = 1400, 720
    BG = "#eef0f3"
    TITLE_Y = 80
    UNDERLINE_Y = TITLE_Y + 18
    BOARD_TOP = 185

    margin = 70
    grid_x = margin
    grid_y = BOARD_TOP
    grid_w = W - margin * 2
    grid_h = 430

    cols, rows2 = 7, 2
    cell_w = grid_w / cols
    cell_h = grid_h / rows2
    R = 78

    x_pos = [grid_x + cell_w * i for i in range(1, cols)]      # 6
    y_pos = [grid_y + cell_h * j for j in range(0, rows2 + 1)] # 3

    parts = []
    parts.append(f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">')
    parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>')

    # 제목 + 밑줄
    parts.append(
        f'<text x="{W/2}" y="{TITLE_Y}" text-anchor="middle" '
        f'font-size="42" font-weight="900" fill="#111" letter-spacing="10">일 일 재 고 현 황 표</text>'
    )
    parts.append(
        f'<line x1="{W*0.23}" y1="{UNDERLINE_Y}" x2="{W*0.77}" y2="{UNDERLINE_Y}" '
        f'stroke="#111" stroke-width="4"/>'
    )

    # 네모 14칸 프레임 1개
    parts.append(
        f'<rect x="{grid_x}" y="{grid_y}" width="{grid_w}" height="{grid_h}" '
        f'fill="none" stroke="#222" stroke-width="4"/>'
    )
    for i in range(1, cols):
        x = grid_x + cell_w * i
        parts.append(f'<line x1="{x}" y1="{grid_y}" x2="{x}" y2="{grid_y + grid_h}" stroke="#222" stroke-width="3"/>')

    y_mid = grid_y + cell_h
    parts.append(f'<line x1="{grid_x}" y1="{y_mid}" x2="{grid_x + grid_w}" y2="{y_mid}" stroke="#222" stroke-width="3"/>')

    # 네모 텍스트(빨강/검정/회색)
    for r_i in range(2):
        for c_i in range(7):
            device = BOX_ROWS[r_i][c_i]
            grain, qty = by_device.get(device, ("", ""))

            cx = grid_x + cell_w * c_i + cell_w / 2
            cy = grid_y + cell_h * r_i + cell_h / 2

            parts.append(f'<text x="{cx}" y="{cy-18}" text-anchor="middle" font-size="20" font-weight="900" fill="#d24a2b">{escape(grain)}</text>')
            parts.append(f'<text x="{cx}" y="{cy+10}" text-anchor="middle" font-size="24" font-weight="900" fill="#111">{escape(qty)}</text>')
            parts.append(f'<text x="{cx}" y="{cy+38}" text-anchor="middle" font-size="16" font-weight="800" fill="#7a7a7a">{escape(device)}</text>')

    # 원 텍스트(파랑/검정/회색)
    for r_i in range(3):
        for c_i in range(6):
            device = CIRCLE_ROWS[r_i][c_i]
            grain, qty = by_device.get(device, ("", ""))

            cx = x_pos[c_i]
            cy = y_pos[r_i]

            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#fff" stroke="#222" stroke-width="3"/>')
            parts.append(f'<text x="{cx}" y="{cy-18}" text-anchor="middle" font-size="20" font-weight="900" fill="#1e4fff">{escape(grain)}</text>')
            parts.append(f'<text x="{cx}" y="{cy+10}" text-anchor="middle" font-size="24" font-weight="900" fill="#111">{escape(qty)}</text>')
            parts.append(f'<text x="{cx}" y="{cy+38}" text-anchor="middle" font-size="16" font-weight="800" fill="#7a7a7a">{escape(device)}</text>')

    parts.append("</svg>")
    return "\n".join(parts)

svg = build_svg()

# SVG 가운데 + 1/2 축소
st.markdown(
    f'<div class="svg-wrap"><div class="svg-scale">{svg}</div></div>',
    unsafe_allow_html=True
)
