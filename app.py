import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 폰트 깨짐 방지 설정 ---
# 스트림릿 클라우드(리눅스) 환경에 설치될 나눔고딕 폰트를 적용합니다.
plt.rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="물의 상태 변화 실험실", page_icon="💧", layout="centered")

st.title("💧 물의 가열 곡선 및 상태 변화 가상 실험실")
st.markdown("""
이 실험실에서는 얼음에 열에너지를 공급할 때 온도가 어떻게 변하는지 관찰할 수 있습니다.
상태가 변하는 구간(**0°C 융해 구간**, **100°C 기화 구간**)에서 온도가 일정하게 유지되는 현상을 눈으로 확인해 보세요!
""")

st.divider()

# --- 사이드바: 조작 패널 ---
st.sidebar.header("🎛️ 실험 조작 패널")

# 1. 물의 질량 (g)
mass = st.sidebar.slider("물의 질량 (g)", min_value=10, max_value=100, value=50, step=10)

# 2. 공급한 열에너지 (kJ)
max_energy = int(mass * 3.0)  
energy = st.sidebar.slider("공급한 열에너지 (kJ)", min_value=0.0, max_value=float(max_energy), value=0.0, step=1.0)

# --- 물의 물리적 상수 ---
c_ice = 2.09       # 얼음의 비열
H_fusion = 334     # 융해열
c_water = 4.184    # 물의 비열
H_vap = 2260       # 기화열
c_steam = 2.01     # 수증기의 비열

# --- 에너지에 따른 온도 및 상태 계산 함수 ---
def calc_temp_and_phase(e_total_kj, m):
    e_total = e_total_kj * 1000 # kJ -> J 변환
    
    e1 = m * c_ice * 20                         
    e2 = e1 + (m * H_fusion)                    
    e3 = e2 + (m * c_water * 100)               
    e4 = e3 + (m * H_vap)                       
    
    if e_total <= e1:
        temp = -20 + e_total / (m * c_ice)
        phase = "🧊 고체 (얼음)"
    elif e_total <= e2:
        temp = 0.0
        phase = "🧊+💧 고체와 액체의 공존 (얼음이 녹는 중)"
    elif e_total <= e3:
        temp = 0.0 + (e_total - e2) / (m * c_water)
        phase = "💧 액체 (물)"
    elif e_total <= e4:
        temp = 100.0
        phase = "💧+💨 액체와 기체의 공존 (물이 끓는 중)"
    else:
        temp = 100 + (e_total - e4) / (m * c_steam)
        phase = "💨 기체 (수증기)"
        
    return temp, phase, [e1/1000, e2/1000, e3/1000, e4/1000]

# 현재 상태 계산
current_temp, current_phase, milestones = calc_temp_and_phase(energy, mass)

# --- 결과 디스플레이 ---
col1, col2, col3 = st.columns(3)
col1.metric("⚖️ 물의 질량", f"{mass} g")
col2.metric("🔥 공급된 에너지", f"{energy} kJ")
col3.metric("🌡️ 현재 온도", f"{current_temp:.0f}°C" if current_temp == 0 or current_temp == 100 else f"{current_temp:.1f}°C")

st.info(f"**현재 물질의 상태:** {current_phase}")

st.divider()

# --- 가열 곡선 그래프 그리기 ---
st.subheader("📈 물의 가열 곡선 그래프")

e_axis = np.linspace(0, max_energy, 500)
t_axis = [calc_temp_and_phase(e, mass)[0] for e in e_axis]

fig, ax = plt.subplots(figsize=(7, 4))
# 한글 레이블 및 텍스트 적용
ax.plot(e_axis, t_axis, color="#4FC3F7", linewidth=2.5, label="가열 곡선")
ax.scatter(energy, current_temp, color="#E53935", s=120, zorder=5, label="현재 상태")

# 그래프 내부 구간 텍스트 한글화
ax.text(milestones[0]/2, -10, "얼음(고체)", fontsize=9, ha='center', color='gray')
ax.text((milestones[0]+milestones[1])/2, 8, "융해(녹는 중)", fontsize=9, ha='center', color='gray')
ax.text((milestones[1]+milestones[2])/2, 50, "물(액체)", fontsize=9, ha='center', color='gray')
ax.text((milestones[2]+milestones[3])/2, 110, "기화(끓는 중)", fontsize=9, ha='center', color='gray')

# 축 및 타이틀 한글화
ax.set_title("물의 가열 곡선 시뮬레이션", fontsize=12, fontweight='bold')
ax.set_xlabel("공급된 열에너지 (kJ)", fontsize=10)
ax.set_ylabel("온도 (°C)", fontsize=10)
ax.set_xlim(0, max_energy)
ax.set_ylim(-25, 130)
ax.axhline(0, color='black', linestyle='--', alpha=0.3)
ax.axhline(100, color='black', linestyle='--', alpha=0.3)
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()

st.pyplot(fig)

st.divider()

# --- 이 아래 부분을 기존 앱 맨 밑에 덮어쓰기 하세요 ---

with st.expander("📚 중학생도 단번에 이해하는 물의 비밀! (쉽게 읽는 과학 원리)"):
    st.markdown("""
    ### 1. 🧊 0°C와 100°C에서 그래프가 멈추는(평평한) 이유는?
    * 열심히 열(에너지)을 주고 있는데도 온도가 오르지 않고 똑같이 유지되는 신기한 구간이 있죠? 
    * 이때 공급된 열은 **온도를 올리는 데 쓰이지 않고, 분자들이 서로 꼭 붙잡고 있는 손(인력)을 끊고 상태를 바꾸는 데** 전부 사용되기 때문이에요!
    * **0°C (녹는점):** 얼음이 물로 변하느라 바쁜 구간 (융해)
    * **100°C (끓는점):** 물이 수증기로 변하느라 바쁜 구간 (기화)
    
    ---
    
    ### 2. 🔥 숨어있는 에너지, '잠열(Hidden Heat)'
    * 상태가 변하는 동안 물질이 흡수하는 열을 **‘잠열’**이라고 해요. 눈에 보이지 않게 숨어버리는 열이라는 뜻이죠.
    * **얼음이 녹을 때**는 주변의 열을 흡수해요. (얼음주머니를 대면 시원해지는 이유!)
    * **물이 끓어 수증기가 될 때**는 엄청난 양의 열을 흡수해요. 그래서 100°C의 물에 데는 것보다, 100°C의 수증기에 데는 것이 훨씬 더 큰 화상을 입을 수 있어 위험하답니다.
    
    ---
    
    ### 🧪 슬라이더를 움직이며 미션에 도전해 보세요!
    1. **미션 1:** 에너지를 조금씩 올려보며 **0°C**에서 빨간 점이 얼마나 오랫동안 멈춰 서 있는지 관찰하기!
    2. **미션 2:** 물의 질량(g)을 100g으로 늘려보기! 물이 많아지면 끓기 시작할 때까지(100°C에 도달할 때까지) 훨씬 더 많은 에너지가 필요하다는 것을 그래프 기울기로 확인해 보세요!
    """)
