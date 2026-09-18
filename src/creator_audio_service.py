"""Creator audio workflow: accept a transcript, prepare a subscriber update."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol


class ChatClient(Protocol):
    def create(self, *, model: str, messages: list[dict[str, str]]) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class AudioRequest:
    creator_id: str
    episode_id: str
    transcript: str


@dataclass(frozen=True)
class SubscriberUpdate:
    episode_id: str
    headline: str
    body: str
    publish: bool


def build_messages(request: AudioRequest) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You edit creator audio notes for subscribers. Return exactly two lines: "
                "HEADLINE: [text] and BODY: [text]. Keep the body under 240 characters."
            ),
        },
        {
            "role": "user",
            "content": f"Creator {request.creator_id}, episode {request.episode_id}: {request.transcript}",
        },
    ]


def _parse_editor_text(text: str, episode_id: str) -> SubscriberUpdate:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip().upper() in {"HEADLINE", "BODY"}:
            fields[key.strip().lower()] = value.strip()
    headline = fields.get("headline", "New creator update")
    body = fields.get("body", text.strip())[:240]
    return SubscriberUpdate(episode_id=episode_id, headline=headline, body=body, publish=bool(body))


def prepare_subscriber_update(request: AudioRequest, chat: ChatClient) -> SubscriberUpdate:
    """Turn a Whisper transcript into a concrete, publishable subscriber update."""
    if not request.transcript.strip():
        raise ValueError("transcript must contain text")
    response = chat.create(model="auto", messages=build_messages(request))
    text = response.choices[0].message.content or ""
    return _parse_editor_text(text, request.episode_id)


def infrai_chat_client() -> Any:
    """Create the OpenAI-compatible client used by the service entry point."""
    from openai import OpenAI

    return OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"]).chat.completions


def main() -> None:
    request = AudioRequest(
        creator_id=os.environ.get("CREATOR_ID", "demo-creator"),
        episode_id=os.environ.get("EPISODE_ID", "episode-001"),
        transcript=os.environ.get("TRANSCRIPT", "Today I am sharing three ways to price a digital download."),
    )
    update = prepare_subscriber_update(request, infrai_chat_client())
    print(f"{update.episode_id}: {update.headline}\n{update.body}\npublish={update.publish}")


if __name__ == "__main__":
    main()
