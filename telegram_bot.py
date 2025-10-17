#!/usr/bin/env python3
"""
Genora Telegram Bot for DeFi Strategy Notifications
Advanced bot for real-time DeFi strategy alerts and analytics
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import redis
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class GenoraTelegramBot:
    """Advanced Telegram bot for DeFi strategy notifications"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        self.subscribers = set()
        self.alert_thresholds = {
            "high_apy": 30.0,
            "low_risk": 3.0,
            "high_tvl": 1000000.0,
            "new_strategy": True
        }
    
    def setup_handlers(self):
        """Setup bot command handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("top", self.top_strategies_command))
        self.application.add_handler(CommandHandler("alerts", self.alerts_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("chart", self.chart_command))
        self.application.add_handler(CommandHandler("search", self.search_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "User"
        
        welcome_message = f"""
🚀 **Welcome to Genora DeFi Bot, {username}!**

I'm your AI-powered DeFi strategy assistant. Here's what I can do:

📊 **Analytics & Insights**
• Real-time strategy monitoring
• APY and risk analysis
• Market trends and predictions

🔔 **Smart Alerts**
• High APY opportunities
• Low-risk strategies
• New protocol launches
• Market volatility warnings

📈 **Interactive Features**
• Strategy comparisons
• Portfolio tracking
• Custom notifications
• Chart generation

**Quick Commands:**
/help - Show all commands
/subscribe - Get strategy alerts
/top - Show top strategies
/alerts - Configure alerts
/settings - Bot settings

Ready to explore the DeFi universe? 🌌
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Top Strategies", callback_data="top_strategies")],
            [InlineKeyboardButton("🔔 Subscribe to Alerts", callback_data="subscribe")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("📈 Market Overview", callback_data="market_overview")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **Genora DeFi Bot Commands**

**📊 Analytics Commands:**
/top - Show top performing strategies
/status - Current market status
/chart [strategy] - Generate strategy chart
/search [query] - Search strategies

**🔔 Alert Commands:**
/subscribe - Subscribe to strategy alerts
/unsubscribe - Unsubscribe from alerts
/alerts - Configure alert settings

**⚙️ Settings Commands:**
/settings - Bot configuration
/portfolio - Portfolio tracking

**📈 Market Commands:**
/trends - Market trends analysis
/volatility - Volatility alerts
/new - New strategy notifications

**💡 Tips:**
• Use /subscribe to get real-time alerts
• Set custom thresholds with /alerts
• Track your portfolio with /portfolio
• Get charts with /chart [strategy_name]

Need help? Just ask! 🚀
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        user_id = update.effective_user.id
        
        if user_id not in self.subscribers:
            self.subscribers.add(user_id)
            redis_client.sadd("telegram_subscribers", user_id)
            
            await update.message.reply_text(
                "✅ **Subscribed to Genora alerts!**\n\n"
                "You'll now receive notifications for:\n"
                "• High APY opportunities (>30%)\n"
                "• Low-risk strategies (<3 risk score)\n"
                "• New protocol launches\n"
                "• Market volatility alerts\n\n"
                "Use /alerts to customize your notifications! 🔔",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "ℹ️ You're already subscribed to Genora alerts!\n\n"
                "Use /alerts to customize your notification settings.",
                parse_mode='Markdown'
            )
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command"""
        user_id = update.effective_user.id
        
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            redis_client.srem("telegram_subscribers", user_id)
            
            await update.message.reply_text(
                "❌ **Unsubscribed from Genora alerts.**\n\n"
                "You won't receive notifications anymore.\n"
                "Use /subscribe to re-enable alerts anytime! 🔔",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "ℹ️ You're not currently subscribed to alerts.\n"
                "Use /subscribe to start receiving notifications!",
                parse_mode='Markdown'
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Get current market data
            latest_data = redis_client.get("strategies:latest")
            if not latest_data:
                await update.message.reply_text(
                    "⚠️ No market data available at the moment.\n"
                    "Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            data = json.loads(latest_data)
            strategies = data.get("items", [])
            
            if not strategies:
                await update.message.reply_text(
                    "⚠️ No strategies data available.\n"
                    "Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            # Calculate market statistics
            total_tvl = sum(s.get("tvl_usd", 0) for s in strategies)
            avg_apy = sum(s.get("apy", 0) for s in strategies) / len(strategies)
            high_apy_count = len([s for s in strategies if s.get("apy", 0) > 20])
            low_risk_count = len([s for s in strategies if s.get("risk_score", 5) < 4])
            
            # Get top protocols
            protocol_counts = {}
            for strategy in strategies:
                protocol = strategy.get("protocol", "Unknown")
                protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
            
            top_protocols = sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            status_message = f"""
📊 **Genora Market Status**

**📈 Market Overview:**
• Total Strategies: {len(strategies):,}
• Total TVL: ${total_tvl:,.0f}
• Average APY: {avg_apy:.2f}%
• High APY (>20%): {high_apy_count}
• Low Risk (<4): {low_risk_count}

**🏆 Top Protocols:**
{chr(10).join([f"• {protocol}: {count} strategies" for protocol, count in top_protocols])}

**⏰ Last Updated:**
{data.get('updated_at', 'Unknown')}

**🔔 Subscribers:**
{len(self.subscribers)} active users

Market is {'🟢 Active' if len(strategies) > 0 else '🔴 Inactive'}
            """
            
            await update.message.reply_text(status_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text(
                "❌ Error retrieving market status.\n"
                "Please try again later.",
                parse_mode='Markdown'
            )
    
    async def top_strategies_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /top command"""
        try:
            # Get current strategies
            latest_data = redis_client.get("strategies:latest")
            if not latest_data:
                await update.message.reply_text(
                    "⚠️ No strategies data available.\n"
                    "Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            data = json.loads(latest_data)
            strategies = data.get("items", [])
            
            if not strategies:
                await update.message.reply_text(
                    "⚠️ No strategies available.\n"
                    "Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            # Sort by APY and get top 5
            top_strategies = sorted(strategies, key=lambda x: x.get("apy", 0), reverse=True)[:5]
            
            message = "🏆 **Top 5 Strategies by APY**\n\n"
            
            for i, strategy in enumerate(top_strategies, 1):
                name = strategy.get("name", "Unknown")[:30]
                protocol = strategy.get("protocol", "Unknown")
                chain = strategy.get("chain", "Unknown")
                apy = strategy.get("apy", 0)
                tvl = strategy.get("tvl_usd", 0)
                risk = strategy.get("risk_score", 5)
                
                # Format TVL
                if tvl >= 1000000:
                    tvl_str = f"${tvl/1000000:.1f}M"
                elif tvl >= 1000:
                    tvl_str = f"${tvl/1000:.0f}K"
                else:
                    tvl_str = f"${tvl:.0f}"
                
                # Risk emoji
                risk_emoji = "🟢" if risk < 3 else "🟡" if risk < 6 else "🔴"
                
                message += f"""
**{i}. {name}**
• Protocol: {protocol}
• Chain: {chain}
• APY: {apy:.2f}%
• TVL: {tvl_str}
• Risk: {risk_emoji} {risk}/10
"""
            
            message += f"\n📊 Total strategies analyzed: {len(strategies)}"
            
            # Add inline buttons
            keyboard = [
                [InlineKeyboardButton("📈 View Charts", callback_data="view_charts")],
                [InlineKeyboardButton("🔍 Search More", callback_data="search_strategies")],
                [InlineKeyboardButton("⚙️ Alert Settings", callback_data="alert_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in top strategies command: {e}")
            await update.message.reply_text(
                "❌ Error retrieving top strategies.\n"
                "Please try again later.",
                parse_mode='Markdown'
            )
    
    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        user_id = update.effective_user.id
        
        if user_id not in self.subscribers:
            await update.message.reply_text(
                "⚠️ You need to subscribe first!\n"
                "Use /subscribe to enable alerts.",
                parse_mode='Markdown'
            )
            return
        
        alert_settings = f"""
🔔 **Alert Settings**

**Current Thresholds:**
• High APY: >{self.alert_thresholds['high_apy']}%
• Low Risk: <{self.alert_thresholds['low_risk']}/10
• High TVL: >${self.alert_thresholds['high_tvl']:,.0f}
• New Strategies: {'✅' if self.alert_thresholds['new_strategy'] else '❌'}

**Alert Types:**
• High APY opportunities
• Low-risk strategies
• New protocol launches
• Market volatility warnings
• TVL changes

Use the buttons below to customize your alerts!
        """
        
        keyboard = [
            [InlineKeyboardButton("📈 APY Threshold", callback_data="set_apy_threshold")],
            [InlineKeyboardButton("🛡️ Risk Threshold", callback_data="set_risk_threshold")],
            [InlineKeyboardButton("💰 TVL Threshold", callback_data="set_tvl_threshold")],
            [InlineKeyboardButton("🆕 New Strategies", callback_data="toggle_new_strategies")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            alert_settings,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        settings_message = """
⚙️ **Genora Bot Settings**

**🔔 Notifications:**
• Strategy alerts
• Market updates
• Risk warnings

**📊 Display Options:**
• Chart format
• Number format
• Currency display

**🌐 Language:**
• English (default)
• Russian (coming soon)

**⏰ Timezone:**
• UTC (default)
• Custom timezone

Use the buttons below to configure your settings!
        """
        
        keyboard = [
            [InlineKeyboardButton("🔔 Notifications", callback_data="notification_settings")],
            [InlineKeyboardButton("📊 Display", callback_data="display_settings")],
            [InlineKeyboardButton("🌐 Language", callback_data="language_settings")],
            [InlineKeyboardButton("⏰ Timezone", callback_data="timezone_settings")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            settings_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def chart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chart command"""
        if not context.args:
            await update.message.reply_text(
                "📈 **Chart Command Usage:**\n\n"
                "`/chart [strategy_name]`\n\n"
                "Examples:\n"
                "• `/chart aave`\n"
                "• `/chart uniswap`\n"
                "• `/chart curve`\n\n"
                "Use /top to see available strategies!",
                parse_mode='Markdown'
            )
            return
        
        strategy_name = " ".join(context.args).lower()
        
        try:
            # Get strategies data
            latest_data = redis_client.get("strategies:latest")
            if not latest_data:
                await update.message.reply_text(
                    "⚠️ No strategies data available.\n"
                    "Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            data = json.loads(latest_data)
            strategies = data.get("items", [])
            
            # Find matching strategies
            matching_strategies = [
                s for s in strategies 
                if strategy_name in s.get("name", "").lower() or 
                   strategy_name in s.get("protocol", "").lower()
            ]
            
            if not matching_strategies:
                await update.message.reply_text(
                    f"❌ No strategies found for '{strategy_name}'.\n\n"
                    "Try searching for:\n"
                    "• Protocol names (aave, uniswap, curve)\n"
                    "• Strategy names\n"
                    "• Chain names\n\n"
                    "Use /top to see available strategies!",
                    parse_mode='Markdown'
                )
                return
            
            # Show matching strategies
            message = f"📈 **Found {len(matching_strategies)} strategies for '{strategy_name}'**\n\n"
            
            for i, strategy in enumerate(matching_strategies[:5], 1):
                name = strategy.get("name", "Unknown")
                protocol = strategy.get("protocol", "Unknown")
                apy = strategy.get("apy", 0)
                tvl = strategy.get("tvl_usd", 0)
                
                if tvl >= 1000000:
                    tvl_str = f"${tvl/1000000:.1f}M"
                elif tvl >= 1000:
                    tvl_str = f"${tvl/1000:.0f}K"
                else:
                    tvl_str = f"${tvl:.0f}"
                
                message += f"""
**{i}. {name}**
• Protocol: {protocol}
• APY: {apy:.2f}%
• TVL: {tvl_str}
"""
            
            if len(matching_strategies) > 5:
                message += f"\n... and {len(matching_strategies) - 5} more strategies"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in chart command: {e}")
            await update.message.reply_text(
                "❌ Error generating chart.\n"
                "Please try again later.",
                parse_mode='Markdown'
            )
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        if not context.args:
            await update.message.reply_text(
                "🔍 **Search Command Usage:**\n\n"
                "`/search [query]`\n\n"
                "Examples:\n"
                "• `/search high apy`\n"
                "• `/search low risk`\n"
                "• `/search ethereum`\n"
                "• `/search aave`\n\n"
                "Search by protocol, chain, or strategy type!",
                parse_mode='Markdown'
            )
            return
        
        query = " ".join(context.args).lower()
        
        try:
            # Get strategies data
            latest_data = redis_client.get("strategies:latest")
            if not latest_data:
                await update.message.reply_text(
                    "⚠️ No strategies data available.\n"
                    "Please try again later.",
                    parse_mode='Markdown'
                )
                return
            
            data = json.loads(latest_data)
            strategies = data.get("items", [])
            
            # Search strategies
            matching_strategies = []
            for strategy in strategies:
                searchable_text = f"{strategy.get('name', '')} {strategy.get('protocol', '')} {strategy.get('chain', '')} {strategy.get('category', '')}".lower()
                if query in searchable_text:
                    matching_strategies.append(strategy)
            
            if not matching_strategies:
                await update.message.reply_text(
                    f"❌ No strategies found for '{query}'.\n\n"
                    "Try different keywords:\n"
                    "• Protocol names\n"
                    "• Chain names\n"
                    "• Strategy types\n"
                    "• Risk levels",
                    parse_mode='Markdown'
                )
                return
            
            # Show search results
            message = f"🔍 **Found {len(matching_strategies)} strategies for '{query}'**\n\n"
            
            for i, strategy in enumerate(matching_strategies[:5], 1):
                name = strategy.get("name", "Unknown")
                protocol = strategy.get("protocol", "Unknown")
                chain = strategy.get("chain", "Unknown")
                apy = strategy.get("apy", 0)
                risk = strategy.get("risk_score", 5)
                
                risk_emoji = "🟢" if risk < 3 else "🟡" if risk < 6 else "🔴"
                
                message += f"""
**{i}. {name}**
• Protocol: {protocol}
• Chain: {chain}
• APY: {apy:.2f}%
• Risk: {risk_emoji} {risk}/10
"""
            
            if len(matching_strategies) > 5:
                message += f"\n... and {len(matching_strategies) - 5} more strategies"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in search command: {e}")
            await update.message.reply_text(
                "❌ Error searching strategies.\n"
                "Please try again later.",
                parse_mode='Markdown'
            )
    
    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command"""
        user_id = update.effective_user.id
        
        # Get user's portfolio from Redis
        portfolio_key = f"portfolio:{user_id}"
        portfolio_data = redis_client.get(portfolio_key)
        
        if not portfolio_data:
            await update.message.reply_text(
                "📊 **Portfolio Tracking**\n\n"
                "You don't have a portfolio set up yet.\n\n"
                "To track your DeFi investments:\n"
                "1. Add strategies to your watchlist\n"
                "2. Set position sizes\n"
                "3. Monitor performance\n\n"
                "Coming soon! 🚀",
                parse_mode='Markdown'
            )
            return
        
        # Display portfolio (placeholder)
        await update.message.reply_text(
            "📊 **Your Portfolio**\n\n"
            "Portfolio tracking feature is coming soon!\n\n"
            "Features will include:\n"
            "• Position tracking\n"
            "• P&L monitoring\n"
            "• Risk analysis\n"
            "• Performance metrics\n\n"
            "Stay tuned! 🚀",
            parse_mode='Markdown'
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "top_strategies":
            await self.top_strategies_command(update, context)
        elif data == "subscribe":
            await self.subscribe_command(update, context)
        elif data == "settings":
            await self.settings_command(update, context)
        elif data == "market_overview":
            await self.status_command(update, context)
        elif data == "view_charts":
            await query.edit_message_text(
                "📈 **Chart Generation**\n\n"
                "Chart generation feature is coming soon!\n\n"
                "You'll be able to:\n"
                "• View APY trends\n"
                "• Compare strategies\n"
                "• Analyze risk metrics\n"
                "• Export data\n\n"
                "Stay tuned! 🚀",
                parse_mode='Markdown'
            )
        elif data == "search_strategies":
            await query.edit_message_text(
                "🔍 **Search Strategies**\n\n"
                "Use /search [query] to find strategies.\n\n"
                "Examples:\n"
                "• /search high apy\n"
                "• /search low risk\n"
                "• /search ethereum\n"
                "• /search aave",
                parse_mode='Markdown'
            )
        elif data == "alert_settings":
            await self.alerts_command(update, context)
        elif data == "main_menu":
            await self.start_command(update, context)
        else:
            await query.edit_message_text(
                "⚠️ Feature coming soon!\n\n"
                "This feature is under development.\n"
                "Stay tuned for updates! 🚀",
                parse_mode='Markdown'
            )
    
    async def send_alert(self, message: str, alert_type: str = "info"):
        """Send alert to all subscribers"""
        if not self.subscribers:
            return
        
        # Add alert type emoji
        emoji_map = {
            "high_apy": "🚀",
            "low_risk": "🛡️",
            "new_strategy": "🆕",
            "volatility": "⚠️",
            "info": "ℹ️"
        }
        
        emoji = emoji_map.get(alert_type, "ℹ️")
        formatted_message = f"{emoji} **Genora Alert**\n\n{message}"
        
        for user_id in self.subscribers:
            try:
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=formatted_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send alert to user {user_id}: {e}")
                # Remove invalid user from subscribers
                self.subscribers.discard(user_id)
                redis_client.srem("telegram_subscribers", user_id)
    
    async def monitor_strategies(self):
        """Monitor strategies and send alerts"""
        while True:
            try:
                # Get current strategies
                latest_data = redis_client.get("strategies:latest")
                if not latest_data:
                    await asyncio.sleep(60)
                    continue
                
                data = json.loads(latest_data)
                strategies = data.get("items", [])
                
                if not strategies:
                    await asyncio.sleep(60)
                    continue
                
                # Check for high APY strategies
                high_apy_strategies = [
                    s for s in strategies 
                    if s.get("apy", 0) > self.alert_thresholds["high_apy"]
                ]
                
                if high_apy_strategies:
                    message = f"🚀 **High APY Alert!**\n\n"
                    for strategy in high_apy_strategies[:3]:
                        name = strategy.get("name", "Unknown")
                        apy = strategy.get("apy", 0)
                        protocol = strategy.get("protocol", "Unknown")
                        message += f"• {name} ({protocol}): {apy:.2f}% APY\n"
                    
                    await self.send_alert(message, "high_apy")
                
                # Check for low risk strategies
                low_risk_strategies = [
                    s for s in strategies 
                    if s.get("risk_score", 5) < self.alert_thresholds["low_risk"]
                ]
                
                if low_risk_strategies:
                    message = f"🛡️ **Low Risk Alert!**\n\n"
                    for strategy in low_risk_strategies[:3]:
                        name = strategy.get("name", "Unknown")
                        risk = strategy.get("risk_score", 5)
                        protocol = strategy.get("protocol", "Unknown")
                        message += f"• {name} ({protocol}): Risk {risk}/10\n"
                    
                    await self.send_alert(message, "low_risk")
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in strategy monitoring: {e}")
                await asyncio.sleep(60)
    
    async def run(self):
        """Run the bot"""
        # Load existing subscribers
        existing_subscribers = redis_client.smembers("telegram_subscribers")
        self.subscribers.update(int(user_id) for user_id in existing_subscribers)
        
        # Start monitoring task
        monitoring_task = asyncio.create_task(self.monitor_strategies())
        
        try:
            # Start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Genora Telegram Bot started successfully!")
            
            # Keep running
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            monitoring_task.cancel()
            await self.application.stop()

# Main function
async def main():
    """Main entry point"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    bot = GenoraTelegramBot(token)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
