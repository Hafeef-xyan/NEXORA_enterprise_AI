from app.rag.generation.answer_generator import AnswerGenerator
from app.rag.generation.context_formatter import format_context


class GenerationPipeline:

    def __init__(self, answer_generator: AnswerGenerator):
        self.answer_generator = answer_generator

    def run(self, question: str, documents: list) -> str:

        # Step 1: Format retrieved documents into context
        context = format_context(documents)

        # Step 2: Generate answer from the context
        answer = self.answer_generator.generate(
            question=question,
            context=context,
        )

        return answer
