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

# Initialize FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def send_progress(message: str):
        """Send progress updates to the client."""
        await websocket.send_text(message)

    try:
        data = await websocket.receive_json()

        try:
            # Parse and validate preferences
            data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            data['end_date'] = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            preferences = TravelPreferences(**data)
            output_format = data.get("output_format", "pdf")

            # Initialize and set up the Graph
            graph = Graph(output_format=output_format, websocket=websocket)
            graph.initialize_state(preferences)  # Initialize the state with preferences

            # Run the graph
            await graph.run(progress_callback=send_progress)
            await send_progress("✔️ Itinerary planning completed.")

        except ValidationError as e:
            await send_progress(f"❌ Invalid travel preferences: {str(e)}")
        except Exception as e:
            await send_progress(f"❌ Unexpected error: {str(e)}")

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Unexpected WebSocket error: {e}")
        await websocket.send_text(f"❌ An unexpected error occurred: {str(e)}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=5000,
        reload=True
    )
