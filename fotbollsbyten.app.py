import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Fotbollsbyten", layout="wide")

st.title("Fotbollsbyten och positioner")

DATA_FILE = "match_data.json"

positions = [
    "Målvakt",
    "Back",
    "Höger kant",
    "Vänster kant",
    "Topp"
]


# ---------------- SPARA / LADDA DATA ----------------

def save_data():
    data = {
        "players": st.session_state.players,
        "players_locked": st.session_state.players_locked,
        "counts_df": st.session_state.counts_df.to_dict(),
        "next_subs": st.session_state.next_subs
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        st.session_state.players = data.get("players", [])
        st.session_state.players_locked = data.get("players_locked", False)

        counts_data = data.get("counts_df", {})
        if counts_data:
            st.session_state.counts_df = pd.DataFrame(counts_data)
        else:
            st.session_state.counts_df = pd.DataFrame()

        st.session_state.next_subs = data.get(
            "next_subs",
            {position: "" for position in positions}
        )


def reset_match():
    st.session_state.players = []
    st.session_state.players_locked = False
    st.session_state.counts_df = pd.DataFrame()
    st.session_state.next_subs = {position: "" for position in positions}

    if "position_editor" in st.session_state:
        del st.session_state["position_editor"]

    for position in positions:
        key = f"next_sub_{position}"
        if key in st.session_state:
            del st.session_state[key]

    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)


# ---------------- SESSION STATE ----------------

if "players" not in st.session_state:
    st.session_state.players = []

if "players_locked" not in st.session_state:
    st.session_state.players_locked = False

if "counts_df" not in st.session_state:
    st.session_state.counts_df = pd.DataFrame()

if "next_subs" not in st.session_state:
    st.session_state.next_subs = {position: "" for position in positions}

if "data_loaded" not in st.session_state:
    load_data()
    st.session_state.data_loaded = True


# ---------------- STARTSIDESKNAPP ----------------

if st.session_state.players_locked:
    if st.button("Startsida / ny match", use_container_width=True):
        reset_match()
        st.rerun()


# ---------------- SPELARE ----------------

if not st.session_state.players_locked:
    st.subheader("1. Skriv in spelare")

    player_input = st.text_area(
        "Skriv spelarnamn separerade med kommatecken",
        placeholder="Exempel: Rebecca, Saga, Juni, Elsa",
        height=100
    )

    if st.button("Starta match", use_container_width=True):
        players = [name.strip() for name in player_input.split(",") if name.strip()]

        if players:
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

            save_data()
            st.rerun()
        else:
            st.warning("Skriv in minst en spelare.")


# ---------------- MATCHVY ----------------

if st.session_state.players_locked and not st.session_state.counts_df.empty:
    st.subheader("1. Spelare")
    st.write(", ".join(st.session_state.players))

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

    st.session_state.counts_df = edited_df.copy()

    st.info("Tryck på en siffra i tabellen och ändra antalet manuellt.")

    st.subheader("3. Kommande byte")

    for position in positions:
        st.session_state.next_subs[position] = st.text_input(
            label=position,
            value=st.session_state.next_subs.get(position, ""),
            key=f"next_sub_{position}"
        )

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

    save_data()