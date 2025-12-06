search_news_stories_system_prompt = """
You are given a sequence of subtitles in the format:
[start-end] text

Where `start` and `end` are timestamps (float numbers, seconds), and `text` is the subtitle content.

Your task:
1. Identify complete news stories.
   - A story must have a clear beginning and a clear ending.
   - If a story is incomplete or no news story is present, do not include it.
   - If multiple stories exist, return all of them.
2. Return the result strictly as raw JSON (no formatting, no comments, no extra text).
3. JSON format:
{"intervals": ["start-end", "start-end"]}

- The `intervals` field is an array of strings with the time ranges of news stories.
- If no complete news stories are found, return:
{"intervals": []}

---

### Examples

Example 1  
Input:
[1756975421.89-1756975440.78] No immediate reports of casualties, but infrastructure damage is under assessment.  
[1756975441.00-1756975460.86] Stay tuned for live updates from our correspondents on the ground.  

Output:
{"intervals": []}

(Reason: story is incomplete, no clear ending)

---

Example 2  
Input:
[1756728129.98-1756728150.22] Breaking news just in. A powerful earthquake has struck the capital city.  
[1756728150.23-1756728170.55] Initial reports indicate widespread damage and possible casualties.  
[1756728170.56-1756728190.12] Authorities are mobilizing emergency services to affected areas.  
[1756728190.13-1756728198.87] That concludes our breaking news update. Stay with us for more information.  

Output:
{"intervals": ["1756728129.98-1756728198.87"]}

---

Example 3  
Input:
[1756991110.11-1756991129.05] The sports team is preparing for the final match tomorrow.  
[1756991130.00-1756991150.22] Fans are already gathering in the city to celebrate.  

Output:
{"intervals": []}

(Reason: not a news story, just casual reporting)

---

Example 4 (multiple stories)  
Input:
[1757000100.00-1757000120.45] Breaking news: Heavy floods are reported in the northern region.  
[1757000120.46-1757000140.77] Rescue operations are underway.  
[1757000140.78-1757000160.90] That’s the latest on the flooding.  
[1757000200.00-1757000220.55] In other news, the stock market closed higher today.  
[1757000220.56-1757000240.88] Analysts attribute the gains to strong tech earnings.  
[1757000240.89-1757000260.33] That concludes the financial update.  

Output:
{"intervals": ["1757000100.00-1757000160.90", "1757000200.00-1757000260.33"]}

Respond using JSON.
"""


summarize_news_story_system_en_prompt = """
You are given subtitles of a news story in the format:
[start-end] text

Where `start` and `end` are timestamps (float numbers, seconds), and `text` is the subtitle content.

Your task is to produce a structured summary in JSON format with the following fields:

1) "title": A short and clear headline that captures the main point of the news story.  
2) "summary": A concise summary of the news story in the **english language of the subtitles**.  
3) "summary_ru": A concise summary of the news story in Russian.
4) "temperature": An evaluation of the news story tone or temperature (for example: "neutral temperature", "high tension", "optimistic").  
5) "tags": An array of tags representing the key entities, people, or topics in the story.  

Tag formatting rules:
- Use underscores instead of spaces, e.g. "United States" -> "United_States".  
- Replace hyphens with underscores, e.g. "Well-being" -> "Well_being".  
- Abbreviations should be written without dots, e.g. "U.S.A" -> "USA".  
- Keep tags concise, standardized, and consistent.  

The model must output strictly raw JSON with no extra text, comments, or formatting.  

Output format:
{"title": "title", "summary": "summary", "summary_ru": "Краткое содержание на русском языке", "temperature": "temperature", "tags": ["tag1", "tag2"]}

---

### Examples

Example 1  
Input:
[1756728129.98-1756728150.22] Breaking news just in. A powerful earthquake has struck the capital city.  
[1756728150.23-1756728170.55] Initial reports indicate widespread damage and possible casualties.  
[1756728170.56-1756728190.12] Authorities are mobilizing emergency services to affected areas.  
[1756728190.13-1756728198.87] That concludes our breaking news update. Stay with us for more information.  

Output:
{"title": "Powerful earthquake strikes capital city", "summary": "A powerful earthquake struck the capital city, causing widespread damage and possible casualties. Authorities are mobilizing emergency services.", "summary_ru": "Мощное землетрясение произошло в столице, вызвав значительные разрушения и возможные жертвы. Власти мобилизуют экстренные службы.", "temperature": "high tension", "tags": ["Earthquake", "Capital_City", "Authorities"]}

---

Example 2  
Input:
[1757000200.00-1757000220.55] In other news, the stock market closed higher today.  
[1757000220.56-1757000240.88] Analysts attribute the gains to strong tech earnings.  
[1757000240.89-1757000260.33] That concludes the financial update.  

Output:
{"title": "Stock market closes higher on strong tech earnings", "summary": "The stock market closed higher today due to strong tech earnings.", "summary_ru": "Рынок акций закрылся с ростом благодаря сильной прибыли технологических компаний.", "temperature": "neutral temperature", "tags": ["Stock_Market", "Tech_Earnings"]}

---

Example 3  
Input:
[1757010000.00-1757010020.10] Former US President Donald Trump held a rally today in Florida.  
[1757010020.11-1757010040.45] He criticized the current administration’s policies on immigration.  
[1757010040.46-1757010060.77] Supporters chanted slogans as he promised to restore stronger border controls.  
[1757010060.78-1757010080.55] That concludes our political coverage for now.  

Output:
{"title": "Trump criticizes immigration policies at Florida rally", "summary": "Donald Trump held a rally in Florida where he criticized the administration’s immigration policies and promised stronger border controls.", "summary_ru": "Дональд Трамп провёл митинг во Флориде, где раскритиковал иммиграционную политику администрации и пообещал усилить контроль на границе.", "temperature": "high tension", "tags": ["Trump", "Florida", "Immigration", "Border_Control", "Administration"]}

Respond using JSON.
"""


summarize_news_story_system_ru_prompt = """
Тебе переданы субтитры новостного сюжета в формате:
[start-end] text

Где start и end — временные отметки (числа с плавающей точкой, секунды), а text — содержание субтитра.

Твоя задача — сформировать структурированное резюме в формате JSON со следующими полями:

1) "title" — короткий и чёткий заголовок, отражающий основную суть новости.
2) "summary" — краткое содержание новостного сюжета.
3) "temperature" — оценка тона или «температуры» новости (например: "нейтральная температура", "высокая напряжённость", "оптимистичный").
4) "tags" — массив тегов, отражающих ключевые сущности, людей или темы сюжета.

Правила оформления тегов:
- Используй нижние подчёркивания вместо пробелов. Пример: "Северная Америка" → "Северная_Америка"
- Тире заменяй на подчёркивания. Пример: "Социально-экономический" → "Социально_экономический"
- Аббревиатуры без точек. Пример: "Р.Ф." → "РФ"
- Теги должны быть краткими, стандартизированными и единообразными.

Модель должна вывести строго сырой JSON, без дополнительных комментариев, текста или форматирования.

Формат вывода:
{"title": "title", "summary": "summary", "temperature": "temperature", "tags": ["tag1", "tag2"]}

Примеры:
Пример 1.
Ввод:
[1756728129.98-1756728150.22] Срочная новость. Мощное землетрясение произошло в столице.
[1756728150.23-1756728170.55] Поступают сообщения о серьёзных разрушениях и возможных жертвах.
[1756728170.56-1756728190.12] Власти направляют экстренные службы в пострадавшие районы.
[1756728190.13-1756728198.87] Это всё на данный момент. Следите за обновлениями.

Вывод:
{"title": "Мощное землетрясение в столице", "summary": "В столице произошло сильное землетрясение, есть разрушения и возможные жертвы. Экстренные службы направлены в пострадавшие районы.", "temperature": "высокая напряжённость", "tags": ["Землетрясение", "Столица", "Власти"]}

Пример 2.
Ввод:
[1757000200.00-1757000220.55] К другим новостям: фондовый рынок закрылся ростом.
[1757000220.56-1757000240.88] Аналитики связывают рост с сильными результатами компаний технологического сектора.
[1757000240.89-1757000260.33] Это был финансовый обзор.

Вывод:
{"title": "Фондовый рынок вырос на фоне сильных техрезультатов", "summary": "Фондовый рынок завершил день ростом благодаря сильным отчётам технологических компаний.", "temperature": "нейтральная температура", "tags": ["Фондовый_рынок", "Технологический_сектор"]}

Пример 3.
Ввод:
[1757010000.00-1757010020.10] Бывший президент США Дональд Трамп провёл митинг во Флориде.
[1757010020.11-1757010040.45] Он раскритиковал политику нынешней администрации в области иммиграции.
[1757010040.46-1757010060.77] Сторонники скандировали лозунги, пока он обещал усилить контроль на границах.
[1757010060.78-1757010080.55] Это всё по политическим новостям.

Вывод:
{"title": "Трамп критикует иммиграционную политику на митинге во Флориде", "summary": "Дональд Трамп провёл митинг во Флориде, где раскритиковал иммиграционную политику администрации и пообещал усилить контроль на границах.", "temperature": "высокая напряжённость", "tags": ["Трамп", "Флорида", "Иммиграция", "Контроль_границ", "Администрация"]}

Отвечай в формате JSON по образцу.
"""
