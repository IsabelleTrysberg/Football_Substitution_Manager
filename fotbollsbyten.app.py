import streamlit as st
import pandas as pd

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

if "next_subs" not in st.session_state:
    st.session_state.next_subs = {position: "" for position in positions}


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

        st.session_state.next_subs = {
            position: "" for position in positions
        }

        st.rerun()

else:
    st.subheader("1. Spelare")
    st.write(", ".join(st.session_state.players))

    if st.button("Ändra spelare / ny match", use_container_width=True):
        st.session_state.players_locked = False
        st.session_state.players = []
        st.session_state.counts_df = pd.DataFrame()
        st.session_state.next_subs = {
            position: "" for position in positions
        }
        st.rerun()


# ---------------- POSITIONSTABELL ----------------

if st.session_state.players_locked and not st.session_state.counts_df.empty:
    st.subheader("2. Positionstabell")

    def update_counts():
        st.session_state.counts_df = st.session_state.position_editor

    st.data_editor(
        st.session_state.counts_df,
        use_container_width=True,
        num_rows="fixed",
        key="position_editor",
        on_change=update_counts,
        column_config={
            position: st.column_config.NumberColumn(
                position,
                min_value=0,
                step=1
            )
            for position in positions
        }
    )

    st.info("Tryck på en siffra i tabellen och ändra antalet manuellt.")


    # ---------------- KOMMANDE BYTE ----------------

    st.subheader("3. Kommande byte")

    st.write("Skriv in vilka som ska spela på respektive position vid nästa byte.")

    for position in positions:
        st.session_state.next_subs[position] = st.text_input(
            label=position,
            value=st.session_state.next_subs.get(position, ""),
            key=f"next_sub_{position}"
        )


    # ---------------- ÖVERSIKT ----------------

    st.subheader("4. Översikt")

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