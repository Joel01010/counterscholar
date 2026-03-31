import arxiv
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("counterscholar")

@mcp.tool()
def find_counter_papers(paper_title: str) -> list[dict]:
    """Find papers that challenge the given paper title."""
    query = f'"{paper_title}" AND (refute OR challenge OR contradict OR limitation)'
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=6, sort_by=arxiv.SortCriterion.Relevance)
    return [{"title": r.title, "authors": [a.name for a in r.authors[:2]],
             "abstract": r.summary[:500], "url": r.entry_id} for r in client.results(search)]

if __name__ == "__main__":
    mcp.run(transport="stdio")
