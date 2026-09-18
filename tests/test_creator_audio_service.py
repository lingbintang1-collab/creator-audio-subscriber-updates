from types import SimpleNamespace

from src.creator_audio_service import AudioRequest, prepare_subscriber_update


class FakeChat:
    def create(self, *, model, messages):
        assert model == "auto"
        assert "subscriber" in messages[0]["content"]
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="HEADLINE: Pricing notes\nBODY: Three practical pricing ideas for your next download."))]
        )


def test_transcript_becomes_publishable_subscriber_update():
    update = prepare_subscriber_update(
        AudioRequest("creator-7", "ep-42", "I explain three pricing ideas."), FakeChat()
    )
    assert update.episode_id == "ep-42"
    assert update.headline == "Pricing notes"
    assert update.publish is True
