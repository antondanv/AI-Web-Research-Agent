from agents import Agent, trace, Runner, OpenAIChatCompletionsModel, function_tool
from agents.model_settings import ModelSettings
from openai import AsyncOpenAI
from WebSearch import WebSearchTool
import asyncio
from pydantic import BaseModel, Field
import os

# Setup model
ollama_client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="not-required")
ollama_model = OpenAIChatCompletionsModel(openai_client=ollama_client, model="llama3.2")

# Set trace_mode_disabled=False to enable tracing for debugging (only when using actual OpenAI models)
trace_mode_disabled = True

# -- Web Search Agent --
INSTRUCTIONS1 = """"You are a researcher. You are given a search query, you search for it on the Internet and
make a short summary of the results. The summary should consist of 2-3 paragraphs and contain no more than 300 words
of the word. Capture the main points. Write briefly, you don't have to use complete sentences or good
grammar. This will be used in the preparation of the report, so it is important to grasp
the essence and not pay attention to inaccuracies. Do not include any additional comments other than the summary itself.
Provide a response in the same language as the user's request."""

# Создание экземпляра WebSearchTool и выбором размер контекста "low"/"high"
search_tool_instance = WebSearchTool(search_context_size="low")


@function_tool
def web_search(query: str) -> str:
    """
    Searches the web for the given query and returns relevant context snippets.
    Useful for finding up-to-date information, news, or specific data.
    """
    return search_tool_instance(query)


search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS1,
    tools=[web_search],
    model=ollama_model,
    model_settings=ModelSettings(tool_choice="required"),
)

# -- Planner Agent --
HOW_MANY_SEARCHES = 3

INSTRUCTIONS2 = f"""You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."""


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")

    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")


planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS2,
    model=ollama_model,
    output_type=WebSearchPlan,
)

# -- Synthesis Agent --
INSTRUCTIONS3 = """You are an information synthesis assistant. You are provided with search results for different aspects of the same topic. 
Your task is to combine this information into a single, logical and well—structured text in natural language. 
Do not add your own conclusions or comments. Just rewrite the found data clearly, coherently and neutrally. 
Save all the key facts, figures, and examples. 
The response must be in the same language as the original request."""

synthesis_agent = Agent(
    name="SynthesisAgent",
    instructions=INSTRUCTIONS3,
    model=ollama_model,
)

async def plan_searches(query: str):
    """ Use the planner_agent to plan which searches to run for the query """
    print("Планирую поисковые запросы...")
    result = await Runner.run(planner_agent, f"Query: {query}")
    print(f"Выполнит поиск по {len(result.final_output.searches)} запросам.")
    print(f"Результат планирования: {result.final_output}")
    return result.final_output

async def perform_searches(search_plan: WebSearchPlan):
    """ Call search() for each item in the search plan """
    print("Запускаю поисковые запросы...")
    tasks = [asyncio.create_task(search(item)) for item in search_plan.searches]
    results = await asyncio.gather(*tasks)
    print("Поиск завершен.")
    return results

async def search(item: WebSearchItem):
    """ Use the search agent to run a web search for each item in the search plan """
    input = f"Поисковый запрос: {item.query}\nОбоснование поискового запроса: {item.reason}"
    result = await Runner.run(search_agent, input)
    return result.final_output

# -- Пример использования --
async def main():
    query = "Какими будут фреймворки искусственного интеллекта на Python в 2025 году?"

    try:
        with trace("Search", disabled=trace_mode_disabled):
            print(f"Запуск поиска: {query}...")
            search_plan = await plan_searches(query)
            search_results = await perform_searches(search_plan)
            context_str = "\n\n---\n\n".join(search_results)


            final_input = f"Вот результаты поиска:\n{context_str}"
            print(final_input)
            write_result = await Runner.run(synthesis_agent, final_input)
            print(f"\nРезультат: \n\n{write_result.final_output}")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())