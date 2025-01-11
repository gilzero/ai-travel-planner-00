from langchain_core.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from ..classes import ResearchState
import json


class EvaluationNode:
    def __init__(self):
        self.model = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0
        )
        print("🛠️ [DEBUG] EvaluationNode initialized with ChatAnthropic model.")

    async def evaluate_itinerary(self, state: ResearchState):
        """
        Evaluates the generated itinerary for completeness, feasibility, and alignment with preferences.
        """
        preferences = state['preferences']
        print(f"🔍 [DEBUG] Evaluating itinerary for destination: {preferences.destination}")

        # Check if the report exists
        report = state.get('report')
        if not report:
            error_msg = "Error: Itinerary report not found in state."
            print(f"🔥 [ERROR] {error_msg}")
            return {
                "messages": [AIMessage(content=error_msg)],
                "eval": {"grade": 1, "critical_gaps": [error_msg]}
            }

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
        {report}

        Grade the itinerary on a scale of 1 to 3:
        - 3: Excellent - Complete, well-balanced, and perfectly aligned with preferences
        - 2: Good - Minor adjustments needed
        - 1: Needs Improvement - Major revisions required

        If grade is 1, specify what critical elements need to be addressed.

        Return your evaluation as a valid JSON object with the following format:
        {{
            "grade": 1-3,
            "critical_gaps": ["gap1", "gap2"] // only if grade is 1
        }}
        """
        print("📝 [DEBUG] Evaluation prompt prepared.")

        messages = [
            ("system", "You are a travel planning expert evaluating itineraries. Please return your evaluation as a valid JSON object."),
            ("human", prompt)
        ]

        try:
            print("🚀 [DEBUG] Sending evaluation request to model.")
            response = await self.model.ainvoke(messages)
            try:
                evaluation = json.loads(response.content)  # Convert string response to dict
            except json.JSONDecodeError as e:
                error_msg = f"Error parsing JSON response: {str(e)}"
                print(f"🔥 [ERROR] {error_msg}")
                return {
                    "messages": [AIMessage(content=error_msg)],
                    "eval": {"grade": 1, "critical_gaps": [error_msg]}
                }

            if "grade" not in evaluation:
                error_msg = "Error: 'grade' key not found in evaluation response."
                print(f"🔥 [ERROR] {error_msg}")
                return {
                    "messages": [AIMessage(content=error_msg)],
                    "eval": {"grade": 1, "critical_gaps": [error_msg]}
                }

            print(f"📊 [DEBUG] Evaluation response received: {evaluation}")

            if evaluation['grade'] == 1:
                msg = f"❌ Itinerary needs improvement. Critical gaps identified:\n"
                if 'critical_gaps' in evaluation and isinstance(evaluation['critical_gaps'], list):
                    for gap in evaluation['critical_gaps']:
                        msg += f"  • {gap}\n"
                    print(f"⚠️ [DEBUG] Critical gaps found: {evaluation['critical_gaps']}")
                else:
                    msg += "  • No critical gaps provided.\n"
                    print(f"⚠️ [DEBUG] No critical gaps found in response.")
            else:
                msg = f"✓ Itinerary received a grade of {evaluation['grade']}/3\n"
                print(f"✅ [DEBUG] Itinerary graded: {evaluation['grade']}")

            return {
                "messages": [AIMessage(content=msg)],
                "eval": evaluation
            }

        except Exception as e:
            error_msg = f"Error during evaluation: {str(e)}"
            print(f"🔥 [ERROR] {error_msg}")
            return {
                "messages": [AIMessage(content=error_msg)],
                "eval": {"grade": 1, "critical_gaps": [error_msg]}
            }

    async def run(self, state: ResearchState):
        print("🚀 [DEBUG] Running evaluation process.")
        result = await self.evaluate_itinerary(state)
        print("🏁 [DEBUG] Evaluation process completed.")
        return result