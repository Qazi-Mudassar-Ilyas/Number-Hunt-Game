
import random
import time
import streamlit as st

st.set_page_config(page_title="Number Hunt", page_icon="🎯", layout="centered")

# ---------- Styling ----------
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #101b35 0%, #172b4d 100%); color: #f5f7ff;}
.block-container {max-width: 680px; padding-top: 2rem; padding-bottom: 2rem;}
h1, h2, h3, p, label {color: #f5f7ff !important;}
.hero {text-align:center; padding: 1.2rem 0 1rem;}
.hero-icon {font-size: 3.2rem;}
.hero-title {font-size: 2.5rem; font-weight: 800; letter-spacing: -1px;}
.hero-sub {color:#c4d2ed; font-size:1.05rem;}
.panel {background:#20385e; border:1px solid #36527b; border-radius:18px;
        padding:1.2rem; margin:0.8rem 0; text-align:center;}
.metric {font-size:2rem; font-weight:800; color:#70e1c1;}
.metric-label {font-size:.85rem; color:#c4d2ed;}
.hint {background:#20385e; border-radius:14px; padding:1rem; text-align:center;
       font-size:1.05rem; margin:1rem 0;}
div.stButton > button, div.stFormSubmitButton > button {
    width:100%; min-height:3rem; border-radius:12px; font-weight:700;
}
div[data-testid="stNumberInput"] input {font-size:1.2rem; text-align:center;}
div[data-testid="stMetric"] {background:#20385e; padding:12px; border-radius:12px;}
@media (max-width: 600px) {
 .block-container {padding:1rem 1rem 2rem;}
 .hero-title {font-size:2rem;}
}
</style>
""", unsafe_allow_html=True)

# ---------- Game state ----------
def initialise():
    defaults = {
        "screen": "home", "secret": None, "deadline": None,
        "attempts": 0, "guesses": [], "hint": "Enter your first guess.",
        "outcome": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def start_game():
    st.session_state.secret = random.randint(1, 100)
    st.session_state.deadline = time.time() + 60
    st.session_state.attempts = 0
    st.session_state.guesses = []
    st.session_state.hint = "Make your first guess."
    st.session_state.outcome = None
    st.session_state.screen = "playing"

def finish_game(outcome):
    st.session_state.outcome = outcome
    st.session_state.screen = "results"

initialise()

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="hero-icon">🎯</div>
  <div class="hero-title">Number Hunt</div>
  <div class="hero-sub">The 60-Second Challenge</div>
</div>
""", unsafe_allow_html=True)

# ---------- Home screen ----------
if st.session_state.screen == "home":
    st.markdown('<div class="panel"><h3>Can you find the hidden number?</h3>'
                '<p>The computer has selected a number between 1 and 100. '
                'You have 60 seconds to find it.</p>'
                '<p>After each guess, you will receive a hint telling you '
                'whether to go higher or lower.</p></div>', unsafe_allow_html=True)
    st.info("You can only submit each number once. Every valid guess counts as an attempt.")
    if st.button("Start Game", type="primary", use_container_width=True):
        start_game()
        st.rerun()

# ---------- Live countdown ----------
elif st.session_state.screen == "playing":
    @st.fragment(run_every="1s")
    def live_timer():
        remaining = max(0, int(st.session_state.deadline - time.time() + 0.999))
        if remaining <= 0 and st.session_state.screen == "playing":
            finish_game("lost")
            st.rerun()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="panel"><div class="metric">{remaining}s</div>'
                        '<div class="metric-label">TIME LEFT</div></div>',
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="panel"><div class="metric">{st.session_state.attempts}</div>'
                        '<div class="metric-label">ATTEMPTS</div></div>',
                        unsafe_allow_html=True)
    live_timer()

    st.markdown('<div class="hint">' + st.session_state.hint + '</div>',
                unsafe_allow_html=True)

    with st.form("guess_form", clear_on_submit=True):
        guess = st.number_input("Enter your guess (1–100)", min_value=1,
                                max_value=100, value=50, step=1)
        submitted = st.form_submit_button("Submit Guess", type="primary",
                                          use_container_width=True)

    if submitted and st.session_state.screen == "playing":
        if time.time() >= st.session_state.deadline:
            finish_game("lost")
            st.rerun()
        elif guess in st.session_state.guesses:
            st.warning("You have already tried that number. Choose another.")
        else:
            st.session_state.guesses.append(guess)
            st.session_state.attempts += 1
            if guess == st.session_state.secret:
                st.session_state.hint = "Correct! You found it!"
                finish_game("won")
                st.rerun()
            elif guess > st.session_state.secret:
                st.session_state.hint = "Too high! Try a smaller number."
            else:
                st.session_state.hint = "Too low! Try a larger number."
            st.rerun()

    if st.session_state.guesses:
        st.caption("Previous guesses: " + ", ".join(map(str, st.session_state.guesses)))

# ---------- Results screen ----------
elif st.session_state.screen == "results":
    if st.session_state.outcome == "won":
        st.success("You won! You found the hidden number.")
        st.balloons()
    else:
        st.error("Time's up! Better luck next time.")
    st.markdown(f'<div class="panel"><h2>Game Over</h2>'
                f'<p>The secret number was</p><div class="metric">'
                f'{st.session_state.secret}</div>'
                f'<p>Total attempts: <b>{st.session_state.attempts}</b></p>'
                '</div>', unsafe_allow_html=True)
    if st.button("Play Again", type="primary", use_container_width=True):
        start_game()
        st.rerun()
