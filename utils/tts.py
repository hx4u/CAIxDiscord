import io
async def generate_tts(cai, answer):
    turn_id = answer.turn_id
    candidate_id = answer.get_primary_candidate().candidate_id
    data = await cai.client.utils.generate_speech(
        cai.history_id,
        turn_id,
        candidate_id,
        cai.voice_id,
        return_url=False
    )
    return io.BytesIO(data)
