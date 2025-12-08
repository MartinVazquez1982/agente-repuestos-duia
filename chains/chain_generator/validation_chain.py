from langchain_core.prompts import ChatPromptTemplate
from schemas.structure_outputs import ValidationRequest
from langchain_core.output_parsers import PydanticOutputParser


def generate_validation_chain(llm):
    with open('prompts/intention_classifier_prompt.txt', 'r', encoding='utf-8') as f:
         CLASSIFIER_SYSTEM_PROMPT = f.read()

    validation_prompt = ChatPromptTemplate.from_messages([
        ("system", CLASSIFIER_SYSTEM_PROMPT),
        ("placeholder", "{messages}")
    ])

    parser = PydanticOutputParser(pydantic_object=ValidationRequest)

    validation_prompt_con_instrucciones = ChatPromptTemplate.from_messages(
        validation_prompt.messages + [
            ("human", "{format_instructions}")
        ]
    ).partial(
        format_instructions=parser.get_format_instructions()
    )

    return (
        validation_prompt_con_instrucciones 
        | llm 
        | parser
    )