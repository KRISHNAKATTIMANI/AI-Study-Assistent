from ddgs import DDGS


def search_web(
    query: str,
    max_results: int = 5,
):
    results = []

    try:

        with DDGS() as ddgs:

            for r in ddgs.text(
                query,
                max_results=max_results,
            ):

                results.append(
                    {
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                        "href": r.get("href", ""),
                    }
                )

    except Exception as e:

        print(
            f"Web Search Error: {e}"
        )

    return results