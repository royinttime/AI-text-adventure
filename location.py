class Location:
    def __init__(self, name, description, exits):
        self.name = name
        self.description = description
        self.exits = exits  # Dictionary: {direction: Location}
