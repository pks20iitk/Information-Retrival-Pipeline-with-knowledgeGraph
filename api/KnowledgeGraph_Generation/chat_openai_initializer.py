from langchain.chat_models import AzureChatOpenAI


class ChatOpenAIInitializer:
    """Initialize AzureChatOpenAI instance."""

    OPENAI_BASE = 'https://prod-open-ai-service.openai.azure.com/'
    OPENAI_CHAT_GPT_4 = 'PROD-GPT-16K-TURBO'

    def __init__(self, openai_key, temperature=0, openai_api_type='azure'):
        self.OPENAI_KEY = openai_key
        self.chat_openai = AzureChatOpenAI(
            temperature=temperature,
            openai_api_type=openai_api_type,
            openai_api_key=self.OPENAI_KEY,
            openai_api_base=self.OPENAI_BASE,
            deployment_name=self.OPENAI_CHAT_GPT_4,
        )

