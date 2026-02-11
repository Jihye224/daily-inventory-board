# -*- coding: utf-8 -*-
import streamlit as st
from datetime import date, time
from urllib.parse import quote_plus

st.set_page_config(page_title="유럽 여행 계획표", layout="wide")

# ----------------------------
# 상태 저장
# ----------------------------
if "plans" not in st.session_state:
    st.session_state["plans"] = []

# ----------------------------
# 무료/키 없는 "후보 사전" (핀란드/포르투갈/스페인)
# 필요하면 계속 추가 가능
# ----------------------------
PLACES = {
    "핀란드": [
        # 도시/지역
        ("헬싱키", "Helsinki, Finland"),
        ("에스포", "Espoo, Finland"),
        ("탐페레", "Tampere, Finland"),
        ("투르쿠", "Turku, Finland"),
        ("로바니에미", "Rovaniemi, Finland"),
        ("라플란드", "Lapland, Finland"),
        # 공항
        ("헬싱키 공항", "Helsinki Airport (HEL), Finland"),
        ("로바니에미 공항", "Rovaniemi Airport, Finland"),
        # 주요 명소
        ("수오멘린나", "Suomenlinna, Helsinki, Finland"),
        ("템펠리아우키오 교회", "Temppeliaukio Church, Helsinki, Finland"),
        ("오디 도서관", "Oodi Library, Helsinki, Finland"),
        ("산타클로스 마을", "Santa Claus Village, Rovaniemi, Finland"),
    ],
    "포르투갈": [
        ("리스본", "Lisbon, Portugal"),
        ("포르투", "Porto, Portugal"),
        ("신트라", "Sintra, Portugal"),
        ("카스카이스", "Cascais, Portugal"),
        ("알부페이라", "Albufeira, Portugal"),
        ("라고스", "Lagos, Portugal"),
        ("파티마", "Fátima, Portugal"),
        # 공항
        ("리스본 공항", "Lisbon Airport (LIS), Portugal"),
        ("포르투 공항", "Porto Airport (OPO), Portugal"),
        ("파루 공항", "Faro Airport (FAO), Portugal"),
        # 주요 명소
        ("제로니무스 수도원", "Jerónimos Monastery, Lisbon, Portugal"),
        ("벨렝 탑", "Belém Tower, Lisbon, Portugal"),
        ("상 조르제 성", "São Jorge Castle, Lisbon, Portugal"),
        ("리베이라", "Ribeira, Porto, Portugal"),
        ("렐루 서점", "Livraria Lello, Porto, Portugal"),
        ("페나 궁전", "Pena Palace, Sintra, Portugal"),
    ],
    "스페인": [
        ("바르셀로나", "Barcelona, Spain"),
        ("마드리드", "Madrid, Spain"),
        ("세비야", "Seville, Spain"),
        ("그라나다", "Granada, Spain"),
        ("발렌시아", "Valencia, Spain"),
        ("빌바오", "Bilbao, Spain"),
        ("톨레도", "Toledo, Spain"),
        ("말라가", "Málaga, Spain"),
        # 공항
        ("바르셀로나 공항", "Barcelona Airport (BCN), Spain"),
        ("마드리드 공항", "Madrid-Barajas Airport (MAD), Spain"),
        ("세비야 공항", "Seville Airport (SVQ), Spain"),
        ("말라가 공항", "Málaga Airport (AGP), Spain"),
        # 주요 명소
        ("사그라다 파밀리아", "Sagrada Família, Barcelona, Spain"),
        ("구엘 공원", "Park Güell, Barcelona, Spain"),
        ("카사 바트요", "Casa Batlló, Barcelona, Spain"),
        ("프라도 미술관", "Prado Museum, Madrid, Spain"),
        ("레티로 공원", "El Retiro Park, Madrid, Spain"),
        ("알함브라", "Alhambra, Granada, Spain"),
        ("세비야 대성당", "Seville Cathedral, Seville, Spain"),
        ("알카사르", "Royal Alcázar of Seville, Spain"),
    ],
}

# 검색용 전체 리스트(표시명, 지도검색문구, 국가)
ALL = []
for country, items in PLACES.items():
    for ko_name, query in items:
        ALL.append({"country": country, "label": f"{ko_name} · {country}", "query": query})

# ----------------------------
# 지도 링크/미리보기(키 없음)
# ----------------------------
def maps_search_url(q: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(q)}"

def maps_embed_html(q: str) -> str:
    q2 = quote_plus(q)
    return f"""
    <iframe
      width="100%"
      height="260"
      style="border:0; border-radius:12px;"
      loading="lazy"
      allowfullscreen
      referrerpolicy="no-referrer-when-downgrade"
      src="https://www.google.com/maps?q={q2}&output=embed">
    </iframe>
    """

# ----------------------------
# UI
# ----------------------------
st.markdown("<h1 style='text-align:center; margin-bottom: 0.2rem;'>유럽 여행 계획표</h1>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.2, 2.4, 1.8])

with c1:
    d = st.date_input("날짜", value=date.today())
    t = st.time_input("시간", value=time(9, 0))

with c2:
    # 방문 국가 선택(요청 반영: 핀란드/포르투갈/스페인)
    country_filter = st.multiselect(
        "방문 국가 선택",
        ["핀란드", "포르투갈", "스페인"],
        default=["핀란드", "포르투갈", "스페인"]
    )

    q = st.text_input("장소 검색(입력하면 후보가 뜹니다)", placeholder="예: 리스본 / 공항 / 사그라다 / helsinki")

    # 후보 생성(간단한 부분일치)
    cand = [x for x in ALL if x["country"] in country_filter]
    q_low = q.strip().lower()

    if q_low:
        def match_score(item):
            # 한글/영문 모두 대충 맞추려고 label + query에 대해 점수
            text = (item["label"] + " " + item["query"]).lower()
            if q_low in text:
                # 더 앞에 나오면 점수 높게
                return 1000 - text.find(q_low)
            return -1

        scored = [(match_score(item), item) for item in cand]
        cand = [it for s, it in sorted(scored, key=lambda x: x[0], reverse=True) if s >= 0][:20]
    else:
        # 입력이 없으면 국가별 대표만 조금 보여주기
        cand = cand[:20]

    if cand:
        labels = [c["label"] for c in cand]
        picked = st.selectbox("후보 선택", labels)
        picked_item = next((c for c in cand if c["label"] == picked), None)
    else:
        picked_item = None

    note = st.text_input("메모(선택)", placeholder="예: 오전 방문 / 예약 필요")

with c3:
    st.markdown("#### 지도 연동")
    if picked_item:
        url = maps_search_url(picked_item["query"])
        st.link_button("Google Maps로 열기", url, use_container_width=True)
        st.components.v1.html(maps_embed_html(picked_item["query"]), height=280)
        st.caption("※ 키 없는 버전이라 ‘구글 공식 자동완성’이 아니라, 미리 등록된 후보에서 선택하는 방식입니다.")
    else:
        st.caption("왼쪽에서 후보를 선택하면\n여기에 지도 미리보기/링크가 표시됩니다.")

# 가운데 버튼
l, m, r = st.columns([3, 1.2, 3])
with m:
    add_clicked = st.button("➕ 일정 추가", use_container_width=True)

if add_clicked:
    if not picked_item:
        st.warning("후보를 선택해 주세요.")
    else:
        st.session_state["plans"].append(
            {
                "date": str(d),
                "time": t.strftime("%H:%M"),
                "place": picked_item["label"].split(" · ")[0],
                "country": picked_item["country"],
                "maps_query": picked_item["query"],
                "note": note.strip(),
            }
        )
        st.success("추가되었습니다! 아래 계획표에 반영됐어요.")

st.markdown("<hr/>", unsafe_allow_html=True)

# 결과
st.subheader("일자별 계획")

if not st.session_state["plans"]:
    st.info("위에서 날짜/시간/장소를 선택하고 [일정 추가]를 누르면 여기에 쌓입니다.")
else:
    plans_sorted = sorted(st.session_state["plans"], key=lambda x: (x["date"], x["time"], x["country"], x["place"]))
    rows = [{"날짜": p["date"], "시간": p["time"], "국가": p["country"], "장소": p["place"], "메모": p["note"]} for p in plans_sorted]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown("### 지도 보기")
    options = [f'{p["date"]} {p["time"]} | {p["place"]} ({p["country"]})' for p in plans_sorted]
    pick2 = st.selectbox("항목 선택", options)

    # 선택된 항목 찾기
    picked_place = pick2.split("|", 1)[1].strip()
    target = None
    for p in plans_sorted:
        label = f'{p["place"]} ({p["country"]})'
        if label == picked_place:
            target = p
            break

    if target:
        url = maps_search_url(target["maps_query"])
        st.link_button("Google Maps로 열기", url)
        st.components.v1.html(maps_embed_html(target["maps_query"]), height=280)

# 관리
st.markdown("<hr/>", unsafe_allow_html=True)
a, b, c = st.columns([1.2, 1.2, 3])
with a:
    if st.button("🗑️ 전체 초기화", use_container_width=True):
        st.session_state["plans"] = []
        st.success("전체 초기화 완료!")
with b:
    if st.button("❌ 마지막 1개 삭제", use_container_width=True):
        if st.session_state["plans"]:
            st.session_state["plans"].pop()
            st.success("마지막 항목 1개 삭제!")
        else:
            st.info("삭제할 항목이 없습니다.")

