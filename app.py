import streamlit as st
from collections import Counter
from datetime import datetime
from itertools import combinations

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS (Sky Blue Theme)
# ==========================================
st.set_page_config(
    page_title="LAO AI PROFESSIONAL v4.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
        gap: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
        border: 1px solid #bae6fd;
        border-top: 4px solid #0284c7;
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(2, 132, 199, 0.08);
    }
    .stat-num {
        font-size: 28px;
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
        padding: 4px 10px;
        margin: 3px;
        font-weight: 600;
        color: #0c4a6e;
        font-size: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .badge-highlight {
        background-color: #0284c7;
        border-color: #0369a1;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ALL 15 FORMULAS & DAILY UTILS
# ==========================================
DAILY_NUMBERS = {
    "Monday": "056787",
    "Tuesday": "657872",
    "Wednesday": "390768",
    "Thursday": "897693",
    "Friday": "305687",
    "Saturday": "7890123",
    "Sunday": "8901234"
}

def get_daily_numbers():
    day_name = datetime.now().strftime("%A")
    return DAILY_NUMBERS.get(day_name, "000000"), day_name

def formula1(number):
    a, b, c, d, e, f = [int(x) for x in number]
    value = ((a+b+c)*(d+e+f)+(a*f)+(c*e)) % 10000
    res = f"{value:04d}"
    return formula5(number) if res == "0000" else res

def formula2(number):
    a, b, c, d, e, f = [int(x) for x in number]
    return f"{((a*b)+(c*d)+(e*f))%10000:04d}"

def formula3(number):
    a, b, c, d, e, f = [int(x) for x in number]
    return f"{((a+b+c+d+e+f)*111)%10000:04d}"

def formula4(number):
    a, b, c, d, e, f = [int(x) for x in number]
    value = ((a+b+c)*(d+e+f)) % 10000
    res = f"{value:04d}"
    return formula5(number) if res == "0000" else res

def formula5(number):
    digits = [int(x) for x in number]
    score = Counter()
    for digit, count in Counter(digits).items():
        score[digit] += count * 5
    for i in range(len(digits) - 1):
        score[(digits[i] + digits[i + 1]) % 10] += 2
        score[(digits[i] * digits[i + 1]) % 10] += 2
        score[abs(digits[i] - digits[i + 1])] += 1
    ranking = sorted(score.items(), key=lambda x: (-x[1], x[0]))
    return "".join(str(digit) for digit, _ in ranking[:4]).zfill(4)

def formula6(number):
    a, b, c, d, e, f = [int(x) for x in number]
    return f"{((a+c+e)*(b+d+f))%10000:04d}"

def formula7(number):
    a, b, c, d, e, f = [int(x) for x in number]
    return f"{((a*10+b)+(e*10+f))%10000:04d}"

def formula8(number):
    a, b, c, d, e, f = [int(x) for x in number]
    return f"{((a+b+c+d+e+f)*123)%10000:04d}"

def formula9(number):
    a, b, c, d, e, f = [int(x) for x in number]
    return f"{abs((a*100+b*10+c)-(d*100+e*10+f))%10000:04d}"

def formula10(number):
    a, b, c, d, e, f = [int(x) for x in number]
    return f"{((a*f)+(b*e)+(c*d))%10000:04d}"

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
    _, _, _, d, e, _ = [int(x) for x in number]
    base = (d + e) % 10
    return f"{base}{(base+1)%10}{(base+2)%10}{(base+3)%10}"

def formula13(number):
    a, _, c, _, _, f = [int(x) for x in number]
    return f"{((a + c + f) * 9)%10000:04d}"

def formula_13_cross(base_number):
    if len(base_number) < 4: return []
    target = base_number[-4:] 
    try:
        d2, d4 = int(target[1]), int(target[3]) 
        pos1 = (d2 + d4) % 10
        top_row = [str((pos1 + 2) % 10), str((pos1 + 3) % 10)]       
        bot_row = [str((pos1 + 8) % 10), str((pos1 + 9) % 10)]       
        return [f"{top}{bot}" for top in top_row for bot in bot_row] 
    except ValueError:
        return []

def formula14(number):
    f = int(number[5])
    return f"{f}{f}{(f+1)%10}{(f+1)%10}"

def formula_cross_multiply(number):
    num_str = str(number)[-4:] if len(str(number)) >= 4 else "0000"
    d1, d2 = int(num_str[0]), int(num_str[1])
    return f"{(d1 + 9) % 10}{(d1 + d2 + 1) % 10}"

def formula_neighbor(number):
    pos4, pos6 = int(number[3]), int(number[5])
    res_front = (pos6 - 1) % 10
    res_back_start = (pos4 + 2) % 10
    return f"{res_front}{res_back_start}{(res_back_start+1)%10}{(res_back_start+2)%10}"

formulas = [
    formula1, formula2, formula3, formula4, formula5, 
    formula6, formula7, formula8, formula9, formula10, 
    formula11, formula12, formula13, formula14, formula_neighbor
]

# ==========================================
# 3. STREAMLIT APP UI
# ==========================================
st.title("🚀 LAO AI PROFESSIONAL v4.0")

target_number = st.text_input("📌 ป้อนเลขฐาน 6 หลัก:", value="723294", max_chars=6)

if len(target_number) == 6 and target_number.isdigit():
    daily_val, day_name = get_daily_numbers()
    
    # รวบรวมผลลัพธ์จาก 15 สูตร + ข้ามสายพันธุ์ + เลขประจำวัน
    all_results_str = ""
    for f in formulas:
        all_results_str += f(target_number)
    
    cross_res = formula_cross_multiply(target_number)
    yt_pairs = formula_13_cross(target_number)
    yt_digits = "".join(yt_pairs)
    
    all_digits_str = all_results_str + cross_res + yt_digits + daily_val
    
    # นับความถี่ตัวเลข 0-9 ครบทุกตัว
    score = {str(i): 0 for i in range(10)}
    for digit in all_digits_str:
        if digit in score:
            score[digit] += 1
            
    # เรียงลำดับจากมากไปน้อย และตัดสไลซ์เฉพาะ 6 ตัวสูงสุด
    ranked_digits = sorted(score.items(), key=lambda x: (-x[1], int(x[0])))
    top_6_digits = ranked_digits[:6]
    digits_only = [item[0] for item in top_6_digits]
    
    # แสดงผลการ์ดความถี่ 6 ตัวสูงสุด
    st.subheader("📊 เลขที่ปรากฏบ่อยเมื่อรวมผลลัพธ์จาก 15 สูตร")
    
    html_parts = ['<div class="grid-container">']
    for num, count in top_6_digits:
        html_parts.append(f'<div class="stat-card"><div class="stat-num">{num}</div><div class="stat-count">{count} ครั้ง</div></div>')
    html_parts.append('</div>')
    
    st.markdown("".join(html_parts), unsafe_allow_html=True)
    st.caption("ความถี้นี้นับจากผลลัพธ์การคำนวณครบทั้ง 15 สูตร และตัดสไลซ์แสดงผลเฉพาะ 6 อันดับสูงสุด")

    # ส่วนจับคู่เลข 2 ตัว และ 3 ตัว
    st.divider()
    st.subheader("🎯 ชุดจับคู่เลขเด่น (จาก 6 ตัวบ่อยสุด)")

    pairs_2d = [f"{a}{b}" for a, b in combinations(digits_only, 2)]
    pairs_3d = [f"{a}{b}{c}" for a, b, c in combinations(digits_only, 3)]
    
    top_3_straight = "".join(digits_only[:3])
    top_2_straight = "".join(digits_only[:2])

    st.markdown(f"""
    <div class="pair-box" style="border-left-color: #0284c7; background-color: #e0f2fe;">
        <div class="pair-title">🔹 ชุดเน้นพิเศษ (Top Pick จากอันดับ 1-3)</div>
        <span class="badge badge-highlight">3 ตัวบน: {top_3_straight}</span>
        <span class="badge badge-highlight">2 ตัวบน/ล่าง: {top_2_straight}</span>
    </div>
    """, unsafe_allow_html=True)

    badges_2d = "".join([f'<span class="badge">{p}</span>' for p in pairs_2d])
    st.markdown(f"""
    <div class="pair-box">
        <div class="pair-title">🎲 ชุด 2 ตัวจับคู่วิน (15 ชุด)</div>
        {badges_2d}
    </div>
    """, unsafe_allow_html=True)

    badges_3d = "".join([f'<span class="badge">{p}</span>' for p in pairs_3d])
    st.markdown(f"""
    <div class="pair-box">
        <div class="pair-title">🎲 ชุด 3 ตัวจับคู่วิน (20 ชุด)</div>
        {badges_3d}
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("⚠️ กรุณากรอกเลขฐานให้ครบ 6 หลัก")
