from langchain_core.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from ..classes import ResearchState


class EvaluationNode:
    def __init__(self):
        self.model = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0
        )

    async def evaluate_itinerary(self, state: ResearchState):
        """
        Evaluates the generated itinerary for completeness, feasibility, and alignment with preferences.
        """
        preferences = state['preferences']

        prompt = f"""
        Evaluate this travel itinerary for a trip to {preferences.destination} based on the following criteria:

        ### Original Requirements
        - Travel Style: {preferences.travel_style}
        - Budget Range: ${preferences.budget_min} - ${preferences.budget_max}
        - Preferred Activities: {', '.join(preferences.preferred_activities)}
        - Special Requirements: {preferences.accessibility_requirements or 'None'}
        - Dietary Restrictions: {', '.join(preferences.dietary_restrictions) if preferences.dietary_restrictions else 'None'}

        ### Evaluation Criteria
        1. Completeness (Are all necessary details included?)
        2. Budget Alignment (Do costs match the specified range?)
        3. Activity Balance (Is there a good mix of preferred activities?)
        4. Practical Feasibility (Are timings and distances realistic?)
        5. Special Requirements Consideration
        6. Contingency Planning (Weather alternatives, backup options)

        ### Itinerary to Evaluate
        {state['report']}

        Grade the itinerary on a scale of 1 to 3:
        - 3: Excellent - Complete, well-balanced, and perfectly aligned with preferences
        - 2: Good - Minor adjustments needed
        - 1: Needs Improvement - Major revisions required

        If grade is 1, specify what critical elements need to be addressed.

        Return evaluation in this format:
        {
        "grade": 1-3,
            "critical_gaps": ["gap1", "gap2"] // only if grade is 1
        }
        """

        messages = [
            ("system", "You are a travel planning expert evaluating itineraries."),
            ("human", prompt)
        ]

        try:
            response = await self.model.ainvoke(messages)
            evaluation = eval(response.content)  # Convert string response to dict

            if evaluation['grade'] == 1:
                msg = f"❌ Itinerary needs improvement. Critical gaps identified:\n"
                for gap in evaluation['critical_gaps']:
                    msg += f"  • {gap}\n"
            else:
                msg = f"✓ Itinerary received a grade of {evaluation['grade']}/3\n"

            return {
                "messages": [AIMessage(content=msg)],
                "eval": evaluation
            }

        except Exception as e:
            error_msg = f"Error during evaluation: {str(e)}"
            return {
                "messages": [AIMessage(content=error_msg)],
                "eval": {"grade": 1, "critical_gaps": [error_msg]}
            }

    async def run(self, state: ResearchState):
        result = await self.evaluate_itinerary(state)
        return result