import gradio as gr
from agent import DEFAULT_PROMPT, run_agent


def research(prompt: str):
    """Stream agent responses as markdown."""
    output = ""
    for chunk in run_agent(prompt):
        output += chunk
        yield output


disable_btn = lambda: gr.Button(interactive=False)
enable_btn = lambda: gr.Button(interactive=True)

with gr.Blocks(title="Claude Managed Agents") as demo:
    gr.Markdown("# Claude Managed Agents Research Demo")

    prompt = gr.Textbox(
        label="Research question",
        value=DEFAULT_PROMPT,
        lines=3,
    )
    btn = gr.Button("Research", variant="primary", size="lg")
    output = gr.Markdown(label="Results", show_label=False)

    for trigger in [btn.click, prompt.submit]:
        trigger(disable_btn, outputs=btn).then(
            research, inputs=prompt, outputs=output,
        ).then(enable_btn, outputs=btn)


if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(primary_hue="yellow", neutral_hue="slate"),
        css="footer {display: none !important}",
    )
