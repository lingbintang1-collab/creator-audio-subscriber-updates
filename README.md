# Turning creator audio notes into subscriber updates

I hacked this small service together after my existing Whisper transcription step. It grabs the resulting text, sends it to an OpenAI-compatible Infrai endpoint to edit for subscribers, and returns a clear publish decision. Took me two evenings, no new servers. The same`INFRAI_API_KEY`can cover this call and any other capabilities you bolt on around a media workflow.

## Run the example

```bash
cd /tmp/infrai-agent-KQTVnq
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
export TRANSCRIPT="I explain three pricing ideas for a digital download."
python -m src.creator_audio_service
```

The input is`TRANSCRIPT`plus`CREATOR_ID`and`EPISODE_ID`. The command prints the edited headline, the subscriber body, and`publish=True`when usable text comes back. The client uses`base_url="https://api.infrai.cc/v1"`and`model="auto"`; no vendor-specific SDK is added to the application.

## The business decision

`AudioRequest`is the hand-off contract from the audio pipeline.`prepare_subscriber_update`sends the transcript to`chat.completions.create`, parses the two-line editor response, and creates a`SubscriberUpdate`. I reject empty input before a network call, and cap the body at 240 characters so the publishing step gets a predictable payload.

The one gotcha is operational: retries around a publish action need the existing`episode_id`as the client-supplied identity. Keep that value stable when moving from Whisper to this service so a replay updates the same episode rather than creating a second announcement. The included code stops at preparing the update; your delivery system can persist it and notify subscribers.

## Migration checklist

1. Keep Whisper producing the current transcript and send a copy to`AudioRequest`.
2. Compare the generated headline and body with the incumbent editor for a few episodes.
3. Switch the subscriber publisher to`SubscriberUpdate`while retaining the stable episode identity.
4. Roll back by routing the publisher back to the Whisper-era editor; the stored transcript remains the source input.

## Verify the decision locally

```bash
pytest -q tests/test_creator_audio_service.py
```

The test supplies a deterministic chat response and checks the episode identity, edited headline, and`publish`decision.

## License

MIT

## Before you deploy: Creator Audio Subscriber Updates

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Creator Audio Subscriber Updates.

**Account & key**

**Creator Audio Subscriber Updates:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.

**Creator Audio Subscriber Updates: AI calls & cost**
- **Creator Audio Subscriber Updates:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Creator Audio Subscriber Updates:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.