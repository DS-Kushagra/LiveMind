"""
📡 Real-Time Data Sources for LiveMind
All using FREE APIs with generous limits!
"""

import feedparser
import praw
import yfinance as yf
import pyowm
import requests
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger("data_sources")

class NewsDataSource:
    """📰 Free News Data Source using RSS feeds"""
    
    def __init__(self):
        self.rss_feeds = [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss", 
            "https://www.reddit.com/r/worldnews/.rss",
            "https://techcrunch.com/feed/",
            "https://www.wired.com/feed/rss"
        ]
    
    async def fetch_latest_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch latest news from RSS feeds"""
        try:
            logger.info("📰 Fetching latest news...")
            news_items = []
            
            for feed_url in self.rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:limit//len(self.rss_feeds)]:
                        news_item = {
                            "title": entry.get('title', ''),
                            "summary": entry.get('summary', ''),
                            "link": entry.get('link', ''),
                            "published": entry.get('published', ''),
                            "source": feed.feed.get('title', 'RSS Feed'),
                            "timestamp": datetime.now().isoformat(),
                            "content_type": "news"
                        }
                        news_items.append(news_item)
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch from {feed_url}: {e}")
                    continue
            
            logger.info(f"📰 Fetched {len(news_items)} news articles")
            return news_items[:limit]
            
        except Exception as e:
            logger.error(f"❌ News fetch failed: {e}")
            return []

class RedditDataSource:
    """🔥 Reddit Data Source (Free API)"""
    
    def __init__(self):
        self.reddit = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Reddit API client"""
        if self.initialized:
            return
        
        try:
            if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
                logger.warning("⚠️ Reddit API credentials not configured")
                self.initialized = True
                return
            
            self.reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent="LiveMind:v1.0 (by /u/livemind)"
            )
            
            self.initialized = True
            logger.info("✅ Reddit API initialized")
            
        except Exception as e:
            logger.error(f"❌ Reddit initialization failed: {e}")
            self.initialized = True
    
    async def fetch_trending_posts(
        self,
        subreddit: str = "all",
        limit: int = 10,
        time_filter: str = "hour"
    ) -> List[Dict[str, Any]]:
        """Fetch trending posts from Reddit"""
        await self.initialize()
        
        if not self.reddit:
            return []
        
        try:
            logger.info(f"🔥 Fetching trending posts from r/{subreddit}")
            posts = []
            
            subreddit_obj = self.reddit.subreddit(subreddit)
            for post in subreddit_obj.hot(limit=limit):
                post_data = {
                    "title": post.title,
                    "content": post.selftext[:500] if post.selftext else "",
                    "score": post.score,
                    "comments": post.num_comments,
                    "url": post.url,
                    "subreddit": post.subreddit.display_name,
                    "author": str(post.author) if post.author else "deleted",
                    "created_utc": datetime.fromtimestamp(post.created_utc).isoformat(),
                    "timestamp": datetime.now().isoformat(),
                    "content_type": "reddit_post"
                }
                posts.append(post_data)
            
            logger.info(f"🔥 Fetched {len(posts)} Reddit posts")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Reddit fetch failed: {e}")
            return []

class FinanceDataSource:
    """💰 Financial Data Source (Free APIs)"""
    
    def __init__(self):
        self.owm = None
        
    async def fetch_stock_data(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch stock data using Yahoo Finance (FREE!)"""
        if not symbols:
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]  # Default popular stocks
        
        try:
            logger.info(f"💰 Fetching stock data for {symbols}")
            stock_data = []
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d", interval="1h")
                    info = ticker.info
                    
                    if not hist.empty:
                        latest = hist.iloc[-1]
                        stock_info = {
                            "symbol": symbol,
                            "price": float(latest['Close']),
                            "change": float(latest['Close'] - hist.iloc[0]['Open']),
                            "change_percent": float((latest['Close'] - hist.iloc[0]['Open']) / hist.iloc[0]['Open'] * 100),
                            "volume": int(latest['Volume']),
                            "market_cap": info.get('marketCap', 0),
                            "company_name": info.get('longName', symbol),
                            "timestamp": datetime.now().isoformat(),
                            "content_type": "stock_data"
                        }
                        stock_data.append(stock_info)
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch data for {symbol}: {e}")
                    continue
            
            logger.info(f"💰 Fetched data for {len(stock_data)} stocks")
            return stock_data
            
        except Exception as e:
            logger.error(f"❌ Stock data fetch failed: {e}")
            return []

class WeatherDataSource:
    """🌤️ Weather Data Source (Free API)"""
    
    def __init__(self):
        self.owm = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize OpenWeatherMap API"""
        if self.initialized:
            return
        
        try:
            if not settings.OPENWEATHER_API_KEY:
                logger.warning("⚠️ OpenWeatherMap API key not configured")
                self.initialized = True
                return
            
            self.owm = pyowm.OWM(settings.OPENWEATHER_API_KEY)
            self.initialized = True
            logger.info("✅ Weather API initialized")
            
        except Exception as e:
            logger.error(f"❌ Weather API initialization failed: {e}")
            self.initialized = True
    
    async def fetch_weather_data(self, cities: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch current weather data"""
        await self.initialize()
        
        if not self.owm:
            return []
        
        if not cities:
            cities = ["New York", "London", "Tokyo", "Mumbai", "Sydney"]
        
        try:
            logger.info(f"🌤️ Fetching weather for {cities}")
            weather_data = []
            
            mgr = self.owm.weather_manager()
            
            for city in cities:
                try:
                    observation = mgr.weather_at_place(city)
                    weather = observation.weather
                    
                    weather_info = {
                        "city": city,
                        "temperature": weather.temperature('celsius')['temp'],
                        "description": weather.detailed_status,
                        "humidity": weather.humidity,
                        "pressure": weather.pressure['press'],
                        "wind_speed": weather.wind().get('speed', 0),
                        "visibility": weather.visibility_distance,
                        "timestamp": datetime.now().isoformat(),
                        "content_type": "weather_data"
                    }
                    weather_data.append(weather_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch weather for {city}: {e}")
                    continue
            
            logger.info(f"🌤️ Fetched weather for {len(weather_data)} cities")
            return weather_data
            
        except Exception as e:
            logger.error(f"❌ Weather fetch failed: {e}")
            return []

class DataSourceManager:
    """🎯 Central manager for all data sources"""
    
    def __init__(self):
        self.news_source = NewsDataSource()
        self.reddit_source = RedditDataSource()
        self.finance_source = FinanceDataSource()
        self.weather_source = WeatherDataSource()
    
    async def initialize_all(self):
        """Initialize all data sources"""
        logger.info("🚀 Initializing all data sources...")
        await asyncio.gather(
            self.reddit_source.initialize(),
            self.weather_source.initialize(),
            return_exceptions=True
        )
        logger.info("✅ Data sources initialized")
    
    async def fetch_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch data from all sources"""
        logger.info("📡 Fetching data from all sources...")
        
        # Fetch data concurrently for speed
        results = await asyncio.gather(
            self.news_source.fetch_latest_news(limit=5),
            self.reddit_source.fetch_trending_posts(limit=5),
            self.finance_source.fetch_stock_data(),
            self.weather_source.fetch_weather_data(),
            return_exceptions=True
        )
        
        return {
            "news": results[0] if not isinstance(results[0], Exception) else [],
            "reddit": results[1] if not isinstance(results[1], Exception) else [],
            "finance": results[2] if not isinstance(results[2], Exception) else [],
            "weather": results[3] if not isinstance(results[3], Exception) else []
        }
    
    async def fetch_by_source(self, source_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Fetch data from specific source"""
        if source_name == "news":
            return await self.news_source.fetch_latest_news(**kwargs)
        elif source_name == "reddit":
            return await self.reddit_source.fetch_trending_posts(**kwargs)
        elif source_name == "finance":
            return await self.finance_source.fetch_stock_data(**kwargs)
        elif source_name == "weather":
            return await self.weather_source.fetch_weather_data(**kwargs)
        else:
            logger.warning(f"Unknown source: {source_name}")
            return []

# Global instance
data_source_manager = DataSourceManager()
