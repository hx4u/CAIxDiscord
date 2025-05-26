async def select_voice(cai, name):
    confirm = input("Search for a voice? (Y/n): ").strip().lower()
    voices = await cai.client.utils.search_voices(name)
    if not voices:
        raise Exception(f"No voices found for name: {name}")
    if confirm == "n":
        await cai.client.account.set_voice(cai.character_id, voices[0].voice_id)
        cai.voice_id = voices[0].voice_id  # ✅ Set it even if auto-selected
        return
    for i, v in enumerate(voices[:99]):
        print(f"{i}: {v.name}")
    index = int(input("Choose a voice index: "))
    selected_voice = voices[index]
    await cai.client.account.set_voice(cai.character_id, selected_voice.voice_id)
    cai.voice_id = selected_voice.voice_id  # ✅ Always set voice_id
