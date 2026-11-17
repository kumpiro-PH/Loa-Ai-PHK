# app.py - Lao AI Professional v4.1 (Final CSV Structured Support)
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from collections import Counter
from itertools import combinations

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS (Sky Blue Theme)
# ==========================================
st.set_page_config(
    page_title="Lao AI Professional v4.4",
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

VERSION = "4.5 LATEST ROW FIX + GITHUB CSV + BACKTEST/FREQUENCY"
# ใช้ path ของโฟลเดอร์ app.py โดยตรง เพื่อให้ Streamlit Cloud อ่านไฟล์ใน Repository ได้
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_MAIN = os.path.join(BASE_DIR, "history_lao.csv")
CSV_FILE_BY_DAY = {
    "Monday": os.path.join(BASE_DIR, "history_lao_mon.csv"),
    "Tuesday": os.path.join(BASE_DIR, "history_lao_tue.csv"),
    "Wednesday": os.path.join(BASE_DIR, "history_lao_wed.csv"),
    "Thursday": os.path.join(BASE_DIR, "history_lao_thu.csv"),
    "Friday": os.path.join(BASE_DIR, "history_lao_fri.csv"),
}

DAY_MAP = {
    "Monday": "mon",
    "Tuesday": "tue",
    "Wednesday": "wed",
    "Thursday": "thu",
    "Friday": "fri",
    "Saturday": "sat",
    "Sunday": "sun",
}

DAILY_NUMBERS = {
    "Monday": "940627",
    "Tuesday": "017562",
    "Wednesday": "394517",
    "Thursday": "643951",
    "Friday": "974516",
    "Saturday": "820739",
    "Sunday": "470076",
}

# ==========================================
# 2. ฟังก์ชันจัดการ CSV และ สูตรคำนวณ (1-15)
# ==========================================
def parse_draw_date(value):
    """แปลงวันที่ DD/MM/YYYY หรือ YYYY-MM-DD รองรับ พ.ศ. และ ค.ศ."""
    raw = str(value).strip()
    if not raw:
        return None
    parsed = None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            parsed = datetime.strptime(raw, fmt)
            break
        except ValueError:
            continue
    if parsed is None:
        return None
    if parsed.year >= 2400:
        parsed = parsed.replace(year=parsed.year - 543)
    return parsed

def sort_history_by_date(df, newest_first=True):
    """เรียงประวัติตามวันที่จริง ไม่พึ่งตำแหน่งแถวใน CSV"""
    if df is None or df.empty or "date" not in df.columns:
        return df.copy() if df is not None else pd.DataFrame()
    result = df.copy()
    result["_parsed_date"] = result["date"].apply(parse_draw_date)
    result = result.sort_values(
        "_parsed_date", ascending=not newest_first, na_position="last", kind="stable"
    )
    return result.drop(columns=["_parsed_date"]).reset_index(drop=True)

def load_csv_data(filename):
    """อ่าน CSV แบบมี header และแบบ history_lao.csv ที่ไม่มี header"""
    standard_columns = ["date", "special", "first_prize", "top_3", "bottom_2"]
    if not os.path.exists(filename):
        return pd.DataFrame(columns=standard_columns)
    try:
        raw = pd.read_csv(filename, dtype=str, keep_default_na=False, header=None)
        if raw.empty:
            return pd.DataFrame(columns=standard_columns)
        first_row = [str(v).strip().lower() for v in raw.iloc[0].tolist()]
        known_headers = set(standard_columns)
        if any(value in known_headers for value in first_row):
            df = pd.read_csv(filename, dtype=str, keep_default_na=False)
            df.columns = [str(c).strip().lower() for c in df.columns]
        else:
            if raw.shape[1] == 2:
                # รูปแบบมาตรฐานของ history_lao.csv: เลขฐาน 6 หลัก, ผล 4 หลัก
                raw.columns = ["special", "first_prize"]
            elif raw.shape[1] == 3 and raw.iloc[:, 2].astype(str).str.strip().eq("").all():
                # CSV ของผู้ใช้มี comma ปิดท้ายทุกบรรทัด เช่น 691489,1489,
                # pandas จึงเห็นเป็น 3 คอลัมน์ โดยคอลัมน์ที่ 3 ว่างทั้งหมด
                raw = raw.iloc[:, :2].copy()
                raw.columns = ["special", "first_prize"]
            elif raw.shape[1] == 5:
                raw.columns = standard_columns
            else:
                st.error(
                    f"รูปแบบ CSV ไม่รองรับ: {os.path.basename(filename)} "
                    f"มี {raw.shape[1]} คอลัมน์ (รองรับ 2 คอลัมน์ หรือ 3 คอลัมน์ที่คอลัมน์สุดท้ายว่าง)"
                )
                return pd.DataFrame(columns=standard_columns)
            df = raw
        for col in standard_columns:
            if col not in df.columns:
                df[col] = ""
        df = df[standard_columns + [c for c in df.columns if c not in standard_columns]]
        df["special"] = df["special"].astype(str).str.strip()
        df["first_prize"] = df["first_prize"].astype(str).str.strip()

        # CSV แบบไม่มีวันที่ (2 คอลัมน์ หรือ 3 คอลัมน์ที่ท้ายว่าง)
        # ประวัติของ Repository เรียงจากเก่าไปใหม่ จึงต้องกลับลำดับ
        # เพื่อให้แถวแรกเป็นงวดล่าสุด ทั้งไฟล์รวมและไฟล์รายวัน
        has_valid_dates = (
            df["date"].apply(parse_draw_date).notna().any()
            if "date" in df.columns else False
        )
        if has_valid_dates:
            return sort_history_by_date(df, newest_first=True)
        return df.iloc[::-1].reset_index(drop=True)
    except Exception as exc:
        st.error(f"ไม่สามารถอ่านไฟล์ {os.path.basename(filename)}: {exc}")
        return pd.DataFrame(columns=standard_columns)

def save_history_upsert(new_row):
    """บันทึกงวดใหม่โดยไม่ลบประวัติเก่าที่ไม่มีวันที่"""
    current = load_csv_data(CSV_FILE_MAIN)
    combined = pd.concat([current, new_row], ignore_index=True)
    combined["date"] = combined["date"].astype(str).str.strip()
    dated = combined[combined["date"] != ""].drop_duplicates(subset=["date"], keep="last")
    undated = combined[combined["date"] == ""]
    combined = pd.concat([dated, undated], ignore_index=True)
    combined = sort_history_by_date(combined, newest_first=True)
    combined.to_csv(CSV_FILE_MAIN, index=False, encoding="utf-8")

def load_specific_day_history(day_en):
    """อ่านประวัติจาก CSV ประจำวันโดยตรง"""
    filename = CSV_FILE_BY_DAY.get(day_en)
    if not filename:
        return pd.DataFrame(columns=["date", "special", "first_prize", "top_3", "bottom_2"])
    return load_csv_data(filename)

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

df_history = load_csv_data(CSV_FILE_MAIN)

with st.sidebar.expander("ตรวจสอบฐานข้อมูล CSV", expanded=False):
    st.write(f"Main CSV: {'พบ' if os.path.exists(CSV_FILE_MAIN) else 'ไม่พบ'}")
    st.write(f"จำนวนงวดรวม: {len(df_history)}")
    for _day, _path in CSV_FILE_BY_DAY.items():
        _df_check = load_csv_data(_path)
        st.write(f"{_day}: {'พบ' if os.path.exists(_path) else 'ไม่พบ'} ({len(_df_check)} งวด)")

# ==========================================
# 4. MAIN CONTENT
# ==========================================
if menu == "1. อัปเดตผลรางวัล":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 📝 อัปเดตผลรางวัลหวยลาวใหม่")
    
    with st.form("update_form"):
        input_date = st.text_input("ใส่วันที่ (DD/MM/YYYY เช่น 16/11/2569)")
        input_6d = st.text_input("เลขฐาน / รางวัล 6 หลัก:")
        submitted = st.form_submit_button("บันทึกผลรางวัล")
        
        if submitted:
            if len(input_6d) >= 6 and input_6d.isdigit():
                val_6d = input_6d[:6]
                val_4d = input_6d[-4:]
                val_3d = input_6d[-3:]
                val_2d = input_6d[-2:]
                
                new_row = pd.DataFrame([{
                    "date": input_date.strip(),
                    "special": val_6d,
                    "first_prize": val_4d,
                    "top_3": val_3d,
                    "bottom_2": val_2d
                }])
                
                parsed_input_date = parse_draw_date(input_date)
                if parsed_input_date is None:
                    st.error("รูปแบบวันที่ไม่ถูกต้อง กรุณาใช้ DD/MM/YYYY เช่น 16/11/2569")
                else:
                    save_history_upsert(new_row)
                    st.success(f"✅ บันทึก/อัปเดตข้อมูลลงในไฟล์ `{CSV_FILE_MAIN}` เรียบร้อยแล้ว!")
                    st.rerun()
            else:
                st.error("กรุณากรอกตัวเลขอย่างน้อย 6 หลักขึ้นไป")

elif menu == "2. แสดงประวัติ (History)":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 📂 แสดงประวัติข้อมูลสถิติย้อนหลัง (history_lao.csv)")
    if df_history is not None and not df_history.empty:
        st.dataframe(df_history, use_container_width=True)
    else:
        st.warning("⚠️ ยังไม่พบข้อมูลประวัติ CSV")

elif menu == "3. ลบข้อมูลงวดล่าสุด":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 🗑️ ลบข้อมูลงวดล่าสุดออกจากระบบ")
    if df_history is not None and not df_history.empty:
        df_history = sort_history_by_date(df_history, newest_first=True)
        st.write("ข้อมูลงวดล่าสุดตามวันที่ (งวดที่จะถูกลบ):")
        st.write(df_history.head(1))
        if st.button("❌ ยืนยันลบข้อมูลงวดล่าสุด", type="primary"):
            latest_date = df_history.iloc[0]["date"]
            df_history = df_history[df_history["date"].astype(str) != str(latest_date)]
            df_history = sort_history_by_date(df_history, newest_first=True)
            df_history.to_csv(CSV_FILE_MAIN, index=False, encoding="utf-8")
            st.success(f"ลบงวดวันที่ {latest_date} เรียบร้อยแล้ว!")
            st.rerun()
    else:
        st.warning("ไม่มีข้อมูลให้ลบ")

elif menu == "4. Formula Ranking (จัดอันดับสูตร)":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 🏆 Formula Ranking — Backtest + Frequency")
    if df_history is not None and not df_history.empty and "special" in df_history.columns:
        history_asc = sort_history_by_date(df_history, newest_first=False)
        parsed_date_count = df_history["date"].apply(parse_draw_date).notna().sum() if "date" in df_history.columns else 0
        if parsed_date_count == 0:
            history_asc = df_history.iloc[::-1].reset_index(drop=True)
        valid_rows = []
        for _, row in history_asc.iterrows():
            base = str(row.get("special", "")).strip()
            actual = str(row.get("first_prize", "")).strip()
            if base.isdigit() and len(base) >= 6 and actual.isdigit() and len(actual) >= 4:
                valid_rows.append((base[:6], actual[-4:]))

        if len(valid_rows) < 2:
            st.warning("ต้องมีข้อมูลอย่างน้อย 2 งวด และมี special 6 หลักกับ first_prize 4 หลัก เพื่อทดสอบสูตรย้อนหลัง")
        else:
            ranking_rows = []
            tests = len(valid_rows) - 1
            for name, func in formulas:
                exact_hits = 0
                digit_hits = 0
                digit_slots = 0
                successful_tests = 0
                output_frequency = Counter()
                for index in range(tests):
                    base_number = valid_rows[index][0]
                    actual_next = valid_rows[index + 1][1]
                    try:
                        predicted = str(func(base_number)).strip()
                        if not predicted.isdigit():
                            continue
                        predicted = predicted.zfill(4)[-4:]
                        successful_tests += 1
                        exact_hits += int(predicted == actual_next)
                        predicted_count = Counter(predicted)
                        actual_count = Counter(actual_next)
                        digit_hits += sum((predicted_count & actual_count).values())
                        digit_slots += 4
                        output_frequency.update(predicted)
                    except Exception:
                        continue

                exact_rate = exact_hits / successful_tests * 100 if successful_tests else 0.0
                frequency_rate = digit_hits / digit_slots * 100 if digit_slots else 0.0
                hybrid_score = exact_rate * 0.70 + frequency_rate * 0.30
                common_digits = ", ".join(
                    f"{digit} ({count})"
                    for digit, count in output_frequency.most_common(3)
                ) or "-"
                ranking_rows.append({
                    "สูตร": name,
                    "ทดสอบสำเร็จ (งวด)": successful_tests,
                    "ตรง 4 หลัก": exact_hits,
                    "Exact Rate (%)": round(exact_rate, 2),
                    "เลขตรงไม่สนตำแหน่ง": digit_hits,
                    "Frequency Rate (%)": round(frequency_rate, 2),
                    "Hybrid Score": round(hybrid_score, 2),
                    "เลขที่สูตรสร้างบ่อย": common_digits,
                })

            result_df = pd.DataFrame(ranking_rows).sort_values(
                ["Hybrid Score", "Exact Rate (%)", "Frequency Rate (%)"],
                ascending=False
            ).reset_index(drop=True)
            result_df.insert(0, "อันดับ", range(1, len(result_df) + 1))
            st.caption(
                "Backtest: ใช้ special ของงวดก่อนหน้าเป็นฐาน แล้วเทียบผล 4 หลักกับ "
                "first_prize ของงวดถัดไป | Hybrid Score = Exact Rate 70% + "
                "Frequency Rate 30% (นับเลขตรงโดยไม่สนตำแหน่งและคำนึงถึงเลขซ้ำ)"
            )
            st.dataframe(result_df, use_container_width=True, hide_index=True)
            st.info(
                f"ใช้ข้อมูล {len(valid_rows)} งวด ทดสอบย้อนหลัง {tests} ช่วง "
                "โดยไม่ใช้ผลรางวัลของงวดเป้าหมายเป็นฐานคำนวณ"
            )
    else:
        st.warning("ยังไม่มีข้อมูลสำหรับจัดอันดับสูตร")

elif menu == "5. Forward Prediction (ทำนายงวดถัดไป)":
    st.title("🧠 Lao AI Professional")
    st.markdown("### 🔮 Forward Prediction (คำนวณผสานสถิติ 3 แหล่งข้อมูล)")
    
    day_selected = st.selectbox(
        "เลือกวันของงวดถัดไป / วันที่ต้องการวิเคราะห์",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )

    # 1. ดึงงวดรวมล่าสุดจากวันที่จริง ไม่พึ่งลำดับแถวใน CSV
    latest_all = "000000"
    history_sorted = sort_history_by_date(df_history, newest_first=True)
    if history_sorted is not None and not history_sorted.empty and "special" in history_sorted.columns:
        for val in history_sorted["special"].tolist():
            v_str = str(val).strip()
            if v_str.isdigit() and len(v_str) >= 6:
                latest_all = v_str[:6]
                break

    # 2. ดึงงวดประจำวันล่าสุดเฉพาะวันที่ตรงกับวันเลือก (เช่น วันจันทร์ล่าสุด = 337038)
    df_day_specific = load_specific_day_history(day_selected)
    latest_day = latest_all
    if df_day_specific is not None and not df_day_specific.empty and "special" in df_day_specific.columns:
        for val in df_day_specific["special"].tolist():
            v_str = str(val).strip()
            if v_str.isdigit() and len(v_str) >= 6:
                latest_day = v_str[:6]
                break

    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"📊 **งวดรวมล่าสุด (`history_lao.csv`)**\n\nเลขฐาน 6 หลัก: `{latest_all}`\n\n3 ตัว/4 ตัว: `{latest_all[-3:]}` / `{latest_all[-4:]}`")
    with col_b:
        st.success(f"📌 **งวดประจำวัน {day_selected} ล่าสุด**\n\nเลขฐาน 6 หลัก: `{latest_day}`\n\n3 ตัว/4 ตัว: `{latest_day[-3:]}` / `{latest_day[-4:]}`")

    daily_6 = DAILY_NUMBERS.get(day_selected, "000000")
    st.write(f"🎯 **ชุดเลขประจำวัน ({day_selected}):** `{daily_6}`")

    display_count = st.radio("เลือกจำนวนตัวเลขความถี่สูงสุดที่ต้องการแสดง:", [5, 6], index=1, horizontal=True)

    if st.button("🚀 ประมวลผลทำนายเลข (ผสาน 3 ส่วน)", type="primary", use_container_width=True):
        if day_selected == "Saturday":
            st.warning("⚠️ [AI WARNING] วันเสาร์มีสถิติการออกเลขเบิ้ลหรือหามสูง แนะนำให้ระวังเป็นพิเศษ!")

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
