import asyncio
import arxiv
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("counterscholar-mcp")

COUNTER_KEYWORDS = [
    "refute", "contradict", "disagree", "challenge",
    "limitation", "critique", "contrary", "overestimate",
    "dispute", "incorrect", "flawed",
]

def _run_arxiv_search(query: str, max_results: int) -> list[dict]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    results = []
    for paper in client.results(search):
        results.append({
            "title": paper.title,
            "authors": [a.name for a in paper.authors[:3]],
            "abstract_excerpt": paper.summary[:800],
            "url": paper.entry_id,
            "published_year": str(paper.published.year),
            "categories": paper.categories[:3],
        })
    return results

@mcp.tool()
async def find_counter_papers(paper_title: str, max_results: int = 5) -> dict:
    """Search ArXiv for papers that counter-argue or challenge a given paper."""
    keyword_clause = " OR ".join([f"abs:{kw}" for kw in COUNTER_KEYWORDS])
    query = f'ti:"{paper_title}" AND ({keyword_clause})'
    results = await asyncio.to_thread(_run_arxiv_search, query, max_results)
    if not results:
        title_words = [w for w in paper_title.split() if len(w) > 3]
        broader_query = f'abs:({" ".join(title_words[:5])}) AND ({keyword_clause})'
        results = await asyncio.to_thread(_run_arxiv_search, broader_query, max_results)
    return {"original_paper": paper_title, "papers_found": len(results), "counter_papers": results}

if __name__ == "__main__":
    mcp.run(transport="stdio")
