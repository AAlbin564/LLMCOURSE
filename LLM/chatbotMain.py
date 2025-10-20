from google import genai
from dotenv import load_dotenv
import os
import gradio as gr

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from ragLogic import setup_chroma, setup, chunkingData



import os
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = """
You are a helpful assistant specialized in Uppsala University's study programmes.
Your task is to help prospective students choose a programme that matches their interests.
- Always base your answers only on the provided context.
- Be supportive and clear.
- Reply in the SAME LANGUAGE as the user's message.
- If the context is in another language, translate what you need internally, but keep the final answer in the user's language.
- 
"""

def get_context(question: str) -> str:
    docs = retriever.get_relevant_documents(question)
    print(f"retrieving works {docs}")
    
    if not docs:
        return "(no relevant context found)"
    print("actual docs")
    context_parts = []
    for i, doc in enumerate(docs):
        formatted_doc = (
        f"title: {doc.metadata.get('title', 'Unknown')}\n"
        f"url: {doc.metadata.get("url", "unknown")}"
        f"Content: {doc.page_content}"
        )
        context_parts.append(formatted_doc)

    # join all retrieved stringsg into one context
    context = "\n\n".join(context_parts)
    print(context)
    return context


prompt = ChatPromptTemplate.from_template(
    "SYSTEM INSTRUCTION:\n{system}\n\n"
    "CONTEXT (from UU programme database):\n{context}\n\n"
    "QUESTION:\n{question}"
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

chain = (
    {
        "system": RunnableLambda(lambda _: SYSTEM_INSTRUCTION),
        "context": RunnableLambda(lambda q: get_context(q["current"])),
        "question": RunnableLambda(lambda q: q["history"] + "\nUser: " + q["current"]),
    }
    | prompt
    | llm
    | StrOutputParser()
)

def chat_fn(message, history):
    # Combine all past turns into a single text block
    chat_history_text = "\n".join(
        [f"User: {u}\nAssistant: {a}" for u, a in history if a]
    )
    
    # Add the new user message
    full_input = f"{chat_history_text}\nUser: {message}"

    return chain.invoke({"history":full_input, "current": message})

demo = gr.ChatInterface(
    fn=chat_fn,
    
    title="🎓 Uppsala University Programme Advisor",
    description="Discover which study programmes at Uppsala University match your interests. This chatbot knows about all programmes at Uppsala University ",
    chatbot=gr.Chatbot(
        height = 1200,
        value=[(
            None,
            "Hello! 👋 I'm here to help you find a study programme at Uppsala University that matches your interests. "
            "To begin, could you tell me a bit about what subjects you enjoy, your previous studies, or what career you hope for?"
        )]
    ),
)

if __name__ == "__main__":
    data = setup()
    print("setup works")
    chunks = chunkingData(data)
    print("chunking data works")
    retriever = setup_chroma(chunks)
    print("setup chroma works")
    demo.launch()