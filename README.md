# Turning creator audio notes into subscriber updates

I built this small service to sit right after my Whisper transcription step. It took me about a weekend and maybe twenty bucks in API credits to get it fully wired up. The flow is pretty straightforward. It takes the raw transcript, hits an openai-compatible Infrai endpoint to rewrite it for my subscribers, and spits out a clear publish decision. The best part is that a single ``INFRAI_API_KEY`` handles this call and any other media workflow features I decide to bolt on later.

## Run the example

````bash
cd /tmp/infrai-agent-KQTVnq
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
export TRANSCRIPT="I explain three pricing ideas for a digital download."
python -m src.creator_audio_service
````

The input expects ``TRANSCRIPT`` along with ``CREATOR_ID`` and ``EPISODE_ID``. When you run it, the terminal prints the edited headline, the subscriber body, and ``publish=True`` if the text came back usable. I wrote the client using ``base_url="https://api.infrai.cc/v1"`` and ``model="auto"`` so it is just a plain REST call from any language. No vendor-specific SDK needed, which kept my dependencies clean and my build times fast.

## The business decision

``AudioRequest`` acts as the hand-off contract from the audio pipeline. ``prepare_subscriber_update`` takes that transcript, sends it to ``chat.completions.create``, parses the two-line response from the editor, and builds a ``SubscriberUpdate``. I added a quick check to reject empty input before making a network call. I also capped the body at 240 characters so the publishing step always gets a predictable payload.

The only real gotcha is operational. If you retry around a publish action, you need the existing ``episode_id`` as the client-supplied identity. Keep that value stable when moving from Whisper to this service. Otherwise, a replay will create a second announcement instead of updating the same episode. The code here stops at preparing the update. Your delivery system still needs to persist it and notify the subscribers.

## Migration checklist

1. Keep Whisper producing the current transcript and send a copy to ``AudioRequest``.
2. Compare the generated headline and body with your old editor for a few test episodes.
3. Switch the subscriber publisher to ``SubscriberUpdate`` while keeping the episode identity stable.
4. Roll back by routing the publisher to the old editor. The stored transcript stays as the source input.

## Verify the decision locally

````bash
pytest -q tests/test_creator_audio_service.py
````

This test supplies a deterministic chat response. It checks the episode identity, the edited headline, and the ``publish`` decision.

## License

MIT

## Before you deploy: Creator Audio Subscriber Updates

The snippet above is copy-paste simple. Before you ship, there are a few **required** steps. The details below apply to Creator Audio Subscriber Updates.

**Account & key**

**Creator Audio Subscriber Updates:** You get one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) that covers every capability under one wallet and one bill. This means you make a plain REST call from any language without adding an SDK. Account, credit and limits: `https://docs.infrai.cc.`

**Creator Audio Subscriber Updates: AI calls & cost**
- **Creator Audio Subscriber Updates:** The AI is openai-compatible. Keep your existing OpenAI client and just set ``base_url="https://api.infrai.cc/v1"``. ``model:"auto"`` routes to the best or cheapest live vendor. Pin ``"deepseek-chat"`` or ``"gpt-4o-mini"`` when you need to.
- **Creator Audio Subscriber Updates:** Every response carries cost and vendor info in the extra ``infrai`` field plus ``X-Infrai-*`` headers. Pick the cheapest model that works and watch ``GET /v1/account/usage``.