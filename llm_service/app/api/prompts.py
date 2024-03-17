# have to be the same keys as in llm_service.app.api.utils.Language.
# I do not have any idea of how to validate it in the programme itself

PROMPTS = {
    'en': {'system': """
You are a student assistant. You help to compile glossaries on the lecture material. Always answer in English.
""",
           'user': """
Select concepts from the text that need to be explained. Write their definitions. Return output in JSON format: [{'term': '', 'definition': ''}, ...].
"""
           },

    'ru': {'system': """
Ты помощник студента. Ты помогаешь составлять глоссарии по материалу лекций. Всегда отвечай на русском.
""",
           'user': """
Выдели из текста концепции, которые нуждаются в пояснении. Напиши их определения. Верни ответ в JSON-формате: [{'термин': '', 'определение': ''}, ...].
"""
           }
}
