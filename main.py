from agent.core import run_react_agent

if __name__ == "__main__":
    # Test query: Flight to Rome in September 2026 from Warsaw
    user_query = "Chcę zaplanować weekendowy wyjazd z Warszawy (WAW) do Rzymu (FCO) na daty od 2026-09-15 do 2026-09-18. Znajdź mi najpierw najtańsze loty."
    
    run_react_agent(user_query)