from web_search import search_web

print("Starting search...")

results = search_web(
    "Artificial Intelligence"
)

print(f"Results found: {len(results)}")

for r in results:

    print("\n----------------")

    print("Title:", r["title"])
    print("URL:", r["href"])
    print("Content:", r["body"])