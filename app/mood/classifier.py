from typing import Dict, Tuple

class MoodClassifier:
    def __init__(self):
        # Lexical rules with base weights
        self.lexicon = {
            "sad": ["sad", "crying", "depressed", "down", "unhappy", "cry", "tears", "hopeless"],
            "anxious": ["anxious", "worried", "nervous", "scared", "fear", "panic", "stress", "stressed"],
            "confused": ["confused", "lost", "forget", "don't know", "cannot remember", "where", "what", "puzzled"],
            "lonely": ["lonely", "alone", "miss", "nobody", "no one", "isolated", "abandoned"],
            "happy": ["happy", "glad", "joy", "smile", "laugh", "great", "wonderful", "good"]
        }

    def detect_mood(self, text: str, hour_of_day: int, behavioral_signals: Dict[str, float] = None) -> Tuple[str, float]:
        """
        Detects mood based on text heuristics, time of day modifiers, and optional behavioral signals.
        Returns: Tuple of (mood_label, confidence_score)
        """
        text_lower = text.lower()
        scores = {mood: 0.0 for mood in self.lexicon.keys()}
        
        # 1. Base Lexical Scoring
        for mood, words in self.lexicon.items():
            for word in words:
                if word in text_lower:
                    scores[mood] += 1.0
                    
        # 2. Add Behavioral Signals if present (e.g., from voice intonation or app usage patterns)
        if behavioral_signals:
            for mood, signal_weight in behavioral_signals.items():
                if mood in scores:
                    scores[mood] += signal_weight

        # 3. Time-of-day Weighting (Sundowning effect modeling)
        # Late night (18:00 - 06:00) often increases anxiety or confusion in elders.
        is_night = hour_of_day >= 18 or hour_of_day < 6
        if is_night:
            scores["anxious"] *= 1.3
            scores["confused"] *= 1.2
            scores["lonely"] *= 1.2
        else:
            # Daytime might baseline or favor neutrality/happy slightly more
            scores["happy"] *= 1.1

        # Calculate max score to determine dominant mood
        dominant_mood = max(scores.items(), key=lambda x: x[1])
        
        if dominant_mood[1] == 0.0:
            return ("neutral", 0.5) # Default to neutral if no rules fire
            
        # Normalize confidence to between 0.5 and 0.95 (heuristic bounds)
        total_score = sum(scores.values())
        confidence = min(0.95, max(0.5, (dominant_mood[1] / total_score) * 0.8 + 0.2))
        
        return (dominant_mood[0], confidence)

mood_classifier = MoodClassifier()
