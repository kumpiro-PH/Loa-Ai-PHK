# app.py - Lao AI Professional v4.1 (GitHub API Sync & Mon-Fri Separated)
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from collections import Counter
from itertools import combinations
import base64
import requests
from io import StringIO

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS (Sky Blue Theme)
# ==========================================
st.set_page_config(
    page_title="หวยลาวพัฒนา v4.1",
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

VERSION = "4.1 GITHUB API SYNC ENGINE"

DAY_MAP = {
    "Monday": "mon",
    "Tuesday": "tue",
    "Wednesday": "wed",
    "Thursday": "thu",
    "Friday": "fri",
}

DAILY_NUMBERS = {
    "Monday": "940627",
    "Tuesday": "017562",
    "Wednesday": "394517",
    "Thursday": "643951",
    "Friday": "974516",
}

# ==========================================
# 2. GITHUB API & CSV FUNCTIONS
# ==========================================
def normalize_date_format(date_str):
    date_str = str(date_str).strip()
    parts = date_str.split('/')
    if len(parts) == 3:
        d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
        if y < 2400: # แปลง ค.ศ. เป็น พ.ศ. เสมอเพื่อความเสถียร
            y += 543
        return f"{d:02d}/{m:02d}/{y}"
    return date_str

def parse_date_for_sort(date_str):
    try:
        parts = str(date_str).strip().split('/')
        if len(parts) == 3:
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            if y > 2400: # แปลง พ.ศ. เป็น ค.ศ. ชั่วคราวเพื่อให้ datetime เปรียบเทียบได้ถูกต้อง
                y -= 543
            return datetime(y, m, d)
    except Exception:
        pass
    return datetime(1900, 1, 1)

def load_csv_data_from_github(filename):
    """อ่าน CSV จาก GitHub API (พร้อม fallback มาอ่านในเครื่องถ้าดึง API ไม่ได้)"""
    github_token = st.secrets.get("GITHUB_TOKEN")
    repo_name = st.secrets.get("GITHUB_REPO")
    
    if github_token and repo_name and filename:
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json"
        }
        file_url = f"https://api.github.com/repos/{repo_name}/contents/{filename}"
        try:
            res = requests.get(file_url, headers=headers)
            if res.status_code == 200:
                file_data = res.json()
                content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
                df = pd.read_csv(StringIO(content_decoded), dtype=str, keep_default_na=False)
                df.columns = df.columns.str.strip()
                return df
        except Exception:
            pass
            
    # Fallback อ่านในเครื่อง
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename, dtype=str, keep_default_na=False)
        except Exception:
            pass
            
    return pd.DataFrame(columns=["date", "special", "first_prize", "top_3", "bottom_2"])

def save_history_to_github(target_day_code, new_row_df):
    """บันทึกและซิงก์ข้อมูล CSV ตรงขึ้น GitHub ผ่าน API อัตโนมัติ"""
    filename = f"history_lao_{target_day_code}.csv"
    github_token = st.secrets.get("GITHUB_TOKEN")
    repo_name = st.secrets.get("GITHUB_REPO")
    branch = st.secrets.get("GITHUB_BRANCH", "main")
    
    if not github_token or not repo_name:
        st.error("ยังไม่ได้ตั้งค่า GITHUB_TOKEN หรือ GITHUB_REPO ใน Streamlit Secrets")
        return False
        
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }
    file_url = f"https://api.github.com/repos/{repo_name}/contents/{filename}"
    
    # 1. ดึงไฟล์เดิมมาจาก GitHub เพื่อเอา SHA และข้อมูลเดิม
    res = requests.get(file_url, headers=headers)
    file_sha = None
    existing_df = pd.DataFrame(columns=["date", "special", "first_prize", "top_3", "bottom_2"])
    
    if res.status_code == 200:
        file_data = res.json()
        file_sha = file_data["sha"]
        content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
        existing_df = pd.read_csv(StringIO(content_decoded), dtype=str, keep_default_na=False)
        existing_df.columns = existing_df.columns.str.strip()
        
    # 2. รวมข้อมูลใหม่กับข้อมูลเดิม (กรองวันที่ซ้ำออก)
    new_date = new_row_df.iloc[0]["date"]
    if not existing_df.empty and "date" in existing_df.columns:
        existing_df = existing_df[existing_df["date"] != new_date]
        
    updated_df = pd.concat([new_row_df, existing_df], ignore_index=True)
    
    # 3. จัดเรียงวันที่จากใหม่ไปเก่าเสมอ
    if "date" in updated_df.columns:
        updated_df["_temp_date"] = updated_df["date"].apply(parse_date_for_sort)
        updated_df = updated_df.sort_values(by="_temp_date", ascending=False, na_position="last")
        updated_df = updated_df.drop(columns=["_temp_date"])
        
    # 4. แปลงเป็น CSV string และเข้ารหัส Base64
    csv_string = updated_df.to_csv(index=False, encoding="utf-8")
    encoded_content = base64.b64encode(csv_string.encode("utf-8")).decode("utf-8")
    
    # 5. ส่งคำขอ PUT ไปที่ GitHub API เพื่อ Commit อัตโนมัติ
    payload = {
        "message": f"Update {filename} for {new_date} via Streamlit App",
        "content": encoded_content,
        "branch": branch
    }
    if file_sha:
        payload["sha"] = file_sha
        
    put_res = requests.put(file_url, headers=headers, json=payload)
    return put_res.status_code in [200, 201]

def load_specific_day_history(day_en):
    day_code = DAY_MAP.get(day_en, "mon")
    filename = f"history_lao_{day_code}.csv"
    return load_csv_data_from_github(filename)

def load_weekday_history():
    weekday_codes = ["mon", "tue", "wed", "thu", "fri"]
    dfs = []
    for code in weekday_codes:
        filename = f"history_lao_{code}.csv"
        df_temp = load_csv_data_from_github(filename)
        if df_temp is not None and not df_temp.empty:
            dfs.append(df_temp)
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    return pd.DataFrame(columns=["date", "special", "first_prize", "top_3", "bottom_2"])


# ==========================================
# 3. FORMULA ENGINE (1-15)
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
# 4. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("### เลือกเมนูการใช้งาน")
menu = st.sidebar.selectbox(
    "",
    [
        "1. อัปเดตผลรางวัล",
        "2. แสดงประวัติแยกรายวัน (Mon-Fri)",
        "3. Formula Ranking (จัดอันดับสูตร)",
        "4. Forward Prediction (ทำนายงวดถัดไป)"
    ],
    label_visibility="collapsed"
)


# ==========================================
# 5. MAIN CONTENT
# ==========================================
if menu == "1. อัปเดตผลรางวัล":
    st.title("🧠 หวยลาวพัฒนา")
    st.markdown("### 📝 อัปเดตผลรางวัลหวยลาวใหม่ (ซิงก์ตรงขึ้น GitHub อัตโนมัติ)")
    
    with st.form("update_form"):
        input_date = st.text_input("ใส่วันที่ (DD/MM/YYYY เช่น 08/11/2569)")
        input_6d = st.text_input("เลขฐาน / รางวัล 6 หลัก (6 หลักขึ้นไป):")
        submitted = st.form_submit_button("บันทึกและซิงก์ขึ้น GitHub")
        
        if submitted:
            if len(input_6d) >= 6 and input_6d.isdigit():
                val_6d = input_6d[:6]
                val_4d = input_6d[-4:]
                val_3d = input_6d[-3:]
                val_2d = input_6d[-2:]
                
                normalized_date = normalize_date_format(input_date)
                new_row = pd.DataFrame([{
                    "date": normalized_date,
                    "special": val_6d,
                    "first_prize": val_4d,
                    "top_3": val_3d,
                    "bottom_2": val_2d
                }])
                
                try:
                    dt_obj = datetime.strptime(input_date.strip(), "%d/%m/%Y")
                    day_en = dt_obj.strftime("%A")
                    
                    if day_en not in DAY_MAP:
                        st.error(f"❌ ไม่อนุญาตให้บันทึกข้อมูลของวัน {day_en} (ระบบรองรับเฉพาะวันจันทร์ - ศุกร์เท่านั้น)")
                    else:
                        day_code = DAY_MAP[day_en]
                        success = save_history_to_github(day_code, new_row)
                        if success:
                            st.success(f"✅ บันทึกและซิงก์ข้อมูลลง GitHub (`history_lao_{day_code}.csv`) สำเร็จเรียบร้อยแล้ว!")
                            st.rerun()
                        else:
                            st.error("❌ เกิดข้อผิดพลาดในการเชื่อมต่อกับ GitHub API กรุณาตรวจสอบ GITHUB_TOKEN และ Secrets อีกครั้ง")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการตรวจสอบวันที่: {e}")
            else:
                st.error("กรุณากรอกตัวเลขอย่างน้อย 6 หลักขึ้นไป")

elif menu == "2. แสดงประวัติแยกรายวัน (Mon-Fri)":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 📂 แสดงประวัติสถิติย้อนหลัง (แยกรายวัน และแสดงงวดล่าสุดขึ้นก่อน)")
    
    selected_view_day = st.selectbox(
        "เลือกวันที่ต้องการดูประวัติ:",
        ["รวมทุกวัน (Mon-Fri)", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )
    
    if selected_view_day == "รวมทุกวัน (Mon-Fri)":
        df_display = load_weekday_history()
        title_text = "ทุกวัน (Mon-Fri)"
    else:
        df_display = load_specific_day_history(selected_view_day)
        title_text = f"วัน{selected_view_day}"
        
    if df_display is not None and not df_display.empty:
        df_display["_temp_date"] = df_display["date"].apply(parse_date_for_sort)
        df_display = df_display.sort_values(by="_temp_date", ascending=False, na_position="last").drop(columns=["_temp_date"]).reset_index(drop=True)
        
        st.info(f"📌 พบข้อมูลของ **{title_text}** ทั้งหมด {len(df_display)} รายการ (เรียงจากงวดล่าสุดไปงวดเก่า)")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.warning(f"⚠️ ยังไม่พบข้อมูลประวัติของ {title_text}")

elif menu == "3. Formula Ranking (จัดอันดับสูตร)":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 🏆 Formula Ranking (จัดอันดับความแม่นยำ 15 สูตร จากข้อมูล Mon-Fri)")
    df_weekday = load_weekday_history()
    if df_weekday is not None and not df_weekday.empty:
        formula_scores = {name: 0 for name, _ in formulas}
        col_name = "special" if "special" in df_weekday.columns else df_weekday.columns[0]
        
        for idx, row in df_weekday.iterrows():
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

elif menu == "4. Forward Prediction (ทำนายงวดถัดไป)":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 🔮 Forward Prediction (คำนวณผสานสถิติ Mon-Fri)")
    
    day_selected = st.selectbox(
        "เลือกวันของงวดถัดไป / วันที่ต้องการวิเคราะห์",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )

    df_weekday_all = load_weekday_history()
    latest_all = "691489"
    if df_weekday_all is not None and not df_weekday_all.empty:
        df_weekday_all["_temp_date"] = df_weekday_all["date"].apply(parse_date_for_sort)
        df_weekday_all = df_weekday_all.sort_values(by="_temp_date", ascending=False, na_position="last")
        col_name = "special" if "special" in df_weekday_all.columns else df_weekday_all.columns[0]
        for raw_val in df_weekday_all[col_name].tolist():
            v_str = str(raw_val).strip()
            if v_str.isdigit() and len(v_str) >= 6:
                latest_all = v_str[:6]
                break

    df_day_specific = load_specific_day_history(day_selected)
    latest_day = latest_all
    if df_day_specific is not None and not df_day_specific.empty:
        df_day_specific["_temp_date"] = df_day_specific["date"].apply(parse_date_for_sort)
        df_day_specific = df_day_specific.sort_values(by="_temp_date", ascending=False, na_position="last")
        col_day = "special" if "special" in df_day_specific.columns else df_day_specific.columns[0]
        for raw_val in df_day_specific[col_day].tolist():
            v_str = str(raw_val).strip()
            if v_str.isdigit() and len(v_str) >= 6:
                latest_day = v_str[:6]
                break

    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"📊 **งวดรวม Mon-Fri ล่าสุด**\n\nเลขฐาน 6 หลัก: `{latest_all}`\n\n3 ตัว/4 ตัว: `{latest_all[-3:]}` / `{latest_all[-4:]}`")
    with col_b:
        st.success(f"📌 **งวดประจำวัน {day_selected} ล่าสุด**\n\nเลขฐาน 6 หลัก: `{latest_day}`\n\n3 ตัว/4 ตัว: `{latest_day[-3:]}` / `{latest_day[-4:]}`")

    daily_6 = DAILY_NUMBERS.get(day_selected, "000000")
    st.write(f"🎯 **ชุดเลขประจำวัน ({day_selected}):** `{daily_6}`")

    display_count = st.radio("เลือกจำนวนตัวเลขความถี่สูงสุดที่ต้องการแสดง:", [5, 6], index=1, horizontal=True)

    if st.button("🚀 ประมวลผลทำนายเลข (ผสานข้อมูล)", type="primary", use_container_width=True):
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

        for d in daily_6:
            digit_scores[d] += 2.0

        counter_all, _ = calculate_formula_frequency(outputs_all, top_n=10)
        for num_str, count in counter_all.items():
            for d in num_str:
                digit_scores[d] += float(count) * 0.3

        counter_day, _ = calculate_formula_frequency(outputs_day, top_n=10)
        for num_str, count in counter_day.items():
            for d in num_str:
                digit_scores[d] += float(count) * 0.3

        sorted_digits = sorted(digit_scores.keys(), key=lambda k: digit_scores[k], reverse=True)
        top_digits_merged = [(d, digit_scores[d]) for d in sorted_digits[:display_count]]
        digits_only = [item[0] for item in top_digits_merged]

        st.markdown(f"### 📊 ผลลัพธ์เลขเด่นผสาน ({day_selected})")
        
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
