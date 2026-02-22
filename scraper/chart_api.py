import os
import json
import time
from datetime import datetime
from groq import Groq

class ChartEngine:
    def __init__(self):
        self.groq_client = None
        # 영화 데이터는 기존처럼 API를 쓸 수 있도록 키만 보관 (필요시 사용)
        self.kobis_key = os.environ.get("KOBIS_API_KEY")
        self.selected_model = "llama-3.3-70b-specdec"

    def set_groq_client(self, api_key):
        """Groq 클라이언트를 설정합니다."""
        self.groq_client = Groq(api_key=api_key)

    def get_top10_chart(self, category):
        """Groq에게 직접 물어봐서 24시간 이내의 데이터를 영어로 가져옵니다."""
        
        # K-Culture 전용 제약 조건 (연예인 배제)
        constraints = ""
        if category == "k-culture":
            constraints = "STRICT RULE: Focus ONLY on locations, food, or traditional trends. NEVER include celebrities, idols, or actors."

        prompt = f"""
        Today is {datetime.now().strftime('%B %d, 2026')}.
        Search for the MOST RECENT South Korean trends within the LAST 24 HOURS.
        Provide the Top 10 rankings for '{category}' in English.
        
        {constraints}

        [OUTPUT RULES]
        1. Translate all titles and info into English.
        2. Ensure data is from the last 24 hours. No old data from 2025 or earlier.
        3. Respond ONLY in JSON:
           {{"top10": [{{"rank": 1, "title": "English Title", "info": "Brief English Info"}}, ...]}}
        """

        try:
            chat = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.selected_model,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            return chat.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq Error for {category}: {e}")
            return json.dumps({"top10": []})
