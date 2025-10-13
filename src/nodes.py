def run_agent(state):
    print("[run_agent] Received state:", state)

    token = state.get("input", "").upper()
    top_apy = {
        "ETH": "3.78%",
        "USDC": "5.32%",
        "DAI": "4.15%"
    }
    result = f"🔍 Лучший APY для {token}: {top_apy.get(token, 'не найден')}"
    
    print("[run_agent] Result:", result)

    return {
        "output": result
    }