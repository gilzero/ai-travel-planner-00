from langchain_core.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from ..classes import ResearchState, TravelSearchInput


class SubQuestionsNode:
    def __init__(self) -> None:
        self.model = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0
        )

    async def generate_sub_questions(self, state: ResearchState):
        try:
            msg = "🤔 Generating detailed travel research questions...\n"

            preferences = state['preferences']
            initial_data = state['initial_data']

            # Prompt to generate detailed travel sub-questions
            prompt = f"""
            You are a travel research expert planning a trip to {preferences.destination} 
            from {preferences.start_date} to {preferences.end_date}.

            ### Travel Preferences
            - Style: {preferences.travel_style}
            - Budget Range: ${preferences.budget_min} - ${preferences.budget_max}
            - Preferred Activities: {', '.join(preferences.preferred_activities)}
            - Number of Travelers: {preferences.number_of_travelers}
            - Additional Destinations: {', '.join(preferences.additional_destinations) if preferences.additional_destinations else 'None'}

            ### Special Requirements
            - Accessibility: {preferences.accessibility_requirements or 'None'}
            - Dietary: {', '.join(preferences.dietary_restrictions) if preferences.dietary_restrictions else 'None'}

            ### Initial Research Data
            {initial_data}

            Generate specific search queries covering:
            1. Accommodations matching the travel style and budget
            2. Activities and attractions aligned with preferences
            3. Local transportation options
            4. Dining options considering any dietary restrictions
            5. Weather-appropriate activities for the dates
            6. Safety and practical considerations
            7. Special events or seasonal activities during the visit

            For multi-destination trips, include queries about:
            - Inter-city transportation
            - Optimal route planning
            - Location-specific considerations

            Format each query with:
            - Specific search terms
            - Location relevance
            - Category (accommodation/activity/transport/dining)
            """

            # Use LLM to generate sub-questions
            messages = [
                ("system", "You are a travel research expert generating specific search queries for trip planning."),
                ("human", prompt)
            ]

            sub_questions = await self.model.with_structured_output(TravelSearchInput).ainvoke(messages)

            msg += f"✓ Generated {len(sub_questions.sub_queries)} specific research queries\n"

        except Exception as e:
            msg = f"An error occurred during query generation: {str(e)}"
            return {"messages": [AIMessage(content=msg)], "sub_queries": None}

        return {
            "messages": [AIMessage(content=msg)],
            "sub_queries": sub_questions,
            "initial_data": state['initial_data']
        }

    async def run(self, state: ResearchState):
        result = await self.generate_sub_questions(state)
        return result