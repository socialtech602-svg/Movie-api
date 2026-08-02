import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup # Nayi library add ki

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def serve_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vidsrc Extractor Tester</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #1e1e1e; color: #fff; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: #2d2d2d; padding: 20px; border-radius: 8px; }
            input { padding: 10px; width: 70%; border: none; border-radius: 4px; outline: none; }
            button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            pre { background: #111; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; color: #00ff00; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Vidsrc Extractor API Test</h2>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="tmdb_id" placeholder="TMDB ID Daalo (e.g., 969681)">
                <button onclick="fetchData()">Extract</button>
            </div>
            <h4 style="margin-top: 20px;">Response Data:</h4>
            <pre id="output">Waiting for request...</pre>
        </div>

        <script>
            async function fetchData() {
                const id = document.getElementById("tmdb_id").value;
                const output = document.getElementById("output");
                
                if(!id) {
                    output.innerText = "Please enter TMDB ID!";
                    return;
                }

                output.innerText = "Extracting data from server... Please wait.";

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

@app.get("/extract/{tmdb_id}")
def extract_vidsrc(tmdb_id: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://vidsrc.sbs/",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    embed_url = f"https://vidsrc.sbs/embed/movie/{tmdb_id}"
    
    try:
        res = requests.get(embed_url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            # BeautifulSoup se HTML parse kar rahe hain
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Page mein jitne bhi iframes hain unka src nikal rahe hain
            iframes = [iframe.get('src') for iframe in soup.find_all('iframe') if iframe.get('src')]
            
            return {
                "status": "success",
                "tmdb_id": tmdb_id,
                "found_iframes": iframes, # Yahan hume player ka link milega
                "message": "HTML parsed successfully!"
            }
        else:
            return {
                "status": "failed", 
                "error": f"Server ne HTTP {res.status_code} return kiya"
            }
            
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
