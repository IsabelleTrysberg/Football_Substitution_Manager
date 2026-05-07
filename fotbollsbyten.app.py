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
        font-size:52px;
        font-weight:bold;
        text-align:center;
        padding:18px;
        border:1px solid white;
        background-color:#111827;
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


# ---------------- TABELL ----------------

if players and st.session_state.players_locked:
    st.subheader("2. Positionstabell")

    st.markdown("""
        <style>
        .header-cell {
            font-weight: bold;
            font-size: 18px;
            background-color: #1f2937;
            padding: 12px;
            border-radius: 6px;
        }

        .position-name {
            font-weight: bold;
            font-size: 18px;
        }

        div.stButton > button {
            padding: 2px 8px;
            font-size: 16px;
            min-height: 32px;
            height: 32px;
            width: 100%;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    cell_style = """
        border: 1px solid white;
        padding: 10px;
        text-align: center;
        background-color: #111827;
    """

    header_cols = st.columns([1.5] + [1] * len(players))

    with header_cols[0]:
        st.markdown(
            f"<div style='{cell_style}'><div class='header-cell'>Position</div></div>",
            unsafe_allow_html=True
        )

    for i, player in enumerate(players):
        with header_cols[i + 1]:
            st.markdown(
                f"<div style='{cell_style}'><div class='header-cell'>{player}</div></div>",
                unsafe_allow_html=True
            )

    for position in positions:
        row_cols = st.columns([1.5] + [1] * len(players))

        with row_cols[0]:
            st.markdown(
                f"<div style='{cell_style}'><div class='position-name'>{position}</div></div>",
                unsafe_allow_html=True
            )

        for i, player in enumerate(players):
            key = f"{position}_{player}"

            with row_cols[i + 1]:
                minus_col, number_col, plus_col = st.columns([1, 1, 1])

                with minus_col:
                    if st.button("−", key=f"minus_{key}"):
                        if st.session_state.counts[key] > 0:
                            st.session_state.counts[key] -= 1
                        st.rerun()

                with number_col:
                    st.markdown(
                        f"""
                        <div style="
                            text-align:center;
                            font-size:32px;
                            font-weight:bold;
                            padding-top:8px;
                        ">
                            {st.session_state.counts[key]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with plus_col:
                    if st.button("＋", key=f"plus_{key}"):
                        st.session_state.counts[key] += 1
                        st.rerun()

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