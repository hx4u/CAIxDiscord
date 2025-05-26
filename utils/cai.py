from PyCharacterAI import get_client
class CAIWrapper:
    def __init__(self, client, character_id, history_id):
        self.client = client
        self.character_id = character_id
        self.history_id = history_id
    @classmethod
    async def create(cls, token, character_id, history_id):
        client = await get_client(token=token)
        return cls(client, character_id, history_id)
    async def send_message(self, msg):
   	 return await self.client.chat.send_message(self.character_id, self.history_id, msg)
    async def generate_image(self, prompt):
    	return await self.client.utils.generate_image(prompt)
