from abc import ABC, abstractmethod
import google.generativeai as genai

class AIProvider(ABC):
    '''Abstract base class for AI providers'''

    @abstractmethod
    def generate_content(self, prompt: str, max_tokens: int = 300, temperature: float = 1.0) -> str:
        '''Generate content using the AI provider'''
        pass

class GoogleAI(AIProvider):
    '''Google Generative AI implementation'''

    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        '''Initialize Google AI with API key and optional model name'''
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_content(self, prompt: str, max_tokens: int = 300, temperature: float = 1.0) -> str:
        """Generate content using Google's generative AI"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )
            return response.text
        except Exception as e:
            print(f'Error generating content with Google AI: {e}')
            return ''

class OpenAI(AIProvider):
    '''OpenAI implementation (placeholder)'''
    
    def __init__(self, api_key: str, model_name: str = 'gpt-3.5-turbo'):
        '''Initialize OpenAI with API key and optional model name'''
        self.api_key = api_key
        self.model_name = model_name
        
    def generate_content(self, prompt: str, max_tokens: int = 300, temperature: float = 1.0) -> str:
        '''Generate content using OpenAI'''
        raise NotImplementedError('OpenAI provider is not yet implemented.')

class AIProviderFactory:
    @staticmethod
    def create_provider(provider_type: str, config: dict) -> AIProvider:
        '''
        Create an AI provider based on the provider type string from config
        
        Args:
            provider_type: String identifier for the provider (e.g., 'google', 'openai')
            config: Dictionary containing provider-specific configuration
        
        Returns:
            An instance of the specified AI provider
        '''
        provider_type = provider_type.lower()
        
        if provider_type == 'google':
            return GoogleAI(
                api_key=config.get('api_key'),
                model_name=config.get('model_name', 'gemini-pro')
            )
        elif provider_type == 'openai':
            return OpenAI(
                api_key=config.get('api_key'),
                model_name=config.get('model_name', 'gpt-3.5-turbo')
            )
        else:
            raise ValueError(f'Unknown AI provider type: {provider_type}')

class AIService:
    @classmethod
    def from_config(cls, config: dict):
        '''
        Create AIService from a configuration dictionary
        
        Args:
            config: Dictionary containing provider type and configuration
            Example:
            {
                'provider': 'google',
                'api_key': 'your-api-key',
                'model_name': 'gemini-pro'
            }
        '''
        provider_type = config.get('provider')
        if not provider_type:
            raise ValueError('Provider type must be specified in config')
            
        provider = AIProviderFactory.create_provider(provider_type, config)
        return cls(provider)
    
    def __init__(self, provider: AIProvider):
        self.provider = provider
    
    def generate_content(self, prompt: str, max_tokens: int = 300, temperature: float = 1.0) -> str:
        return self.provider.generate_content(prompt, max_tokens, temperature)
    
    def switch_provider(self, new_provider: AIProvider):
        self.provider = new_provider
