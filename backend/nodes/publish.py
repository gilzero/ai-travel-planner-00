"""
This module defines the PublishNode class, which is responsible for formatting and saving the generated travel itinerary.
The itinerary can be saved in different formats such as PDF or Markdown, based on the user's preferences.
The class ensures that the output directory exists and handles the generation of the output file with a timestamped filename.
"""
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
        print(f"📂 [DEBUG] Output directory set to: {self.output_dir}")

    async def format_output(self, state: ResearchState):
        if "report" not in state:
            msg = "❌ Error: Itinerary report not found in state."
            print(f"⚠️ [ERROR] {msg}")
            return {"messages": [AIMessage(content=msg)]}

        itinerary = state["report"]
        output_format = state.get("output_format", "pdf")
        preferences = state["preferences"]
        print(f"📝 [DEBUG] Itinerary retrieved. Output format: {output_format}")

        # Generate filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        destination = preferences.destination.replace(" ", "_")
        file_base = f"{self.output_dir}/{destination}_Itinerary_{timestamp}"
        print(f"🕒 [DEBUG] Timestamp for filename: {timestamp}")
        print(f"📁 [DEBUG] Base filename: {file_base}")

        if output_format == "pdf":
            pdf_file_path = f"{file_base}.pdf"
            print(f"📄 [DEBUG] PDF file path: {pdf_file_path}")
            result = generate_travel_pdf(
                content=itinerary,
                filename=pdf_file_path
            )
            formatted_report = f"📥 {result}"
            print(f"✅ [DEBUG] PDF generated: {result}")
        else:
            markdown_file_path = f"{file_base}.md"
            print(f"📝 [DEBUG] Markdown file path: {markdown_file_path}")
            with open(markdown_file_path, "w", encoding='utf-8') as md_file:
                md_file.write(itinerary)
            formatted_report = f"📥 Markdown itinerary saved at {markdown_file_path}"
            print(f"✅ [DEBUG] Markdown file saved.")

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
        print(f"📨 [DEBUG] Summary message prepared.")

        return {"messages": [AIMessage(content=msg.strip())]}

    async def run(self, state: ResearchState):
        print("🚀 [DEBUG] Running format_output method.")
        result = await self.format_output(state)
        print("🏁 [DEBUG] Format output process completed.")
        return result