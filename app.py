from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from backend.graph import Graph
from backend.classes.travel.models import TravelPreferences
from datetime import datetime
from pydantic import ValidationError

from dotenv import load_dotenv

load_dotenv('.env')

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive initial preferences from the WebSocket client
        data = await websocket.receive_json()

        try:
            # Convert dates from string to datetime objects
            data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            data['end_date'] = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

            # Validate and create TravelPreferences object
            preferences = TravelPreferences(**data)
            output_format = data.get("output_format", "pdf")

            # Initialize the Graph with travel preferences and output format
            graph = Graph(preferences=preferences, output_format=output_format, websocket=websocket)

            # Progress callback to send messages back to the client
            async def progress_callback(message):
                await websocket.send_text(message)

            # Run the graph process
            await graph.run(progress_callback=progress_callback)

            await websocket.send_text("✔️ Itinerary planning completed.")

        except ValidationError as e:
            error_msg = "Invalid travel preferences: " + str(e)
            await websocket.send_text(f"❌ {error_msg}")

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        try:
            await websocket.send_text(f"❌ {error_msg}")
        except:
            print(f"Failed to send error message: {error_msg}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=5000,
        reload=True
    )