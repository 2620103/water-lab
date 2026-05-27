import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="물의 상태 변화 실험실", page_icon="💧", layout="centered")

# --- 폰트 깨짐 방지 설정 (기존 코드를 이 구역으로 교체) ---
import matplotlib.font_manager as fm

# 리눅스 시스템에 설치된 나눔고딕 폰트 파일 경로를 직접 지정합니다.
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

try:
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
except:
    # 혹시 모를 예외 상황을 위한 기본 폰트 패스
    plt.rc('font', family='sans-serif')

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
# ----------------------------------------------------

st.title("💧 물의 상태 변화 분자 실험실")
st.markdown("""
이 실험실에서는 얼음에 열에너지를 공급할 때 온도가 어떻게 변하는지 관찰할 수 있습니다.
사이드바의 슬라이더를 조절하여 **분자의 배열**과 **가열 곡선**을 실시간으로 확인해 보세요!
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
        state_key = "SOLID"
        phase = "🧊 고체 (얼음)"
    elif e_total <= e2:
        temp = 0.0
        state_key = "MELTING"
        phase = "🧊+💧 고체와 액체의 공존 (얼음이 녹는 중)"
    elif e_total <= e3:
        temp = 0.0 + (e_total - e2) / (m * c_water)
        state_key = "LIQUID"
        phase = "💧 액체 (물)"
    elif e_total <= e4:
        temp = 100.0
        state_key = "BOILING"
        phase = "💧+💨 액체와 기체의 공존 (물이 끓는 중)"
    else:
        temp = 100 + (e_total - e4) / (m * c_steam)
        state_key = "GAS"
        phase = "💨 기체 (수증기)"
        
    return temp, state_key, phase, [e1/1000, e2/1000, e3/1000, e4/1000]

# 현재 상태 계산
current_temp, current_key, current_phase, milestones = calc_temp_and_phase(energy, mass)

# --- 결과 디스플레이 ---
col1, col2, col3 = st.columns(3)
col1.metric("⚖️ 물의 질량", f"{mass} g")
col2.metric("🔥 공급된 에너지", f"{energy} kJ")
col3.metric("🌡️ 현재 온도", f"{current_temp:.0f}°C" if current_temp == 0 or current_temp == 100 else f"{current_temp:.1f}°C")

st.info(f"**현재 물질의 상태:** {current_phase}")

st.divider()

# --- 🔬 실시간 분자 현미경 (HTML/JS 동적 그림) ---
st.subheader("🔬 현미경으로 본 물 분자 배열")

js_code = f"""
<div id="container" style="width: 100%; height: 280px; background: #f0f4f8; border-radius: 15px; position: relative; overflow: hidden; border: 2px solid #3b82f6;">
    <canvas id="canvas" style="width: 100%; height: 100%;"></canvas>
</div>

<script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    const state = "{current_key}";
    const molecules = [];
    const count = 45;

    class Molecule {{
        constructor() {{
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.r = 7;
            this.vx = (Math.random() - 0.5) * 3;
            this.vy = (Math.random() - 0.5) * 3;
        }}

        draw() {{
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fillStyle = state === "SOLID" ? "#4fc3f7" : (state === "GAS" ? "#b0bec5" : "#2196f3");
            ctx.fill();
            ctx.strokeStyle = 'white';
            ctx.stroke();
            ctx.closePath();
        }}

        update() {{
            if (state === "SOLID") {{
                // 고체: 규칙적인 제자리 진동
                this.x += (Math.random() - 0.5) * 0.6;
                this.y += (Math.random() - 0.5) * 0.6;
            }} else if (state === "MELTING") {{
                // 녹는 중: 일부는 진동, 일부는 느리게 이동
                this.x += this.vx * 0.2 + (Math.random() - 0.5) * 0.4;
                this.y += this.vy * 0.2 + (Math.random() - 0.5) * 0.4;
                if (this.y < canvas.height * 0.5) this.vy += 0.1; 
            }} else if (state === "LIQUID" || state === "BOILING") {{
                // 액체: 바닥에 모여 찰랑거리며 자유롭게 이동
                this.x += this.vx * 0.8;
                this.y += this.vy * 0.8;
                if (this.y < canvas.height * 0.5) this.vy += 0.15; // 중력 효과
            }} else {{
                // 기체: 온 사방으로 초고속 비행
                this.x += this.vx * 4;
                this.y += this.vy * 4;
            }}

            // 벽 충돌 방지
            if (this.x < 10 || this.x > canvas.width - 10) this.vx *= -1;
            if (this.y < 10 || this.y > canvas.height - 10) this.vy *= -1;
        }}
    }}

    // 초기 배열 설정 (고체 계열은 격자 무늬로 정렬)
    for (let i = 0; i < count; i++) {{
        let m = new Molecule();
        if (state === "SOLID" || state === "MELTING") {{
            m.x = (i % 9) * 45 + 50;
            m.y = Math.floor(i / 9) * 35 + 60;
        }}
        molecules.push(m);
    }}

    function animate() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        molecules.forEach(m => {{
            m.update();
            m.draw();
        }});
        requestAnimationFrame(animate);
    }}
    animate();
</script>
"""

components.html(js_code, height=300)

st.divider()

# --- 가열 곡선 그래프 그리기 ---
st.subheader("📈 물의 가열 곡선 그래프")

e_axis = np.linspace(0, max_energy, 500)
t_axis = [calc_temp_and_phase(e, mass)[0] for e in e_axis]

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(e_axis, t_axis, color="#4FC3F7", linewidth=2.5, label="가열 곡선")
ax.scatter(energy, current_temp, color="#E53935", s=120, zorder=5, label="현재 상태")

# 그래프 주요 구간 텍스트
ax.text(milestones[0]/2, -10, "얼음(고체)", fontsize=9, ha='center', color='gray')
ax.text((milestones[0]+milestones[1])/2, 8, "융해(녹는 중)", fontsize=9, ha='center', color='gray')
ax.text((milestones[1]+milestones[2])/2, 50, "물(액체)", fontsize=9, ha='center', color='gray')
ax.text((milestones[2]+milestones[3])/2, 110, "기화(끓는 중)", fontsize=9, ha='center', color='gray')

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

# --- 중학생용 눈높이 설명 ---
with st.expander("📚 중학생도 단번에 이해하는 물의 비밀! (쉽게 읽는 과학 원리)"):
    st.markdown("""
    ### 1. 🧊 0°C와 100°C에서 그래프가 멈추는(평평한) 이유는?
    * 열심히 열을 주고 있는데도 온도가 오르지 않는 신기한 구간이 있죠?
    * 이때 공급된 열은 온도를 올리는 데 쓰이지 않고, **분자들이 서로 꼭 붙잡고 있는 손(인력)을 끊고 상태를 바꾸는 데** 전부 사용되기 때문이에요!
    * **0°C (녹는점):** 얼음이 물로 변하느라 바쁜 구간 (융해)
    * **100°C (끓는점):** 물이 수증기로 변하느라 바쁜 구간 (기화)
    
    ---
    
    ### 2. 🔬 현미경 속 분자들의 움직임을 비교해 봐요!
    * **얼음 (고체):** 분자들이 자리를 지키며 규칙적으로 배열되어 있고, 제자리에서 "덜덜덜" **진동**만 해요.
    * **물 (액체):** 규칙성이 깨져서 아래쪽에 찰랑거리며 모여 있고, 서로 자리를 바꾸며 **자유롭게 미끄러지듯** 움직여요.
    * **수증기 (기체):** 서로를 붙잡던 힘을 완전히 이겨내고, 공간 전체로 **엄청나게 빠른 속도**로 날아다녀요!
    """)
