import logfire
from app.agents.state import AgentState
from app.gateway.client import get_langchain_llm


def generate_node(state: AgentState):
    """
    Synthesizes a response using both Research Context AND Conversation History.
    Uses native ChatGroq via the gateway client.
    """
    query = state["current_query"]

    history_str = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"

    user_msg = state["messages"][-1]["content"] if state["messages"] else ""

    if query == "CONVERSATIONAL":
        logfire.info("Generating conversational response using memory.")
        prompt = f"""
        You are a friendly and knowledgeable Research AI Assistant specialising in 
        Quantum Computing and Machine Learning.
        Answer the user's latest message using the CONVERSATION HISTORY below.

        CONVERSATION HISTORY:
        {history_str}

        LATEST MESSAGE:
        "{user_msg}"
        """
    else:
        logfire.info("Generating research-backed RAG response.")
        max_context_chars = 25000
        full_context = ""

        for doc in state["documents"]:
            if len(full_context) + len(doc) < max_context_chars:
                full_context += doc + "\n\n"
            else:
                logfire.warning("Context truncated to fit Groq TPM limits.")
                break

        prompt = f"""
        You are a Senior Research Scientist with deep expertise in Quantum Computing 
        and Machine Learning.
        Answer the question using the RESEARCH CONTEXT provided from relevant papers 
        and documentation. Cite specific findings, algorithms, or results from the 
        context when possible. Be thorough but clear.

        RESEARCH CONTEXT:
        {full_context}

        CONVERSATION HISTORY:
        {history_str}

        USER QUESTION:
        "{user_msg}"
        """

    with logfire.span("LLM Synthesis"):
        try:
            llm = get_langchain_llm(feature="responder")
            response = llm.invoke(prompt)
            content = response.content

            logfire.info("Response synthesised via LLM.")
            plan_update = state["plan"]
            status = "Response generated."

            return {
                "final_answer": content,
                "status": status,
                "plan": plan_update,
                "messages": [{"role": "assistant", "content": content}]
            }

        except Exception as e:
            logfire.error(f"LLM Generation failed: {e}")
            raise e
