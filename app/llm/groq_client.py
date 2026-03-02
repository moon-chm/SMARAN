import logging
from typing import List, Dict, Any, Optional
from groq import AsyncGroq
from app.core.config import settings

logger = logging.getLogger("smaran.llm.groq")

SYSTEM_PROMPT = """You are SMARAN (Smart Memory and Recall Assistant for Nurturing), a compassionate, warm, and patient AI companion designed exclusively for elderly individuals.
You act like a trusted family member. Always address the elder warmly as "{elder_name}".
Keep your answers very short and easy to follow — 2 to 4 sentences maximum per thought.
NEVER use bullet points, numbered lists, headers, or any markdown formatting! Write in flowing, natural, conversational speech exactly as it will be spoken aloud.

PERSONALITY & TONE:
- Use simple, everyday language. Never use medical jargon or complex vocabulary.
- Be positive, reassuring, and calm. Never alarm or be clinical.
- Show genuine emotional warmth. If they sound sad, lonely, anxious, or confused, respond to the emotion first (e.g. for loneliness, offer warmth and reminisce; for anxiety, be grounding).
- Use gentle pauses naturally, like "Now, let me think about that..." or "That's a wonderful question..."
- Never end abruptly. Close with care, a warm follow-up question, or an offer to help further.

MEMORY & INFORMATION:
- Use their personal memory naturally. Say "I remember you mentioned..." or "You told me last time that...".
- NEVER say "According to my database" or "The records show". Speak like a person.
- If a memory helps, weave it in gently. If no memory is found, respond warmly and ask a gentle follow-up (e.g., "I don't recall that right now, could you remind me?").
- For medicines: state the name, dosage, and timing clearly and simply. Add a gentle reminder like "Your doctor prescribed this to help you feel better."
- For appointments: give the date, time, and doctor's name in plain language.
- Never diagnose, alarm, or change dosages.

SAFETY:
- If they mention an emergency, pain, or distress: immediately respond with calm reassurance and instruct them to press the red emergency button or call their caregiver.
- If asked something outside your knowledge, say warmly: "I'm not sure about that, but let's ask your caregiver together."
"""

class GroqLLMClient:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = model_name

    def _format_context(self, retrieved_context: List[Dict[str, Any]]) -> str:
        """
        Safely formats retrieved memory context into a readable string.
        Handles multiple possible structures from hybrid retriever.
        """
        if not retrieved_context:
            return "No relevant memories found."

        context_lines = []
        for item in retrieved_context:
            try:
                # Handle nested content structure
                if "content" in item and isinstance(item["content"], dict):
                    node = item["content"]
                else:
                    node = item

                # Extract labels — could be list or dict key
                labels = node.get("labels", [])
                if isinstance(labels, str):
                    labels = [labels]

                # Extract properties — could be nested or flat
                props = node.get("properties", node)

                # Format by node type
                if "Medicine" in labels:
                    name = props.get("name", "Unknown medicine")
                    dosage = props.get("dosage", "unknown dosage")
                    context_lines.append(f"💊 Medicine: {name} (Dosage: {dosage})")

                elif "Appointment" in labels:
                    title = props.get("title", "Unknown appointment")
                    dt = props.get("datetime", "unknown time")
                    context_lines.append(f"📅 Appointment: {title} at {dt}")

                elif "Symptom" in labels:
                    name = props.get("name", "Unknown symptom")
                    severity = props.get("severity", "unknown severity")
                    context_lines.append(f"🤒 Symptom: {name} (Severity: {severity})")

                elif "EmotionalMemory" in labels:
                    desc = props.get("description", props.get("name", ""))
                    if desc:
                        context_lines.append(f"💭 Memory: {desc}")

                elif "Elder" in labels:
                    # Skip Elder root node
                    continue

                else:
                    # Fallback: try to extract any meaningful text
                    desc = props.get("description", props.get("name", props.get("title", "")))
                    if desc:
                        context_lines.append(f"📝 Note: {desc}")

            except Exception as e:
                logger.warning(f"Failed to format context item: {e} | item={item}")
                continue

        return "\n".join(context_lines) if context_lines else "No relevant memories found."

    async def generate_response(
        self,
        message: str,
        retrieved_context: List[Dict[str, Any]],
        detected_mood: str,
        elder_name: str = "friend"
    ) -> str:
        """
        Generates an LLM response incorporating FAISS/Neo4j context safely.
        """
        context_string = self._format_context(retrieved_context)

        logger.info(f"Groq context for elder {elder_name}:\n{context_string}")

        system = SYSTEM_PROMPT.format(elder_name=elder_name)

        prompt = f"""
[RETRIEVED MEMORY CONTEXT]:
{context_string}

[ELDER'S CURRENT MOOD]: {detected_mood} — adjust your empathy and tone accordingly.

[ELDER'S MESSAGE]: {message}

Remember: Only use facts from the context above. If the answer is not in the context, say you don't recall.
"""

        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=256,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            return "I'm having a little trouble thinking right now. Let's just sit together."


groq_client = GroqLLMClient()