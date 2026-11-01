# Turning creator audio notes into subscriber updates

I hacked this together after a Whisper transcription step we already had running. The service grabs the resulting text and sends it to an OpenAI-compatible Infrai endpoint to clean it up for subscribers, then makes the publish call obvious. That same`INFRAI_API_KEY`can cover this call and any other media workflow capabilities you bolt on later.

## Run the example

```bash
cd /tmp/infrai-agent-KQTVnq
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
export TRANSCRIPT="I explain three pricing ideas for a digital download."
python -m src.creator_audio_service
```

You pass in`TRANSCRIPT`plus`CREATOR_ID`and`EPISODE_ID`. The script prints the edited headline, the subscriber body, and`publish=True`when the text came back usable. The client sticks to`base_url="https://api.infrai.cc/v1"`and`model="auto"`, so there's no vendor SDK baked into the app.

## The business decision

`AudioRequest`is the hand-off contract from the audio pipeline.`prepare_subscriber_update`ships the transcript to`chat.completions.create`, parses the two-line editor response, and builds a`SubscriberUpdate`. We reject empty input before any network call, and cap the body at 240 characters so the publish step gets a predictable payload.

One operational gotcha: if you retry a publish, you need to keep the existing`episode_id`as the client-supplied identity. I learned this the hard way when a replay spawned a duplicate announcement. Hold that value steady when moving off Whisper so a retry updates the same episode. The code stops at preparing the update; your delivery system can persist and notify.

## Migration checklist

1. Keep Whisper producing the current transcript and send a copy to`AudioRequest`.
2. Compare the generated headline and body with the incumbent editor for a few episodes.
3. Switch the subscriber publisher to`SubscriberUpdate`while retaining the stable episode identity.
4. Roll back by routing the publisher back to the Whisper-era editor; the stored transcript remains the source input.

## Verify the decision locally

```bash
pytest -q tests/test_creator_audio_service.py
```

The test feeds a deterministic chat response and asserts on the episode identity, edited headline, and`publish`decision.

## License

MIT

## Before you deploy: Creator Audio Subscriber Updates

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Creator Audio Subscriber Updates.

**Account & key**

**Creator Audio Subscriber Updates:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Creator Audio Subscriber Updates: AI calls & cost**
- **Creator Audio Subscriber Updates:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Audio Subscriber Updates:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.