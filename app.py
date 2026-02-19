import streamlit as st
import time
from robust_sql_chain import initial_generation, feedback_generation

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="SQL Assistant AI", page_icon="🤖", layout="centered")

st.title("SQL Data Assistant")
st.markdown("Interogheaza baza de date folosind limbaj natural.")

# --- INIȚIALIZARE STATE (Memoria aplicației) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Variabile pentru a ține minte ultimul context pentru feedback
if "last_question" not in st.session_state:
    st.session_state.last_question = None
if "last_sql" not in st.session_state:
    st.session_state.last_sql = None

# --- AFIȘAREA ISTORICULUI DE CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Dacă mesajul conține SQL, îl afișăm într-un bloc de cod
        if "sql" in message and message["sql"]:
            st.code(message["sql"], language="sql")

# --- ZONA DE FEEDBACK (SIDEBAR) ---
# Apare doar dacă avem un răspuns anterior
with st.sidebar:
    st.header(" Feedback ")
    if st.session_state.last_sql:
        st.info("Ultima interogare poate fi rafinata daca rezultatul nu e bun.")
        
        with st.form("feedback_form"):
            motiv = st.text_area("Ce nu a fost bine?", placeholder="Ex: Nu vreau ordonare dupa nume...")
            submit_feedback = st.form_submit_button("Repara Raspunsul")
            
            if submit_feedback and motiv:
                # Aici apelăm funcția ta de feedback_generation
                with st.spinner("Se aplica feedback-ul tau..."):
                    new_answer, new_sql = feedback_generation(
                        st.session_state.last_question, 
                        st.session_state.last_sql, 
                        motiv
                    )
                    
                    # Adăugăm corecția în chat
                    st.session_state.messages.append({"role": "user", "content": f"Feedback: {motiv}"})
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"**Revizuit:** {new_answer}",
                        "sql": new_sql
                    })
                    
                    # Actualizăm starea
                    st.session_state.last_sql = new_sql
                    st.rerun() # Reîncărcăm pagina pentru a arăta mesajele noi
    else:
        st.write("Pune o intrebare pentru a activa optiunile de feedback.")

# --- ZONA DE INPUT PRINCIPALĂ ---
if prompt := st.chat_input("Ce vrei sa afli din baza de date?"):
    # 1. Afișăm întrebarea utilizatorului
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Procesăm răspunsul
    with st.chat_message("assistant"):
        with st.spinner("AI-ul gandeste si ruleaza SQL..."):
            # Apelăm funcția din robust_sql_chain.py
            answer, sql_used = initial_generation(prompt)
            
            st.markdown(answer)
            if sql_used:
                st.code(sql_used, language="sql")
    
    # 3. Salvăm în istoric și actualizăm contextul pentru feedback
    st.session_state.messages.append({"role": "assistant", "content": answer, "sql": sql_used})
    st.session_state.last_question = prompt
    st.session_state.last_sql = sql_used
    
    # Forțăm o mică reîncărcare pentru a actualiza sidebar-ul
    time.sleep(0.1)
    st.rerun()