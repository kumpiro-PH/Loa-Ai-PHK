# app.py - Lao AI Professional v4.1 (Full Complete Code with Corrected Latest Row Retrieval)
import os
import base64
import requests
from io import StringIO
import streamlit as st
import pandas as pd
from datetime import datetime
from collections import Counter
from itertools import combinations

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS (Sky Blue Theme)
# ==========================================
st.set_page_config(
    page_title="Lao AI Professional v4.1",
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

VERSION = "4.2 GITHUB MON-FRI 3-WAY FUSION"

DAY_MAP = {
    "Monday": "mon", "Tuesday": "tue", "Wednesday": "wed",
    "Thursday": "thu", "Friday": "fri",
}
DAY_CSV_MAP = {day: f"history_lao_{code}.csv" for day, code in DAY_MAP.items()}
ALLOWED_CSV_FILES = set(DAY_CSV_MAP.values())
WEEKDAYS = list(DAY_MAP.keys())
DAILY_NUMBERS = {
    "Monday": "940627", "Tuesday": "017562", "Wednesday": "394517",
    "Thursday": "643951", "Friday": "974516",
}
EXPECTED_COLUMNS = ["date", "special", "first_prize", "top_3", "bottom_2"]

# ==========================================
# 2. ฟังก์ชันจัดการ CSV และ สูตรคำนวณ (1-15)
# ==========================================
def parse_draw_date(value):
    """รองรับวันที่ DD/MM/YYYY ทั้ง พ.ศ. และ ค.ศ."""
    try:
        day, month, year = [int(part) for part in str(value).strip().split("/")[:3]]
        if year > 2400:
            year -= 543
        elif year < 100:
            year += 2000
        return pd.Timestamp(year=year, month=month, day=day)
    except Exception:
        return pd.NaT


def normalize_csv(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    mapping = {
        "วันที่": "date", "date_be": "date",
        "เลข 6 ตัว": "special", "รางวัลพิเศษ": "special",
        "รางวัลที่ 1": "first_prize", "รางวัลที่1": "first_prize",
        "3 ตัวบน": "top_3", "เลข 3 ตัวบน": "top_3",
        "2 ตัวล่าง": "bottom_2", "เลข 2 ตัวล่าง": "bottom_2",
    }
    df = df.rename(columns=mapping)
    if not any(col in df.columns for col in EXPECTED_COLUMNS) and len(df.columns) >= 5:
        df = df.iloc[:, :5].copy()
        df.columns = EXPECTED_COLUMNS
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = "-"
    df = df[EXPECTED_COLUMNS].fillna("").astype(str)
    df["_sort_date"] = df["date"].apply(parse_draw_date)
    df = df.sort_values("_sort_date", ascending=False, na_position="last")
    return df.drop(columns=["_sort_date"]).reset_index(drop=True)


def github_settings():
    return (
        st.secrets.get("GITHUB_TOKEN", ""),
        st.secrets.get("GITHUB_REPO", ""),
        st.secrets.get("GITHUB_BRANCH", "main"),
    )


def read_csv_text(raw_text):
    """อ่าน CSV ได้ทั้งแบบมี header และไม่มี header"""
    try:
        frame = pd.read_csv(StringIO(raw_text), dtype=str, keep_default_na=False)
        aliases = {
            "date", "date_be", "วันที่", "special", "เลข 6 ตัว", "รางวัลพิเศษ",
            "first_prize", "รางวัลที่ 1", "top_3", "3 ตัวบน", "เลข 3 ตัวบน",
            "bottom_2", "2 ตัวล่าง", "เลข 2 ตัวล่าง",
        }
        if not any(str(column).strip() in aliases for column in frame.columns):
            frame = pd.read_csv(
                StringIO(raw_text),
                header=None,
                dtype=str,
                keep_default_na=False,
            )
            if frame.shape[1] >= 5:
                frame = frame.iloc[:, :5]
                frame.columns = EXPECTED_COLUMNS
        return normalize_csv(frame)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)


def load_csv_data(filename):
    """โหลดเฉพาะ CSV วันจันทร์-ศุกร์จาก GitHub API พร้อม fallback local"""
    if filename not in ALLOWED_CSV_FILES:
        st.error(f"ไม่อนุญาตให้อ่านไฟล์: {filename}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    token, repo, branch = github_settings()
    if token and repo:
        url = f"https://api.github.com/repos/{repo}/contents/{filename}"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        try:
            response = requests.get(url, headers=headers, params={"ref": branch}, timeout=15)
            if response.status_code == 200:
                raw = base64.b64decode(response.json()["content"]).decode("utf-8-sig")
                return read_csv_text(raw)
            if response.status_code != 404:
                st.warning(f"GitHub อ่าน {filename} ไม่สำเร็จ: HTTP {response.status_code}")
        except Exception as exc:
            st.warning(f"เชื่อมต่อ GitHub เพื่ออ่าน {filename} ไม่สำเร็จ: {exc}")

    if os.path.exists(filename):
        try:
            return read_csv_text(open(filename, "r", encoding="utf-8-sig").read())
        except Exception as exc:
            st.error(f"ไม่สามารถอ่านไฟล์ {filename}: {exc}")
    return pd.DataFrame(columns=EXPECTED_COLUMNS)


def save_csv_data(filename, dataframe, commit_message):
    """บันทึก CSV รายวันขึ้น GitHub ผ่าน Contents API"""
    if filename not in ALLOWED_CSV_FILES:
        st.error(f"ไม่อนุญาตให้บันทึกไฟล์: {filename}")
        return False
    token, repo, branch = github_settings()
    if not token or not repo:
        st.error("กรุณาตั้งค่า GITHUB_TOKEN และ GITHUB_REPO ใน Streamlit Secrets")
        return False
    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    try:
        current = requests.get(url, headers=headers, params={"ref": branch}, timeout=15)
        sha = current.json().get("sha") if current.status_code == 200 else None
        csv_text = normalize_csv(dataframe).to_csv(index=False, encoding="utf-8-sig")
        body = {
            "message": commit_message,
            "content": base64.b64encode(csv_text.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        if sha:
            body["sha"] = sha
        result = requests.put(url, headers=headers, json=body, timeout=20)
        if result.status_code in (200, 201):
            normalize_csv(dataframe).to_csv(filename, index=False, encoding="utf-8-sig")
            return True
        st.error(f"GitHub บันทึกไม่สำเร็จ: HTTP {result.status_code} - {result.text}")
        return False
    except Exception as exc:
        st.error(f"เกิดข้อผิดพลาดขณะบันทึก GitHub: {exc}")
        return False


def load_specific_day_history(day_en):
    filename = DAY_CSV_MAP.get(day_en)
    return load_csv_data(filename) if filename else pd.DataFrame(columns=EXPECTED_COLUMNS)


def load_all_weekday_history():
    """รวมประวัติจาก CSV ทั้ง 5 วันและเรียงตามวันที่"""
    frames = [load_csv_data(filename) for filename in DAY_CSV_MAP.values()]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    return normalize_csv(pd.concat(frames, ignore_index=True))


def get_latest_valid_base(dataframe):
    """หาเลขฐาน 6 หลักจากคอลัมน์ special ของงวดวันที่ใหม่ที่สุด"""
    if dataframe is None or dataframe.empty:
        return None
    for _, row in normalize_csv(dataframe).iterrows():
        value = str(row.get("special", "")).strip()
        if value.isdigit() and len(value) >= 6:
            return value[:6]
    return None


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
# 3. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("### เลือกเมนูการใช้งาน")
menu = st.sidebar.selectbox(
    "",
    [
        "1. อัปเดตผลรางวัล",
        "2. แสดงประวัติ (History)",
        "3. ลบข้อมูลงวดล่าสุด",
        "4. Formula Ranking (จัดอันดับสูตร)",
        "5. Forward Prediction (ทำนายงวดถัดไป)"
    ],
    label_visibility="collapsed"
)

# รวมประวัติจาก CSV Monday-Friday เท่านั้น
df_history = load_all_weekday_history()
latest_base = get_latest_valid_base(df_history) or "000000"

# ==========================================
# 4. MAIN CONTENT
# ==========================================
if menu == "1. อัปเดตผลรางวัล":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 📝 อัปเดตผลรางวัลหวยลาวใหม่")
    
    with st.form("update_form"):
        input_date = st.text_input("ใส่วันที่ (DD/MM/YYYY เช่น 04/11/2569)")
        input_6d = st.text_input("เลขฐาน / รางวัล 6 หลัก (6 หลักขึ้นไป):")
        submitted = st.form_submit_button("บันทึกผลรางวัล")
        
        if submitted:
            if len(input_6d) >= 6 and input_6d.isdigit():
                val_6d = input_6d[:6]
                val_4d = input_6d[-4:]
                val_3d = input_6d[-3:]
                val_2d = input_6d[-2:]
                
                new_row = pd.DataFrame([{
                    "date": input_date,
                    "special": val_6d,
                    "first_prize": val_4d,
                    "top_3": val_3d,
                    "bottom_2": val_2d
                }])
                
                dt_obj = parse_draw_date(input_date)
                if pd.isna(dt_obj):
                    st.error("รูปแบบวันที่ไม่ถูกต้อง กรุณาใช้ DD/MM/YYYY")
                    st.stop()
                day_en = dt_obj.day_name()
                if day_en not in DAY_CSV_MAP:
                    st.error("ระบบรองรับเฉพาะผลวันจันทร์-ศุกร์")
                    st.stop()

                target_file = DAY_CSV_MAP[day_en]
                current_df = load_csv_data(target_file)
                new_row = pd.DataFrame([{
                    "date": input_date.strip(),
                    "special": val_6d,
                    "first_prize": val_4d,
                    "top_3": val_3d,
                    "bottom_2": val_2d,
                }])
                updated = normalize_csv(pd.concat([current_df, new_row], ignore_index=True))
                if save_csv_data(target_file, updated, f"Update {target_file} - {input_date}"):
                    st.success(f"บันทึกและ Sync `{target_file}` ไป GitHub เรียบร้อยแล้ว")
                st.rerun()
            else:
                st.error("กรุณากรอกตัวเลขอย่างน้อย 6 หลักขึ้นไป")

elif menu == "2. แสดงประวัติ (History)":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 📂 ประวัติรวมจาก CSV วันจันทร์–ศุกร์")
    if df_history is not None and not df_history.empty:
        st.dataframe(df_history, use_container_width=True)
    else:
        st.warning("⚠️ ยังไม่พบข้อมูลประวัติ CSV")

elif menu == "3. ลบข้อมูลงวดล่าสุด":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 🗑️ ลบข้อมูลงวดล่าสุดออกจากระบบ")
    if df_history is not None and not df_history.empty:
        st.write("เลือกวัน แล้วลบงวดล่าสุดจากไฟล์ประจำวันนั้น")
        delete_day = st.selectbox("เลือกไฟล์วันที่ต้องการลบ", WEEKDAYS, key="delete_day")
        delete_file = DAY_CSV_MAP[delete_day]
        delete_df = load_csv_data(delete_file)
        if not delete_df.empty:
            st.write(delete_df.head(1))
            if st.button("❌ ยืนยันลบงวดล่าสุดและ Sync GitHub", type="primary"):
                updated_delete = delete_df.iloc[1:].reset_index(drop=True)
                if save_csv_data(delete_file, updated_delete, f"Delete latest draw from {delete_file}"):
                    st.success(f"ลบงวดล่าสุดจาก {delete_file} เรียบร้อยแล้ว")
                    st.rerun()
        else:
            st.warning(f"ไม่มีข้อมูลใน {delete_file}")
    else:
        st.warning("ไม่มีข้อมูลให้ลบ")

elif menu == "4. Formula Ranking (จัดอันดับสูตร)":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 🏆 Formula Ranking (ข้อมูลรวมจาก CSV วันจันทร์–ศุกร์)")
    if df_history is not None and not df_history.empty:
        formula_scores = {name: 0 for name, _ in formulas}
        col_name = "special" if "special" in df_history.columns else df_history.columns[0]
        
        for idx, row in df_history.iterrows():
            v_str = str(row[col_name]).strip()
            if v_str.isdigit() and len(v_str) >= 6:
                for name, func in formulas:
                    try:
                        func(v_str)
                        formula_scores[name] += 1
                    except:
                        pass
        sorted_formulas = sorted(formula_scores.items(), key=lambda x: x[1], reverse=True)
        for rank, (fname, score) in enumerate(sorted_formulas, 1):
            st.write(f"**{rank}. {fname}** — คะแนนประสิทธิภาพ: {score}")
    else:
        st.warning("ยังไม่มีข้อมูลสำหรับจัดอันดับสูตร")

elif menu == "5. Forward Prediction (ทำนายงวดถัดไป)":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 🔮 Forward Prediction (คำนวณผสานสถิติ 3 แหล่งข้อมูล)")
    
    day_selected = st.selectbox(
        "เลือกวันของงวดถัดไป / วันที่ต้องการวิเคราะห์",
        WEEKDAYS
    )

    # เลขฐานรวมล่าสุดจากข้อมูลรวม CSV ทั้ง 5 วัน
    latest_all = get_latest_valid_base(df_history) or "000000"

    # อ่านเลขฐานล่าสุดของไฟล์วันที่เลือก
    df_day_specific = load_specific_day_history(day_selected)
    latest_day = get_latest_valid_base(df_day_specific) or "000000"

    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"📊 **งวดรวมล่าสุด (CSV Monday–Friday)**\n\nเลขฐาน 6 หลัก: `{latest_all}`\n\n3 ตัว/4 ตัว: `{latest_all[-3:]}` / `{latest_all[-4:]}`")
    with col_b:
        st.success(f"📌 **งวดประจำวัน {day_selected} ล่าสุด**\n\nเลขฐาน 6 หลัก: `{latest_day}`\n\n3 ตัว/4 ตัว: `{latest_day[-3:]}` / `{latest_day[-4:]}`")

    if latest_all == "000000":
        st.warning("ไม่พบเลขฐาน 6 หลักใน CSV ทั้ง 5 วัน กรุณาตรวจสอบคอลัมน์ special")
    if latest_day == "000000":
        st.warning(f"ไม่พบเลขฐาน 6 หลักใน {DAY_CSV_MAP[day_selected]}")

    daily_6 = DAILY_NUMBERS.get(day_selected, "000000")
    st.write(f"🎯 **ชุดเลขประจำวัน ({day_selected}):** `{daily_6}`")

    display_count = st.radio("เลือกจำนวนตัวเลขความถี่สูงสุดที่ต้องการแสดง:", [5, 6], index=1, horizontal=True)

    if st.button("🚀 ประมวลผลทำนายเลข (ผสาน 3 ส่วน)", type="primary", use_container_width=True):
        outputs_all = {}
        outputs_day = {}
        
        for name, func in formulas:
            try:
                res_a = str(func(latest_all)).strip()
                if res_a.isdigit():
                    outputs_all[name] = res_a.zfill(4)[-4:]
                res_d = str(func(latest_day)).strip()
                if res_d.isdigit():
                    outputs_day[name] = res_d.zfill(4)[-4:]
            except Exception:
                pass

        digit_scores = {str(i): 0.0 for i in range(10)}

        # 1. เลขประจำวันให้โบนัสสูงสุด (+2.0 แต้ม)
        for d in daily_6:
            digit_scores[d] += 2.0

        # 2. คะแนนจากสูตรของงวดรวมล่าสุด
        counter_all, _ = calculate_formula_frequency(outputs_all, top_n=10)
        for num_str, count in counter_all.items():
            for d in num_str:
                digit_scores[d] += float(count) * 0.3

        # 3. คะแนนจากสูตรของงวดรายวันล่าสุด
        counter_day, _ = calculate_formula_frequency(outputs_day, top_n=10)
        for num_str, count in counter_day.items():
            for d in num_str:
                digit_scores[d] += float(count) * 0.3

        sorted_digits = sorted(digit_scores.keys(), key=lambda k: digit_scores[k], reverse=True)
        top_digits_merged = [(d, digit_scores[d]) for d in sorted_digits[:display_count]]
        digits_only = [item[0] for item in top_digits_merged]

        st.markdown(f"### 📊 ผลลัพธ์เลขเด่นผสาน 3 ส่วน ({day_selected})")
        
        if top_digits_merged:
            html_parts = ['<div class="grid-container">']
            for num, score in top_digits_merged:
                html_parts.append(f'<div class="stat-card"><div class="stat-num">{num}</div><div class="stat-count">{score:.1f} แต้ม</div></div>')
            html_parts.append('</div>')
            st.markdown("".join(html_parts), unsafe_allow_html=True)

        if len(digits_only) >= 3:
            st.markdown("---")
            st.markdown("### 🎯 ชุดจับคู่เลขเด่น (จากผลการวิเคราะห์ผสาน)")

            pairs_2d = [f"{a}{b}" for a, b in combinations(digits_only, 2)]
            pairs_3d = [f"{a}{b}{c}" for a, b, c in combinations(digits_only, 3)]
            
            top_3_straight = "".join(digits_only[:3])
            top_2_straight = "".join(digits_only[:2])

            st.markdown(f"""
            <div class="pair-box" style="border-left-color: #0284c7; background-color: #e0f2fe;">
                <div class="pair-title">🔹 ชุดเน้นพิเศษ (Top Pick จากอันดับ 1-3)</div>
                <span class="badge badge-highlight">3 ตัว: {top_3_straight}</span>
                <span class="badge badge-highlight">2 ตัว: {top_2_straight}</span>
            </div>
            """, unsafe_allow_html=True)

            badges_2d = "".join([f'<span class="badge">{p}</span>' for p in pairs_2d])
            st.markdown(f"""
            <div class="pair-box">
                <div class="pair-title">🎲 ชุด 2 ตัวจับคู่วิน ({len(pairs_2d)} ชุด)</div>
                {badges_2d}
            </div>
            """, unsafe_allow_html=True)

            badges_3d = "".join([f'<span class="badge">{p}</span>' for p in pairs_3d])
            st.markdown(f"""
            <div class="pair-box">
                <div class="pair-title">🎲 ชุด 3 ตัวจับคู่วิน ({len(pairs_3d)} ชุด)</div>
                {badges_3d}
            </div>
            """, unsafe_allow_html=True)
