import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Fotbollsbyten", layout="wide")

st.title("Fotbollsbyten och positioner")

positions = [
    "Målvakt",
    "Back",
    "Höger kant",
    "Vänster kant",
    "Topp"
]

# ---------------- SESSION STATE ----------------

if "players" not in st.session_state:
    st.session_state.players = []

if "players_locked" not in st.session_state:
    st.session_state.players_locked = False

if "counts" not in st.session_state:
    st.session_state.counts = {}

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "dismissed_sub_round" not in st.session_state:
    st.session_state.dismissed_sub_round = 0


# ---------------- TIMER ----------------

st.subheader("⏱ Matchtid")

sub_interval = st.number_input(
    "Byte efter antal minuter",
    min_value=1,
    max_value=30,
    value=7
)

timer_cols = st.columns(3)

with timer_cols[0]:
    if st.button("▶ Start", use_container_width=True):
        if not st.session_state.timer_running:
            st.session_state.start_time = time.time()
            st.session_state.timer_running = True
            st.rerun()

with timer_cols[1]:
    if st.button("⏸ Paus", use_container_width=True):
        if st.session_state.timer_running:
            st.session_state.elapsed_time += time.time() - st.session_state.start_time
            st.session_state.timer_running = False
            st.session_state.start_time = None
            st.rerun()

with timer_cols[2]:
    if st.button("⏹ Reset", use_container_width=True):
        st.session_state.timer_running = False
        st.session_state.elapsed_time = 0
        st.session_state.start_time = None
        st.session_state.dismissed_sub_round = 0
        st.rerun()

if st.session_state.timer_running:
    current_time = st.session_state.elapsed_time + (time.time() - st.session_state.start_time)
else:
    current_time = st.session_state.elapsed_time

minutes = int(current_time // 60)
seconds = int(current_time % 60)

st.markdown(
    f"""
    <div style="
        font-size:46px;
        font-weight:bold;
        text-align:center;
        padding:14px;
        border:1px solid #d1d5db;
        background-color:#f8fafc;
        color:black;
        border-radius:10px;
        margin-bottom:15px;
    ">
        {minutes:02}:{seconds:02}
    </div>
    """,
    unsafe_allow_html=True
)

current_sub_round = minutes // sub_interval

if (
    st.session_state.timer_running
    and minutes >= sub_interval
    and current_sub_round > st.session_state.dismissed_sub_round
):
    st.error("🔁 BYTE!")

    if st.button("Stäng bytesvarning", use_container_width=True):
        st.session_state.dismissed_sub_round = current_sub_round
        st.rerun()


# ---------------- SPELARE ----------------

if not st.session_state.players_locked:
    st.subheader("1. Skriv in spelare")

    player_input = st.text_area(
        "Skriv spelarnamn separerade med kommatecken",
        placeholder="Exempel: Alice, Elsa, Maja, Nora, Sara",
        height=100
    )

    if st.button("Klar", use_container_width=True):
        players = [name.strip() for name in player_input.split(",") if name.strip()]
        st.session_state.players = players
        st.session_state.players_locked = True

        for position in positions:
            for player in players:
                key = f"{position}_{player}"
                if key not in st.session_state.counts:
                    st.session_state.counts[key] = 0

        st.rerun()

else:
    st.subheader("1. Spelare")
    st.write(", ".join(st.session_state.players))

    if st.button("Ändra spelare", use_container_width=True):
        st.session_state.players_locked = False
        st.rerun()

players = st.session_state.players


# ---------------- MOBILANPASSAD TABELL ----------------

if players and st.session_state.players_locked:
    st.subheader("2. Positioner")

    st.markdown("""
        <style>

        .position-box {
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 8px;
            margin-bottom: 12px;
            background-color: #f8fafc;
        }

        .position-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 8px;
            text-align: center;
            color: black;
        }

        .player-name {
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            padding-top: 6px;
            color: black;
        }

        .count-number {
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            padding-top: 6px;
            color: black;
        }

        div.stButton > button {
            min-height: 28px;
            height: 28px;
            font-size: 14px;
            padding: 0px 4px;
        }

        </style>
    """, unsafe_allow_html=True)

    for position in positions:
        st.markdown(
            f"""
            <div class="position-box">
                <div class="position-title">{position}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        for player in players:
            key = f"{position}_{player}"

            player_col, minus_col, number_col, plus_col = st.columns([2, 1, 1, 1])

            with player_col:
                st.markdown(
                    f"<div class='player-name'>{player}</div>",
                    unsafe_allow_html=True
                )

            with minus_col:
                if st.button("−", key=f"minus_{key}"):
                    if st.session_state.counts[key] > 0:
                        st.session_state.counts[key] -= 1
                    st.rerun()

            with number_col:
                st.markdown(
                    f"<div class='count-number'>{st.session_state.counts[key]}</div>",
                    unsafe_allow_html=True
                )

            with plus_col:
                if st.button("＋", key=f"plus_{key}"):
                    st.session_state.counts[key] += 1
                    st.rerun()

        st.divider()

    st.subheader("3. Sammanfattning")

    data = []
    for position in positions:
        row = {"Position": position}
        for player in players:
            key = f"{position}_{player}"
            row[player] = st.session_state.counts[key]
        data.append(row)

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ---------------- AUTOUPPDATERING ----------------

if st.session_state.timer_running:
    time.sleep(1)
    st.rerun()