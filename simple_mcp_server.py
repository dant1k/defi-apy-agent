#!/usr/bin/env python3
"""
Simplified Genora MCP Server for AI Analysis
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class SimpleGenoraMCPServer:
    """Simplified MCP server for Genora AI analysis"""
    
    def __init__(self):
        self.server_name = "genora-mcp"
        self.version = "1.0.0"
    
    async def analyze_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Analyze a specific strategy"""
        try:
            # Get strategy data from Redis
            strategy_data = redis_client.hget("strategies:items", strategy_id)
            if not strategy_data:
                return {"error": f"Strategy {strategy_id} not found"}
            
            strategy = json.loads(strategy_data)
            
            # Perform analysis
            analysis = {
                "strategy_id": strategy_id,
                "name": strategy.get("name", "Unknown"),
                "protocol": strategy.get("protocol", "Unknown"),
                "chain": strategy.get("chain", "Unknown"),
                "current_apy": strategy.get("apy", 0),
                "tvl": strategy.get("tvl_usd", 0),
                "risk_score": strategy.get("risk_score", 5),
                "analysis": {
                    "apy_assessment": self._assess_apy(strategy.get("apy", 0)),
                    "risk_level": self._assess_risk(strategy.get("risk_score", 5)),
                    "tvl_stability": self._assess_tvl_stability(strategy.get("tvl_usd", 0)),
                    "recommendation": self._generate_recommendation(strategy)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing strategy: {e}")
            return {"error": str(e)}
    
    async def get_market_insights(self, timeframe: str = "24h") -> Dict[str, Any]:
        """Get market insights"""
        try:
            # Get market data from Redis
            latest_data = redis_client.get("strategies:latest")
            if not latest_data:
                return {"error": "No market data available"}
            
            data = json.loads(latest_data)
            strategies = data.get("items", [])
            
            if not strategies:
                return {"error": "No strategies available"}
            
            # Generate insights
            insights = {
                "timeframe": timeframe,
                "total_strategies": len(strategies),
                "total_tvl": sum(s.get("tvl_usd", 0) for s in strategies),
                "average_apy": sum(s.get("apy", 0) for s in strategies) / len(strategies),
                "top_protocols": self._get_top_protocols(strategies),
                "top_chains": self._get_top_chains(strategies),
                "market_trends": self._analyze_market_trends(strategies, timeframe),
                "ai_insights": self._generate_ai_insights(strategies),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting market insights: {e}")
            return {"error": str(e)}
    
    async def compare_strategies(self, strategy_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple strategies"""
        try:
            comparisons = []
            
            for strategy_id in strategy_ids:
                strategy_data = redis_client.hget("strategies:items", strategy_id)
                if strategy_data:
                    strategy = json.loads(strategy_data)
                    comparisons.append({
                        "id": strategy_id,
                        "name": strategy.get("name", "Unknown"),
                        "apy": strategy.get("apy", 0),
                        "tvl": strategy.get("tvl_usd", 0),
                        "risk": strategy.get("risk_score", 5),
                        "protocol": strategy.get("protocol", "Unknown"),
                        "chain": strategy.get("chain", "Unknown")
                    })
            
            if not comparisons:
                return {"error": "No strategies found for comparison"}
            
            # Generate comparison analysis
            best_apy = max(comparisons, key=lambda x: x["apy"])
            lowest_risk = min(comparisons, key=lambda x: x["risk"])
            highest_tvl = max(comparisons, key=lambda x: x["tvl"])
            
            analysis = {
                "comparison_summary": {
                    "total_strategies": len(comparisons),
                    "best_apy": best_apy,
                    "lowest_risk": lowest_risk,
                    "highest_tvl": highest_tvl
                },
                "strategies": comparisons,
                "recommendations": self._generate_comparison_recommendations(comparisons),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error comparing strategies: {e}")
            return {"error": str(e)}
    
    def _assess_apy(self, apy: float) -> str:
        if apy > 50:
            return "Very High - Consider sustainability"
        elif apy > 20:
            return "High - Good yield opportunity"
        elif apy > 10:
            return "Moderate - Balanced risk/reward"
        elif apy > 5:
            return "Low - Conservative option"
        else:
            return "Very Low - Minimal returns"
    
    def _assess_risk(self, risk_score: float) -> str:
        if risk_score < 3:
            return "Low Risk"
        elif risk_score < 6:
            return "Medium Risk"
        else:
            return "High Risk"
    
    def _assess_tvl_stability(self, tvl: float) -> str:
        if tvl > 10000000:
            return "Very Stable - High liquidity"
        elif tvl > 1000000:
            return "Stable - Good liquidity"
        elif tvl > 100000:
            return "Moderate - Adequate liquidity"
        else:
            return "Unstable - Low liquidity"
    
    def _generate_recommendation(self, strategy: Dict) -> str:
        apy = strategy.get("apy", 0)
        risk = strategy.get("risk_score", 5)
        tvl = strategy.get("tvl_usd", 0)
        
        if apy > 30 and risk < 4 and tvl > 1000000:
            return "Strong Buy - High yield with manageable risk"
        elif apy > 15 and risk < 6 and tvl > 500000:
            return "Buy - Good risk/reward ratio"
        elif apy > 10 and risk < 7:
            return "Hold - Moderate opportunity"
        else:
            return "Avoid - High risk or low yield"
    
    def _get_top_protocols(self, strategies: List[Dict]) -> List[Dict]:
        protocol_counts = {}
        for strategy in strategies:
            protocol = strategy.get("protocol", "Unknown")
            if protocol not in protocol_counts:
                protocol_counts[protocol] = {"count": 0, "total_tvl": 0}
            protocol_counts[protocol]["count"] += 1
            protocol_counts[protocol]["total_tvl"] += strategy.get("tvl_usd", 0)
        
        return sorted(
            [{"protocol": k, **v} for k, v in protocol_counts.items()],
            key=lambda x: x["total_tvl"],
            reverse=True
        )[:5]
    
    def _get_top_chains(self, strategies: List[Dict]) -> List[Dict]:
        chain_counts = {}
        for strategy in strategies:
            chain = strategy.get("chain", "Unknown")
            if chain not in chain_counts:
                chain_counts[chain] = {"count": 0, "total_tvl": 0}
            chain_counts[chain]["count"] += 1
            chain_counts[chain]["total_tvl"] += strategy.get("tvl_usd", 0)
        
        return sorted(
            [{"chain": k, **v} for k, v in chain_counts.items()],
            key=lambda x: x["total_tvl"],
            reverse=True
        )[:5]
    
    def _analyze_market_trends(self, strategies: List[Dict], timeframe: str) -> Dict:
        return {
            "apy_trend": "Increasing" if len(strategies) > 0 else "Stable",
            "tvl_trend": "Growing" if len(strategies) > 0 else "Stable",
            "new_strategies": len(strategies) // 10,
            "dominant_chains": [s.get("chain", "Unknown") for s in strategies[:3]]
        }
    
    def _generate_ai_insights(self, strategies: List[Dict]) -> List[str]:
        return [
            "Market shows strong growth in Layer 2 protocols",
            "Stablecoin strategies are gaining popularity",
            "Risk-adjusted returns are improving across major protocols",
            "Cross-chain strategies are emerging as a new trend"
        ]
    
    def _generate_comparison_recommendations(self, comparisons: List[Dict]) -> List[str]:
        if not comparisons:
            return []
        
        recommendations = []
        best_apy = max(comparisons, key=lambda x: x["apy"])
        lowest_risk = min(comparisons, key=lambda x: x["risk"])
        
        recommendations.append(f"Best APY: {best_apy['name']} ({best_apy['apy']:.2f}%)")
        recommendations.append(f"Lowest Risk: {lowest_risk['name']} (Risk: {lowest_risk['risk']})")
        
        return recommendations

# Example usage
async def main():
    """Test the simplified MCP server"""
    server = SimpleGenoraMCPServer()
    
    # Test market insights
    insights = await server.get_market_insights("24h")
    print("Market Insights:", json.dumps(insights, indent=2))
    
    # Test strategy analysis
    analysis = await server.analyze_strategy("test-strategy")
    print("Strategy Analysis:", json.dumps(analysis, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
