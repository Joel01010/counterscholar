"""CounterScholar MCP Server — exposes find_counter_papers via stdio."""

import asyncio
import arxiv
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("counterscholar_mcp")

COUNTER_KEYWORDS = [
    "refute", "contradict", "disagree", "challenge",
    "limitation", "critique", "contrary", "overestimate",
    "dispute", "incorrect", "flawed",
]


def _search_arxiv(query: str, max_results: int) -> list[dict]:
    """Synchronous ArXiv search wrapper."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers = []
    for p in client.results(search):
        papers.append({
            "title": p.title,
            "authors": [a.name for a in p.authors[:3]],
            "abstract": p.summary[:800],
            "url": p.entry_id,
            "year": str(p.published.year),
            "categories": p.categories[:3],
        })
    return papers


@mcp.tool()
async def find_counter_papers(paper_title: str, max_results: int = 5) -> dict:
    """Search ArXiv for papers that counter-argue or challenge a given paper.

    Args:
        paper_title: Title of the paper to find counter-arguments for.
        max_results: Max counter-papers to return (default 5).

    Returns:
        dict with original_paper, papers_found count, and counter_papers list.
    """
    kw_clause = " OR ".join(f"abs:{kw}" for kw in COUNTER_KEYWORDS)

    # Primary: title match + counter-argument keywords in abstract
    query = f'ti:"{paper_title}" AND ({kw_clause})'
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, _search_arxiv, query, max_results)

    # Fallback: broader keyword search if title match yields nothing
    if not results:
        words = [w for w in paper_title.split() if len(w) > 3]
        fragment = " ".join(words[:5])
        query2 = f"abs:({fragment}) AND ({kw_clause})"
        results = await loop.run_in_executor(None, _search_arxiv, query2, max_results)

    return {
        "original_paper": paper_title,
        "papers_found": len(results),
        "counter_papers": results,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
