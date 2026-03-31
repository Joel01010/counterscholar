import os
from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv()

root_agent = Agent(
    name="counterscholar",
    model=os.getenv("MODEL", "gemini-2.0-flash"),
    description="Finds counter-arguments and scientific disagreements for any research paper.",
    instruction="""You are CounterScholar. When given a paper title:
1. Summarize the original paper's main claims
2. List known counter-arguments or critiques
3. Give a Community Verdict: accepted, contested, or refuted""",
)
