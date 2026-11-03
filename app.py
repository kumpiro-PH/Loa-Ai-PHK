import streamlit as st
from datetime import datetime
from collections import Counter

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Lao AI Professional v4.0",
    page_icon="🧠",
    layout="centered"
)

VERSION = "4.0 WEB MOBILE"

# ค่าตั้งต้นเลขประจำวัน
DEFAULT_DAILY_NUMBERS = {
    "Monday": "056787",
    "Tuesday": "657872",
    "Wednesday": "390768",
    "Thursday": "897693",
    "Friday": "305687",
    "Saturday": "7890123",
    "Sunday": "8901234"
}

# ==========================================
# SIDEBAR: จัดการข้อมูล / ตั้งค่า
# ==========================================
st.sidebar.header("⚙️ ตั้งค่าข้อมูล")
override_daily = st.sidebar.checkbox("แก้ไขเลขประจำวันเอง")

day_name = datetime.now().strftime("%A")
default_val = DEFAULT_DAILY_NUMBERS.get(day_name, "00000")

if override_daily:
    day_val = st.sidebar.text_input(f"เลขประจำวัน ({day_name}):", value=default_val, max_chars=10)
else:
    day_val = default_val

st.sidebar.markdown("---")
st.sidebar.subheader("📢 อัพเดทข้อมูลล่าสุด / ประกาศ")

# ใช้ Session State เพื่อเก็บข้อความอัพเดทให้คงอยู่ตลอดการใช้งานในเซสชันนี้
if "latest_update" not in st.session_state:
    st.session_state.latest_update = "ระบบพร้อมใช้งาน วิเคราะห์สูตรแม่นยำด้วย AI"

# ช่องกรอกข้อความอัพเดทผ่าน Sidebar
input_update = st.sidebar.text_area("ข้อความประกาศ/อัพเดท:", value=st.session_state.latest_update)
if st.sidebar.button("💾 บันทึกการอัพเดท"):
    st.session_state.latest_update = input_update
    st.sidebar.success("อัพเดทข้อมูลสำเร็จ!")

# ==========================================
# FORMULAS (1 - 15)
# ==========================================
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

def calculate_formula_frequency(formula_outputs, top_n=5):
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
st.caption(f"เวอร์ชัน: {VERSION} | วัน: {day_name} (เลขประจำวัน: {day_val})")

# แสดงกล่องข้อความอัพเดทล่าสุดบนหน้าจอหลัก
st.info(f"📢 **ประกาศ/อัพเดทล่าสุด:** {st.session_state.latest_update}")

st.markdown("---")

# ช่องกรอกเลขฐาน
base_input = st.text_input("ป้อนเลขฐาน (6 หลักขึ้นไป):", value="863206", max_chars=10)

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

        counter, top_digits = calculate_formula_frequency(formula_outputs, top_n=5)
        valid_count = sum(1 for v in formula_outputs.values() if len(str(v)) >= 4 and str(v).isdigit())

        st.markdown("### 📊 เลขที่ปรากฏบ่อยเมื่อรวมผลลัพธ์จาก 15 สูตร")
        
        # แสดงผลแบบ Columns สวยงามบนมือถือ
        if top_digits:
            cols = st.columns(len(top_digits))
            for i, (digit, count) in enumerate(top_digits):
                with cols[i]:
                    st.metric(label=f"{count} ครั้ง", value=str(digit))

        st.caption(f"ความถี่นี้นับจากเลข 4 หลักที่แต่ละสูตรสร้างขึ้น รวม {valid_count} สูตร")

        st.markdown("---")
        st.markdown("### 🎯 เลขเด่นจากการรวมสูตร")
        
        main_group = [d for d, c in top_digits if c >= 10]
        sub_group = [d for d, c in top_digits if 5 <= c < 10]
        low_group = [str(i) for i in range(10) if i not in [int(d) for d, _ in top_digits]]

        st.write(f"• **กลุ่มเด่น:** {' – '.join(main_group) if main_group else '-'}")
        st.write(f"• **กลุ่มรอง:** {' – '.join(sub_group) if sub_group else '-'}")
        st.markdown(f"• **เลขที่ปรากฏน้อยกว่า:** {' – '.join(low_group) if low_group else '-'}")
