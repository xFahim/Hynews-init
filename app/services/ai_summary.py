"""AI-powered news summarization service using Google Gemini."""

import os
import json
from typing import List, Dict, Any, Optional
from google import genai


class AISummaryService:
    """Service for generating AI-powered news summaries using Gemini."""

    def __init__(self):
        """Initialize the Gemini client with API key from environment."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please add it to your .env file."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    def generate_daily_summary(
        self, news_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a daily executive briefing from a list of news items.

        Args:
            news_items: List of news item dictionaries containing 'title', 'body', etc.

        Returns:
            Dictionary containing:
            - story_of_day: Object with title and summary of most significant story
            - categories: List of objects with category name and items

        Raises:
            Exception: If AI generation fails
        """
        # Limit to top 15 items for optimal token usage
        selected_items = news_items[:15]

        if not selected_items:
            return {
                "story_of_day": {
                    "title": "No News Available",
                    "summary": "No news items were available for summarization.",
                },
                "categories": [],
            }

        # Build the prompt with formatted news items
        prompt = self._build_prompt(selected_items)

        try:
            # Call Gemini API
            response = self.client.models.generate_content(
                model=self.model, contents=prompt
            )

            # Extract the text response
            response_text = response.text.strip()

            # Try to parse as JSON
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON response
            summary_data = json.loads(response_text)

            return summary_data

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")

    def _build_prompt(self, news_items: List[Dict[str, Any]]) -> str:
        """
        Build the prompt for Gemini with formatted news items.

        Args:
            news_items: List of news item dictionaries

        Returns:
            Formatted prompt string
        """
        # Format each news item
        formatted_items = []
        for i, item in enumerate(news_items, 1):
            # Extract title (different sources use different field names)
            title = (
                item.get("title")
                or item.get("news_header")
                or item.get("heading")
                or "Untitled"
            )

            # Extract body text (try different field names)
            body = (
                item.get("news_body_text_full")
                or item.get("body")
                or item.get("summary")
                or ""
            )

            # Truncate body to first 500 characters to save tokens
            body_preview = body[:500] + "..." if len(body) > 500 else body

            formatted_items.append(
                f"Item {i}:\nTitle: {title}\nContent: {body_preview}\n"
            )

        news_content = "\n".join(formatted_items)

        # Build the complete prompt
        prompt = f"""You are a professional news editor creating a Daily Executive Briefing for busy readers.

TASK:
Based ONLY on the news items provided below, generate a structured daily news summary.

INSTRUCTIONS:
1. Group related stories into logical categories (e.g., Politics, Sports, International, Economy, Technology, etc.)
2. For each category, provide a bulleted list of 1-sentence takeaways
3. Select ONE "Story of the Day" - the most significant or impactful story from all items
4. Keep language professional and concise
5. Do not invent or add information not present in the provided news items

OUTPUT FORMAT:
Return ONLY a valid JSON object with this exact structure:
{{
  "story_of_day": {{
    "title": "Title of most significant story",
    "summary": "2-3 sentence summary explaining why this story matters"
  }},
  "categories": [
    {{
      "category": "Category Name",
      "items": [
        "One-sentence takeaway 1",
        "One-sentence takeaway 2"
      ]
    }}
  ]
}}

NEWS ITEMS TO SUMMARIZE:
{news_content}

Remember: Return ONLY the JSON object, no additional text or markdown formatting."""

        return prompt


# Lazy-loaded singleton instance
_ai_summary_service_instance: Optional[AISummaryService] = None


def get_ai_summary_service() -> AISummaryService:
    """
    Get the AI summary service singleton instance.
    Creates the instance on first call (lazy initialization).

    Returns:
        AISummaryService instance

    Raises:
        ValueError: If GOOGLE_API_KEY is not set in environment
    """
    global _ai_summary_service_instance

    if _ai_summary_service_instance is None:
        _ai_summary_service_instance = AISummaryService()

    return _ai_summary_service_instance
