import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter

# 1. Încărcăm variabilele de mediu
load_dotenv()

# 2. Conectarea la Baza de Date
# Asigură-te că calea către folderul 'data' este corectă
db_path = "sqlite:///data/test_db.sqlite"
db = SQLDatabase.from_uri(db_path)

# 3. Inițializăm LLM-ul
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# --- CONSTRUIREA LANȚULUI (CHAIN) ---

# Pasul A: Generarea SQL-ului
generate_query_chain = create_sql_query_chain(llm, db)

# Pasul B: Executarea SQL-ului
execute_query_tool = QuerySQLDataBaseTool(db=db)

# Pasul C: Răspunsul Final (Summarization)
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question in Romanian.
    
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    
    Answer: """
)

answer_chain = answer_prompt | llm | StrOutputParser()

# Pasul D: Asamblarea finală
chain = (
    RunnablePassthrough.assign(query=generate_query_chain)
    .assign(
        result=itemgetter("query") | execute_query_tool
    )
    | answer_chain
)

# --- TESTAREA LANȚULUI ---

if __name__ == "__main__":
    print("\n--- TESTARE TEXT-TO-SQL ---")
    
    # Întrebare 1
    q1 = "Câți utilizatori avem în baza de date?"
    print(f"\n🤖 Întrebare: {q1}")
    try:
        response = chain.invoke({"question": q1})
        print(f"✅ Răspuns: {response}")
    except Exception as e:
        print(f"❌ Eroare Q1: {e}")

    # Întrebare 2
    q2 = "Care este media de pret a produselor?"
    print(f"\n🤖 Întrebare: {q2}")
    try:
        response = chain.invoke({"question": q2})
        print(f"✅ Răspuns: {response}")
    except Exception as e:
        print(f"❌ Eroare Q2: {e}")