# -*- coding: utf-8 -*-
import streamlit as st
from datetime import date, time
from urllib.parse import quote_plus
import csv
import io

st.set_page_config(page_title="유럽 여행 계획표", layout="wide")

# ----------------------------
# 상태 저장
# ----------------------------
if "plans" not in st.session_state:
    st.session_state["plans"] = []
if "seq" not in st.session_state:
    st.session_state["seq"] = 1  # 항목 고유 ID용

# ----------------------------
# 무료/키 없는 "후보 사전" (핀란드/포르투갈/스페인)
# ----------------------------
PLACES = {
    "핀란드": [
        ("헬싱키", "Helsinki, Finland"),
        ("에스포", "Espoo, Finland"),
        ("탐페레", "Tampere, Finland"),
        ("투르쿠", "Turku, Finland"),
        ("로바니에미", "Rovaniemi, Finland"),
        ("라플란드", "Lapland, Finland"),
        ("헬싱키 공항", "Helsinki Airport (HEL), Finland"),
        ("로바니에미 공항", "Rovaniemi Airport, Finland"),
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
        ("리스본 공항", "Lisbon Airport (LIS), Portugal"),
        ("포르투 공항", "Porto Airport (OPO), Portugal"),
        ("파루 공항", "Faro Airport (FAO), Portugal"),
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
        ("바르셀로나 공항", "Barcelona Airport (BCN), Spain"),
        ("마드리드 공항", "Madrid-Barajas Airport (MAD), Spain"),
        ("세비야 공항", "Seville Airport (SVQ), Spain"),
        ("말라가 공항", "Málaga Airport (AGP), Spain"),
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
      height="240"
      style="border:0; border-radius:12px;"
      loading="lazy"
      allowfullscreen
      referrerpolicy="no-referrer-when-downgrade"
      src="https://www.google.com/maps?q={q2}&output=embed">
    </iframe>
    """

# ----------------------------
# CSV 다운로드 생성
# ----------------------------
def make_csv_bytes(plans):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "time", "country", "place", "category", "priority", "done", "note", "maps_query"])
    for p in plans:
        writer.writerow([p["date"], p["time"], p["country"], p["place"], p["category"], p["priority"], p["done"], p["note"], p["maps_query"]])
    return output.getvalue().encode("utf-8-sig")

# ----------------------------
# UI
# ----------------------------
st.markdown("<h1 style='text-align:center; margin-bottom: 0.2rem;'>유럽 여행 계획표</h1>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# 입력(상단)
c1, c2, c3 = st.columns([1.2, 2.6, 1.8])

CATEGORIES = ["관광", "맛집", "쇼핑", "이동", "숙소", "기타"]
PRIORITIES = ["필수", "가능", "여유"]

with c1:
    d = st.date_input("날짜", value=date.today())
    t = st.time_input("시간", value=time(9, 0))
    category = st.selectbox("카테고리", CATEGORIES, index=0)
    priority = st.selectbox("우선순위", PRIORITIES, index=0)

with c2:
    country_filter = st.multiselect(
        "방문 국가 선택",
        ["핀란드", "포르투갈", "스페인"],
        default=["핀란드", "포르투갈", "스페인"]
    )
    q = st.text_input("장소 검색(입력하면 후보가 뜹니다)", placeholder="예: 공항 / 리스본 / 사그라다 / helsinki")

    cand = [x for x in ALL if x["country"] in country_filter]
    q_low = q.strip().lower()

    if q_low:
        def match_score(item):
            text = (item["label"] + " " + item["query"]).lower()
            if q_low in text:
                return 1000 - text.find(q_low)
            return -1

        scored = [(match_score(item), item) for item in cand]
        cand = [it for s, it in sorted(scored, key=lambda x: x[0], reverse=True) if s >= 0][:25]
    else:
        cand = cand[:25]

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
        st.components.v1.html(maps_embed_html(picked_item["query"]), height=260)
        st.caption("※ 키 없는 버전: 미리 등록된 후보에서 선택하는 방식입니다.")
    else:
        st.caption("왼쪽에서 후보를 선택하면\n여기에 지도 미리보기/링크가 표시됩니다.")

# 추가 버튼(가운데)
l, m, r = st.columns([3, 1.2, 3])
with m:
    add_clicked = st.button("➕ 일정 추가", use_container_width=True)

if add_clicked:
    if not picked_item:
        st.warning("후보를 선택해 주세요.")
    else:
        st.session_state["plans"].append(
            {
                "id": st.session_state["seq"],
                "date": str(d),
                "time": t.strftime("%H:%M"),
                "place": picked_item["label"].split(" · ")[0],
                "country": picked_item["country"],
                "maps_query": picked_item["query"],
                "note": note.strip(),
                "category": category,
                "priority": priority,
                "done": False,
            }
        )
        st.session_state["seq"] += 1
        st.success("추가되었습니다! 아래 DAY별 계획에 반영됐어요.")

st.markdown("<hr/>", unsafe_allow_html=True)

# 상단 옵션: 필터/다운로드
top1, top2, top3, top4 = st.columns([1.4, 1.4, 1.4, 2.4])

with top1:
    f_category = st.selectbox("표시 카테고리", ["전체"] + CATEGORIES)
with top2:
    f_priority = st.selectbox("표시 우선순위", ["전체"] + PRIORITIES)
with top3:
    show_done = st.selectbox("완료 항목", ["전체", "미완료만", "완료만"])
with top4:
    if st.session_state["plans"]:
        csv_bytes = make_csv_bytes(st.session_state["plans"])
        st.download_button(
            "⬇️ CSV 다운로드",
            data=csv_bytes,
            file_name="europe_trip_plan.csv",
            mime="text/csv",
            use_container_width=True
        )

# ----------------------------
# 결과: 날짜별 그룹(DAY1/DAY2…)
# ----------------------------
st.subheader("일자별 계획 (DAY별)")

def passes_filters(p):
    if f_category != "전체" and p["category"] != f_category:
        return False
    if f_priority != "전체" and p["priority"] != f_priority:
        return False
    if show_done == "미완료만" and p["done"] is True:
        return False
    if show_done == "완료만" and p["done"] is False:
        return False
    return True

filtered = [p for p in st.session_state["plans"] if passes_filters(p)]
filtered_sorted = sorted(filtered, key=lambda x: (x["date"], x["time"], x["country"], x["place"]))

if not filtered_sorted:
    st.info("표시할 일정이 없습니다. (필터를 해제하거나 일정을 추가해 주세요.)")
else:
    dates = sorted({p["date"] for p in filtered_sorted})
    date_to_day = {d: i + 1 for i, d in enumerate(dates)}

    for d0 in dates:
        day_no = date_to_day[d0]
        st.markdown(f"## DAY{day_no}  ·  {d0}")
        st.markdown("---")

        day_items = [p for p in filtered_sorted if p["date"] == d0]

        # 표 + 완료 체크(항목별)
        # checkbox는 개별 key가 필요
        for p in day_items:
            row = st.columns([0.8, 1.1, 1.1, 2.0, 1.2, 1.1, 2.5])
            # 완료 체크
            with row[0]:
                new_done = st.checkbox("완료", value=p["done"], key=f"done_{p['id']}")
            p["done"] = new_done

            with row[1]:
                st.markdown(f"**{p['time']}**")
            with row[2]:
                st.markdown(p["country"])
            with row[3]:
                st.markdown(f"**{p['place']}**")
            with row[4]:
                st.markdown(p["category"])
            with row[5]:
                st.markdown(p["priority"])
            with row[6]:
                if p["note"]:
                    st.markdown(p["note"])
                else:
                    st.markdown("")

        st.markdown("### 지도 보기")
        options = [f'{p["time"]} | {p["place"]} ({p["country"]})' for p in day_items]
        pick = st.selectbox(f"DAY{day_no} 항목 선택", options, key=f"pick_{d0}")

        picked_place = pick.split("|", 1)[1].strip()
        target = None
        for p in day_items:
            label = f'{p["place"]} ({p["country"]})'
            if label == picked_place:
                target = p
                break

        if target:
            url = maps_search_url(target["maps_query"])
            st.link_button("Google Maps로 열기", url, key=f"link_{d0}")
            st.components.v1.html(maps_embed_html(target["maps_query"]), height=260)

        st.markdown("<br/>", unsafe_allow_html=True)

# ----------------------------
# 관리
# ----------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
a, b, c = st.columns([1.2, 1.2, 3])
with a:
    if st.button("🗑️ 전체 초기화", use_container_width=True):
        st.session_state["plans"] = []
        st.session_state["seq"] = 1
        st.success("전체 초기화 완료!")
with b:
    if st.button("❌ 마지막 1개 삭제", use_container_width=True):
        if st.session_state["plans"]:
            st.session_state["plans"].pop()
            st.success("마지막 항목 1개 삭제!")
        else:
            st.info("삭제할 항목이 없습니다.")
