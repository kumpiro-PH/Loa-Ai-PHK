import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from collections import Counter
from itertools import combinations

# =========================================================
# LAO AI PROFESSIONAL v4.1 - CALCULATION FIX
# =========================================================
st.set_page_config(
    page_title="Lao AI Professional v4.1",
    page_icon="🧠",
    layout="wide"
)

VERSION = "4.1 CALCULATION FIX"
CSV_FILE_NAME = "history_lao.csv"
DEFAULT_DAILY_NUMBER = "657872"
DEFAULT_HISTORY = [
    ["691489", "1489"],
    ["922679", "2679"],
    ["680172", "0172"],
    ["352415", "2415"],
    ["738155", "8155"],
]

# =========================================================
# DATA HELPERS
# =========================================================
def clean_numeric_text(value):
    """Return a clean digit string, preserving leading zeroes where possible."""
    if value is None:
        return ""
    value = str(value).strip()
    if value.endswith(".0") and value[:-2].isdigit():
        value = value[:-2]
    return value if value.isdigit() else ""


def load_history(uploaded_file):
    """Read uploaded CSV first; otherwise read local CSV; otherwise use demo data."""
    if uploaded_file is not None:
        try:
            raw = uploaded_file.getvalue()
            return pd.read_csv(
                io.BytesIO(raw),
                header=None,
                dtype=str,
                keep_default_na=False
            ), "ไฟล์ที่อัปโหลด"
        except Exception as exc:
            st.error(f"อ่านไฟล์ CSV ที่อัปโหลดไม่สำเร็จ: {exc}")

    if os.path.exists(CSV_FILE_NAME):
        try:
            return pd.read_csv(
                CSV_FILE_NAME,
                header=None,
                dtype=str,
                keep_default_na=False
            ), f"ไฟล์ในเครื่อง: {CSV_FILE_NAME}"
        except Exception as exc:
            st.error(f"อ่านไฟล์ {CSV_FILE_NAME} ไม่สำเร็จ: {exc}")

    return pd.DataFrame(DEFAULT_HISTORY), "ข้อมูลตัวอย่าง (ยังไม่พบ CSV)"


def find_latest_base(history_df):
    """Search from the last row upwards, and from right to left within each row."""
    if history_df is None or history_df.empty:
        return ""
    for row_index in range(len(history_df) - 1, -1, -1):
        row = history_df.iloc[row_index]
        for value in reversed(row.tolist()):
            text_value = clean_numeric_text(value)
            if len(text_value) >= 6:
                return text_value[:6]
    return ""


# =========================================================
# FORMULAS 1-15
# All formulas use exactly the FIRST SIX digits of the base.
# =========================================================
def formula5(number):
    digits = [int(x) for x in number]
    score = Counter()

    for digit, count in Counter(digits).items():
        score[digit] += count * 5

    for i in range(len(digits) - 1):
        score[(digits[i] + digits[i + 1]) % 10] += 2
        score[(digits[i] * digits[i + 1]) % 10] += 2
        score[abs(digits[i] - digits[i + 1])] += 1

    # Rank all ten digits. This avoids zfill() creating artificial zeroes.
    ranking = sorted(
        range(10),
        key=lambda digit: (-score[digit], digit)
    )
    return "".join(str(digit) for digit in ranking[:4])


def formula1(number):
    a, b, c, d, e, f = map(int, number)
    value = ((a + b + c) * (d + e + f) + (a * f) + (c * e)) % 10000
    return formula5(number) if value == 0 else f"{value:04d}"


def formula2(number):
    a, b, c, d, e, f = map(int, number)
    return f"{((a * b) + (c * d) + (e * f)) % 10000:04d}"


def formula3(number):
    return f"{(sum(map(int, number)) * 111) % 10000:04d}"


def formula4(number):
    a, b, c, d, e, f = map(int, number)
    value = ((a + b + c) * (d + e + f)) % 10000
    return formula5(number) if value == 0 else f"{value:04d}"


def formula6(number):
    a, b, c, d, e, f = map(int, number)
    return f"{((a + c + e) * (b + d + f)) % 10000:04d}"


def formula7(number):
    a, b, c, d, e, f = map(int, number)
    return f"{((a * 10 + b) + (e * 10 + f)) % 10000:04d}"


def formula8(number):
    return f"{(sum(map(int, number)) * 123) % 10000:04d}"


def formula9(number):
    a, b, c, d, e, f = map(int, number)
    left = a * 100 + b * 10 + c
    right = d * 100 + e * 10 + f
    return f"{abs(left - right) % 10000:04d}"


def formula10(number):
    a, b, c, d, e, f = map(int, number)
    return f"{((a * f) + (b * e) + (c * d)) % 10000:04d}"


def formula11(number):
    digits = [int(x) for x in number]
    pair_results = [
        f"{(left * right) % 100:02d}"
        for left, right in combinations(digits, 2)
    ]
    ranking = sorted(
        Counter(pair_results).items(),
        key=lambda item: (-item[1], int(item[0]))
    )
    if not ranking:
        return "0000"
    if len(ranking) == 1:
        return ranking[0][0] * 2
    return ranking[0][0] + ranking[1][0]


def formula12(number):
    digits = [int(x) for x in number]
    base = (digits[3] + digits[4]) % 10
    return "".join(str((base + offset) % 10) for offset in range(4))


def formula13(number):
    digits = [int(x) for x in number]
    return f"{((digits[0] + digits[2] + digits[5]) * 9) % 10000:04d}"


def formula14(number):
    last_digit = int(number[5])
    next_digit = (last_digit + 1) % 10
    return f"{last_digit}{last_digit}{next_digit}{next_digit}"


def formula_neighbor(number):
    digits = [int(x) for x in number]
    front = (digits[5] - 1) % 10
    back_start = (digits[3] + 2) % 10
    return "".join(str(x) for x in (
        front,
        back_start,
        (back_start + 1) % 10,
        (back_start + 2) % 10
    ))


FORMULAS = [
    ("Formula 1", formula1),
    ("Formula 2", formula2),
    ("Formula 3", formula3),
    ("Formula 4", formula4),
    ("Formula 5", formula5),
    ("Formula 6", formula6),
    ("Formula 7", formula7),
    ("Formula 8", formula8),
    ("Formula 9", formula9),
    ("Formula 10", formula10),
    ("Formula 11", formula11),
    ("Formula 12", formula12),
    ("Formula 13", formula13),
    ("Formula 14", formula14),
    ("Formula Neighbor", formula_neighbor),
]


# =========================================================
# CALCULATION / VALIDATION
# =========================================================
def calculate_all(base_input):
    """Normalize to six digits, calculate every formula, and validate outputs."""
    base = clean_numeric_text(base_input)
    if len(base) < 6:
        raise ValueError("เลขฐานต้องมีอย่างน้อย 6 หลัก")
    base = base[:6]

    outputs = {}
    errors = {}
    for name, function in FORMULAS:
        try:
            result = str(function(base)).strip()
            if not result.isdigit():
                raise ValueError("ผลลัพธ์ไม่ใช่ตัวเลข")
            if len(result) > 4:
                result = result[-4:]
            result = result.zfill(4)
            if len(result) != 4:
                raise ValueError("ผลลัพธ์ไม่ครบ 4 หลัก")
            outputs[name] = result
        except Exception as exc:
            errors[name] = str(exc)

    if len(outputs) != 15:
        raise RuntimeError(
            f"คำนวณสำเร็จ {len(outputs)}/15 สูตร; ข้อผิดพลาด: {errors}"
        )
    return base, outputs


def get_frequency(outputs, daily_number=None):
    formula_counter = Counter()
    for result in outputs.values():
        formula_counter.update(result)

    combined_counter = formula_counter.copy()
    if daily_number:
        combined_counter.update(daily_number)

    def ranked(counter):
        return sorted(
            [(str(digit), count) for digit, count in counter.items()],
            key=lambda item: (-item[1], int(item[0]))
        )

    # Include all digits 0-9, including zero-frequency digits.
    all_digits = {
        str(digit): formula_counter.get(str(digit), 0)
        for digit in range(10)
    }
    combined_all = {
        str(digit): combined_counter.get(str(digit), 0)
        for digit in range(10)
    }

    formula_ranking = sorted(
        all_digits.items(), key=lambda item: (-item[1], int(item[0]))
    )
    combined_ranking = sorted(
        combined_all.items(), key=lambda item: (-item[1], int(item[0]))
    )
    return formula_counter, formula_ranking, combined_counter, combined_ranking


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("⚙️ จัดการข้อมูล & ตั้งค่า")
uploaded_csv = st.sidebar.file_uploader(
    "📂 อัปโหลดไฟล์ history_lao.csv",
    type=["csv"],
    key="history_upload"
)

history_df, history_source = load_history(uploaded_csv)
latest_base = find_latest_base(history_df)

if st.sidebar.button("🔄 รีเฟรชข้อมูล CSV", use_container_width=True):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Daily Number")
day_name = datetime.now().strftime("%A")
daily_override = st.sidebar.checkbox("แก้ไขเลขประจำวันเอง", value=False)
daily_number = st.sidebar.text_input(
    f"เลขประจำวัน ({day_name})",
    value=DEFAULT_DAILY_NUMBER,
    max_chars=6,
    disabled=not daily_override
)
if not daily_override:
    daily_number = DEFAULT_DAILY_NUMBER

daily_valid = len(daily_number) == 6 and daily_number.isdigit()
if not daily_valid:
    st.sidebar.warning("Daily Number ต้องเป็นตัวเลข 6 หลัก")

st.sidebar.markdown("---")
st.sidebar.subheader("📢 ประกาศ / อัปเดตข้อมูล")
if "latest_update" not in st.session_state:
    st.session_state.latest_update = "ระบบ LAO AI PROFESSIONAL พร้อมใช้งาน"

input_update = st.sidebar.text_area(
    "ข้อความประกาศ:",
    value=st.session_state.latest_update
)
if st.sidebar.button("💾 บันทึกประกาศ"):
    st.session_state.latest_update = input_update
    st.sidebar.success("บันทึกข้อความสำเร็จ")


# =========================================================
# MAIN UI
# =========================================================
st.title("🧠 LAO AI PROFESSIONAL")
st.caption(f"เวอร์ชัน: {VERSION} | วัน: {day_name}")
st.info(f"📢 **ประกาศล่าสุด:** {st.session_state.latest_update}")

st.caption(f"แหล่งข้อมูลประวัติ: {history_source}")
with st.expander("📂 ดูประวัติ history_lao.csv"):
    st.dataframe(history_df, use_container_width=True)

st.markdown("---")
st.subheader("🔢 เลขฐาน")

if "base_number" not in st.session_state:
    st.session_state.base_number = latest_base or "738155"

# If the latest CSV base changes, refresh the default only when the user
# has not manually edited the input since the previous load.
if "last_loaded_base" not in st.session_state:
    st.session_state.last_loaded_base = latest_base
elif latest_base and st.session_state.last_loaded_base != latest_base:
    st.session_state.base_number = latest_base
    st.session_state.last_loaded_base = latest_base

base_input = st.text_input(
    "ป้อนเลขฐาน (6 หลักขึ้นไป):",
    key="base_number",
    max_chars=20,
    help="ระบบใช้เลข 6 หลักแรกของเลขฐานที่ป้อน"
)

st.caption(
    f"เลขฐานล่าสุดที่อ่านได้จาก CSV: {latest_base or 'ไม่พบเลขฐาน 6 หลัก'}"
)

if st.button(
    "🚀 วิเคราะห์ข้อมูล",
    type="primary",
    use_container_width=True
):
    clean_base_input = clean_numeric_text(base_input)

    if len(clean_base_input) < 6:
        st.error("กรุณากรอกเลขฐานอย่างน้อย 6 หลัก และใช้ตัวเลขเท่านั้น")
    elif not daily_valid:
        st.error("กรุณาตรวจสอบ Daily Number ให้เป็นตัวเลข 6 หลัก")
    else:
        try:
            used_base, formula_outputs = calculate_all(clean_base_input)
            formula_counter, formula_ranking, combined_counter, combined_ranking = (
                get_frequency(formula_outputs, daily_number)
            )

            st.session_state.last_result = {
                "base": used_base,
                "daily": daily_number,
                "outputs": formula_outputs,
                "formula_ranking": formula_ranking,
                "combined_ranking": combined_ranking,
            }
        except Exception as exc:
            st.error(f"เกิดข้อผิดพลาดในการคำนวณ: {exc}")

# Display the last successful calculation until a new calculation is submitted.
if "last_result" in st.session_state:
    result = st.session_state.last_result
    outputs = result["outputs"]

    st.markdown("---")
    st.subheader("🧾 ข้อมูลที่ใช้คำนวณ")
    c1, c2 = st.columns(2)
    c1.metric("เลขฐานที่ใช้จริง (6 หลักแรก)", result["base"])
    c2.metric("Daily Number", result["daily"])

    st.subheader("📋 ผลลัพธ์แยกทั้ง 15 สูตร")
    formula_table = pd.DataFrame(
        [{"สูตร": name, "เลข 4 หลัก": outputs[name]} for name, _ in FORMULAS]
    )
    st.dataframe(formula_table, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📊 ความถี่จาก 15 สูตรเท่านั้น")
    st.caption("15 สูตร × 4 หลัก = 60 ตำแหน่ง (ไม่นับ Daily Number)")
    formula_freq_df = pd.DataFrame(
        [{"เลข": digit, "จำนวนครั้ง": count}
         for digit, count in result["formula_ranking"]]
    )
    st.dataframe(formula_freq_df, use_container_width=True, hide_index=True)
    st.bar_chart(formula_freq_df.set_index("เลข"))

    top_formula = result["formula_ranking"][:5]
    metric_cols = st.columns(5)
    for col, (digit, count) in zip(metric_cols, top_formula):
        col.metric(f"{count} ครั้ง", digit)

    st.markdown("---")
    st.subheader("📅 ความถี่รวม Daily Number")
    st.caption("60 ตำแหน่งจาก 15 สูตร + 6 ตำแหน่งจาก Daily Number = 66 ตำแหน่ง")
    combined_freq_df = pd.DataFrame(
        [{"เลข": digit, "จำนวนครั้ง": count}
         for digit, count in result["combined_ranking"]]
    )
    st.dataframe(combined_freq_df, use_container_width=True, hide_index=True)
    st.bar_chart(combined_freq_df.set_index("เลข"))

    st.subheader("🎯 กลุ่มเลขตามความถี่รวม")
    main_group = [
        digit for digit, count in result["combined_ranking"] if count >= 10
    ]
    secondary_group = [
        digit for digit, count in result["combined_ranking"] if 5 <= count < 10
    ]
    lower_group = [
        digit for digit, count in result["combined_ranking"] if count < 5
    ]

    st.write(f"**กลุ่มเด่น (10 ครั้งขึ้นไป):** {' – '.join(main_group) or '-'}")
    st.write(f"**กลุ่มรอง (5–9 ครั้ง):** {' – '.join(secondary_group) or '-'}")
    st.write(f"**กลุ่มความถี่ต่ำ (0–4 ครั้ง):** {' – '.join(lower_group) or '-'}")

    st.caption(
        "หมายเหตุ: ความถี่เป็นสถิติจากสูตรที่กำหนด ไม่ใช่ความน่าจะเป็น "
        "หรือการรับประกันผลรางวัล"
    )
else:
    st.info("กรอกเลขฐานและกด “วิเคราะห์ข้อมูล” เพื่อคำนวณผลลัพธ์")
