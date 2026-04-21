# ⚡ JobHunter WebWide — Data Analysis Job Search Engine

نسخة مستقلة من JobHunter للبحث الأوسع عن الوظائف عبر الويب (وليس LinkedIn فقط).

---

## 🚀 التثبيت والتشغيل

### الخطوة 1: تثبيت Python
تأكد من وجود Python 3.10+ على جهازك.

### الخطوة 2: تثبيت المكتبات المطلوبة
```bash
pip install -r requirements.txt
```

### الخطوة 3: تشغيل البرنامج
```bash
python main.py
```

---

## 📦 المكتبات المطلوبة

```
PySide6>=6.5.0
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
openpyxl>=3.1.0
lxml>=4.9.0
```

---

## ✨ المميزات

### 🔍 البحث
- يبحث في **Indeed, Wuzzuf, LinkedIn, Glassdoor, Bayt, RemoteOK**
- يدعم مصادر ويب إضافية عبر APIs عامة: **Remotive, Arbeitnow, TheMuse, Jobicy**
- مناسب للبحث العالمي وليس منصة واحدة فقط
- 15+ مسمى وظيفي لتحليل البيانات
- بحث متوازي بـ Multi-threading لأقصى سرعة

### 🎛 الفلاتر
- فلتر بالدولة/المدينة
- فلتر بمستوى الخبرة (Entry / Junior / Mid)
- فلتر بنوع الوظيفة (Full Time / Remote / Hybrid / Internship...)
- فلتر نصي لحظي على النتائج
- زر Remote فقط

### 📊 إدارة النتائج
- جدول منظم بجميع تفاصيل الوظيفة
- انقر مرتين على أي وظيفة لفتح رابط التقديم مباشرة
- إضافة وظائف إلى المفضلة (★)
- تصدير لـ CSV أو Excel
- إزالة التكرار تلقائياً

### 🎨 الواجهة
- تصميم Dark Mode احترافي
- تنبيه بصري عند ظهور وظائف جديدة
- شريط تقدم أثناء البحث

---

## 📁 هيكل الملفات

```
JobHunter_WebWide/
├── main.py              # نقطة الدخول
├── requirements.txt     # المكتبات
├── core/
│   ├── models.py        # نماذج البيانات
│   ├── scrapers.py      # محركات الكشط من كل موقع
│   └── search_manager.py # إدارة البحث المتوازي
└── ui/
    ├── main_window.py   # النافذة الرئيسية
    └── styles.py        # الأنماط والألوان
```

---

## ⚠️ ملاحظات مهمة

1. **بعض المواقع** مثل LinkedIn وGlassdoor قد تطلب تسجيل دخول أو تحظر الكشط الآلي. البرنامج يستخدم طرقاً مشروعة مثل Public Search Pages.

2. **Wuzzuf** هو الأفضل للوظائف في مصر والشرق الأوسط.

3. **RemoteOK** ممتاز للوظائف الريموت الدولية.

4. لتحسين النتائج، أدخل موقعك مثل "Cairo" أو "Egypt" في خانة الدولة.

---

## 🔧 استكشاف الأخطاء

**مشكلة: لا تظهر نتائج**
- تحقق من اتصال الإنترنت
- قد تكون المواقع تمنع الكشط مؤقتاً — انتظر دقيقة وأعد المحاولة

**مشكلة: خطأ في التثبيت**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**مشكلة: PySide6 لا تعمل**
```bash
pip install PySide6 --force-reinstall
```
