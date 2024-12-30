class Character:
    def __init__(self, aibot, name, data):
        self.aibot = aibot
        self.name = name
        self.age = data.get("age")
        self.relationships = data.get("relationships", {})
        self.height = data.get("height")
        self.appearance = data.get("appearance")
        self.personality = data.get("personality")
        self.interests = data.get("interests")
        self.habits = data.get("habits")
        self.location = None
        self.memory = []

    def move(self, direction):
        if direction in self.location.exits:
            self.location = self.location.exits[direction]
            return f"{self.name} moves {direction} to the {self.location.name}."
        else:
            return f"{self.name} cannot go that way."

    def generate_dialogue(self, context=""):
        prompt = f"""You are {self.name}, a {self.age}-year-old. Your relationships are: {self.relationships}. You are {self.height}. Your appearance: {self.appearance}. Your personality: {self.personality}. Your interests are: {self.interests}. Your habits are: {self.habits}. You are currently in the {self.location.name}. {context} Generate a short sentence of dialogue."""
        try:
            response = self.aibot.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=50,
                    temperature=1.0
                )
            )
            return response.text
        except Exception as e:
            print(f"Error generating dialogue: {e}")
            return "..."
