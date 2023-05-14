import uasyncio as asyncio

class CUSTOM_EXTENSIBLE_CLASS():
    WAIT_TIME = 30
    def __init__(self, endpoint_id):
        self.run = True
        self.description = "This is a skeleton which demonstrates the minimum methods to be implemented"
        self.endpoint_id = endpoint_id
        self.attributes : dict[str, list[str | float]] = {}
        self.state : dict[str, str | float] = {}

    def get_description(self) -> str:
        return self.description
    
    def get_html(self, file_type: str) -> str:
        return ""    

    def get_attributes(self) -> dict[str, list[str | float]]:
        return self.attributes

    def set_value(self, values: dict[str, str]) -> bool | None:
        return self.state

    def get_value(self, values: list[str]) -> dict[str, str | float] | None:
        return self.state
    
    def stop(self) -> None:
        self.run = False
        
    async def infinite_loop(self):
        while self.run:
            await asyncio.sleep(CUSTOM_EXTENSIBLE_CLASS.WAIT_TIME)
