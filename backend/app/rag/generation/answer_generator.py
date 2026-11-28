from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

from app.rag.generation.prompt import ANSWER_PROMPT


class AnswerGenerator:

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

        self.chain = (
            ANSWER_PROMPT
            | self.llm
            | StrOutputParser()
        )

    def generate(
        self,
        question: str,
        context: str,
    ) -> str:

        if not context.strip():
            return (
                "I couldn't find sufficient information "
                "in the available company documents "
                "to answer this question."
            )

        answer = self.chain.invoke(
            {
                "question": question,
                "context": context,
            }
        )

        return answer.strip()