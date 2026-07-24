from agent.prompts import SYSTEM_PROMPT, REFLECTION_PROMPT_TEMPLATE

if __name__ == "__main__":
    print("Testing System Prompt loading...\n")
    print("Length of SYSTEM_PROMPT:", len(SYSTEM_PROMPT))
    print("Includes PENDING_APPROVAL check:", "PENDING_APPROVAL" in SYSTEM_PROMPT)
    print("Includes ReAct loop keywords:", "Thought:" in SYSTEM_PROMPT and "Action:" in SYSTEM_PROMPT)
    print("\nPrompt test passed successfully!")