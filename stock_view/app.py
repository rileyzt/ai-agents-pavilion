import gradio as gr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple
import asyncio
import aiohttp
from dataclasses import dataclass
import re

# Enhanced imports for current news and discussions
import praw
import time
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

@dataclass
class StockAnalysis:
    """Data class to hold comprehensive stock analysis"""
    symbol: str
    company_name: str
    fundamentals: Dict
    trading_stats: Dict
    financial_health: Dict
    risk_metrics: Dict
    dividend_info: Dict
    news_links: List[str]
    reddit_links: List[str]
    twitter_links: List[str]
    financial_news: List[str]  # New field for trusted financial news

class StockAnalysisAgent:
    def __init__(self):
        # You'll need to add your API keys here
        self.alpha_vantage_key = "YOUR_ALPHA_VANTAGE_KEY"
        self.news_api_key = "YOUR_NEWS_API_KEY"
        self.reddit_client_id = "YOUR_REDDIT_CLIENT_ID"
        self.reddit_client_secret = "YOUR_REDDIT_CLIENT_SECRET"
        
        # Enhanced Reddit client initialization for latest posts
        try:
            self.reddit = praw.Reddit(
                client_id="dummy",
                client_secret=None,
                user_agent="StockAnalysis:v1.0",
                check_for_async=False
            )
            self.reddit.read_only = True
        except:
            self.reddit = None

    def get_stock_symbol(self, user_input: str) -> str:
        """Convert company name to stock symbol or validate symbol"""
        user_input = user_input.strip().upper()

        name_to_symbol = {
            'APPLE': 'AAPL',
            'MICROSOFT': 'MSFT',
            'GOOGLE': 'GOOGL',
            'ALPHABET': 'GOOGL',
            'AMAZON': 'AMZN',
            'TESLA': 'TSLA',
            'META': 'META',
            'FACEBOOK': 'META',
            'NETFLIX': 'NFLX',
            'NVIDIA': 'NVDA',
            'INTEL': 'INTC',
            'IBM': 'IBM',
            'ORACLE': 'ORCL',
            'SALESFORCE': 'CRM',

            'RELIANCE': 'RELIANCE.NS',
            'RELIANCE POWER': 'RPOWER.NS',
            'TATA MOTORS': 'TATAMOTORS.NS',
            'TATA': 'TATAMOTORS.NS',
            'INFOSYS': 'INFY.NS',
            'TCS': 'TCS.NS',
            'WIPRO': 'WIPRO.NS',
            'HDFC BANK': 'HDFCBANK.NS',
            'ICICI BANK': 'ICICIBANK.NS',
            'SBI': 'SBIN.NS',
            'BHARTI AIRTEL': 'BHARTIARTL.NS',
            'ITC': 'ITC.NS',
            'MARUTI': 'MARUTI.NS',
            'BAJAJ FINANCE': 'BAJFINANCE.NS'
        }

        for name, symbol in name_to_symbol.items():
            if name in user_input:
                return symbol

        if len(user_input) <= 8 and user_input.replace('.', '').isalpha():
            if not any(suffix in user_input for suffix in ['.NS', '.BO', '.L', '.TO']):
                test_symbols = [user_input, f"{user_input}.NS", f"{user_input}.BO"]
                for test_symbol in test_symbols:
                    try:
                        stock = yf.Ticker(test_symbol)
                        info = stock.info
                        if info and 'symbol' in info and info.get('regularMarketPrice') is not None:
                            return test_symbol
                    except:
                        continue
            return user_input

        return user_input

    def get_fundamentals(self, symbol: str) -> Dict:
        """Get fundamental analysis data"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            fundamentals = {
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'peg_ratio': info.get('pegRatio', 'N/A'),
                'price_to_book': info.get('priceToBook', 'N/A'),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 'N/A'),
                'enterprise_value': info.get('enterpriseValue', 'N/A'),
                'ev_to_revenue': info.get('enterpriseToRevenue', 'N/A'),
                'ev_to_ebitda': info.get('enterpriseToEbitda', 'N/A'),
                'profit_margin': info.get('profitMargins', 'N/A'),
                'operating_margin': info.get('operatingMargins', 'N/A'),
                'return_on_equity': info.get('returnOnEquity', 'N/A'),
                'return_on_assets': info.get('returnOnAssets', 'N/A'),
                'book_value': info.get('bookValue', 'N/A'),
                'earnings_growth': info.get('earningsGrowth', 'N/A'),
                'revenue_growth': info.get('revenueGrowth', 'N/A')
            }

            return fundamentals
        except Exception as e:
            return {'error': f'Failed to get fundamentals: {str(e)}'}

    def get_trading_stats(self, symbol: str) -> Dict:
        """Get recent trading session statistics"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="5d")

            if not hist.empty:
                latest_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else latest_price
                volume = hist['Volume'].iloc[-1]
                avg_volume = hist['Volume'].mean()
            else:
                latest_price = info.get('currentPrice', 'N/A')
                prev_close = info.get('previousClose', 'N/A')
                volume = info.get('volume', 'N/A')
                avg_volume = info.get('averageVolume', 'N/A')

            trading_stats = {
                'current_price': latest_price,
                'previous_close': prev_close,
                'day_change': (latest_price - prev_close) if isinstance(latest_price, (int, float)) and isinstance(prev_close, (int, float)) else 'N/A',
                'day_change_percent': ((latest_price - prev_close) / prev_close * 100) if isinstance(latest_price, (int, float)) and isinstance(prev_close, (int, float)) else 'N/A',
                'volume': volume,
                'avg_volume': avg_volume,
                'day_high': info.get('dayHigh', 'N/A'),
                'day_low': info.get('dayLow', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'shares_outstanding': info.get('sharesOutstanding', 'N/A')
            }

            return trading_stats
        except Exception as e:
            return {'error': f'Failed to get trading stats: {str(e)}'}

    def get_financial_health(self, symbol: str) -> Dict:
        """Get financial health metrics"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            financial_health = {
                'total_cash': info.get('totalCash', 'N/A'),
                'total_debt': info.get('totalDebt', 'N/A'),
                'debt_to_equity': info.get('debtToEquity', 'N/A'),
                'current_ratio': info.get('currentRatio', 'N/A'),
                'quick_ratio': info.get('quickRatio', 'N/A'),
                'cash_per_share': info.get('totalCashPerShare', 'N/A'),
                'revenue_ttm': info.get('totalRevenue', 'N/A'),
                'gross_profit': info.get('grossProfits', 'N/A'),
                'ebitda': info.get('ebitda', 'N/A'),
                'net_income': info.get('netIncomeToCommon', 'N/A'),
                'free_cash_flow': info.get('freeCashflow', 'N/A'),
                'operating_cash_flow': info.get('operatingCashflow', 'N/A')
            }

            return financial_health
        except Exception as e:
            return {'error': f'Failed to get financial health: {str(e)}'}

    def get_risk_metrics(self, symbol: str) -> Dict:
        """Calculate risk management metrics"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")
            info = stock.info

            if not hist.empty:
                returns = hist['Close'].pct_change().dropna()
                volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
                max_drawdown = self.calculate_max_drawdown(hist['Close'])
            else:
                volatility = 'N/A'
                max_drawdown = 'N/A'

            risk_metrics = {
                'beta': info.get('beta', 'N/A'),
                'volatility_1y': volatility,
                'max_drawdown_1y': max_drawdown,
                'analyst_rating': info.get('recommendationKey', 'N/A'),
                'target_high_price': info.get('targetHighPrice', 'N/A'),
                'target_low_price': info.get('targetLowPrice', 'N/A'),
                'target_mean_price': info.get('targetMeanPrice', 'N/A'),
                'number_of_analysts': info.get('numberOfAnalystOpinions', 'N/A')
            }

            return risk_metrics
        except Exception as e:
            return {'error': f'Failed to get risk metrics: {str(e)}'}

    def calculate_max_drawdown(self, prices) -> float:
        """Calculate maximum drawdown"""
        try:
            peak = prices.expanding().max()
            drawdown = (prices - peak) / peak
            return drawdown.min()
        except:
            return 'N/A'

    def get_dividend_info(self, symbol: str) -> Dict:
        """Get dividend policy information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            dividend_info = {
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'dividend_rate': info.get('dividendRate', 'N/A'),
                'ex_dividend_date': info.get('exDividendDate', 'N/A'),
                'payout_ratio': info.get('payoutRatio', 'N/A'),
                'five_year_avg_yield': info.get('fiveYearAvgDividendYield', 'N/A'),
                'dividend_growth_rate': 'N/A'
            }

            return dividend_info
        except Exception as e:
            return {'error': f'Failed to get dividend info: {str(e)}'}

    def search_news_articles(self, symbol: str, company_name: str) -> List[str]:
        """Search for latest news articles about the stock"""
        try:
            # Using yfinance news (free alternative)
            stock = yf.Ticker(symbol)
            news = stock.news

            news_links = []
            for article in news[:5]:  # Get top 5 articles
                if 'link' in article:
                    news_links.append(article['link'])

            return news_links
        except Exception as e:
            return [f"Error fetching news: {str(e)}"]

    def search_reddit_discussions_enhanced(self, symbol: str, company_name: str) -> List[str]:
        """Enhanced Reddit search for LATEST and TRENDING posts"""
        if not self.reddit:
            return self._fallback_reddit_links(symbol)
            
        try:
            # Generate targeted keywords
            keywords = []
            base_symbol = symbol.replace('.NS', '').replace('.BO', '')
            keywords.append(base_symbol)
            if company_name:
                keywords.append(company_name)
            keywords.append(f"${base_symbol}")
            
            discussions = []
            
            # Define target subreddits with priority for trending content
            if '.NS' in symbol or '.BO' in symbol:
                target_subreddits = ['IndiaInvestments', 'IndianStockMarket', 'investing', 'stocks']
            else:
                target_subreddits = ['stocks', 'wallstreetbets', 'investing', 'SecurityAnalysis', 'StockMarket']
                
            request_count = 0
            max_requests = 6
            current_time = datetime.now()
            
            for subreddit_name in target_subreddits:
                if request_count >= max_requests:
                    break
                    
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for posts from last 24 hours first (trending/hot)
                    for search_term in keywords[:2]:  # Use top 2 keywords
                        if request_count >= max_requests:
                            break
                            
                        # Get hot posts first (trending)
                        hot_submissions = list(subreddit.search(search_term, limit=3, sort='hot', time_filter='day'))
                        request_count += 1
                        
                        for submission in hot_submissions:
                            # Check if post is from last 48 hours
                            post_time = datetime.fromtimestamp(submission.created_utc)
                            hours_ago = (current_time - post_time).total_seconds() / 3600
                            
                            if hours_ago <= 48:  # Within 48 hours
                                title = submission.title[:80] + '...' if len(submission.title) > 80 else submission.title
                                time_str = f"{int(hours_ago)}h ago" if hours_ago < 24 else f"{int(hours_ago/24)}d ago"
                                discussions.append(f"🔥 **{title}** (r/{subreddit_name}) - {submission.score} upvotes - {time_str} - https://reddit.com{submission.permalink}")
                        
                        time.sleep(0.1)  # Small delay
                        break  # Only use first keyword per subreddit to stay within limits
                    
                except Exception as e:
                    continue
                    
            # If we don't have enough recent posts, get some from 'new' sorted
            if len(discussions) < 3:
                try:
                    for subreddit_name in target_subreddits[:2]:  # Check top 2 subreddits
                        if request_count >= max_requests:
                            break
                            
                        subreddit = self.reddit.subreddit(subreddit_name)
                        main_keyword = company_name if company_name else base_symbol
                        
                        new_submissions = list(subreddit.search(main_keyword, limit=2, sort='new', time_filter='week'))
                        request_count += 1
                        
                        for submission in new_submissions:
                            post_time = datetime.fromtimestamp(submission.created_utc)
                            hours_ago = (current_time - post_time).total_seconds() / 3600
                            
                            if hours_ago <= 168:  # Within 1 week
                                title = submission.title[:80] + '...' if len(submission.title) > 80 else submission.title
                                if hours_ago < 24:
                                    time_str = f"{int(hours_ago)}h ago"
                                else:
                                    time_str = f"{int(hours_ago/24)}d ago"
                                discussions.append(f"📝 **{title}** (r/{subreddit_name}) - {submission.score} upvotes - {time_str} - https://reddit.com{submission.permalink}")
                        
                        time.sleep(0.1)
                        
                except:
                    pass
                    
            return discussions[:8] if discussions else self._fallback_reddit_links(symbol)
            
        except Exception as e:
            return self._fallback_reddit_links(symbol)

    def _fallback_reddit_links(self, symbol: str) -> List[str]:
        """Fallback Reddit search URLs optimized for latest posts"""
        base_symbol = symbol.replace('.NS', '').replace('.BO', '')
        return [
            f"🔥 **Hot discussions today** - https://www.reddit.com/r/stocks/search/?q={base_symbol}&restrict_sr=1&sort=hot&t=day",
            f"📈 **Recent posts** - https://www.reddit.com/r/investing/search/?q={base_symbol}&restrict_sr=1&sort=new&t=week",
            f"💎 **WSB mentions** - https://www.reddit.com/r/wallstreetbets/search/?q={base_symbol}&restrict_sr=1&sort=hot&t=day",
            f"🎯 **Today's discussions** - https://www.reddit.com/r/StockMarket/search/?q={base_symbol}&restrict_sr=1&sort=hot&t=day"
        ]

    def search_twitter_mentions_enhanced(self, symbol: str, company_name: str) -> List[str]:
        """Enhanced Twitter search for CURRENT trending mentions"""
        try:
            base_symbol = symbol.replace('.NS', '').replace('.BO', '')
            
            # Create more targeted search queries for current discussions
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            search_queries = [
                f"${base_symbol} since:{current_date}",  # Today's mentions
                f"{company_name} stock breaking" if company_name else f"{base_symbol} breaking",
                f"${base_symbol} earnings OR results OR news",
                f"{company_name} buy OR sell OR hold" if company_name else f"{base_symbol} analysis",
                f"${base_symbol} price target OR upgrade OR downgrade",
            ]
            
            twitter_links = []
            for i, query in enumerate(search_queries[:5]):
                encoded_query = quote(query)
                if i == 0:
                    twitter_links.append(f"🔥 **Today's ${base_symbol} mentions** - https://twitter.com/search?q={encoded_query}&src=typed_query&f=live")
                elif "breaking" in query:
                    twitter_links.append(f"⚡ **Breaking news** - https://twitter.com/search?q={encoded_query}&src=typed_query&f=live")
                elif "earnings" in query:
                    twitter_links.append(f"📊 **Earnings & Results** - https://twitter.com/search?q={encoded_query}&src=typed_query&f=live")
                elif "buy OR sell" in query:
                    twitter_links.append(f"💭 **Trading sentiment** - https://twitter.com/search?q={encoded_query}&src=typed_query&f=live")
                else:
                    twitter_links.append(f"🎯 **Price targets** - https://twitter.com/search?q={encoded_query}&src=typed_query&f=live")
                
            return twitter_links
            
        except Exception as e:
            return [f"Error fetching Twitter links: {str(e)}"]

    def search_trusted_financial_news(self, symbol: str, company_name: str) -> List[str]:
        """NEW: Search trusted financial news sources for latest stories (max 2 days old)"""
        try:
            base_symbol = symbol.replace('.NS', '').replace('.BO', '')
            current_date = datetime.now()
            two_days_ago = (current_date - timedelta(days=2)).strftime("%Y-%m-%d")
            
            financial_news = []
            
            # Trusted financial news sources with direct search URLs
            news_sources = [
                {
                    "name": "Yahoo Finance",
                    "url": f"https://finance.yahoo.com/quote/{symbol}/news/",
                    "description": f"Latest {base_symbol} news from Yahoo Finance"
                },
                {
                    "name": "MarketWatch", 
                    "url": f"https://www.marketwatch.com/investing/stock/{base_symbol.lower()}",
                    "description": f"MarketWatch analysis for {base_symbol}"
                },
                {
                    "name": "Seeking Alpha",
                    "url": f"https://seekingalpha.com/symbol/{base_symbol}/news",
                    "description": f"Seeking Alpha latest articles on {base_symbol}"
                },
                {
                    "name": "Bloomberg",
                    "url": f"https://www.bloomberg.com/quote/{base_symbol}:US",
                    "description": f"Bloomberg coverage of {base_symbol}"
                },
                {
                    "name": "Reuters",
                    "url": f"https://www.reuters.com/companies/{base_symbol}.O",
                    "description": f"Reuters business news for {base_symbol}"
                },
                {
                    "name": "CNBC",
                    "url": f"https://www.cnbc.com/quotes/{base_symbol}",
                    "description": f"CNBC latest on {base_symbol}"
                }
            ]
            
            # For Indian stocks, add Indian financial news sources
            if '.NS' in symbol or '.BO' in symbol:
                indian_sources = [
                    {
                        "name": "Economic Times",
                        "url": f"https://economictimes.indiatimes.com/markets/stocks/news",
                        "description": f"Economic Times coverage of {base_symbol}"
                    },
                    {
                        "name": "Moneycontrol",
                        "url": f"https://www.moneycontrol.com/india/stockpricequote/{base_symbol}",
                        "description": f"Moneycontrol analysis for {base_symbol}"
                    },
                    {
                        "name": "Business Standard",
                        "url": f"https://www.business-standard.com/search?q={base_symbol}",
                        "description": f"Business Standard news on {base_symbol}"
                    }
                ]
                news_sources.extend(indian_sources)
            
            # Format the trusted sources
            for source in news_sources[:6]:  # Limit to top 6 sources
                financial_news.append(f"📰 **{source['description']}** - {source['url']}")
            
            # Add Google News search for recent articles
            company_search = company_name if company_name else base_symbol
            google_news_url = f"https://news.google.com/search?q={quote(company_search + ' stock news')}&hl=en-US&gl=US&ceid=US:en"
            financial_news.append(f"🔍 **Google News: Latest {company_search} stories** - {google_news_url}")
            
            return financial_news
            
        except Exception as e:
            return [f"Error fetching financial news: {str(e)}"]

    def search_reddit_discussions(self, symbol: str) -> List[str]:
        """Original Reddit search method - kept for compatibility"""
        try:
            reddit_links = [
                f"https://www.reddit.com/r/investing/search/?q={symbol}&restrict_sr=1&sort=new",
                f"https://www.reddit.com/r/stocks/search/?q={symbol}&restrict_sr=1&sort=new",
                f"https://www.reddit.com/r/SecurityAnalysis/search/?q={symbol}&restrict_sr=1&sort=new",
                f"https://www.reddit.com/r/ValueInvesting/search/?q={symbol}&restrict_sr=1&sort=new",
                f"https://www.reddit.com/r/StockMarket/search/?q={symbol}&restrict_sr=1&sort=new"
            ]
            return reddit_links
        except Exception as e:
            return [f"Error fetching Reddit links: {str(e)}"]

    def search_twitter_mentions(self, symbol: str) -> List[str]:
        """Original Twitter search method - kept for compatibility"""
        try:
            twitter_links = [
                f"https://twitter.com/search?q=${symbol}&src=typed_query&f=live",
                f"https://twitter.com/search?q={symbol}%20stock&src=typed_query&f=live",
                f"https://twitter.com/search?q={symbol}%20earnings&src=typed_query&f=live",
                f"https://twitter.com/search?q={symbol}%20analysis&src=typed_query&f=live"
            ]
            return twitter_links
        except Exception as e:
            return [f"Error fetching Twitter links: {str(e)}"]

    def format_analysis_report(self, analysis: StockAnalysis) -> str:
        """Format the complete analysis into a readable report"""

        def format_value(value, is_currency=True, decimal_places=2):
            if value == 'N/A' or value is None or value == '':
                return 'N/A'

            try:
                if isinstance(value, str):
                    clean_value = re.sub(r'[^\d.-]', '', str(value))
                    if clean_value and clean_value != '-':
                        value = float(clean_value)
                    else:
                        return 'N/A'

                if isinstance(value, (int, float)):
                    if is_currency:
                        if abs(value) > 1000000000:
                            return f"${value/1000000000:.{decimal_places}f}B"
                        elif abs(value) > 1000000:
                            return f"${value/1000000:.{decimal_places}f}M"
                        elif abs(value) > 1000:
                            return f"${value/1000:.{decimal_places}f}K"
                        else:
                            return f"${value:.{decimal_places}f}"
                    else:
                        return f"{value:.{decimal_places}f}"
                else:
                    return str(value)
            except (ValueError, TypeError):
                return str(value) if value else 'N/A'

        report = f"""
# 📊 Stock Analysis Report: {analysis.company_name} ({analysis.symbol})

## 🔍 Fundamental Analysis
- **Market Cap**: {format_value(analysis.fundamentals.get('market_cap'))}
- **P/E Ratio**: {format_value(analysis.fundamentals.get('pe_ratio'), False)}
- **Forward P/E**: {format_value(analysis.fundamentals.get('forward_pe'), False)}
- **PEG Ratio**: {format_value(analysis.fundamentals.get('peg_ratio'), False)}
- **Price-to-Book**: {format_value(analysis.fundamentals.get('price_to_book'), False)}
- **Price-to-Sales**: {format_value(analysis.fundamentals.get('price_to_sales'), False)}
- **Enterprise Value**: {format_value(analysis.fundamentals.get('enterprise_value'))}
- **EV/Revenue**: {format_value(analysis.fundamentals.get('ev_to_revenue'), False)}
- **EV/EBITDA**: {format_value(analysis.fundamentals.get('ev_to_ebitda'), False)}

## 📈 Trading Statistics
- **Current Price**: {format_value(analysis.trading_stats.get('current_price'))}
- **Previous Close**: {format_value(analysis.trading_stats.get('previous_close'))}
- **Day Change**: {format_value(analysis.trading_stats.get('day_change'))} ({format_value(analysis.trading_stats.get('day_change_percent'), False)}%)
- **Volume**: {format_value(analysis.trading_stats.get('volume'), False, 0)}
- **Average Volume**: {format_value(analysis.trading_stats.get('avg_volume'), False, 0)}
- **Day Range**: {format_value(analysis.trading_stats.get('day_low'))} - {format_value(analysis.trading_stats.get('day_high'))}
- **52-Week Range**: {format_value(analysis.trading_stats.get('52_week_low'))} - {format_value(analysis.trading_stats.get('52_week_high'))}
- **Beta**: {format_value(analysis.trading_stats.get('beta'), False)}

## 💰 Financial Health
- **Total Cash**: {format_value(analysis.financial_health.get('total_cash'))}
- **Total Debt**: {format_value(analysis.financial_health.get('total_debt'))}
- **Debt-to-Equity**: {format_value(analysis.financial_health.get('debt_to_equity'), False)}
- **Current Ratio**: {format_value(analysis.financial_health.get('current_ratio'), False)}
- **Quick Ratio**: {format_value(analysis.financial_health.get('quick_ratio'), False)}
- **Revenue (TTM)**: {format_value(analysis.financial_health.get('revenue_ttm'))}
- **Gross Profit**: {format_value(analysis.financial_health.get('gross_profit'))}
- **EBITDA**: {format_value(analysis.financial_health.get('ebitda'))}
- **Free Cash Flow**: {format_value(analysis.financial_health.get('free_cash_flow'))}

## ⚠️ Risk Management
- **Beta**: {format_value(analysis.risk_metrics.get('beta'), False)}
- **1-Year Volatility**: {format_value(analysis.risk_metrics.get('volatility_1y'), False)}%
- **Max Drawdown (1Y)**: {format_value(analysis.risk_metrics.get('max_drawdown_1y'), False)}%
- **Analyst Rating**: {analysis.risk_metrics.get('analyst_rating', 'N/A')}
- **Price Targets**: {format_value(analysis.risk_metrics.get('target_low_price'))} - {format_value(analysis.risk_metrics.get('target_high_price'))} (Mean: {format_value(analysis.risk_metrics.get('target_mean_price'))})

## 💎 Dividend Policy
- **Dividend Yield**: {format_value(analysis.dividend_info.get('dividend_yield'), False)}%
- **Dividend Rate**: {format_value(analysis.dividend_info.get('dividend_rate'))}
- **Ex-Dividend Date**: {analysis.dividend_info.get('ex_dividend_date', 'N/A')}
- **Payout Ratio**: {format_value(analysis.dividend_info.get('payout_ratio'), False)}%
- **5-Year Avg Yield**: {format_value(analysis.dividend_info.get('five_year_avg_yield'), False)}%

## 📰 Latest News Articles
"""

        for i, link in enumerate(analysis.news_links[:5], 1):
            report += f"{i}. {link}\n"

        report += f"""
## 🏛️ Trusted Financial News Sources
"""

        for i, link in enumerate(analysis.financial_news[:8], 1):
            report += f"{i}. {link}\n"

        report += f"""
## 💬 Latest Reddit Discussions (Trending & Current)
"""

        for i, link in enumerate(analysis.reddit_links[:8], 1):
            report += f"{i}. {link}\n"

        report += f"""
## 🐦 Current Twitter Mentions & Trends
"""

        for i, link in enumerate(analysis.twitter_links[:6], 1):
            report += f"{i}. {link}\n"

        report += f"""
---
*Analysis generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Latest data and trending discussions*
"""

        return report

    def analyze_stock(self, user_input: str, progress=gr.Progress()) -> str:
        """Main function to perform comprehensive stock analysis with latest data"""

        if not user_input.strip():
            return "❌ Please enter a stock symbol or company name."

        progress(0.1, desc="Resolving stock symbol...")
        symbol = self.get_stock_symbol(user_input)

        try:

            stock = yf.Ticker(symbol)
            info = stock.info

            if not info or len(info) < 5:
                return f"❌ Could not find data for '{user_input}'. Please check the symbol.\n\n**Suggestions:**\n- For Indian stocks, try adding .NS (e.g., RELIANCE.NS)\n- For US stocks, use the ticker symbol (e.g., AAPL for Apple)\n- Check if the company is publicly traded"

            company_name = info.get('longName', info.get('shortName', symbol))

            progress(0.15, desc="Gathering fundamental data...")
            fundamentals = self.get_fundamentals(symbol)

            progress(0.3, desc="Analyzing trading statistics...")
            trading_stats = self.get_trading_stats(symbol)

            progress(0.45, desc="Evaluating financial health...")
            financial_health = self.get_financial_health(symbol)

            progress(0.55, desc="Calculating risk metrics...")
            risk_metrics = self.get_risk_metrics(symbol)

            progress(0.65, desc="Getting dividend information...")
            dividend_info = self.get_dividend_info(symbol)

            progress(0.75, desc="Searching for latest news...")
            news_links = self.search_news_articles(symbol, company_name)

            progress(0.8, desc="Gathering trusted financial news...")
            financial_news = self.search_trusted_financial_news(symbol, company_name)

            progress(0.9, desc="Finding trending Reddit discussions...")
            reddit_links = self.search_reddit_discussions_enhanced(symbol, company_name)

            progress(0.95, desc="Collecting current Twitter mentions...")
            twitter_links = self.search_twitter_mentions_enhanced(symbol, company_name)

            progress(1.0, desc="Generating comprehensive report...")

            # Create analysis object with new financial_news field
            analysis = StockAnalysis(
                symbol=symbol,
                company_name=company_name,
                fundamentals=fundamentals,
                trading_stats=trading_stats,
                financial_health=financial_health,
                risk_metrics=risk_metrics,
                dividend_info=dividend_info,
                news_links=news_links,
                reddit_links=reddit_links,
                twitter_links=twitter_links,
                financial_news=financial_news
            )

            return self.format_analysis_report(analysis)

        except Exception as e:
            return f"❌ Error analyzing '{user_input}': {str(e)}\n\n**Troubleshooting:**\n- Verify the stock symbol is correct\n- For Indian stocks, try adding .NS (e.g., RELIANCE.NS)\n- For other international stocks, try adding country suffix (.L for London, .TO for Toronto)\n- Check your internet connection"

def create_gradio_interface():
    """Create a chat-style interface similar to your second app"""
    
    agent = StockAnalysisAgent()
    
    def chat_analyze_stock(message, history):
        """Chat function that analyzes stock based on user message"""
        if not message.strip():
            return "Please enter a stock symbol or company name to analyze."
        
        # Extract stock symbol/name from the message
        # You could make this more sophisticated with NLP
        stock_input = message.strip()
        
        # Perform the analysis
        result = agent.analyze_stock(stock_input)
        return result
    
    # Create the interface using ChatInterface like your second app
    interface = gr.ChatInterface(
        chat_analyze_stock,
        type="messages",
        title="🤖 Stock Analysis AI Agent",
        description="Hi! I'm your AI Stock Analysis assistant. Just tell me any stock symbol (like TSLA, AAPL) or company name and I'll give you comprehensive analysis with latest news and trends!",
        theme=gr.themes.Soft(),
        examples=[
            "Analyze Tesla stock",
            "Tell me about AAPL",
            "What's the latest on Microsoft?",
            "RELIANCE.NS analysis",
            "Show me NVIDIA fundamentals",
            "Bitcoin related stocks"
        ]
    )
    
    return interface

# Launch configuration
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch()

