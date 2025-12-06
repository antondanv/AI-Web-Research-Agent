import logging
from typing import List
from search_engine.query import search_web
from search_engine.scraper import fetch_page
from search_engine.content_extraction import extract_content

class WebSearchTool:
    def __init__(self, search_context_size: str = "low"):
        """
        Инициализация инструмента поиска.
        """
        self.name = "web_search"

        self.context_size = search_context_size

        if self.context_size == "high":
            self.num_search_results = 10
            self.top_k_chunks = 10
        else:
            self.num_search_results = 5
            self.top_k_chunks = 5

    def __call__(self, query: str) -> str:
        """
        Searches the web for the given query, scrapes the results, and returns relevant context snippets.
        Useful for finding up-to-date information, news, or specific data not in the training set.

        Args:
            query: The search string (e.g., 'Weather in Riyadh tomorrow', 'Latest AI Agent frameworks').

        Returns:
            A string containing the most relevant text chunks found on the web.
        """
        # print(f"DEBUG: Starting web search for '{query}' with mode {self.context_size}...")

        try:
            print("[INFO]: Importing search modules...")
            from search_engine.indexer import Indexer
            from search_engine.retrieval import Retriever
            # Шаг 1: Поиск в Google/DuckDuckGo (через search_web)
            results = search_web(query, num_results=self.num_search_results)
            if not results:
                return "No search results found."
            print(f"[INFO]: Found {len(results)} search results. Starting scraping...")
            # Шаг 2: Скрапинг страниц
            pages = []
            for res in results:
                try:
                    # fetch_page и extract_content - синхронные функции из репо
                    html = fetch_page(res['url'])
                    if not html:
                        continue

                    content = extract_content(html, query=query)

                    # Собираем весь текст для индексации
                    full_text = " ".join([
                        content.get("title", ""),
                        content.get("meta_description", ""),
                        content.get("text", ""),
                        content.get("hidden_text", "")
                    ])

                    if len(full_text.strip()) > 50: # Игнорируем пустые страницы
                        pages.append((full_text, res['url']))
                except Exception as e:
                    print(f"Error processing {res['url']}: {e}")
                    continue

            if not pages:
                return "Found search results, but failed to extract content from them."

            # Шаг 3: Индексация
            indexer = Indexer()
            indexer.index_documents(pages)

            # Шаг 4: Поиск (Retrieval)
            retriever = Retriever(indexer)
            top_chunks = retriever.semantic_search(query, top_k=self.top_k_chunks)

            # Форматирование результата для LLM
            output_lines = []
            for item in top_chunks:
                source_info = f"[Source: {item['source']}]"
                text_content = item['text'].strip()
                output_lines.append(f"{source_info}\n{text_content}\n")

            final_result = "\n---\n".join(output_lines)
            # print(f"DEBUG: Web search result:\n{final_result}")
            print("[INFO]: Web search completed.")
            return final_result

        except Exception as e:
            return f"An error occurred during web search: {str(e)}"