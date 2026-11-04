import streamlit as st
import pandas as pd
import os
from datetime import datetime
from collections import Counter
from itertools import combinations

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS (Sky Blue Theme)
# ==========================================
st.set_page_config(
    page_title="Lao AI Professional v4.0",
    page_icon="🧠",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Grid Container สำหรับการ์ดความถี่ */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
        gap: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
        border: 1px solid #bae6fd;
        border-top: 4px solid #0284c7;
        border-radius: 12px;
        padding: 12px 6px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(2, 132, 199, 0.08);
    }
    .stat-num {
        font-size: 26px;
        font-weight: 800;
        color: #0c4a6e;
        line-height: 1.2;
    }
    .stat-count {
        font-size: 12px;
        font-weight: 600;
        color: #0369a1;
        background-color: #e0f2fe;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
        margin-top: 6px;
    }

    /* กล่องจับคู่เลข */
    .pair-box {
        background-color: #f0f9ff;
        border-left: 4px solid #0284c7;
        border-radius: 8px;
        padding: 12px 15px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .pair-title {
        font-weight: 700;
        color: #0369a1;
        margin-bottom: 8px;
        font-size: 15px;
    }
    .badge {
        display: inline-block;
        background-color: #ffffff;
        border: 1px solid #7dd3fc;
        border-radius: 6px;
        padding: 4px 8px;
        margin: 3px;
        font-weight: 600;
        color: #0c4a6e;
        font-size: 13px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .badge-highlight {
        background-color: #0284c7;
        border-color: #0369a1;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

VERSION = "4.0 WEB MOBILE"
CSV_FILE_NAME = "history_lao.csv"

# ==========================================
# SIDEBAR: จัดการข้อมูล & ตั้งค่า
# ==========================================
st.sidebar.header("⚙️ จัดการข้อมูล CSV")

# ฟังก์ชันโหลดข้อมูล CSV พร้อมระบบรีเฟรช
@st.cache_data(ttl=1)
def load_csv_data(filename):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename, header=None)
        except Exception:
            pass
    return pd.DataFrame({
        0: ["691489", "922679", "680172", "352415", "738155"],
        1: ["1489", "2679", "172", "2415", "8155"]
    })

df_history = load_csv_data(CSV_FILE_NAME)

# ปุ่มรีเฟรชข้อมูลล่าสุด
if st.sidebar.button("🔄 รีเฟรชข้อมูล CSV"):
    st.cache_data.clear()
    if "base_number" in st.session_state:
        del st.session_state.base_number
    st.rerun()

# ค้นหาเลขฐานล่าสุดจากแถวสุดท้ายของ CSV เสมอ
latest_base = "738155"
if df_history is not None and not df_history.empty:
    for row_idx in range(len(df_history) - 1, -1, -1):
        row_data = df_history.iloc[row_idx]
        found = False
        for val in row_data:
            val_str = str(val).strip()
            if val_str.isdigit() and len(val_str) >= 6:
                latest_base = val_str
                found = True
                break
        if found:
            break

# ==========================================
# FORMULAS (1 - 15)
# ==========================================
def formula5(number):
    digits = [int(x) for x in number]
    score = Counter()
    counter = Counter(digits)
    for digit, count in counter.items(): score[digit] += count * 5
    for i in range(len(digits) - 1): score[(digits[i] + digits[i + 1]) % 10] += 2
    for i in range(len(digits) - 1): score[(digits[i] * digits[i + 1]) % 10] += 2
    for i in range(len(digits) - 1): score[abs(digits[i] - digits[i + 1])] += 1
    ranking = sorted(score.items(), key=lambda x: (-x[1], x[0]))
    return "".join(str(digit) for digit, _ in ranking[:4]).zfill(4)

def formula1(number):
    a, b, c, d, e, f = [int(x) for x in number[:6]]
    value = ((a+b+c)*(d+e+f)+(a*f)+(c*e)) % 10000
    res = f"{value:04d}"
    return formula5(number) if res == "0000" else res

def formula2(number):
    a, b, c, d, e, f = [int(x) for x in number[:6]]
    return f"{((a*b)+(c*d)+(e*f)) % 10000:04d}"

def formula3(number):
    a, b, c, d, e, f = [int(x) for x in number[:6]]
    return f"{((a+b+c+d+e+f)*111) % 10000:04d}"

def formula4(number):
    a, b, c, d, e, f = [int(x) for x in number[:6]]
    value = ((a+b+c)*(d+e+f)) % 10000
    res = f"{value:04d}"
    return formula5(number) if res == "0000" else res

def formula6(number):
    a, b, c, d, e, f = [int(x) for x in number[:6]]
    return f"{((a+c+e)*(b+d+f)) % 10000:04d}"

def formula7(number):
    a, b, c, d, e, f = [int(x) for x in number[:6]]
    return f"{((a*10+b)+(e*10+f)) % 10000:04d}"

def formula8(number):
    a, b, c, d, e, f = [int(x) for x in number[:6]]
    return f"{((a+b+c+d+e+f)*123) % 10000:04d}"

def formula9(number):
    a, b, c, d, e, f = [int(x) for x in number[:6]]
    return f"{abs((a*100+b*10+c)-(d*100+e*10+f)) % 10000:04d}"

def formula10(number):
    a, b, c, d, e, f = [int(x) for x in number[:6]]
    return f"{((a*f)+(b*e)+(c*d)) % 10000:04d}"

def formula11(number):
    digits = [int(x) for x in number]
    results = []
    for i in range(len(digits)):
        for j in range(i + 1, len(digits)):
            results.append(f"{(digits[i] * digits[j]) % 100:02d}")
    counter = Counter(results)
    ranking = sorted(counter.items(), key=lambda x: (-x[1], int(x[0])))
    if not ranking: return "0000"
    if len(ranking) == 1: return ranking[0][0] * 2
    return ranking[0][0] + ranking[1][0]

def formula12(number):
    num_list = [int(x) for x in number]
    d, e = num_list[3], num_list[4]
    base = (d + e) % 10
    return f"{base}{(base+1)%10}{(base+2)%10}{(base+3)%10}"

def formula13(number):
    num_list = [int(x) for x in number]
    a, c, f = num_list[0], num_list[2], num_list[5]
    return f"{((a + c + f) * 9) % 10000:04d}"

def formula14(number):
    f = int(number[5])
    return f"{f}{f}{(f+1)%10}{(f+1)%10}"

def formula_neighbor(number):
    num_list = [int(x) for x in number]
    pos4, pos6 = num_list[3], num_list[5]
    res_front = (pos6 - 1) % 10
    res_back_start = (pos4 + 2) % 10
    return f"{res_front}{res_back_start}{(res_back_start+1)%10}{(res_back_start+2)%10}"

formulas = [
    ("Formula 1", formula1), ("Formula 2", formula2), ("Formula 3", formula3),
    ("Formula 4", formula4), ("Formula 5", formula5), ("Formula 6", formula6),
    ("Formula 7", formula7), ("Formula 8", formula8), ("Formula 9", formula9),
    ("Formula 10", formula10), ("Formula 11", formula11), ("Formula 12", formula12), 
    ("Formula 13", formula13), ("Formula 14", formula14), ("Formula Neighbor", formula_neighbor)
]

def calculate_formula_frequency(formula_outputs, top_n=6):
    counter = Counter()
    for result in formula_outputs.values():
        number = str(result).strip()
        if len(number) >= 4 and number.isdigit():
            counter.update(number)
    ranking = sorted(counter.items(), key=lambda item: (-item[1], int(item[0])))
    return counter, ranking[:top_n]

# ==========================================
# STREAMLIT UI
# ==========================================
st.title("🧠 LAO AI PROFESSIONAL")
day_name = datetime.now().strftime("%A")
st.caption(f"เวอร์ชัน: {VERSION} | วัน: {day_name}")

# แสดงตารางประวัติจาก history_lao.csv แบบพับเก็บได้
with st.expander("📂 ดูประวัติข้อมูลสถิติย้อนหลัง (history_lao.csv)"):
    if df_history is not None:
        st.dataframe(df_history, use_container_width=True)
    else:
        st.warning("⚠️ ยังไม่พบข้อมูลประวัติ CSV")

st.markdown("---")

# จัดการค่าเริ่มต้นในช่องกรอกเลขฐานให้ดึงจาก CSV ล่าสุดเสมอ
if "base_number" not in st.session_state or st.session_state.get("last_loaded_base") != latest_base:
    st.session_state.base_number = latest_base
    st.session_state.last_loaded_base = latest_base

base_input = st.text_input("ป้อนเลขฐาน (6 หลักขึ้นไป):", key="base_number", max_chars=10)

# ตัวเลือกจำนวนที่ต้องการแสดงผล (5 หรือ 6 ตัว)
display_count = st.radio("เลือกจำนวนตัวเลขความถี่สูงสุดที่ต้องการแสดง:", [5, 6], index=1, horizontal=True)

# 🚀 ปุ่มกดวิเคราะห์ (คำนวณใหม่สดๆ ทุกครั้งที่กด)
if st.button("🚀 วิเคราะห์ข้อมูล", type="primary", use_container_width=True):
    if len(base_input) < 6 or not base_input.isdigit():
        st.error("❌ กรุณากรอกเลขฐานอย่างน้อย 6 หลัก และต้องเป็นตัวเลขเท่านั้น")
    else:
        formula_outputs = {}
        for name, func in formulas:
            try:
                res = str(func(base_input)).strip()
                if res.isdigit():
                    formula_outputs[name] = res.zfill(4)[-4:]
            except Exception:
                pass

        counter, top_digits = calculate_formula_frequency(formula_outputs, top_n=display_count)
        valid_count = sum(1 for v in formula_outputs.values() if len(str(v)) >= 4 and str(v).isdigit())
        digits_only = [item[0] for item in top_digits]

        st.markdown(f"### 📊 เลขที่ปรากฏบ่อยเมื่อรวมผลลัพธ์จาก 15 สูตร (แสดง {display_count} อันดับ)")
        
        # แสดงผลเป็นการ์ด Responsive โทนสีฟ้า
        if top_digits:
            html_parts = ['<div class="grid-container">']
            for num, count in top_digits:
                html_parts.append(f'<div class="stat-card"><div class="stat-num">{num}</div><div class="stat-count">{count} ครั้ง</div></div>')
            html_parts.append('</div>')
            st.markdown("".join(html_parts), unsafe_allow_html=True)

        st.caption(f"ความถี้นี้นับจากเลข 4 หลักที่แต่ละสูตรสร้างขึ้น รวม {valid_count} สูตร")

        # ==========================================
        # เพิ่มส่วนชุดจับคู่เลขเด่น 2 ตัว และ 3 ตัว (วิน)
        # ==========================================
        if len(digits_only) >= 3:
            st.markdown("---")
            st.markdown("### 🎯 ชุดจับคู่เลขเด่น (จากผลการตัดสไลซ์)")

            pairs_2d = [f"{a}{b}" for a, b in combinations(digits_only, 2)]
            pairs_3d = [f"{a}{b}{c}" for a, b, c in combinations(digits_only, 3)]
            
            top_3_straight = "".join(digits_only[:3])
            top_2_straight = "".join(digits_only[:2])

            # แสดงชุดเน้นพิเศษ
            st.markdown(f"""
            <div class="pair-box" style="border-left-color: #0284c7; background-color: #e0f2fe;">
                <div class="pair-title">🔹 ชุดเน้นพิเศษ (Top Pick จากอันดับ 1-3)</div>
                <span class="badge badge-highlight">3 ตัว: {top_3_straight}</span>
                <span class="badge badge-highlight">2 ตัว: {top_2_straight}</span>
            </div>
            """, unsafe_allow_html=True)

            # แสดงชุด 2 ตัว
            badges_2d = "".join([f'<span class="badge">{p}</span>' for p in pairs_2d])
            st.markdown(f"""
            <div class="pair-box">
                <div class="pair-title">🎲 ชุด 2 ตัวจับคู่วิน ({len(pairs_2d)} ชุด)</div>
                {badges_2d}
            </div>
            """, unsafe_allow_html=True)

            # แสดงชุด 3 ตัว
            badges_3d = "".join([f'<span class="badge">{p}</span>' for p in pairs_3d])
            st.markdown(f"""
            <div class="pair-box">
                <div class="pair-title">🎲 ชุด 3 ตัวจับคู่วิน ({len(pairs_3d)} ชุด)</div>
                {badges_3d}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 3. เลขเด่นจากการรวมสูตร")
        
        main_group = [d for d, c in top_digits if c >= 10]
        sub_group = [d for d, c in top_digits if 5 <= c < 10]
        low_group = [str(i) for i in range(10) if i not in [int(d) for d, _ in top_digits]]

        st.write(f"• **กลุ่มเด่น:** {' – '.join(main_group) if main_group else '-'}")
        st.write(f"• **กลุ่มรอง:** {' – '.join(sub_group) if sub_group else '-'}")
        st.write(f"• **เลขอื่นๆ:** {' – '.join(low_group) if low_group else '-'}")
