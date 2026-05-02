"""
MCP Gateway Template — Selenium Server
"""
import os, base64, uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Selenium MCP Server")
BROWSER  = os.getenv("SELENIUM_BROWSER", "chrome").lower()
HEADLESS = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"
TIMEOUT  = int(os.getenv("SELENIUM_TIMEOUT", "10"))
_driver  = None

def get_driver():
    global _driver
    if _driver: return _driver
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    opts = Options()
    if HEADLESS: opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    _driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    _driver.implicitly_wait(TIMEOUT)
    return _driver

class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}

@app.get("/health")
def health():
    return {"status": "ok", "server": "selenium"}

@app.post("/call")
async def call(req: CallRequest):
    try:
        driver = get_driver()
        if req.tool == "navigate":
            driver.get(req.arguments["url"])
            return {"success": True, "result": {"url": driver.current_url, "title": driver.title}}
        elif req.tool == "click":
            _find(driver, req.arguments["selector"], req.arguments.get("by","css")).click()
            return {"success": True, "result": {"clicked": req.arguments["selector"]}}
        elif req.tool == "type":
            el = _find(driver, req.arguments["selector"], req.arguments.get("by","css"))
            if req.arguments.get("clear", True): el.clear()
            el.send_keys(req.arguments.get("text",""))
            return {"success": True, "result": {"typed": req.arguments.get("text","")}}
        elif req.tool == "get_text":
            el = _find(driver, req.arguments["selector"], req.arguments.get("by","css"))
            return {"success": True, "result": {"text": el.text}}
        elif req.tool == "screenshot":
            b64 = base64.b64encode(driver.get_screenshot_as_png()).decode()
            return {"success": True, "result": {"screenshot_base64": b64}}
        elif req.tool == "execute_script":
            result = driver.execute_script(req.arguments["script"], *req.arguments.get("args",[]))
            return {"success": True, "result": {"result": result}}
        elif req.tool == "find_elements":
            els = _find_all(driver, req.arguments["selector"], req.arguments.get("by","css"))
            return {"success": True, "result": {"count": len(els), "texts": [e.text for e in els[:20]]}}
        elif req.tool == "get_page_source":
            return {"success": True, "result": {"source": driver.page_source}}
        elif req.tool == "back":
            driver.back(); return {"success": True, "result": {"url": driver.current_url}}
        elif req.tool == "refresh":
            driver.refresh(); return {"success": True, "result": {"url": driver.current_url}}
        elif req.tool == "close":
            global _driver
            if _driver: _driver.quit(); _driver = None
            return {"success": True, "result": {"closed": True}}
        else:
            raise HTTPException(400, f"Unknown tool: {req.tool}")
    except HTTPException: raise
    except Exception as e:
        return {"success": False, "error": str(e)}

def _find(driver, selector, by="css"):
    from selenium.webdriver.common.by import By
    return driver.find_element({"css": By.CSS_SELECTOR,"xpath": By.XPATH,"id": By.ID,"name": By.NAME}.get(by, By.CSS_SELECTOR), selector)

def _find_all(driver, selector, by="css"):
    from selenium.webdriver.common.by import By
    return driver.find_elements({"css": By.CSS_SELECTOR,"xpath": By.XPATH,"id": By.ID,"name": By.NAME}.get(by, By.CSS_SELECTOR), selector)

if __name__ == "__main__":
    port = int(os.getenv("SELENIUM_PORT", "8110"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
