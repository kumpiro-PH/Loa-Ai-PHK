import streamlit as st
from collections import Counter
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS (Responsive)
# ==========================================
st.set_page_config(
    page_title="LAO AI PROFESSIONAL v4.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Grid Container สำหรับจัดเลย์เอาต์การ์ดตัวเลข */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    /* สไตล์การ์ดแสดงผลความถี่ */
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e9ecef;
        border-top: 4px solid #ff4b4b;
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stat-num {
        font-size: 28px;
        font-weight: 800;
        color: #1f2937;
        line-height: 1.2;
    }
    .stat-count {
        font-size: 13px;
        font-weight: 600;
        color: #ef4444;
        background-color: #fee2e2;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FORMULAS & CALCULATION LOGIC
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

def formula1(num): return f"{((int(num[0])+int(num[1])+int(num[2]))*(int(num[3])+int(num[4])+int(num[5])))%10000:04d}"
def formula2(num): return f"{((int(num[0])*int(num[1]))+(int(num[2])*int(num[3]))+(int(num[4])*int(num[5])))%10000:04d}"
def formula3(num): return f"{sum(int(x) for x in num)*111%10000:04d}"
def formula_cross(num): return f"{(int(num[-4])+9)%10}{(int(num[-4])+int(num[-3])+1)%10}"

# ==========================================
# 3. STREAMLIT APP UI
# ==========================================
st.title("🚀 LAO AI PROFESSIONAL v4.0")

# ช่องรับเลขฐาน 6 หลัก
target_number = st.text_input("📌 ป้อนเลขฐาน 6 หลัก:", value="723294", max_chars=6)

if len(target_number) == 6 and target_number.isdigit():
    daily_val, day_name = get_daily_numbers()
    
    # 1. คำนวณผลลัพธ์จากสูตรต่าง ๆ
    f1_res = formula1(target_number)
    f2_res = formula2(target_number)
    f3_res = formula3(target_number)
    cross_res = formula_cross(target_number)
    
    # 2. ตั้งค่าการนับความถี่ตัวเลข (0-9) ครบทุกตัว
    score = {str(i): 0 for i in range(10)}
    
    # รวบรวมผลลัพธ์จากทุกสูตรมารวมกัน
    all_digits_str = f1_res + f2_res + f3_res + cross_res + daily_val
    for digit in all_digits_str:
        if digit in score:
            score[digit] += 1
            
    # 3. เรียงลำดับตามความถี่จากมากไปน้อย
    ranked_digits = sorted(score.items(), key=lambda x: (-x[1], int(x[0])))
    
    # 4. [สำคัญ] ตัดสไลซ์ข้อมูลอาเรย์ เลือกเฉพาะ 6 อันดับแรกที่มีความถี่สูงสุด
    top_6_digits = ranked_digits[:6]
    
    # 5. แสดงผลบนหน้าจอด้วย CSS Grid
    st.subheader("📊 เลขที่ปรากฏบ่อยเมื่อรวมผลลัพธ์จาก 15 สูตร")
    
    cards_html = '<div class="grid-container">'
    for num, count in top_6_digits:
        cards_html += f"""
        <div class="stat-card">
            <div class="stat-num">{num}</div>
            <div class="stat-count">{count} ครั้ง</div>
        </div>
        """
    cards_html += '</div>'
    
    st.markdown(cards_html, unsafe_allow_html=True)
    st.caption("ความถี้นี้นับจากผลลัพธ์การคำนวณทั้งหมด และตัดสไลซ์แสดงผลเฉพาะ 6 อันดับสูงสุด")

else:
    st.warning("⚠️ กรุณากรอกเลขฐานให้ครบ 6 หลัก")
