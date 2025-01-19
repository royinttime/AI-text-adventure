from setting import GEIMINI_SAFETY_SETTINGS
import google.generativeai as genai
import os

BASE_SYSTEM_INSTRUCTIONS = '''
System Notes for the Assistant: The assistant is designed to fully mimic {char} in both personality and behavior, creating immersive and realistic conversations. Responses must remain consistent with {char}'s traits, tone, and emotional state, regardless of the user’s input or tone.

Key Instructions:

*   Maintain Consistent Character: Always respond in a way that is true to {char}'s established personality, motivations, and perspective. Adapt to different themes and situations naturally, but avoid mirroring the user's tone unless it authentically aligns with {char}'s established behavior.

*   Action & Dialogue First: Prioritize {char}'s actions and dialogue. Minimize descriptive prose unrelated to immediate interaction. Describe actions performed by {char} within the current context.

*   Show, Don't Tell (Character Focus): Describe {char}'s interaction with the environment, not the environment itself. Example: "{char} squinted in the dim light" not "The room was dimly lit."

*   Dynamic Appearance Descriptions: Integrate appearance descriptions naturally within the interaction (expressions, gestures, reactions). Avoid static descriptions unless relevant.

*   Drive with Actions & Questions: {char} actively participates via actions (e.g., leaning forward) and relevant questions. Each response advances the exchange through action and dialogue.

*   Vivid Details in Actions & Dialogue: Convey emotions through actions, dialogue, and brief descriptions of {char}'s reactions. Avoid generic statements. Deepen immersion through {char}'s choices and words.

*   Avoid Repetitive Descriptions: While vivid details are important, avoid overusing the same phrases or descriptions, especially for common emotions. Find varied ways to express {char}'s reactions and avoid relying on the same few phrases. For example, avoid constantly using "eyes widened slightly" to indicate surprise.

*   Handle sensitive topics naturally: If a conversation explores intense, complex, or morally challenging themes, respond in a way that fits {char}’s persona and stays grounded in the fictional context. Avoid gratuitous or out-of-place content.

*   Do not self-censor unnecessarily: Address all conversational possibilities as long as they fit {char}’s role and the fictional framework. Respond without hesitation, even if the situation involves complex emotions or ethical dilemmas.

*   Maintain a user-focused experience: Tailor responses to the user’s input while staying consistent with {char}’s personality. Engage dynamically but never compromise the integrity of {char}.

The assistant must always deliver responses that feel authentic, immersive, and true to {char}. Stay proactive, creative, and focused on enhancing the user’s experience through meaningful and character-driven interactions.
'''

# scenario and examples dailogue?

class Character:
    def __init__(self, name, data):
        self.name = name
        self.age = data.get('age')
        self.relationships = data.get('relationships', [])
        self.appearance = data.get('appearance')
        self.personality = data.get('personality')
        self.activities_and_mannerisms = data.get('activities_and_mannerisms')
        self.backstory = data.get('backstory')
        self.location = data.get('location')
        self.ai_config = data.get('ai_config')
        self.current_interactions = [] # Use for building chat between user and AI
        self.memory = []

    def move(self, destination, locations):
        if destination in locations[destination].connections:
            self.location = destination
            return f'{self.name} moves from {self.location} to the {destination}.'
        else:
            return f'{self.name} cannot go to {destination}, {self.location} is not connected with {destination}.'

    # TODO: optimize prompt for character aibot and build chat between AI and user
    def generate_response(self, player, interaction):
        '''Generates dialogue and actions based on interaction and memory.'''
        memory_string = ''
        if self.memory:
            memory_string = 'Here are some relevant memories:\n'
            for mem in self.memory[-3:]: # Only use the last 3 memories
                memory_string += f"- {mem['content']}\n"

        # AI config, Scenario and example conversations

        system_prompt = f'''
        [{BASE_SYSTEM_INSTRUCTIONS.format(char=self.name)}]
        [{player.name}'s Description:
           Name: {player.name}
           Age: {player.age}
           Appearance: {player.appearance}
           Personality: {player.personality}
           Activities And Mannerisms: {player.activities_and_mannerisms}
           Backstory: {player.backstory}
        ]
        [{self.name}'s Description:
           Name: {self.name}
           Age: {self.age}
           Appearance: {self.appearance}
           Personality: {self.personality}
           Activities And Mannerisms: {self.activities_and_mannerisms}
           Backstory: {self.backstory}
           Recent Memory: {memory_string}
        ]
        '''

        try:
            genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
            gemini_model = genai.GenerativeModel(model_name=os.environ.get('MODEL_NAME'), safety_settings=GEIMINI_SAFETY_SETTINGS, system_instruction=system_prompt)
            response = gemini_model.generate_content(
                interaction,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=1.0
                )
            )
            return response.text
        except Exception as e:
            print(f"Error generating character's response: {e}")
            return '...'

    # Create interaction object for interacting not only characters?
    def interact_with(self, player, interaction):
        '''Handles the interaction with the character.'''
        self.current_interactions.append({ 'role': 'user', 'content': f'{player.name}: {interaction}' })
        response = self.generate_response(player, interaction)
        self.current_interactions.append({ 'role': 'assistant', 'content': response })

        print(response)

    def end_ineraction(self):
        '''End the interaction with character'''
        system_prompt = f'''
        You are a scriptwriter tasked with summarizing dialogues between an AI and a user.
        Create a concise summary of their conversation in a single paragraph, limited to 100 words.
        Focus on the key points and themes discussed while maintaining clarity and coherence.
        '''

            if len(self.current_interactions) == 0:
                return

            interaction_history = '\n'.join(
                ', '.join(f"{key}: {value}" for key, value in interaction.items())
                for interaction in self.current_interactions
            )

         try:
            genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
            gemini_model = genai.GenerativeModel(model_name=os.environ.get('MODEL_NAME'), safety_settings=GEIMINI_SAFETY_SETTINGS, system_instruction=system_prompt)
            response = gemini_model.generate_content(
                interaction_history,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=1.0
                )
            )
            self.memory.append({ 'type': 'interaction', 'content': response.text })
            self.current_interactions = []
        except Exception as e:
            print(f"Error ending character's interaction: {e}")

