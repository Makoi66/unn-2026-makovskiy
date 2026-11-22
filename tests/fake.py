class Fake:
    def __init__(self, attributes: dict) -> None:
        for name, value in attributes.items():
            setattr(self, name, value)
