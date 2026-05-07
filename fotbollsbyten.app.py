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

if "counts_df" not in st.session_state:
    st.session_state.counts_df = pd.DataFrame()

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
        placeholder="Exempel: Rebecca, Saga, Juni, Elsa",
        height=100
    )

    if st.button("Klar", use_container_width=True):
        players = [name.strip() for name in player_input.split(",") if name.strip()]
        st.session_state.players = players
        st.session_state.players_locked = True

        st.session_state.counts_df = pd.DataFrame(
            0,
            index=players,
            columns=positions
        )

        st.rerun()

else:
    st.subheader("1. Spelare")
    st.write(", ".join(st.session_state.players))

    if st.button("Ändra spelare / ny match", use_container_width=True):
        st.session_state.players_locked = False
        st.session_state.players = []
        st.session_state.counts_df = pd.DataFrame()
        st.rerun()


# ---------------- POSITIONSTABELL ----------------

if st.session_state.players_locked and not st.session_state.counts_df.empty:
    st.subheader("2. Positionstabell")

    edited_df = st.data_editor(
        st.session_state.counts_df,
        use_container_width=True,
        num_rows="fixed",
        key="position_editor",
        column_config={
            position: st.column_config.NumberColumn(
                position,
                min_value=0,
                step=1
            )
            for position in positions
        }
    )

    st.session_state.counts_df = edited_df

    st.info("Tryck på en siffra i tabellen och ändra antalet manuellt.")

    st.subheader("3. Översikt")
    st.dataframe(
        st.session_state.counts_df,
        use_container_width=True
    )

    st.download_button(
    "Ladda ner som CSV",
    st.session_state.counts_df.to_csv().encode("utf-8"),
    "match_oversikt.csv",
    "text/csv"
    )

# ---------------- AUTOUPPDATERING ----------------

if st.session_state.timer_running:
    time.sleep(1)
    st.rerun()