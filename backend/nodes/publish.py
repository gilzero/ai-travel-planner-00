import os
from datetime import datetime
from langchain_core.messages import AIMessage
from ..utils.utils import generate_travel_pdf
from ..classes import ResearchState


class PublishNode:
    def __init__(self, output_dir="itineraries"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def format_output(self, state: ResearchState):
        itinerary = state["report"]
        output_format = state.get("output_format", "pdf")
        preferences = state["preferences"]

        # Generate filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        destination = preferences.destination.replace(" ", "_")
        file_base = f"{self.output_dir}/{destination}_Itinerary_{timestamp}"

        if output_format == "pdf":
            pdf_file_path = f"{file_base}.pdf"
            result = generate_travel_pdf(
                content=itinerary,
                filename=pdf_file_path
            )
            formatted_report = f"📥 {result}"
        else:
            markdown_file_path = f"{file_base}.md"
            with open(markdown_file_path, "w", encoding='utf-8') as md_file:
                md_file.write(itinerary)
            formatted_report = f"📥 Markdown itinerary saved at {markdown_file_path}"

        # Generate summary message
        msg = f"""
✨ Your travel itinerary is ready!

🌍 Destination: {preferences.destination}
📅 Dates: {preferences.start_date} to {preferences.end_date}
👥 Travelers: {preferences.number_of_travelers}
🎯 Style: {preferences.travel_style}

{formatted_report}

Enjoy your trip! 🚀
        """

        return {"messages": [AIMessage(content=msg.strip())]}

    async def run(self, state: ResearchState):
        result = await self.format_output(state)
        return result