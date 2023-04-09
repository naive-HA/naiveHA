class CUSTOM_EXTENSIBLE_CLASS():
    def __init__(self, endpoint_id):
        self.description = "This is a skeleton which demonstrates the minimum methods to be implemented"
        self.endpoint_id = endpoint_id
        self.attributes : dict[str, list[str | float]] = {}
        self.state : dict[str, str | float] = {}

    def get_description(self) -> str:
        return self.description
    
    def get_html5(self, file_type) -> str:
        return ""    

    def get_attributes(self) -> dict[str, list[str | float]]:
        return self.attributes

    def set_value(self, attributes: dict[str, str | float]) -> bool | None:
        return self.state

    def get_value(self, attributes: list[str]) -> dict[str, str | float] | None:
        return self.state