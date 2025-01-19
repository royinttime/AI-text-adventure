import google.generativeai as genai

class Narrator:
    def __init__(self, aibot):
        """Initialize the Narrator with an AI bot instance."""
        self.aibot = aibot

    def generate_world_setting(self, world_description):
        '''Generate detail description from basic world setting.'''
        prompt = f'''Generate a more detailed description of a world described as: {world_description}. Include details about the environment, atmosphere, and any notable features.'''
        try:
            response = self.aibot.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=1.0
                )
            )
            return response.text
        except Exception as e:
            print(f'Error generating world description: {e}')
            return 'A mysterious world.'
