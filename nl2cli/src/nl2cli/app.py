import gradio as gr
from . import config
from .agent import to_command

MESSAGES = {
    "SAFE": "✅ פקודה בטוחה",
    "RISKY": "⚠️ פקודה מסוכנת - נדרש אישור לפני הרצה",
    "BLOCKED": "⛔ הפקודה נחסמה מטעמי בטיחות",
    "UNSUPPORTED": "❔ לא ניתן לבצע זאת בפקודת טרמינל",
}


def run(instruction: str, version: str):
    if not instruction.strip():
        return "", ""
    try:
        res = to_command(instruction, version)
    except Exception as e:  # missing key, network, etc.
        return "", f"שגיאה: {e}"
    shown = res["command"] if res["command"] else res["raw"]
    return shown, MESSAGES[res["status"]]


def main():
    versions = sorted(p.stem for p in config.PROMPTS_DIR.glob("v*.txt"))
    with gr.Blocks(title="NL → CLI") as demo:
        gr.Markdown("# הפיכת הוראה בשפה טבעית לפקודת CLI")
        with gr.Row():
            inp = gr.Textbox(label="הוראה", lines=3, rtl=True)
            ver = gr.Dropdown(versions, value=config.DEFAULT_PROMPT_VERSION, label="גרסת פרומפט")
        btn = gr.Button("המר")
        out = gr.Textbox(label="פקודה", interactive=False)
        status = gr.Textbox(label="סטטוס", interactive=False, rtl=True)
        btn.click(run, [inp, ver], [out, status])
        inp.submit(run, [inp, ver], [out, status])
    demo.launch()


if __name__ == "__main__":
    main()
