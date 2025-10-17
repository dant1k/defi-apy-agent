#!/usr/bin/env python3
"""
MCP API Router for Genora AI Analysis
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..cache import get_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/analyze-strategy/{strategy_id}")
async def analyze_strategy(strategy_id: str) -> JSONResponse:
    """Analyze a specific strategy"""
    try:
        # Get strategy data from cache
        async with get_cache() as cache:
            snapshot = await cache.get_latest_strategies()
            
            if not snapshot:
                raise HTTPException(status_code=404, detail="No strategies data available")
            
            strategies = snapshot.get("items", [])
            strategy = next((s for s in strategies if s.get("id") == strategy_id), None)
            
            if not strategy:
                raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found")
            
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
                    "apy_assessment": _assess_apy(strategy.get("apy", 0)),
                    "risk_level": _assess_risk(strategy.get("risk_score", 5)),
                    "tvl_stability": _assess_tvl_stability(strategy.get("tvl_usd", 0)),
                    "recommendation": _generate_recommendation(strategy)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return JSONResponse(analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-insights")
async def get_market_insights(
    timeframe: str = Query("24h", description="Timeframe for analysis")
) -> JSONResponse:
    """Get market insights"""
    try:
        # Get market data from cache
        async with get_cache() as cache:
            snapshot = await cache.get_latest_strategies()
            
            if not snapshot:
                raise HTTPException(status_code=404, detail="No market data available")
            
            strategies = snapshot.get("items", [])
            
            if not strategies:
                raise HTTPException(status_code=404, detail="No strategies available")
            
            # Generate insights
            total_tvl = sum(s.get("tvl_usd", 0) for s in strategies)
            avg_apy = sum(s.get("apy", 0) for s in strategies) / len(strategies) if strategies else 0
            
            insights = {
                "timeframe": timeframe,
                "total_strategies": len(strategies),
                "total_tvl": float(total_tvl) if total_tvl != float('inf') else 0,
                "average_apy": float(avg_apy) if avg_apy != float('inf') else 0,
                "top_protocols": _get_top_protocols(strategies),
                "top_chains": _get_top_chains(strategies),
                "market_trends": _analyze_market_trends(strategies, timeframe),
                "ai_insights": _generate_ai_insights(strategies),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return JSONResponse(insights)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare-strategies")
async def compare_strategies(strategy_ids: List[str]) -> JSONResponse:
    """Compare multiple strategies"""
    try:
        if not strategy_ids:
            raise HTTPException(status_code=400, detail="No strategy IDs provided")
        
        # Get strategy data from cache
        async with get_cache() as cache:
            snapshot = await cache.get_latest_strategies()
            
            if not snapshot:
                raise HTTPException(status_code=404, detail="No strategies data available")
            
            strategies = snapshot.get("items", [])
            comparisons = []
            
            for strategy_id in strategy_ids:
                strategy = next((s for s in strategies if s.get("id") == strategy_id), None)
                if strategy:
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
                raise HTTPException(status_code=404, detail="No strategies found for comparison")
            
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
                "recommendations": _generate_comparison_recommendations(comparisons),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return JSONResponse(analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict-trends")
async def predict_trends(
    protocol: Optional[str] = Query(None, description="Protocol name to analyze"),
    chain: Optional[str] = Query(None, description="Blockchain network")
) -> JSONResponse:
    """Predict APY trends"""
    try:
        # Mock predictions (in real scenario, this would use ML models)
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
        
        return JSONResponse(predictions)
        
    except Exception as e:
        logger.error(f"Error predicting trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _assess_apy(apy: float) -> str:
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

def _assess_risk(risk_score: float) -> str:
    if risk_score < 3:
        return "Low Risk"
    elif risk_score < 6:
        return "Medium Risk"
    else:
        return "High Risk"

def _assess_tvl_stability(tvl: float) -> str:
    if tvl > 10000000:
        return "Very Stable - High liquidity"
    elif tvl > 1000000:
        return "Stable - Good liquidity"
    elif tvl > 100000:
        return "Moderate - Adequate liquidity"
    else:
        return "Unstable - Low liquidity"

def _generate_recommendation(strategy: Dict) -> str:
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

def _get_top_protocols(strategies: List[Dict]) -> List[Dict]:
    protocol_counts = {}
    for strategy in strategies:
        protocol = strategy.get("protocol", "Unknown")
        if protocol not in protocol_counts:
            protocol_counts[protocol] = {"count": 0, "total_tvl": 0}
        protocol_counts[protocol]["count"] += 1
        tvl = strategy.get("tvl_usd", 0)
        protocol_counts[protocol]["total_tvl"] += float(tvl) if tvl != float('inf') else 0
    
    return sorted(
        [{"protocol": k, **v} for k, v in protocol_counts.items()],
        key=lambda x: x["total_tvl"],
        reverse=True
    )[:5]

def _get_top_chains(strategies: List[Dict]) -> List[Dict]:
    chain_counts = {}
    for strategy in strategies:
        chain = strategy.get("chain", "Unknown")
        if chain not in chain_counts:
            chain_counts[chain] = {"count": 0, "total_tvl": 0}
        chain_counts[chain]["count"] += 1
        tvl = strategy.get("tvl_usd", 0)
        chain_counts[chain]["total_tvl"] += float(tvl) if tvl != float('inf') else 0
    
    return sorted(
        [{"chain": k, **v} for k, v in chain_counts.items()],
        key=lambda x: x["total_tvl"],
        reverse=True
    )[:5]

def _analyze_market_trends(strategies: List[Dict], timeframe: str) -> Dict:
    return {
        "apy_trend": "Increasing" if len(strategies) > 0 else "Stable",
        "tvl_trend": "Growing" if len(strategies) > 0 else "Stable",
        "new_strategies": len(strategies) // 10,
        "dominant_chains": [s.get("chain", "Unknown") for s in strategies[:3]]
    }

def _generate_ai_insights(strategies: List[Dict]) -> List[str]:
    return [
        "Market shows strong growth in Layer 2 protocols",
        "Stablecoin strategies are gaining popularity",
        "Risk-adjusted returns are improving across major protocols",
        "Cross-chain strategies are emerging as a new trend"
    ]

def _generate_comparison_recommendations(comparisons: List[Dict]) -> List[str]:
    if not comparisons:
        return []
    
    recommendations = []
    best_apy = max(comparisons, key=lambda x: x["apy"])
    lowest_risk = min(comparisons, key=lambda x: x["risk"])
    
    recommendations.append(f"Best APY: {best_apy['name']} ({best_apy['apy']:.2f}%)")
    recommendations.append(f"Lowest Risk: {lowest_risk['name']} (Risk: {lowest_risk['risk']})")
    
    return recommendations
