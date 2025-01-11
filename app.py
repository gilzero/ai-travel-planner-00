"""
@fileoverview This module sets up a FastAPI application for handling HTTP 
              requests and WebSocket connections for travel itinerary 
              planning.
@filepath app.py
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from backend.graph import Graph
from backend.classes.travel.base_models import TravelPreferences
from datetime import datetime
from pydantic import ValidationError
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')
print("🔧 [INFO] Environment variables loaded.")

# Initialize FastAPI app
app = FastAPI()
print("🚀 [INFO] FastAPI application initialized.")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")
print("📁 [INFO] Static files and templates configured.")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the index page.
    
    Args:
        request (Request): The incoming HTTP request.
    
    Returns:
        TemplateResponse: The rendered HTML page.
    """
    print("🌐 [INFO] Rendering index page.")
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handle WebSocket connections for real-time communication.
    
    Args:
        websocket (WebSocket): The WebSocket connection.
    """
    await websocket.accept()
    print("🔌 [INFO] WebSocket connection accepted.")

    async def send_progress(message: str):
        """
        Send progress updates to the client.
        
        Args:
            message (str): The progress message to send.
        """
        print(f"📤 [INFO] Sending progress: {message}")
        await websocket.send_text(message)

    try:
        data = await websocket.receive_json()
        print(f"📥 [INFO] Received data: {data}")

        try:
            # Parse and validate preferences
            data['start_date'] = datetime.strptime(
                data['start_date'], '%Y-%m-%d'
            ).date()
            data['end_date'] = datetime.strptime(
                data['end_date'], '%Y-%m-%d'
            ).date()
            preferences = TravelPreferences(**data)
            output_format = data.get("output_format", "pdf")
            print(f"✅ [INFO] Preferences parsed: {preferences}, Output format: {output_format}")

            # Initialize and set up the Graph
            graph = Graph(output_format=output_format, websocket=websocket)
            graph.initialize_state(preferences)
            print("🔄 [INFO] Graph initialized with preferences.")

            # Run the graph
            await graph.run(progress_callback=send_progress)
            await send_progress("✔️ Itinerary planning completed.")
            print("🏁 [INFO] Itinerary planning completed.")

        except ValidationError as e:
            error_message = f"❌ Invalid travel preferences: {str(e)}"
            await send_progress(error_message)
            print(f"⚠️ [ERROR] {error_message}")
        except Exception as e:
            error_message = f"❌ Unexpected error: {str(e)}"
            await send_progress(error_message)
            print(f"🔥 [ERROR] {error_message}")

    except WebSocketDisconnect:
        print("🔌 [INFO] WebSocket disconnected")
    except Exception as e:
        error_message = f"❌ An unexpected error occurred: {str(e)}"
        print(f"🔥 [ERROR] {error_message}")
        await websocket.send_text(error_message)
    finally:
        await websocket.close()
        print("🔒 [INFO] WebSocket connection closed.")

if __name__ == "__main__":
    print("🚀 [INFO] Starting FastAPI server...")
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=5000,
        reload=True
    )
