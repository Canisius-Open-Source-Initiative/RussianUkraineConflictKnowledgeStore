from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

def getLLMChain(prompt, context_max_tokens):
    global qa_chain
    my_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.,
        max_tokens=context_max_tokens,
    )
    # Create the LLMChain for QA
    qa_chain = LLMChain(llm=my_llm, prompt=prompt)
    return qa_chain