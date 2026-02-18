import os
import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter

load_dotenv()

# 1. Setup Bază de Date & LLM
db_path = "sqlite:///data/test_db.sqlite"
db = SQLDatabase.from_uri(db_path)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Obținem data de azi pentru a o "cimenta" în prompt (evităm eroarea de variabilă lipsă)
today = datetime.date.today().isoformat()

# 2. PROMPT ENGINEERING AVANSAT (Corectat pentru LangChain 0.3)
# ATENȚIE: Trebuie să folosim {input}, {table_info}, și {top_k} obligatoriu!

system_instruction = f"""You are an expert SQL Data Analyst. Given an input question, create a syntactically correct SQLite query to run.

Here is the database schema regarding Users, Products, and Orders:
{{table_info}}

IMPORTANT RULES FOR AMBIGUITY:
1. "Best customer" or "Top client" -> Order by 'total_amount' DESC (money spent), not number of orders.
2. "Popular product" -> Order by quantity sold or count of orders.
3. "Recent" -> Use the 'order_date' column. compare with current date: {today}.
4. If the user asks for a specific name but uses vague spelling, use 'LIKE' with wildcards (e.g. '%name%').
5. Limit results to {{top_k}} unless specified otherwise.
6. Return ONLY the SQL query, no markdown, no explanation.
"""

# Definim promptul folosind variabilele standard
prompt = ChatPromptTemplate.from_messages([
    ("system", system_instruction),
    ("human", "{input}"), # LangChain cere 'input', nu 'question'
])

# 3. Construirea Lanțului
# create_sql_query_chain va popula automat {table_info} și {top_k} (default 5)
generate_query_chain = create_sql_query_chain(llm, db, prompt=prompt)
execute_query_tool = QuerySQLDataBaseTool(db=db)

# Prompt pentru răspuns final (Natural Language)
final_answer_prompt = ChatPromptTemplate.from_template(
    """Based on the user question and the SQL result, write a natural answer in Romanian.
    
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    
    Answer:"""
)

# 4. Pipeline-ul Final (LCEL)
chain = (
    RunnablePassthrough.assign(
        # Convertim 'question' de la user în 'input' pentru SQL chain
        input=itemgetter("question")
    )
    .assign(query=generate_query_chain)
    .assign(result=itemgetter("query") | execute_query_tool)
    | final_answer_prompt | llm | StrOutputParser()
)

# --- TESTARE CU INTREBARI VAGI ---
if __name__ == "__main__":
    print(f"--- TESTARE AMBIGUITATE (Schema Aware) ---")
    
    # Caz 1: Ambiguitate "Cel mai bun client"
    q1 = "Cine este cel mai bun client al nostru?" 
    print(f"🤖 Întrebare VAGĂ: {q1}")
    try:
        # Observă că trimitem tot "question", dar RunnablePassthrough îl rezolvă
        res = chain.invoke({"question": q1})
        print(f"✅ Răspuns: {res}\n")
    except Exception as e:
        print(f"❌ Eroare: {e}")

    # Caz 2: Filtrare după nume parțial
    q2 = "Ce a comandat clientul Popescu?" 
    print(f"🤖 Întrebare NUME PARȚIAL: {q2}")
    try:
        res = chain.invoke({"question": q2})
        print(f"✅ Răspuns: {res}\n")
    except Exception as e:
        print(f"❌ Eroare: {e}")