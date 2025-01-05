class Location:
    def __init__(self, name, data):
        self.name = name
        self.description = data.get('description')
        self.connections = data.get('connections', [])
