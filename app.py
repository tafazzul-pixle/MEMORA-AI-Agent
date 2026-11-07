import streamlit as st
import asyncio
from groq import Groq
from hindsight_client import Hindsight

st.set_page_config(
    page_title="MEMORA AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 MEMORA")
st.subheader("AI-Powered Customer Intelligence Agent")

st.write(
    "An AI agent that remembers customer experiences, "
    "analyses feedback and recommends business improvements."
)

# API credentials
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    HINDSIGHT_API_KEY = st.secrets["HINDSIGHT_API_KEY"]
except Exception:
    st.error("Please configure your API keys in Streamlit Secrets.")
    st.stop()

# Connect Groq
client = Groq(api_key=GROQ_API_KEY)

# Connect Hindsight
memory = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY
)

BANK_ID = "memora"

def run_async(coro):
    return asyncio.run(coro)


st.header("1. Customer Feedback")

customer = st.text_input("Customer name")
feedback = st.text_area("Enter customer feedback")

if st.button("Analyse and Remember"):
    if customer.strip() and feedback.strip():
        try:
            with st.spinner("MEMORA is working..."):

                run_async(memory.aretain(
                    bank_id=BANK_ID,
                    content=f"Customer: {customer}. Feedback: {feedback}"
                ))

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are MEMORA, an AI customer intelligence agent. Analyse feedback and suggest practical business actions. Do not invent facts."
                        },
                        {
                            "role": "user",
                            "content": f"Customer: {customer}\nFeedback: {feedback}\nIdentify the problem, sentiment and recommended action."
                        }
                    ]
                )

                st.success("Feedback saved successfully!")

                st.subheader("AI Analysis")
                st.write(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Enter customer name and feedback.")


st.header("2. Recall Customer Memories")

query = st.text_input(
    "Ask MEMORA about previous complaints",
    value="What problems have customers reported?"
)

if st.button("Recall Memories"):
    try:
        with st.spinner("Searching memory..."):

            result = run_async(memory.arecall(
                bank_id=BANK_ID,
                query=query
            ))

            if result.results:
                for item in result.results:
                    st.write("•", item.text)
            else:
                st.info("No memories found.")

    except Exception as e:
        st.error(f"Memory error: {e}")


st.header("3. Business Recommendations")

if st.button("Generate Recommendations"):
    try:
        with st.spinner("Analysing historical feedback..."):

            result = run_async(memory.arecall(
                bank_id=BANK_ID,
                query="Summarise customer complaints, business decisions and outcomes."
            ))

            history = "\n".join(
                item.text for item in result.results
            )

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are MEMORA. Analyse historical customer memories, identify evidence-based patterns and recommend business actions. Distinguish measured outcomes from unverified assumptions."
                    },
                    {
                        "role": "user",
                        "content": f"Historical memories:\n{history}\n\nProvide problems, patterns, recommendations and next steps."
                    }
                ]
            )

            st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Recommendation error: {e}")


st.divider()
st.caption("MEMORA | AI + Hindsight Memory + Business Intelligence")
