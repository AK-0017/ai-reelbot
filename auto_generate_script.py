import os
import re
import random

def clean_grammar(text):
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    corrections = {
        "Inititiative": "Initiative",
        "electrictiy": "electricity",
        "are were": "where",
        "is not steady as in cities": "is not as steady as in cities",
        " it's ": " it’s ",
        "dont": "don't",
        "Dont": "Don't",
        " teh ": " the ",
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text.strip()

# 🔁 Random fallback insight lines for natural variation
fallback_insights = [
    "💡 This could change how we use AI forever.",
    "💡 A major step forward in technology.",
    "💡 It’s a game-changer for the AI industry.",
    "💡 This breakthrough might lead to big real-world impact.",
    "💡 Big things ahead for AI with this move.",
    "💡 A powerful sign of what's coming in tech.",
    "💡 This could shape the next decade of innovation.",
    "💡 Another milestone in AI evolution.",
    "💡 This update brings us closer to smarter machines.",
    "💡 This one might surprise even the experts."
]

def extract_single_story(script_path):
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r"<.*?>", "", content).replace("&nbsp;", " ").strip()
    blocks = re.split(r"(?=(?:🚨|🤖|💡|🔥|👀|📢)\s)", content)
    clean_stories = []

    for i, block in enumerate(blocks):
        lines = [line.strip() for line in block.strip().splitlines() if line.strip()]
        if len(lines) < 2:
            print(f"⚠️ Skipped block {i}: not enough content.")
            continue

        hook = lines[0]
        body_lines = lines[1:]

        insight_line = next((line for line in body_lines if "why it matters" in line.lower()), None)
        cta_line = next((line for line in reversed(body_lines) if any(kw in line.lower() for kw in ["follow", "stay ahead", "more stories"])), None)

        summary_lines = [
            line for line in body_lines
            if line != insight_line and line != cta_line
        ]
        summary = " ".join(summary_lines).strip()

        if len(summary.split()) < 3:
            print(f"⚠️ Skipped block {i}: summary too short.")
            continue

        if not insight_line:
            insight_line = random.choice(fallback_insights)
        if not cta_line:
            cta_line = "📲 For more updates like this, follow us now."

        # Clean all parts
        hook = clean_grammar(hook)
        summary = clean_grammar(summary)
        insight_line = clean_grammar(insight_line)
        cta_line = clean_grammar(cta_line)

        story = f"{hook}\n\n{summary}\n\n{insight_line}\n\n{cta_line}".strip()
        clean_stories.append(story)
        print(f"✅ Added block {i} to candidates.")

    if not clean_stories:
        print("❌ No usable stories found.")
        return None

    final_story = random.choice(clean_stories)
    print("🎉 Story selected for reel generation.")
    return final_story

def save_single_story(folder, story):
    output_path = os.path.join(folder, "single_script.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(story.strip())
    print(f"✅ Final script saved to: {output_path}")

if __name__ == "__main__":
    try:
        latest = sorted(os.listdir("assets"), reverse=True)[0]
        folder = os.path.join("assets", latest)
        script_path = os.path.join(folder, "script.txt")

        story = extract_single_story(script_path)
        if story:
            save_single_story(folder, story)
        else:
            print("❌ No valid story found.")
    except Exception as e:
        print(f"❌ Error: {e}")
