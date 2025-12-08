from langchain_core.prompts import ChatPromptTemplate


def generate_ranking_chain(llm):
    with open('prompts/reranking_prompt.txt', 'r', encoding='utf-8') as f:
        RERANKING_PROMPT = f.read()

    ranking_prompt_template = ChatPromptTemplate.from_messages([
        ("system", RERANKING_PROMPT),
        ("user", "Analiza las siguientes opciones y genera un ranking completo:\n\n{opciones_texto}")
    ])

    return ranking_prompt_template | llm