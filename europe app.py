# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import date
from urllib.parse import quote_plus

st.set_page_config(page_title="유럽 여행 계획표", layout="wide")

# ----------------------------
# 상태(저장공간) 준비
# ----------------------------
if "plans" not in st.session_state:
    # 각 항목: {"date": "2026-02-11", "place": "Paris", "note": "..."}
    st.session_state["plans"] = []

# ----------------------------
# 제목
# ----------------------------
st.markdown(
    "<h1 style='text-align:center;'>유럽 여행 계획표</h1>",
    unsafe_allow_html=True
)

st.markdown("---")

# ----------------------------
# 입력 영역
# ----------------------------
left, mid, right = st.columns([1.2, 2.2, 1.2])

with left:
    d = st.date_input("날짜", value=date.today())

with mid:
    place = st.text_input("가고 싶은 장소", placeholder="예: Eiffel Tower, Paris / Sagrada Família, Barcelona")

with right:
    note = st.text_input("메모(선택)", placeholder="예: 오전 방문 / 예약 필요")

add_col1, add_col2, add_col3 = st.columns([3, 1.2, 3])
with add_col2:
    add_clicked = st.button("➕ 추가", use_container_width=True)

if add_clicked:
    if not place.strip():
        st.warning("장소를 입력해 주세요.")
    else:
        st.session_state["plans"].append(
            {"date": str(d), "place": place.strip(), "note": note.strip()}
        )
        # 입력칸 즉시 비우고 싶으면 아래 2줄을 사용(단, Streamlit 특성상 키 지정 필요)
        # st.session_state["place_input"] = ""
        # st.session_state["note_input"] = ""

st.markdown("---")

# ----------------------------
# 결과 표시(표 + 구글지도 링크)
# ----------------------------
st.subheader("일자별 계획")

if len(st.session_state["plans"]) == 0:
    st.info("위에서 날짜와 장소를 입력한 뒤 [추가]를 누르면 여기에 쌓입니다.")
else:
    df = pd.DataFrame(st.session_state["plans"])
    df = df.sort_values(["date", "place"], ascending=[True, True]).reset_index(drop=True)

    # Google Maps 링크 생성 (API 키 없이 사용 가능)
    def maps_link(q: str) -> str:
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(q)}"

    df["지도"] = df["place"].apply(lambda x: maps_link(x))

    # 표는 클릭 가능한 링크가 기본으로 안 보여서, 아래처럼 마크다운 표로 보여줌
    show = df[["date", "place", "note", "지도"]].copy()
    show["지도"] = show["지도"].apply(lambda url: f"[열기]({url})")

    st.markdown(
        show.to_markdown(index=False),
        unsafe_allow_html=True
    )

    # ----------------------------
    # (옵션) 선택한 장소 지도 미리보기(iframe)
    # ----------------------------
    st.markdown("### 지도 미리보기 (선택)")
    options = [f'{r["date"]} | {r["place"]}' for _, r in df.iterrows()]
    pick = st.selectbox("미리볼 항목 선택", options)

    picked_place = pick.split("|", 1)[1].strip()
    q = quote_plus(picked_place)

    # iframe embed (키 없이 되는 검색형)
    # 환경/브라우저에 따라 제한될 수 있어요. 링크 방식은 항상 동작합니다.
    iframe = f"""
    <iframe
      width="100%"
      height="420"
      style="border:0; border-radius:12px;"
      loading="lazy"
      allowfullscreen
      referrerpolicy="no-referrer-when-downgrade"
      src="https://www.google.com/maps?q={q}&output=embed">
    </iframe>
    """
    st.components.v1.html(iframe, height=440)

# ----------------------------
# 관리 기능(삭제/초기화)
# ----------------------------
st.markdown("---")
admin1, admin2, admin3 = st.columns([2, 1.2, 2])

with admin2:
    if st.button("🗑️ 전체 초기화", use_container_width=True):
        st.session_state["plans"] = []
        st.success("초기화 완료!")
