import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import os

# ============================================================
#  کلاس‌ها و توابع پایتون (همونی که با آرتین ساختید)
# ============================================================

class Iranian_market:
    """بازار ایران - قیمت طلا، دلار، تتر، بیت‌کوین، نفت، سکه، بورس"""
    
    def __init__(self):
        self.data = {}
        self.extraction_time = None
    
    def set(self):
        """دریافت قیمت‌ها از سایت‌های ایرانی"""
        # اینجا کد اصلی شما برای گرفتن قیمت‌ها
        # (برای تست با دیتای نمونه پر میکنم)
        self.data = {
            "gold 18": "160,852,000",
            "coin": "1,630,100,000",
            "stock market": "5,160,903",
            "Shekel of gold": "696,840,000",
            "dollar": "1,615,000",
            "Brent oil": "73.03",
            "Tether": "1,671,700",
            "Bitcoin": "61525.26",
            "extraction time": datetime.now().isoformat()
        }
        self.extraction_time = datetime.now()
        return self.data
    
    def get_currencies(self):
        """برگشت همه قیمت‌ها"""
        if not self.data:
            self.set()
        return self.data
    
    def search(self, query: str):
        """جستجو در قیمت‌ها"""
        if not self.data:
            self.set()
        results = {}
        for key, value in self.data.items():
            if query.lower() in key.lower():
                results[key] = value
        return results
    
    def search_time(self):
        """زمان آخرین بروزرسانی"""
        return self.extraction_time


class World_Market:
    """بازار جهانی - ارزهای دیجیتال، طلا، شاخص‌ها"""
    
    def __init__(self):
        self.data = []
        self.extraction_time = None
    
    def set(self):
        """دریافت قیمت‌ها از API جهانی"""
        # دیتای نمونه برای تست
        self.data = [
            {"BTCUSDT": {"price": "61,733.7", "change_24h": "-1.44%", "volume": "8.91B"}},
            {"ETHUSDT": {"price": "1,647.54", "change_24h": "-1.15%", "volume": "5.45B"}},
            {"SOLUSDT": {"price": "68.90", "change_24h": "-0.43%", "volume": "696.99M"}},
            {"DOGEUSDT": {"price": "0.07693", "change_24h": "-2.35%", "volume": "75.19M"}},
            {"XRPUSDT": {"price": "1.0806", "change_24h": "-1.55%", "volume": "119.09M"}},
            {"XAUUSDT": {"price": "3,992.79", "change_24h": "-1.89%", "volume": "223.45M"}},
        ]
        self.extraction_time = datetime.now()
        return self.data
    
    def get_currencies(self):
        if not self.data:
            self.set()
        return self.data
    
    def search(self, query: str, field: str = None):
        if not self.data:
            self.set()
        for item in self.data:
            for key, value in item.items():
                if query.lower() in key.lower():
                    if field == "price" and isinstance(value, dict):
                        return value.get("price")
                    return {key: value}
        return None


def Dollar_to_Rial(amount: float) -> float:
    """تبدیل دلار به ریال"""
    dollar_price = 1615000  # قیمت دلار
    return amount * dollar_price


def Rial_to_Dollar(amount: float) -> float:
    """تبدیل ریال به دلار"""
    dollar_price = 1615000
    return amount / dollar_price


def Tether_to_Rial(amount: float) -> float:
    """تبدیل تتر به ریال"""
    tether_price = 1671700
    return amount * tether_price


def Gold_to_Rial(amount: float) -> float:
    """تبدیل طلا به ریال (هر گرم)"""
    gold_price = 696840000  # هر گرم طلا
    return amount * gold_price


def analyst(market_class):
    """تحلیل بازار - تغییرات قیمت‌ها"""
    if isinstance(market_class, Iranian_market):
        data = market_class.get_currencies()
        return {
            "market": "Iran",
            "total_items": len(data),
            "last_update": data.get("extraction time"),
            "prices": data
        }
    elif isinstance(market_class, World_Market):
        data = market_class.get_currencies()
        return {
            "market": "World",
            "total_items": len(data),
            "last_update": market_class.extraction_time,
            "prices": data
        }
    return {"error": "market not recognized"}


def Read_price(price: int) -> str:
    """تبدیل عدد به حروف فارسی"""
    if price < 1000:
        return str(price)
    if price < 1000000:
        return f"{price // 1000:,} هزار"
    if price < 1000000000:
        return f"{price // 1000000:,} میلیون"
    return f"{price // 1000000000:,} میلیارد"


def export_to_csv_iran():
    """خروجی CSV بازار ایران"""
    data = Iranian_market().set()
    output = "currency,price,time\n"
    for key, value in data.items():
        output += f"{key},{value},{datetime.now().isoformat()}\n"
    return output


def export_to_csv_world():
    """خروجی CSV بازار جهانی"""
    data = World_Market().set()
    output = "currency,price,time\n"
    for item in data:
        for key, value in item.items():
            if isinstance(value, dict):
                price = value.get("price", "-")
                output += f"{key},{price},{datetime.now().isoformat()}\n"
            else:
                output += f"{key},{value},{datetime.now().isoformat()}\n"
    return output


# ============================================================
#  FASTAPI - تبدیل به API
# ============================================================

app = FastAPI(
    title="Market API - بازارهای مالی ایران و جهان",
    description="API برای دریافت قیمت‌های بازار ایران و جهان، تبدیل ارز، مدیریت معاملات",
    version="2.0.0"
)

# CORS برای ارتباط با UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
#  مدل‌های داده (Pydantic)
# ============================================================

class TradeRequest(BaseModel):
    symbol: str
    trade_type: str  # buy / sell
    quantity: float
    price: float
    tp: Optional[float] = None
    sl: Optional[float] = None

class TradeUpdateRequest(BaseModel):
    symbol: str
    trade_type: str
    quantity: float
    price: float
    tp: Optional[float] = None
    sl: Optional[float] = None

class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

# ============================================================
#  ذخیره معاملات در فایل JSON
# ============================================================

TRADES_FILE = "trades.json"

def load_trades() -> List[Dict]:
    try:
        with open(TRADES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_trades(trades: List[Dict]):
    with open(TRADES_FILE, "w", encoding="utf-8") as f:
        json.dump(trades, f, indent=2, ensure_ascii=False, default=str)

# ============================================================
#  API Endpoints
# ============================================================

@app.get("/")
async def root():
    return {
        "name": "Market API",
        "version": "2.0.0",
        "status": "online",
        "time": datetime.now().isoformat(),
        "endpoints": {
            "/iran/prices": "قیمت‌های بازار ایران",
            "/world/prices": "قیمت‌های بازار جهانی",
            "/search/{query}": "جستجو در بازارها",
            "/convert": "تبدیل ارز",
            "/trades": "مدیریت معاملات",
            "/analyze/{market_type}": "تحلیل بازار",
            "/export/iran": "خروجی CSV ایران",
            "/export/world": "خروجی CSV جهان"
        }
    }

# ====== 1. قیمت‌های ایران ======
@app.get("/iran/prices")
async def get_iran_prices():
    try:
        iran = Iranian_market()
        data = iran.set()
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ====== 2. قیمت‌های جهانی ======
@app.get("/world/prices")
async def get_world_prices():
    try:
        world = World_Market()
        data = world.set()
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ====== 3. جستجو ======
@app.get("/search/{query}")
async def search_market(query: str):
    try:
        iran = Iranian_market()
        iran.set()
        iran_result = iran.search(query)
        
        world = World_Market()
        world.set()
        world_result = world.search(query)
        
        return {
            "status": "success",
            "query": query,
            "iran": iran_result,
            "world": world_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ====== 4. تبدیل ارز ======
@app.post("/convert")
async def convert_currency(request: ConversionRequest):
    try:
        result = None
        method = None
        
        if request.from_currency.upper() == "USD" and request.to_currency.upper() == "IRR":
            result = Dollar_to_Rial(request.amount)
            method = "Dollar_to_Rial"
        elif request.from_currency.upper() == "IRR" and request.to_currency.upper() == "USD":
            result = Rial_to_Dollar(request.amount)
            method = "Rial_to_Dollar"
        elif request.from_currency.upper() == "USDT" and request.to_currency.upper() == "IRR":
            result = Tether_to_Rial(request.amount)
            method = "Tether_to_Rial"
        elif request.from_currency.upper() == "GOLD" and request.to_currency.upper() == "IRR":
            result = Gold_to_Rial(request.amount)
            method = "Gold_to_Rial"
        else:
            return {
                "status": "error",
                "message": f"تبدیل {request.from_currency} به {request.to_currency} پشتیبانی نمی‌شود"
            }
        
        return {
            "status": "success",
            "from": request.from_currency.upper(),
            "to": request.to_currency.upper(),
            "amount": request.amount,
            "result": result,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ====== 5. مدیریت معاملات ======
@app.get("/trades")
async def get_trades():
    trades = load_trades()
    return {
        "status": "success",
        "data": trades,
        "count": len(trades)
    }

@app.post("/trades")
async def add_trade(trade: TradeRequest):
    trades = load_trades()
    
    new_trade = {
        "id": len(trades) + 1,
        "symbol": trade.symbol,
        "type": trade.trade_type,
        "quantity": trade.quantity,
        "price": trade.price,
        "tp": trade.tp,
        "sl": trade.sl,
        "date": datetime.now().isoformat(),
        "status": "open"
    }
    
    trades.append(new_trade)
    save_trades(trades)
    
    return {
        "status": "success",
        "message": "معامله با موفقیت ثبت شد",
        "trade": new_trade
    }

@app.delete("/trades/{trade_id}")
async def delete_trade(trade_id: int):
    trades = load_trades()
    trades = [t for t in trades if t.get("id") != trade_id]
    save_trades(trades)
    
    return {
        "status": "success",
        "message": f"معامله {trade_id} حذف شد"
    }

@app.put("/trades/{trade_id}")
async def update_trade(trade_id: int, trade: TradeUpdateRequest):
    trades = load_trades()
    
    for t in trades:
        if t.get("id") == trade_id:
            t.update({
                "symbol": trade.symbol,
                "type": trade.trade_type,
                "quantity": trade.quantity,
                "price": trade.price,
                "tp": trade.tp,
                "sl": trade.sl,
                "updated_at": datetime.now().isoformat()
            })
            save_trades(trades)
            return {
                "status": "success",
                "message": "معامله ویرایش شد",
                "trade": t
            }
    
    raise HTTPException(status_code=404, detail="معامله یافت نشد")

@app.get("/trades/pl")
async def get_trades_pl():
    """محاسبه سود/زیان شناور همه معاملات"""
    trades = load_trades()
    iran = Iranian_market()
    iran.set()
    prices = iran.get_currencies()
    
    results = []
    total_pl = 0
    
    for trade in trades:
        symbol = trade.get("symbol")
        price = trade.get("price")
        quantity = trade.get("quantity")
        trade_type = trade.get("type")
        
        current_price = None
        for key, value in prices.items():
            if symbol.lower() in key.lower():
                try:
                    current_price = float(str(value).replace(",", ""))
                except:
                    current_price = None
                break
        
        if current_price:
            if trade_type == "buy":
                pl = (current_price - price) * quantity
            else:
                pl = (price - current_price) * quantity
            
            total_pl += pl
            results.append({
                "id": trade.get("id"),
                "symbol": symbol,
                "pl": round(pl, 2)
            })
    
    return {
        "status": "success",
        "total_pl": round(total_pl, 2),
        "trades": results,
        "timestamp": datetime.now().isoformat()
    }

# ====== 6. تحلیل بازار ======
@app.get("/analyze/{market_type}")
async def analyze_market(market_type: str):
    try:
        if market_type.lower() == "iran":
            iran = Iranian_market()
            iran.set()
            result = analyst(iran)
        elif market_type.lower() == "world":
            world = World_Market()
            world.set()
            result = analyst(world)
        else:
            return {
                "status": "error",
                "message": "market_type باید iran یا world باشد"
            }
        
        return {
            "status": "success",
            "market": market_type,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ====== 7. خروجی CSV ======
@app.get("/export/iran")
async def export_iran():
    try:
        result = export_to_csv_iran()
        return {
            "status": "success",
            "message": "CSV ساخته شد",
            "file": "iran_market.csv",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/export/world")
async def export_world():
    try:
        result = export_to_csv_world()
        return {
            "status": "success",
            "message": "CSV ساخته شد",
            "file": "world_market.csv",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ====== 8. قیمت تکی با تبدیل ======
@app.get("/price/{symbol}")
async def get_price(symbol: str):
    """دریافت قیمت یک نماد خاص"""
    try:
        iran = Iranian_market()
        iran.set()
        iran_data = iran.get_currencies()
        
        for key, value in iran_data.items():
            if symbol.lower() in key.lower():
                return {
                    "status": "success",
                    "symbol": key,
                    "price": value,
                    "timestamp": datetime.now().isoformat()
                }
        
        world = World_Market()
        world.set()
        world_data = world.get_currencies()
        
        for item in world_data:
            for key, value in item.items():
                if symbol.lower() in key.lower():
                    price = value.get("price") if isinstance(value, dict) else value
                    return {
                        "status": "success",
                        "symbol": key,
                        "price": price,
                        "timestamp": datetime.now().isoformat()
                    }
        
        return {
            "status": "error",
            "message": f"نماد {symbol} یافت نشد"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ============================================================
#  اجرا
# ============================================================

if __name__ == "__main__":
    print("🚀 راه‌اندازی Market API...")
    print("📍 آدرس: http://localhost:8000")
    print("📚 مستندات: http://localhost:8000/docs")
    print("⚡ برای توقف Ctrl+C بزن")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )