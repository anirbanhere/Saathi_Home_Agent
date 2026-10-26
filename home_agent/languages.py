"""Small reviewed-by-code demo templates, not a claim of general language fluency."""
import re

LANGUAGES = {"en": "English", "ta": "தமிழ்", "ml": "മലയാളം", "kn": "ಕನ್ನಡ", "hi": "हिन्दी"}

COPY = {
    "en": {
        "help": "I can check a sample train, prepare a sandbox electricity payment, or plan a meal. Try: train 12627 tomorrow; pay electricity bill DEMO-1042; cook tomato rice for 2. Offline mode recognizes a small set of phrases; it is not Muse.",
        "train_prompt": "Which five-digit train number and travel date? Example: 12627 2026-11-01.",
        "train_result": "{name}: sample delay {delay} min at {station}. FIXTURE ONLY — this is not live train information. Requested date: {date}.",
        "train_missing": "No fixture is available for this train. I have not checked a live provider.",
        "bill_prompt": "What is the demo account number? Try DEMO-1042. This workflow cannot pay real bills.",
        "bill_ready": "Sandbox electricity bill for {account}: ₹{amount}. Review the details and approve using the task card. No real payment will be made.",
        "booking_prompt": "For a sandbox booking, use the travel form to choose origin, destination and date. No real tickets are issued.",
        "booking_ready": "Sandbox journey: {origin} → {destination}, {date}. Demo fare ₹{amount}. Review and approve using the task card.",
        "recipe_ready": "Cooking plan for {name}, {servings} servings. Quantities are estimates. Review missing ingredients before cooking. Mark cooked only after the meal is actually made.",
        "suggestions": "Here are meal ideas based on current stock and recent meals. Suggestions do not change inventory.",
        "inventory": "Here is the kitchen inventory. Opening stock and meal consumption are estimates; you can correct quantities.",
        "completed": "Sandbox task completed. Reference: {receipt}. No money moved and no real ticket was issued.",
        "cancelled": "Task cancelled. No sandbox action was executed.",
        "meal_done": "Meal recorded. Estimated ingredient usage was deducted once from inventory.",
    },
    "ta": {
        "help": "மாதிரி ரயில் நிலை, சோதனை மின் கட்டணம், சமையல் திட்டம் ஆகியவற்றில் உதவ முடியும். உதாரணம்: ரயில் 12627 நாளை. இது சில சொற்றொடர்களை மட்டும் அறியும் ஆஃப்லைன் முறை; Muse இணைக்கப்படவில்லை.",
        "train_prompt": "ஐந்து இலக்க ரயில் எண்ணையும் பயணத் தேதியையும் சொல்லுங்கள். உதாரணம்: 12627 2026-11-01.",
        "train_result": "{name}: {station} நிலையத்தில் மாதிரி தாமதம் {delay} நிமிடங்கள். இது மாதிரித் தகவல் மட்டுமே; நேரடி ரயில் நிலை அல்ல. கேட்ட தேதி: {date}.",
        "train_missing": "இந்த ரயிலுக்கான மாதிரித் தகவல் இல்லை. நேரடி சேவையில் சரிபார்க்கவில்லை.",
        "bill_prompt": "சோதனைக் கணக்கு எண் என்ன? DEMO-1042 பயன்படுத்தலாம். உண்மையான கட்டணம் செலுத்தப்படாது.",
        "bill_ready": "{account} கணக்கின் சோதனை மின் கட்டணம் ₹{amount}. விவரங்களைப் பார்த்து பணி அட்டையில் ஒப்புதல் அளிக்கவும். உண்மையான பணப் பரிமாற்றம் இல்லை.",
        "booking_prompt": "சோதனை முன்பதிவுக்கு பயணப் படிவத்தில் புறப்படும் இடம், சேரும் இடம், தேதி ஆகியவற்றைத் தேர்ந்தெடுக்கவும். உண்மையான பயணச்சீட்டு வழங்கப்படாது.",
        "booking_ready": "சோதனைப் பயணம்: {origin} → {destination}, {date}. மாதிரிக் கட்டணம் ₹{amount}. பணி அட்டையில் சரிபார்த்து ஒப்புதல் அளிக்கவும்.",
        "recipe_ready": "{name}: {servings} பேருக்கான சமையல் திட்டம். அளவுகள் மதிப்பீடுகள். இல்லாத பொருட்களைச் சரிபார்க்கவும். உணவு தயாரான பிறகே சமைத்ததாகப் பதிவு செய்யவும்.",
        "suggestions": "இருப்பிலுள்ள பொருட்களையும் அண்மைய உணவுகளையும் வைத்து சில பரிந்துரைகள். இவை இருப்பைக் குறைக்காது.",
        "inventory": "சமையலறை இருப்பு இதோ. ஆரம்ப இருப்பும் பயன்படுத்திய அளவும் மதிப்பீடுகள்; அவற்றைத் திருத்தலாம்.",
        "completed": "சோதனைப் பணி முடிந்தது. குறிப்பு: {receipt}. உண்மையான பணப் பரிமாற்றமோ பயணச்சீட்டோ இல்லை.",
        "cancelled": "பணி ரத்து செய்யப்பட்டது. சோதனை நடவடிக்கை எதுவும் செயல்படுத்தப்படவில்லை.",
        "meal_done": "உணவு பதிவு செய்யப்பட்டது. மதிப்பிடப்பட்ட பொருட்களின் பயன்பாடு இருப்பிலிருந்து ஒருமுறை குறைக்கப்பட்டது.",
    },
    "ml": {
        "help": "മാതൃകാ ട്രെയിൻ നില, പരീക്ഷണ വൈദ്യുതി ബിൽ, പാചക പദ്ധതി എന്നിവയിൽ സഹായിക്കാം. ഉദാഹരണം: ട്രെയിൻ 12627 നാളെ. ഇത് ചില വാക്കുകൾ തിരിച്ചറിയുന്ന ഓഫ്‌ലൈൻ രീതിയാണ്; Muse ബന്ധിപ്പിച്ചിട്ടില്ല.",
        "train_prompt": "അഞ്ചക്ക ട്രെയിൻ നമ്പറും യാത്രാ തീയതിയും പറയൂ. ഉദാഹരണം: 12627 2026-11-01.",
        "train_result": "{name}: {station} സ്റ്റേഷനിൽ മാതൃകാ വൈകൽ {delay} മിനിറ്റ്. ഇത് മാതൃക മാത്രമാണ്; തത്സമയ ട്രെയിൻ വിവരമല്ല. ആവശ്യപ്പെട്ട തീയതി: {date}.",
        "train_missing": "ഈ ട്രെയിനിന് മാതൃകാ വിവരം ലഭ്യമല്ല. തത്സമയ സേവനത്തിൽ പരിശോധിച്ചിട്ടില്ല.",
        "bill_prompt": "പരീക്ഷണ അക്കൗണ്ട് നമ്പർ എന്താണ്? DEMO-1042 ഉപയോഗിക്കാം. യഥാർത്ഥ ബിൽ അടയ്ക്കില്ല.",
        "bill_ready": "{account} അക്കൗണ്ടിന്റെ പരീക്ഷണ വൈദ്യുതി ബിൽ ₹{amount}. വിവരങ്ങൾ പരിശോധിച്ച് ടാസ്‌ക് കാർഡിൽ അംഗീകരിക്കുക. യഥാർത്ഥ പണം കൈമാറില്ല.",
        "booking_prompt": "പരീക്ഷണ ബുക്കിങ്ങിന് യാത്രാ ഫോമിൽ പുറപ്പെടുന്ന സ്ഥലം, എത്തുന്ന സ്ഥലം, തീയതി എന്നിവ തിരഞ്ഞെടുക്കൂ. യഥാർത്ഥ ടിക്കറ്റ് നൽകില്ല.",
        "booking_ready": "പരീക്ഷണ യാത്ര: {origin} → {destination}, {date}. മാതൃകാ നിരക്ക് ₹{amount}. ടാസ്‌ക് കാർഡിൽ പരിശോധിച്ച് അംഗീകരിക്കൂ.",
        "recipe_ready": "{name}: {servings} പേർക്കുള്ള പാചക പദ്ധതി. അളവുകൾ ഏകദേശമാണ്. ഇല്ലാത്ത ചേരുവകൾ പരിശോധിക്കുക. ഭക്ഷണം തയ്യാറാക്കിയ ശേഷമേ പൂർത്തിയായതായി രേഖപ്പെടുത്താവൂ.",
        "suggestions": "ഇപ്പോഴത്തെ ചേരുവകളും അടുത്തിടെ പാകം ചെയ്ത ഭക്ഷണവും അടിസ്ഥാനമാക്കിയുള്ള നിർദേശങ്ങൾ. ഇവ സ്റ്റോക്ക് മാറ്റില്ല.",
        "inventory": "അടുക്കളയിലെ സ്റ്റോക്ക് ഇതാ. ആദ്യ സ്റ്റോക്കും ഉപയോഗവും ഏകദേശമാണ്; അളവുകൾ തിരുത്താം.",
        "completed": "പരീക്ഷണ ടാസ്‌ക് പൂർത്തിയായി. റഫറൻസ്: {receipt}. യഥാർത്ഥ പണമിടപാടോ ടിക്കറ്റോ ഇല്ല.",
        "cancelled": "ടാസ്‌ക് റദ്ദാക്കി. പരീക്ഷണ നടപടിയൊന്നും നടത്തിയിട്ടില്ല.",
        "meal_done": "ഭക്ഷണം രേഖപ്പെടുത്തി. ഏകദേശ ചേരുവ ഉപയോഗം സ്റ്റോക്കിൽ നിന്ന് ഒരിക്കൽ കുറച്ചു.",
    },
    "kn": {
        "help": "ಮಾದರಿ ರೈಲು ಸ್ಥಿತಿ, ಪರೀಕ್ಷಾ ವಿದ್ಯುತ್ ಬಿಲ್ ಮತ್ತು ಅಡುಗೆ ಯೋಜನೆಗೆ ಸಹಾಯ ಮಾಡಬಹುದು. ಉದಾಹರಣೆ: ರೈಲು 12627 ನಾಳೆ. ಇದು ಕೆಲವು ಪದಗಳನ್ನು ಮಾತ್ರ ಗುರುತಿಸುವ ಆಫ್‌ಲೈನ್ ವಿಧಾನ; Muse ಸಂಪರ್ಕಿಸಿಲ್ಲ.",
        "train_prompt": "ಐದು ಅಂಕಿಯ ರೈಲು ಸಂಖ್ಯೆ ಮತ್ತು ಪ್ರಯಾಣದ ದಿನಾಂಕ ಹೇಳಿ. ಉದಾಹರಣೆ: 12627 2026-11-01.",
        "train_result": "{name}: {station} ನಿಲ್ದಾಣದಲ್ಲಿ ಮಾದರಿ ವಿಳಂಬ {delay} ನಿಮಿಷ. ಇದು ಮಾದರಿ ಮಾತ್ರ; ನೇರ ರೈಲು ಮಾಹಿತಿ ಅಲ್ಲ. ಕೇಳಿದ ದಿನಾಂಕ: {date}.",
        "train_missing": "ಈ ರೈಲಿಗೆ ಮಾದರಿ ಮಾಹಿತಿ ಇಲ್ಲ. ನೇರ ಸೇವೆಯಲ್ಲಿ ಪರಿಶೀಲಿಸಿಲ್ಲ.",
        "bill_prompt": "ಪರೀಕ್ಷಾ ಖಾತೆ ಸಂಖ್ಯೆ ಏನು? DEMO-1042 ಬಳಸಬಹುದು. ನಿಜವಾದ ಬಿಲ್ ಪಾವತಿಯಾಗುವುದಿಲ್ಲ.",
        "bill_ready": "{account} ಖಾತೆಯ ಪರೀಕ್ಷಾ ವಿದ್ಯುತ್ ಬಿಲ್ ₹{amount}. ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಟಾಸ್ಕ್ ಕಾರ್ಡ್‌ನಲ್ಲಿ ಅನುಮೋದಿಸಿ. ನಿಜವಾದ ಹಣ ವರ್ಗಾವಣೆಯಾಗುವುದಿಲ್ಲ.",
        "booking_prompt": "ಪರೀಕ್ಷಾ ಬುಕ್ಕಿಂಗ್‌ಗಾಗಿ ಪ್ರಯಾಣದ ಫಾರ್ಮ್‌ನಲ್ಲಿ ಹೊರಡುವ ಸ್ಥಳ, ಸೇರುವ ಸ್ಥಳ ಮತ್ತು ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ. ನಿಜವಾದ ಟಿಕೆಟ್ ನೀಡುವುದಿಲ್ಲ.",
        "booking_ready": "ಪರೀಕ್ಷಾ ಪ್ರಯಾಣ: {origin} → {destination}, {date}. ಮಾದರಿ ದರ ₹{amount}. ಟಾಸ್ಕ್ ಕಾರ್ಡ್‌ನಲ್ಲಿ ಪರಿಶೀಲಿಸಿ ಅನುಮೋದಿಸಿ.",
        "recipe_ready": "{name}: {servings} ಜನರಿಗೆ ಅಡುಗೆ ಯೋಜನೆ. ಪ್ರಮಾಣಗಳು ಅಂದಾಜು. ಇಲ್ಲದ ಪದಾರ್ಥಗಳನ್ನು ಪರಿಶೀಲಿಸಿ. ಅಡುಗೆ ಮಾಡಿದ ನಂತರವೇ ಪೂರ್ಣಗೊಂಡಿದೆ ಎಂದು ದಾಖಲಿಸಿ.",
        "suggestions": "ಈಗಿನ ದಾಸ್ತಾನು ಮತ್ತು ಇತ್ತೀಚಿನ ಊಟಗಳ ಆಧಾರದ ಮೇಲೆ ಸಲಹೆಗಳು. ಇವು ದಾಸ್ತಾನು ಬದಲಿಸುವುದಿಲ್ಲ.",
        "inventory": "ಅಡುಗೆಮನೆಯ ದಾಸ್ತಾನು ಇಲ್ಲಿದೆ. ಆರಂಭದ ಪ್ರಮಾಣ ಮತ್ತು ಬಳಕೆ ಅಂದಾಜುಗಳು; ಪ್ರಮಾಣಗಳನ್ನು ಸರಿಪಡಿಸಬಹುದು.",
        "completed": "ಪರೀಕ್ಷಾ ಟಾಸ್ಕ್ ಪೂರ್ಣಗೊಂಡಿದೆ. ಉಲ್ಲೇಖ: {receipt}. ನಿಜವಾದ ಹಣ ವರ್ಗಾವಣೆ ಅಥವಾ ಟಿಕೆಟ್ ಇಲ್ಲ.",
        "cancelled": "ಟಾಸ್ಕ್ ರದ್ದಾಗಿದೆ. ಯಾವುದೇ ಪರೀಕ್ಷಾ ಕ್ರಮ ಕಾರ್ಯಗತವಾಗಿಲ್ಲ.",
        "meal_done": "ಊಟ ದಾಖಲಿಸಲಾಗಿದೆ. ಅಂದಾಜು ಪದಾರ್ಥಗಳ ಬಳಕೆಯನ್ನು ದಾಸ್ತಾನಿನಿಂದ ಒಮ್ಮೆ ಕಡಿತಗೊಳಿಸಲಾಗಿದೆ.",
    },
    "hi": {
        "help": "मैं नमूना ट्रेन स्थिति, परीक्षण बिजली भुगतान और खाना बनाने की योजना में मदद कर सकता हूँ। उदाहरण: ट्रेन 12627 कल। ऑफलाइन मोड कुछ वाक्यांश ही पहचानता है; Muse अभी जुड़ा नहीं है।",
        "train_prompt": "पाँच अंकों का ट्रेन नंबर और यात्रा की तारीख बताइए। उदाहरण: 12627 2026-11-01।",
        "train_result": "{name}: {station} स्टेशन पर नमूना देरी {delay} मिनट। यह केवल नमूना है, लाइव ट्रेन जानकारी नहीं। माँगी गई तारीख: {date}।",
        "train_missing": "इस ट्रेन का नमूना उपलब्ध नहीं है। लाइव सेवा से जाँच नहीं की गई है।",
        "bill_prompt": "परीक्षण खाता नंबर क्या है? DEMO-1042 इस्तेमाल कर सकते हैं। असली बिल का भुगतान नहीं होगा।",
        "bill_ready": "{account} खाते का परीक्षण बिजली बिल ₹{amount} है। विवरण देखकर टास्क कार्ड पर मंज़ूरी दें। असली पैसे नहीं भेजे जाएँगे।",
        "booking_prompt": "परीक्षण बुकिंग के लिए यात्रा फ़ॉर्म में शुरुआती स्टेशन, गंतव्य और तारीख चुनें। असली टिकट जारी नहीं होगा।",
        "booking_ready": "परीक्षण यात्रा: {origin} → {destination}, {date}। नमूना किराया ₹{amount}। टास्क कार्ड पर जाँचकर मंज़ूरी दें।",
        "recipe_ready": "{name}: {servings} लोगों के लिए खाना बनाने की योजना। मात्राएँ अनुमानित हैं। कम सामग्री जाँचें। खाना बनने के बाद ही पका हुआ दर्ज करें।",
        "suggestions": "मौजूदा सामग्री और हाल के भोजन के आधार पर सुझाव। सुझाव से स्टॉक नहीं बदलता।",
        "inventory": "रसोई का स्टॉक यहाँ है। शुरुआती स्टॉक और खपत अनुमानित हैं; आप मात्रा सुधार सकते हैं।",
        "completed": "परीक्षण काम पूरा हुआ। संदर्भ: {receipt}। असली पैसे नहीं भेजे गए और असली टिकट जारी नहीं हुआ।",
        "cancelled": "काम रद्द हुआ। कोई परीक्षण कार्रवाई नहीं की गई।",
        "meal_done": "भोजन दर्ज हुआ। सामग्री की अनुमानित खपत स्टॉक से एक बार घटाई गई।",
    },
}


def say(language: str, key: str, **values) -> str:
    return COPY.get(language, COPY["en"])[key].format(**values)


def detect_language(value: str, fallback: str) -> str:
    for pattern, language in [(r"[\u0b80-\u0bff]", "ta"), (r"[\u0d00-\u0d7f]", "ml"),
                              (r"[\u0c80-\u0cff]", "kn"), (r"[\u0900-\u097f]", "hi")]:
        if re.search(pattern, value):
            return language
    return fallback
