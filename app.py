import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="물의 분자 시뮬레이션 실험실", page_icon="💧", layout="centered")

# 나눔고딕 폰트 설정 (그래프용)
plt.rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False

st.title("💧 물의 상태 변화 분자 실험실")
st.markdown("온도 조절 슬라이더를 움직여 **얼음, 물, 수증기** 속 분자들의 움직임을 관찰해 보세요!")

# --- 사이드바 조작 ---
st.sidebar.header("🎛️ 실험 패널")
mass = st.sidebar.slider("물의 질량 (g)", 10, 100, 50, 10)
energy = st.sidebar.slider("공급 에너지 (kJ)", 0.0, float(mass * 3.0), 0.0, 1.0)

# --- 상태 계산 로직 ---
def get_status(e_kj, m):
    e = e_kj * 1000
    e1 = m * 2.09 * 20
    e2 = e1 + (m * 334)
    e3 = e2 + (m * 4.184 * 100)
    e4 = e3 + (m * 2260)
    
    if e <= e1: return -20 + e/(m*2.09), "SOLID", "🧊 얼음 (고체)"
    elif e <= e2: return 0.0, "MELTING", "🧊→💧 녹는 중"
    elif e <= e3: return (e-e2)/(m*4.184), "LIQUID", "💧 물 (액체)"
    elif e <= e4: return 100.0, "BOILING", "💧→💨 끓는 중"
    else: return 100 + (e-e4)/(m*2.01), "GAS", "💨 수증기 (기체)"

temp, state_key, state_desc = get_status(energy, mass)

# --- 결과 표시 ---
c1, c2 = st.columns(2)
c1.metric("🌡️ 현재 온도", f"{temp:.1f}°C")
c2.info(f"**현재 상태:** {state_desc}")

# --- 핵심: 분자 시뮬레이션 (HTML/JS) ---
# 상태별 분자 움직임을 자바스크립트로 구현
st.subheader("🔬 현미경으로 본 분자 배열")

js_code = f"""
<div id="container" style="width: 100%; height: 300px; background: #f0f2f6; border-radius: 15px; position: relative; overflow: hidden; border: 2px solid #3b82f6;">
    <canvas id="canvas" style="width: 100%; height: 100%;"></canvas>
</div>

<script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    const state = "{state_key}";
    const molecules = [];
    const count = 40;

    class Molecule {{
        constructor() {{
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.r = 8;
            this.vx = (Math.random() - 0.5) * 2;
            this.vy = (Math.random() - 0.5) * 2;
        }}

        draw() {{
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fillStyle = '#3b82f6';
            ctx.fill();
            ctx.strokeStyle = 'white';
            ctx.stroke();
            ctx.closePath();
        }}

        update() {{
            if (state === "SOLID") {{
                // 고체: 제자리 진동
                this.x += (Math.random() - 0.5) * 0.5;
                this.y += (Math.random() - 0.5) * 0.5;
            }} else if (state === "LIQUID" || state === "MELTING") {{
                // 액체: 바닥에 모여서 흐름
                this.x += this.vx * 0.5;
                this.y += this.vy * 0.5;
                if (this.y < canvas.height * 0.6) this.vy += 0.1; // 중력 효과
            }} else {{
                // 기체: 매우 빠르게 날아다님
                this.x += this.vx * 5;
                this.y += this.vy * 5;
            }}

            // 벽 충돌 처리
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }}
    }}

    // 초기 배치 (고체는 규칙적으로)
    for (let i = 0; i < count; i++) {{
        let m = new Molecule();
        if (state === "SOLID" || state === "MELTING") {{
            m.x = (i % 8) * 40 + 80;
            m.y = Math.floor(i / 8) * 40 + 100;
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

components.html(js_code, height=320)

st.divider()

# --- 가열 곡선 그래프 ---
st.subheader("📈 가열 곡선")
e_axis = np.linspace(0, mass * 3.0, 200)
t_axis = [get_status(e, mass)[0] for e in e_axis]
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(e_axis, t_axis, color="#3b82f6", alpha=0.5)
ax.scatter(energy, temp, color="red", s=100, zorder=5)
ax.set_title("열에너지-온도 그래프")
ax.set_xlabel("에너지 (kJ)")
ax.set_ylabel("온도 (°C)")
st.pyplot(fig)

st.divider()

# --- 중학생용 설명 ---
with st.expander("📖 중학생 눈높이 상태 변화 설명"):
    st.markdown(f"""
    ### 현재 상태: {state_desc}
    * **🧊 고체 (얼음):** 위 그림을 보세요! 분자들이 규칙적으로 딱딱 붙어있죠? 제자리에서 **진동**만 하고 있어요.
    * **💧 액체 (물):** 분자들이 서로 조금씩 떨어져서 **자유롭게 자리바꿈**을 해요. 그래서 흐를 수 있는 거예요.
    * **💨 기체 (수증기):** 분자들이 서로 아주 멀리 떨어져서 **엄청나게 빠른 속도**로 날아다녀요!
    """)
