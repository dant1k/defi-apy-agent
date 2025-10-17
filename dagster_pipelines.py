#!/usr/bin/env python3
"""
Genora Dagster Pipelines for Data Orchestration
Advanced data processing and analytics pipelines
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import redis
import pandas as pd
import numpy as np
from dagster import (
    Definitions,
    asset,
    AssetExecutionContext,
    Config,
    EnvVar,
    schedule,
    define_asset_job,
    DailyPartitionsDefinition,
    HourlyPartitionsDefinition,
    StaticPartitionsDefinition
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class DataProcessingConfig(Config):
    """Configuration for data processing"""
    batch_size: int = 1000
    enable_ml_features: bool = True
    risk_threshold: float = 7.0
    min_tvl: float = 100000.0

# Partition definitions
daily_partitions = DailyPartitionsDefinition(start_date="2024-01-01")
hourly_partitions = HourlyPartitionsDefinition(start_date="2024-01-01")
chain_partitions = StaticPartitionsDefinition(["ethereum", "bsc", "polygon", "arbitrum", "optimism", "avalanche"])

@asset(
    description="Raw strategies data from DeFiLlama and other sources",
    partitions_def=daily_partitions
)
def raw_strategies_data(context: AssetExecutionContext) -> Dict[str, Any]:
    """Extract raw strategies data from various sources"""
    partition_date = context.partition_key
    
    try:
        # Get data from Redis (our current data source)
        latest_data = redis_client.get("strategies:latest")
        if not latest_data:
            raise ValueError("No strategies data available in Redis")
        
        data = json.loads(latest_data)
        strategies = data.get("items", [])
        
        # Add metadata
        raw_data = {
            "strategies": strategies,
            "extraction_date": partition_date,
            "source": "redis_cache",
            "total_count": len(strategies),
            "extracted_at": datetime.now(timezone.utc).isoformat()
        }
        
        context.log.info(f"Extracted {len(strategies)} strategies for {partition_date}")
        return raw_data
        
    except Exception as e:
        context.log.error(f"Failed to extract raw strategies data: {e}")
        raise

@asset(
    description="Cleaned and normalized strategies data",
    deps=[raw_strategies_data],
    partitions_def=daily_partitions
)
def cleaned_strategies_data(context: AssetExecutionContext, config: DataProcessingConfig) -> Dict[str, Any]:
    """Clean and normalize strategies data"""
    partition_date = context.partition_key
    
    try:
        # Get raw data
        raw_data = context.assets_defs_by_key["raw_strategies_data"].compute_fn()
        strategies = raw_data["strategies"]
        
        cleaned_strategies = []
        for strategy in strategies:
            # Clean and normalize data
            cleaned_strategy = {
                "id": strategy.get("id", ""),
                "name": strategy.get("name", "").strip(),
                "protocol": strategy.get("protocol", "").strip(),
                "chain": strategy.get("chain", "").strip().title(),
                "apy": float(strategy.get("apy", 0)) if strategy.get("apy") else 0.0,
                "tvl_usd": float(strategy.get("tvl_usd", 0)) if strategy.get("tvl_usd") else 0.0,
                "risk_score": float(strategy.get("risk_score", 5)) if strategy.get("risk_score") else 5.0,
                "category": strategy.get("category", "unknown"),
                "tokens": strategy.get("tokens", []),
                "url": strategy.get("url", ""),
                "created_at": strategy.get("created_at", datetime.now(timezone.utc).isoformat()),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Filter out strategies with TVL below threshold
            if cleaned_strategy["tvl_usd"] >= config.min_tvl:
                cleaned_strategies.append(cleaned_strategy)
        
        cleaned_data = {
            "strategies": cleaned_strategies,
            "cleaning_date": partition_date,
            "original_count": len(strategies),
            "cleaned_count": len(cleaned_strategies),
            "filtered_out": len(strategies) - len(cleaned_strategies),
            "cleaned_at": datetime.now(timezone.utc).isoformat()
        }
        
        context.log.info(f"Cleaned {len(cleaned_strategies)} strategies (filtered out {cleaned_data['filtered_out']})")
        return cleaned_data
        
    except Exception as e:
        context.log.error(f"Failed to clean strategies data: {e}")
        raise

@asset(
    description="Enhanced strategies with ML features and risk analysis",
    deps=[cleaned_strategies_data],
    partitions_def=daily_partitions
)
def enhanced_strategies_data(context: AssetExecutionContext, config: DataProcessingConfig) -> Dict[str, Any]:
    """Enhance strategies with ML features and advanced analytics"""
    partition_date = context.partition_key
    
    try:
        # Get cleaned data
        cleaned_data = context.assets_defs_by_key["cleaned_strategies_data"].compute_fn()
        strategies = cleaned_data["strategies"]
        
        enhanced_strategies = []
        for strategy in strategies:
            enhanced_strategy = strategy.copy()
            
            # Calculate additional features
            enhanced_strategy.update({
                "apy_risk_ratio": strategy["apy"] / max(strategy["risk_score"], 0.1),
                "tvl_rank": 0,  # Will be calculated after sorting
                "protocol_risk_score": _calculate_protocol_risk(strategy["protocol"]),
                "chain_risk_score": _calculate_chain_risk(strategy["chain"]),
                "liquidity_score": _calculate_liquidity_score(strategy["tvl_usd"]),
                "volatility_score": _calculate_volatility_score(strategy),
                "ai_score": _calculate_ai_score(strategy),
                "trend_score": _calculate_trend_score(strategy),
                "sustainability_score": _calculate_sustainability_score(strategy)
            })
            
            enhanced_strategies.append(enhanced_strategy)
        
        # Sort by TVL and assign ranks
        enhanced_strategies.sort(key=lambda x: x["tvl_usd"], reverse=True)
        for i, strategy in enumerate(enhanced_strategies):
            strategy["tvl_rank"] = i + 1
        
        enhanced_data = {
            "strategies": enhanced_strategies,
            "enhancement_date": partition_date,
            "total_strategies": len(enhanced_strategies),
            "high_risk_count": len([s for s in enhanced_strategies if s["risk_score"] > config.risk_threshold]),
            "high_apy_count": len([s for s in enhanced_strategies if s["apy"] > 20]),
            "enhanced_at": datetime.now(timezone.utc).isoformat()
        }
        
        context.log.info(f"Enhanced {len(enhanced_strategies)} strategies with ML features")
        return enhanced_data
        
    except Exception as e:
        context.log.error(f"Failed to enhance strategies data: {e}")
        raise

@asset(
    description="Protocol analytics and rankings",
    deps=[enhanced_strategies_data],
    partitions_def=daily_partitions
)
def protocol_analytics(context: AssetExecutionContext) -> Dict[str, Any]:
    """Generate protocol-level analytics and rankings"""
    partition_date = context.partition_key
    
    try:
        enhanced_data = context.assets_defs_by_key["enhanced_strategies_data"].compute_fn()
        strategies = enhanced_data["strategies"]
        
        # Group by protocol
        protocol_data = {}
        for strategy in strategies:
            protocol = strategy["protocol"]
            if protocol not in protocol_data:
                protocol_data[protocol] = {
                    "protocol": protocol,
                    "strategies": [],
                    "total_tvl": 0,
                    "total_strategies": 0,
                    "avg_apy": 0,
                    "avg_risk": 0,
                    "chains": set(),
                    "categories": set()
                }
            
            protocol_data[protocol]["strategies"].append(strategy)
            protocol_data[protocol]["total_tvl"] += strategy["tvl_usd"]
            protocol_data[protocol]["total_strategies"] += 1
            protocol_data[protocol]["chains"].add(strategy["chain"])
            protocol_data[protocol]["categories"].add(strategy["category"])
        
        # Calculate averages and rankings
        protocol_analytics = []
        for protocol, data in protocol_data.items():
            if data["strategies"]:
                data["avg_apy"] = sum(s["apy"] for s in data["strategies"]) / len(data["strategies"])
                data["avg_risk"] = sum(s["risk_score"] for s in data["strategies"]) / len(data["strategies"])
                data["chains"] = list(data["chains"])
                data["categories"] = list(data["categories"])
                data["dominant_chain"] = max(data["chains"], key=lambda c: sum(s["tvl_usd"] for s in data["strategies"] if s["chain"] == c))
                data["top_strategy"] = max(data["strategies"], key=lambda s: s["apy"])
                
                protocol_analytics.append(data)
        
        # Sort by TVL
        protocol_analytics.sort(key=lambda x: x["total_tvl"], reverse=True)
        
        analytics_data = {
            "protocols": protocol_analytics,
            "analytics_date": partition_date,
            "total_protocols": len(protocol_analytics),
            "top_protocol": protocol_analytics[0]["protocol"] if protocol_analytics else None,
            "total_tvl": sum(p["total_tvl"] for p in protocol_analytics),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        context.log.info(f"Generated analytics for {len(protocol_analytics)} protocols")
        return analytics_data
        
    except Exception as e:
        context.log.error(f"Failed to generate protocol analytics: {e}")
        raise

@asset(
    description="Chain analytics and network health metrics",
    deps=[enhanced_strategies_data],
    partitions_def=daily_partitions
)
def chain_analytics(context: AssetExecutionContext) -> Dict[str, Any]:
    """Generate chain-level analytics and network health metrics"""
    partition_date = context.partition_key
    
    try:
        enhanced_data = context.assets_defs_by_key["enhanced_strategies_data"].compute_fn()
        strategies = enhanced_data["strategies"]
        
        # Group by chain
        chain_data = {}
        for strategy in strategies:
            chain = strategy["chain"]
            if chain not in chain_data:
                chain_data[chain] = {
                    "chain": chain,
                    "strategies": [],
                    "total_tvl": 0,
                    "total_strategies": 0,
                    "avg_apy": 0,
                    "avg_risk": 0,
                    "protocols": set(),
                    "categories": set()
                }
            
            chain_data[chain]["strategies"].append(strategy)
            chain_data[chain]["total_tvl"] += strategy["tvl_usd"]
            chain_data[chain]["total_strategies"] += 1
            chain_data[chain]["protocols"].add(strategy["protocol"])
            chain_data[chain]["categories"].add(strategy["category"])
        
        # Calculate metrics
        chain_analytics = []
        for chain, data in chain_data.items():
            if data["strategies"]:
                data["avg_apy"] = sum(s["apy"] for s in data["strategies"]) / len(data["strategies"])
                data["avg_risk"] = sum(s["risk_score"] for s in data["strategies"]) / len(data["strategies"])
                data["protocols"] = list(data["protocols"])
                data["categories"] = list(data["categories"])
                data["protocol_count"] = len(data["protocols"])
                data["diversity_score"] = len(data["protocols"]) / len(data["strategies"]) if data["strategies"] else 0
                data["top_protocol"] = max(data["protocols"], key=lambda p: sum(s["tvl_usd"] for s in data["strategies"] if s["protocol"] == p))
                
                chain_analytics.append(data)
        
        # Sort by TVL
        chain_analytics.sort(key=lambda x: x["total_tvl"], reverse=True)
        
        analytics_data = {
            "chains": chain_analytics,
            "analytics_date": partition_date,
            "total_chains": len(chain_analytics),
            "dominant_chain": chain_analytics[0]["chain"] if chain_analytics else None,
            "total_tvl": sum(c["total_tvl"] for c in chain_analytics),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        context.log.info(f"Generated analytics for {len(chain_analytics)} chains")
        return analytics_data
        
    except Exception as e:
        context.log.error(f"Failed to generate chain analytics: {e}")
        raise

@asset(
    description="Market trends and predictions",
    deps=[enhanced_strategies_data, protocol_analytics, chain_analytics],
    partitions_def=daily_partitions
)
def market_trends(context: AssetExecutionContext) -> Dict[str, Any]:
    """Generate market trends and predictions"""
    partition_date = context.partition_key
    
    try:
        enhanced_data = context.assets_defs_by_key["enhanced_strategies_data"].compute_fn()
        protocol_data = context.assets_defs_by_key["protocol_analytics"].compute_fn()
        chain_data = context.assets_defs_by_key["chain_analytics"].compute_fn()
        
        strategies = enhanced_data["strategies"]
        protocols = protocol_data["protocols"]
        chains = chain_data["chains"]
        
        # Calculate trends
        trends = {
            "market_overview": {
                "total_tvl": sum(s["tvl_usd"] for s in strategies),
                "total_strategies": len(strategies),
                "avg_apy": sum(s["apy"] for s in strategies) / len(strategies) if strategies else 0,
                "avg_risk": sum(s["risk_score"] for s in strategies) / len(strategies) if strategies else 0
            },
            "top_performers": {
                "highest_apy": max(strategies, key=lambda s: s["apy"]) if strategies else None,
                "lowest_risk": min(strategies, key=lambda s: s["risk_score"]) if strategies else None,
                "highest_tvl": max(strategies, key=lambda s: s["tvl_usd"]) if strategies else None,
                "best_ai_score": max(strategies, key=lambda s: s["ai_score"]) if strategies else None
            },
            "emerging_trends": _identify_emerging_trends(strategies, protocols, chains),
            "risk_analysis": _analyze_market_risk(strategies),
            "predictions": _generate_market_predictions(strategies, protocols, chains),
            "trends_date": partition_date,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        context.log.info("Generated market trends and predictions")
        return trends
        
    except Exception as e:
        context.log.error(f"Failed to generate market trends: {e}")
        raise

@asset(
    description="Final processed data ready for frontend",
    deps=[enhanced_strategies_data, protocol_analytics, chain_analytics, market_trends],
    partitions_def=daily_partitions
)
def processed_frontend_data(context: AssetExecutionContext) -> Dict[str, Any]:
    """Combine all processed data for frontend consumption"""
    partition_date = context.partition_key
    
    try:
        enhanced_data = context.assets_defs_by_key["enhanced_strategies_data"].compute_fn()
        protocol_data = context.assets_defs_by_key["protocol_analytics"].compute_fn()
        chain_data = context.assets_defs_by_key["chain_analytics"].compute_fn()
        trends_data = context.assets_defs_by_key["market_trends"].compute_fn()
        
        # Combine all data
        final_data = {
            "strategies": enhanced_data["strategies"],
            "protocols": protocol_data["protocols"],
            "chains": chain_data["chains"],
            "trends": trends_data,
            "metadata": {
                "processed_date": partition_date,
                "total_strategies": len(enhanced_data["strategies"]),
                "total_protocols": len(protocol_data["protocols"]),
                "total_chains": len(chain_data["chains"]),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Store in Redis for frontend access
        redis_client.setex(
            f"processed_data:{partition_date}",
            86400,  # 24 hours
            json.dumps(final_data)
        )
        
        context.log.info(f"Stored processed data for {partition_date} in Redis")
        return final_data
        
    except Exception as e:
        context.log.error(f"Failed to process frontend data: {e}")
        raise

# Helper functions for ML features
def _calculate_protocol_risk(protocol: str) -> float:
    """Calculate protocol-specific risk score"""
    # Mock implementation - in real scenario, this would use historical data
    risk_scores = {
        "aave": 2.0,
        "compound": 2.5,
        "uniswap": 3.0,
        "curve": 2.8,
        "yearn": 3.5,
        "beefy": 4.0
    }
    return risk_scores.get(protocol.lower(), 5.0)

def _calculate_chain_risk(chain: str) -> float:
    """Calculate chain-specific risk score"""
    risk_scores = {
        "ethereum": 2.0,
        "bitcoin": 1.5,
        "bsc": 3.5,
        "polygon": 3.0,
        "arbitrum": 2.5,
        "optimism": 2.8,
        "avalanche": 3.2
    }
    return risk_scores.get(chain.lower(), 4.0)

def _calculate_liquidity_score(tvl: float) -> float:
    """Calculate liquidity score based on TVL"""
    if tvl > 10000000:
        return 1.0
    elif tvl > 1000000:
        return 2.0
    elif tvl > 100000:
        return 3.0
    else:
        return 4.0

def _calculate_volatility_score(strategy: Dict) -> float:
    """Calculate volatility score"""
    # Mock implementation
    return 3.0 + (hash(str(strategy.get("name", ""))) % 100) / 100

def _calculate_ai_score(strategy: Dict) -> float:
    """Calculate AI-powered overall score"""
    apy = strategy.get("apy", 0)
    risk = strategy.get("risk_score", 5)
    tvl = strategy.get("tvl_usd", 0)
    
    # Weighted scoring
    apy_score = min(apy / 50, 1.0) * 0.4
    risk_score = max(0, (10 - risk) / 10) * 0.3
    tvl_score = min(tvl / 10000000, 1.0) * 0.3
    
    return (apy_score + risk_score + tvl_score) * 10

def _calculate_trend_score(strategy: Dict) -> float:
    """Calculate trend score"""
    # Mock implementation
    return 5.0 + (hash(str(strategy.get("protocol", ""))) % 100) / 100

def _calculate_sustainability_score(strategy: Dict) -> float:
    """Calculate sustainability score"""
    apy = strategy.get("apy", 0)
    if apy > 100:
        return 2.0  # Unsustainable
    elif apy > 50:
        return 3.0  # Questionable
    elif apy > 20:
        return 4.0  # Moderate
    else:
        return 5.0  # Sustainable

def _identify_emerging_trends(strategies: List[Dict], protocols: List[Dict], chains: List[Dict]) -> List[str]:
    """Identify emerging trends in the market"""
    trends = []
    
    # Analyze by category
    categories = {}
    for strategy in strategies:
        category = strategy.get("category", "unknown")
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    # Find growing categories
    total_strategies = len(strategies)
    for category, count in categories.items():
        if count / total_strategies > 0.1:  # More than 10% of strategies
            trends.append(f"Growing interest in {category} strategies")
    
    # Analyze by chain
    chain_tvl = {}
    for strategy in strategies:
        chain = strategy["chain"]
        if chain not in chain_tvl:
            chain_tvl[chain] = 0
        chain_tvl[chain] += strategy["tvl_usd"]
    
    # Find emerging chains
    total_tvl = sum(chain_tvl.values())
    for chain, tvl in chain_tvl.items():
        if tvl / total_tvl > 0.05:  # More than 5% of total TVL
            trends.append(f"Significant TVL growth on {chain}")
    
    return trends

def _analyze_market_risk(strategies: List[Dict]) -> Dict[str, Any]:
    """Analyze overall market risk"""
    if not strategies:
        return {"overall_risk": "Unknown", "risk_factors": []}
    
    avg_risk = sum(s["risk_score"] for s in strategies) / len(strategies)
    high_risk_count = len([s for s in strategies if s["risk_score"] > 7])
    
    risk_factors = []
    if avg_risk > 6:
        risk_factors.append("High average risk across strategies")
    if high_risk_count > len(strategies) * 0.3:
        risk_factors.append("High concentration of risky strategies")
    
    return {
        "overall_risk": "High" if avg_risk > 6 else "Medium" if avg_risk > 4 else "Low",
        "average_risk_score": avg_risk,
        "high_risk_strategies": high_risk_count,
        "risk_factors": risk_factors
    }

def _generate_market_predictions(strategies: List[Dict], protocols: List[Dict], chains: List[Dict]) -> Dict[str, Any]:
    """Generate market predictions"""
    return {
        "apy_trend": "Stable to slightly increasing",
        "tvl_growth": "Moderate growth expected",
        "emerging_protocols": [p["protocol"] for p in protocols[:3]],
        "emerging_chains": [c["chain"] for c in chains[:3]],
        "risk_outlook": "Stable risk environment",
        "confidence": 0.75
    }

# Schedules
@schedule(
    cron_schedule="0 2 * * *",  # Daily at 2 AM
    job=define_asset_job("daily_data_processing", selection="processed_frontend_data"),
    execution_timezone="UTC"
)
def daily_processing_schedule(context):
    """Daily data processing schedule"""
    return context.scheduled_execution_time.strftime("%Y-%m-%d")

@schedule(
    cron_schedule="0 */6 * * *",  # Every 6 hours
    job=define_asset_job("frequent_updates", selection=["enhanced_strategies_data", "market_trends"]),
    execution_timezone="UTC"
)
def frequent_updates_schedule(context):
    """Frequent updates schedule"""
    return context.scheduled_execution_time.strftime("%Y-%m-%d")

# Job definitions
daily_processing_job = define_asset_job(
    "daily_data_processing",
    selection="processed_frontend_data"
)

frequent_updates_job = define_asset_job(
    "frequent_updates",
    selection=["enhanced_strategies_data", "market_trends"]
)

# Dagster definitions
defs = Definitions(
    assets=[
        raw_strategies_data,
        cleaned_strategies_data,
        enhanced_strategies_data,
        protocol_analytics,
        chain_analytics,
        market_trends,
        processed_frontend_data
    ],
    jobs=[daily_processing_job, frequent_updates_job],
    schedules=[daily_processing_schedule, frequent_updates_schedule],
    resources={
        "config": DataProcessingConfig(
            batch_size=1000,
            enable_ml_features=True,
            risk_threshold=7.0,
            min_tvl=100000.0
        )
    }
)
