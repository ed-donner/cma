from anthropic import Anthropic
from collections.abc import Generator
from dotenv import load_dotenv

load_dotenv(override=True)

client = Anthropic()

DEFAULT_PROMPT = """
Please research a high quality 60 inch smart LED 4K TV that gets great feedback from customers,
and has good contrast and picture quality, and is reasonably priced. Give your top 3 recommendations with the best online
price and a link to where I can buy each.
""".strip()


def run_agent(prompt: str) -> Generator[str, None, None]:
    """Create a managed agent session, send a prompt, and yield streamed output."""
    
    yield "> *Creating Agent...*"
    agent = client.beta.agents.create(
        name="Researcher",
        model="claude-sonnet-4-6",
        system="You are able to carry out research tasks using tools at your disposal.",
        tools=[{"type": "agent_toolset_20260401"}],
    )

    yield f" - created Agent ID `{agent.id}`\n\n"
    yield "> *Creating Environment...*"

    environment = client.beta.environments.create(
        name=f"env-{agent.id}",
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )
    yield f" - created Environment ID `{environment.id}`\n\n"
    yield "> *Creating Session...*"

    session = client.beta.sessions.create(
        agent=agent.id,
        environment_id=environment.id,
    )
    yield f" - created Session ID `{session.id}`\n\n"

    events = [{"type": "user.message", "content": [{"type": "text", "text": prompt}]}]

    yield "\n\n> *Sending prompt and streaming response...*\n\n"

    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(session.id, events=events)

        for event in stream:
            match event.type:
                case "agent.message":
                    for block in event.content:
                        yield block.text
                case "agent.tool_use":
                    yield f"\n\n> **Tool call:** `{event.name}`\n\n"
                case "agent.tool_result":
                    yield "> *Tool completed*\n\n"
                case "session.status_idle":
                    break
