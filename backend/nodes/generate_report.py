from datetime import datetime
from langchain_core.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from ..classes import ResearchState


class GenerateNode:
    def __init__(self):
        self.model = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0
        )

    def format_budget_summary(self, preferences, activities):
        total_budget = 0
        budget_breakdown = {
            'Accommodation': 0,
            'Activities': 0,
            'Transportation': 0,
            'Food & Dining': 0,
            'Miscellaneous': 0
        }

        # Calculate estimated costs
        # Implementation would go here

        return budget_breakdown, total_budget

    def extract_markdown_content(self, content):
        start_index_hash = content.find("#")
        start_index_bold = content.find("**")

        if start_index_hash != -1 and (start_index_bold == -1 or start_index_hash < start_index_bold):
            return content[start_index_hash:].strip()
        elif start_index_bold != -1:
            return content[start_index_bold:].strip()
        else:
            return content.strip()

    async def generate_itinerary(self, state: ResearchState):
        preferences = state['preferences']
        documents = state['documents']

        report_title = f"Travel Itinerary: {preferences.destination}"
        report_date = datetime.now().strftime('%B %d, %Y')

        # Calculate trip duration
        trip_duration = (preferences.end_date - preferences.start_date).days + 1

        prompt = f"""
        Create a detailed travel itinerary for a {trip_duration}-day trip to {preferences.destination}.

        ### Trip Details
        - Dates: {preferences.start_date} to {preferences.end_date}
        - Style: {preferences.travel_style}
        - Budget Range: ${preferences.budget_min} - ${preferences.budget_max}
        - Travelers: {preferences.number_of_travelers}
        - Preferred Activities: {', '.join(preferences.preferred_activities)}

        ### Special Requirements
        - Accessibility: {preferences.accessibility_requirements or 'None'}
        - Dietary: {', '.join(preferences.dietary_restrictions) if preferences.dietary_restrictions else 'None'}

        ### Additional Destinations
        {', '.join(preferences.additional_destinations) if preferences.additional_destinations else 'None'}

        Write the itinerary in Markdown format with the following sections:

        1. **Trip Overview**:
            - Brief introduction to the destination(s)
            - Travel style and focus
            - Key highlights and experiences

        2. **Pre-Trip Preparation**:
            - Essential items to pack based on activities and weather
            - Visa/documentation requirements if any
            - Health and safety considerations

        3. **Budget Overview**:
            - Estimated cost breakdown
            - Money-saving tips
            - Payment methods and currency information

        4. **Daily Itinerary**:
            For each day, include:
            - Date and day number
            - Morning activities
            - Afternoon activities
            - Evening activities
            - Meal recommendations
            - Transportation details
            - Estimated costs
            - Alternative options for weather/availability

        5. **Practical Information**:
            - Local transportation
            - Emergency contacts
            - Cultural considerations
            - Weather considerations
            - Booking requirements

        6. **Additional Recommendations**:
            - Alternative activities
            - Local events during the stay
            - Shopping opportunities
            - Hidden gems and local favorites

        Use the following researched information to create the itinerary:
        {documents}

        Important Guidelines:
        1. Include clickable links to booking/information pages
        2. Maintain a balanced pace of activities
        3. Consider travel time between locations
        4. Account for stated preferences and requirements
        5. Include specific costs and booking details where available
        6. Provide alternatives for flexibility
        """

        messages = [
            ("system", "You are a travel planning expert creating detailed, personalized itineraries."),
            ("human", prompt)
        ]

        try:
            response = await self.model.ainvoke(messages)
            markdown_content = self.extract_markdown_content(response.content)

            full_itinerary = f"# {report_title}\n\n*Generated on {report_date}*\n\n{markdown_content}"

            return {
                "messages": [AIMessage(content="✓ Generated detailed travel itinerary!")],
                "report": full_itinerary
            }

        except Exception as e:
            error_message = f"Error generating itinerary: {str(e)}"
            return {
                "messages": [AIMessage(content=error_message)],
                "report": f"# Error Generating Itinerary\n\n*{report_date}*\n\n{error_message}"
            }

    async def run(self, state: ResearchState, websocket):
        if websocket:
            await websocket.send_text("⌛️ Generating your travel itinerary...")
        result = await self.generate_itinerary(state)
        return result