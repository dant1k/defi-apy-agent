#!/usr/bin/env python3
"""
Genora MCP Server for AI Analysis
Provides AI models with access to DeFi strategy data and analytics
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

import redis
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class GenoraMCPServer:
    def __init__(self):
        self.server = Server("genora-mcp")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP handlers for tools and resources"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools for AI analysis"""
            return [
                Tool(
                    name="analyze_strategy",
                    description="Analyze a specific DeFi strategy for risk, APY, and market conditions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "strategy_id": {
                                "type": "string",
                                "description": "ID of the strategy to analyze"
                            }
                        },
                        "required": ["strategy_id"]
                    }
                ),
                Tool(
                    name="compare_strategies",
                    description="Compare multiple DeFi strategies across different metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "strategy_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of strategy IDs to compare"
                            }
                        },
                        "required": ["strategy_ids"]
                    }
                ),
                Tool(
                    name="get_market_insights",
                    description="Get AI-powered market insights and trends",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timeframe": {
                                "type": "string",
                                "enum": ["24h", "7d", "30d"],
                                "description": "Timeframe for analysis"
                            }
                        },
                        "required": ["timeframe"]
                    }
                ),
                Tool(
                    name="predict_apy_trends",
                    description="Predict APY trends for specific protocols or chains",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "protocol": {
                                "type": "string",
                                "description": "Protocol name to analyze"
                            },
                            "chain": {
                                "type": "string",
                                "description": "Blockchain network"
                            }
                        }
                    }
                ),
                Tool(
                    name="risk_assessment",
                    description="Perform comprehensive risk assessment of DeFi strategies",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "strategy_id": {
                                "type": "string",
                                "description": "Strategy ID for risk assessment"
                            },
                            "include_historical": {
                                "type": "boolean",
                                "description": "Include historical risk data"
                            }
                        },
                        "required": ["strategy_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls from AI models"""
            try:
                if name == "analyze_strategy":
                    return await self.analyze_strategy(arguments.get("strategy_id"))
                elif name == "compare_strategies":
                    return await self.compare_strategies(arguments.get("strategy_ids", []))
                elif name == "get_market_insights":
                    return await self.get_market_insights(arguments.get("timeframe", "24h"))
                elif name == "predict_apy_trends":
                    return await self.predict_apy_trends(
                        arguments.get("protocol"),
                        arguments.get("chain")
                    )
                elif name == "risk_assessment":
                    return await self.risk_assessment(
                        arguments.get("strategy_id"),
                        arguments.get("include_historical", False)
                    )
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available data resources"""
            return [
                Resource(
                    uri="genora://strategies",
                    name="DeFi Strategies",
                    description="All available DeFi yield strategies",
                    mimeType="application/json"
                ),
                Resource(
                    uri="genora://protocols",
                    name="Protocols",
                    description="DeFi protocols and their metrics",
                    mimeType="application/json"
                ),
                Resource(
                    uri="genora://chains",
                    name="Blockchain Networks",
                    description="Supported blockchain networks",
                    mimeType="application/json"
                ),
                Resource(
                    uri="genora://market-data",
                    name="Market Data",
                    description="Real-time market data and trends",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read data resources"""
            try:
                if uri == "genora://strategies":
                    return await self.get_strategies_data()
                elif uri == "genora://protocols":
                    return await self.get_protocols_data()
                elif uri == "genora://chains":
                    return await self.get_chains_data()
                elif uri == "genora://market-data":
                    return await self.get_market_data()
                else:
                    return json.dumps({"error": f"Unknown resource: {uri}"})
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return json.dumps({"error": str(e)})
    
    async def analyze_strategy(self, strategy_id: str) -> List[TextContent]:
        """Analyze a specific strategy"""
        try:
            # Get strategy data from Redis
            strategy_data = redis_client.hget("strategies:items", strategy_id)
            if not strategy_data:
                return [TextContent(type="text", text=f"Strategy {strategy_id} not found")]
            
            strategy = json.loads(strategy_data)
            
            # Perform AI analysis
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
            
            return [TextContent(type="text", text=json.dumps(analysis, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error analyzing strategy: {str(e)}")]
    
    async def compare_strategies(self, strategy_ids: List[str]) -> List[TextContent]:
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
            
            # Generate comparison analysis
            if comparisons:
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
                
                return [TextContent(type="text", text=json.dumps(analysis, indent=2))]
            else:
                return [TextContent(type="text", text="No strategies found for comparison")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error comparing strategies: {str(e)}")]
    
    async def get_market_insights(self, timeframe: str) -> List[TextContent]:
        """Get AI-powered market insights"""
        try:
            # Get market data from Redis
            latest_data = redis_client.get("strategies:latest")
            if not latest_data:
                return [TextContent(type="text", text="No market data available")]
            
            data = json.loads(latest_data)
            strategies = data.get("items", [])
            
            # Generate insights
            insights = {
                "timeframe": timeframe,
                "total_strategies": len(strategies),
                "total_tvl": sum(s.get("tvl_usd", 0) for s in strategies),
                "average_apy": sum(s.get("apy", 0) for s in strategies) / len(strategies) if strategies else 0,
                "top_protocols": self._get_top_protocols(strategies),
                "top_chains": self._get_top_chains(strategies),
                "market_trends": self._analyze_market_trends(strategies, timeframe),
                "ai_insights": self._generate_ai_insights(strategies),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return [TextContent(type="text", text=json.dumps(insights, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting market insights: {str(e)}")]
    
    async def predict_apy_trends(self, protocol: Optional[str] = None, chain: Optional[str] = None) -> List[TextContent]:
        """Predict APY trends"""
        try:
            # Get historical data (mock for now)
            predictions = {
                "protocol": protocol,
                "chain": chain,
                "predictions": {
                    "next_24h": {
                        "apy_change": round((0.5 + (hash(str(protocol or "")) % 100) / 100) * 2 - 1, 2),
                        "confidence": 0.75
                    },
                    "next_7d": {
                        "apy_change": round((0.3 + (hash(str(protocol or "")) % 100) / 100) * 4 - 2, 2),
                        "confidence": 0.65
                    },
                    "next_30d": {
                        "apy_change": round((0.2 + (hash(str(protocol or "")) % 100) / 100) * 6 - 3, 2),
                        "confidence": 0.55
                    }
                },
                "factors": [
                    "Market volatility trends",
                    "Protocol TVL stability",
                    "Historical APY patterns",
                    "Network congestion levels"
                ],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return [TextContent(type="text", text=json.dumps(predictions, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error predicting trends: {str(e)}")]
    
    async def risk_assessment(self, strategy_id: str, include_historical: bool = False) -> List[TextContent]:
        """Perform comprehensive risk assessment"""
        try:
            strategy_data = redis_client.hget("strategies:items", strategy_id)
            if not strategy_data:
                return [TextContent(type="text", text=f"Strategy {strategy_id} not found")]
            
            strategy = json.loads(strategy_data)
            
            risk_assessment = {
                "strategy_id": strategy_id,
                "risk_factors": {
                    "smart_contract_risk": self._assess_smart_contract_risk(strategy),
                    "liquidity_risk": self._assess_liquidity_risk(strategy),
                    "market_risk": self._assess_market_risk(strategy),
                    "protocol_risk": self._assess_protocol_risk(strategy),
                    "chain_risk": self._assess_chain_risk(strategy)
                },
                "overall_risk_score": self._calculate_overall_risk(strategy),
                "risk_level": self._get_risk_level(self._calculate_overall_risk(strategy)),
                "recommendations": self._generate_risk_recommendations(strategy),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if include_historical:
                risk_assessment["historical_data"] = self._get_historical_risk_data(strategy_id)
            
            return [TextContent(type="text", text=json.dumps(risk_assessment, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error assessing risk: {str(e)}")]
    
    # Helper methods for analysis
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
            "new_strategies": len(strategies) // 10,  # Mock calculation
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
    
    def _assess_smart_contract_risk(self, strategy: Dict) -> Dict:
        return {
            "score": 3.5,
            "level": "Medium",
            "factors": ["Audited contracts", "Time in market", "Bug bounty programs"]
        }
    
    def _assess_liquidity_risk(self, strategy: Dict) -> Dict:
        tvl = strategy.get("tvl_usd", 0)
        if tvl > 10000000:
            score = 2.0
        elif tvl > 1000000:
            score = 3.0
        else:
            score = 5.0
        
        return {
            "score": score,
            "level": "Low" if score < 3 else "Medium" if score < 4 else "High",
            "factors": ["TVL size", "Liquidity depth", "Withdrawal patterns"]
        }
    
    def _assess_market_risk(self, strategy: Dict) -> Dict:
        return {
            "score": 4.0,
            "level": "Medium",
            "factors": ["Token volatility", "Market conditions", "Correlation risk"]
        }
    
    def _assess_protocol_risk(self, strategy: Dict) -> Dict:
        return {
            "score": 3.0,
            "level": "Low",
            "factors": ["Protocol maturity", "Team reputation", "Governance structure"]
        }
    
    def _assess_chain_risk(self, strategy: Dict) -> Dict:
        chain = strategy.get("chain", "").lower()
        if chain in ["ethereum", "bitcoin"]:
            score = 2.0
        elif chain in ["bsc", "polygon", "arbitrum"]:
            score = 3.0
        else:
            score = 4.0
        
        return {
            "score": score,
            "level": "Low" if score < 3 else "Medium" if score < 4 else "High",
            "factors": ["Network security", "Decentralization", "Uptime history"]
        }
    
    def _calculate_overall_risk(self, strategy: Dict) -> float:
        # Weighted average of all risk factors
        return 3.5  # Mock calculation
    
    def _get_risk_level(self, score: float) -> str:
        if score < 3:
            return "Low"
        elif score < 6:
            return "Medium"
        else:
            return "High"
    
    def _generate_risk_recommendations(self, strategy: Dict) -> List[str]:
        return [
            "Monitor TVL changes regularly",
            "Diversify across multiple protocols",
            "Set appropriate position sizes",
            "Consider stop-loss strategies"
        ]
    
    def _get_historical_risk_data(self, strategy_id: str) -> Dict:
        return {
            "30d_risk_trend": "Stable",
            "historical_incidents": 0,
            "recovery_time": "N/A"
        }
    
    async def get_strategies_data(self) -> str:
        """Get all strategies data"""
        try:
            latest_data = redis_client.get("strategies:latest")
            return latest_data or json.dumps({"error": "No strategies data available"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_protocols_data(self) -> str:
        """Get protocols data"""
        try:
            protocols = redis_client.smembers("strategies:protocols")
            return json.dumps(list(protocols))
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_chains_data(self) -> str:
        """Get chains data"""
        try:
            chains = redis_client.smembers("strategies:chains")
            return json.dumps(list(chains))
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def get_market_data(self) -> str:
        """Get market data"""
        try:
            latest_data = redis_client.get("strategies:latest")
            if latest_data:
                data = json.loads(latest_data)
                return json.dumps({
                    "total_strategies": len(data.get("items", [])),
                    "last_updated": data.get("updated_at"),
                    "total_tvl": sum(s.get("tvl_usd", 0) for s in data.get("items", []))
                })
            return json.dumps({"error": "No market data available"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="genora-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )

async def main():
    """Main entry point"""
    server = GenoraMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
