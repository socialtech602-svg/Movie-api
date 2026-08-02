import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

# Frontend Route - Taki 404 Not Found na aaye
@app.get("/", response_class=HTMLResponse)
def serve_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vidsrc Playwright Extractor</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #1e1e1e; color: #fff; padding: 20px; }
            .container { max-width: 650px; margin: 0 auto; background: #2d2d2d; padding: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
            input { padding: 10px; width: 65%; border: none; border-radius: 4px; outline: none; background: #333; color: white; border: 1px solid #555; }
            button { padding: 10px 15px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #218838; }
            pre { background: #111; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; color: #00ff00; border: 1px solid #444; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Vidsrc Playwright Extractor API</h2>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="tmdb_id" placeholder="Enter TMDB ID (e.g., 969681)">
                <button onclick="fetchData()">Extract</button>
            </div>
            <h4 style="margin-top: 20px; color: #ffc107;">Response Data:</h4>
            <p style="font-size: 12px; color: #aaa;">Status: Backend browser run kar raha hai. 30-45 seconds lag sakte hain...</p>
            <pre id="output">Waiting for request...</pre>
        </div>

        <script>
            async function fetchData() {
                const id = document.getElementById("tmdb_id").value;
                const output = document.getElementById("output");
                
                if(!id) {
                    output.innerText = "Error: Please enter a valid TMDB ID!";
                    return;
                }

                output.innerText = "Connecting to Cloud Server... Browser is opening in background. Please wait...";

                try {
                    const response = await fetch(`/extract/${id}`);
                    const data = await response.json();
                    output.innerText = JSON.stringify(data, null, 4);
                } catch (error) {
                    output.innerText = "Error fetching data: " + error;
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

# Backend Route - Playwright Network Interceptor
@app.get("/extract/{tmdb_id}")
async def extract_vidsrc(tmdb_id: str):
    target_url = f"https://web.nxsha.app/embed/movie/{tmdb_id}?server=AwsPly-[Multi-Lang]"
    
    extracted_urls = {
        "m3u8_links": [],
        "ts_chunks": []
    }

    async with async_playwright() as p:
        # Chromium ko specific flags ke sath launch karna taaki cloud pe crash na ho
        browser = await p.chromium.launch(
            headless=True, 
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            referer="https://vidsrc.sbs/"
        )
        page = await context.new_page()

        # Har network request intercept karna
        async def handle_request(request):
            url = request.url
            if ".m3u8" in url or "/getm3u8/" in url or "/stream/" in url:
                if url not in extracted_urls["m3u8_links"]:
                    extracted_urls["m3u8_links"].append(url)
            elif ".ts" in url or ".png" in url and "id=" in url:
                if url not in extracted_urls["ts_chunks"]:
                    extracted_urls["ts_chunks"].append(url)

        page.on("request", handle_request)

        try:
            await page.goto(target_url, timeout=60000)
            await asyncio.sleep(5)
            
            # Simulated Clicks to trigger the video
            await page.mouse.click(x=300, y=200)
            await asyncio.sleep(2)
            await page.mouse.click(x=300, y=200)
            
            # Wait for video streaming links to hit network tab
            await asyncio.sleep(10)
            
        except Exception as e:
            return {"status": "error", "message": f"Execution error: {str(e)}"}
        finally:
            await browser.close()

    if len(extracted_urls["m3u8_links"]) > 0:
        return {
            "status": "success",
            "tmdb_id": tmdb_id,
            "message": "Play button clicked and network intercepted successfully!",
            "data": extracted_urls
        }
    else:
        return {
            "status": "failed",
            "message": "Network tab par m3u8 link nahi mila. Page load block ho gaya hoga.",
            "data": extracted_urls
        }
