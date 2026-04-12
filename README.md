# منصة إحسان (Ihsane Platform) 🎓

**إحسان** (Ihsane) - منصة تعليمية بيداغوجية ذكية وتفاعلية مخصصة للطور الابتدائي (من 6 إلى 11 سنة) مبنية خصيصاً للتوافق مع المنهاج التربوي الجزائري. تهدف المنصة إلى التشخيص الدقيق للتعثرات الدراسية وتقديم مسارات معالجة فردية تعتمد على مقاربة تجمع بين الكفاءة المعرفية، الدعم الوجداني، والبعد التربوي القيمي.

---

## 🎯 الرؤية والرسالة (Vision & Mission)

تغيير مفهوم "الخطأ" في العملية التعليمية من إخفاق إلى **"مؤشر ذكي للتعلم"**. تعمل إحسان على مرافقة المتعلم بمسارات تكيفية ذكية (Adaptive Learning) بدلاً من التكرار النمطي، مع ربط الأولياء والأساتذة (الخبراء البيداغوجيين) بلوحات قياس تحليلية دقيقة تساهم في تحقيق نتائج أفضل.

---

## ✨ المميزات الرئيسية

### 1. 🔍 محرك التشخيص الذكي (Adaptive Diagnostic Engine)
- تقييم أولي تفاعلي وديناميكي يكيف صعوبة الأسئلة بناءً على سرعة ودقة إجابات التلميذ
- تصنيف الأخطاء آلياً إلى: أخطاء تخص الموارد، أخطاء في منهجية الحل، أو أخطاء عرضية
- خوارزمية Bayesian Knowledge Tracing (BKT) لتتبع مستوى إتقان كل كفاءة

### 2. 🛤️ مسارات المعالجة التكيفية (Remediation Pathways)
- توجيه التلميذ نحو "كبسولات معرفية" (Micro-learning Atoms) تعالج ثغرة المفاهيم المحددة
- التدرج في تقديم المعلومة (من المحسوس إلى المجرد)
- التعديل التلقائي لمستوى الصعوبة لتجنب الملل أو الإحباط

### 3. 👨‍👩‍👧 لوحة تحكم الأولياء (Parent Dashboard)
- واجهة مبسطة ومصممة للهواتف المحمولة
- رسائل تربوية تحفيزية بدلاً من مجرد أرقام صارمة
- توصيات عملية يومية ومبسطة للوالد

### 4. 📊 لوحات التحليلات للخبراء (Expert Analytics)
- خرائط حرارية (Heatmaps) لمستويات تحكم التلاميذ في الكفاءات
- الفرز الآلي وتشكيل "مجموعات معالجة"
- تصدير تقارير PDF/CSV

### 5. 🔔 نظام التنبيهات البيداغوجية (Pedagogical Alerts)
- إشعارات ذكية عند تسجيل تعثر مستمر
- تصنيف التنبيهات: INFO, WARNING, CRITICAL

### 6. 🌐 دعم ثنائي اللغة (Bilingual)
- واجهة عربية (RTL) وفرنسية (LTR)
- تبديل فوري للغة دون إعادة تحميل
- خطوط محسّنة للعربية (Tajawal, Cairo) واللاتينية (Plus Jakarta Sans)

---

## 👥 أدوار المستخدمين

| الدور | الوصف |
|-------|-------|
| **🎒 التلميذ** | يتفاعل مع المنصة عبر واجهة ممتعة، يحقق مساره الدراسي عبر التقييم والمعالجة |
| **👨‍👩‍👦 الولي** | يراقب التقدم، يدير حسابات أبنائه، يتلقى إشعارات وتوجيهات |
| **👨‍🏫 الخبير البيداغوجي** | يصمم الوحدات، ينشئ بنوك الأسئلة، يتابع مؤشرات الأداء |

---

## 🛠 البنية التقنية

### الواجهة الأمامية (Frontend)
- **Vue 3** with Composition API
- **TypeScript** for type safety
- **Pinia** for state management
- **Tailwind CSS** for styling
- **vue-i18n** for internationalization
- **Vite PWA** for offline support

### الواجهة الخلفية (Backend)
- **FastAPI** with Python 3.12+
- **SQLAlchemy** with PostgreSQL 16+
- **Pydantic v2** for validation
- **JWT** authentication
- **Alembic** for migrations
- **Celery** for background tasks

### البنية التحتية
- **Docker** containerization
- **Valkey** (Redis fork) for caching
- **Nginx** reverse proxy
- **OVH Cloud** hosting
- **Cloudflare** CDN

---

## 🚀 دليل البدء السريع (Quickstart)

### المتطلبات الأساسية
- Docker & Docker Compose
- Node.js 20+ (للتطوير المحلي)
- Python 3.12+ (للتطوير المحلي)

### التشغيل عبر Docker

```bash
# استنساخ المستودع
git clone https://github.com/your-org/ihsane-platform.git
cd ihsane-platform

# تشغيل الخدمات
docker compose up -d

# إنشاء الجداول
-docker compose exec backend alembic upgrade head
```

### التطوير المحلي

**الواجهة الخلفية:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # أو venv\Scripts\activate على Windows
pip install -r requirements.txt
alembic upgrade head
fastapi dev app/main.py --port 8000
```

**الواجهة الأمامية:**
```bash
cd frontend
pnpm install
pnpm run dev
```

---

## 📂 هيكل المشروع

```
ihsane-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration & security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── tests/            # PyTest test suite
│   └── alembic/          # Database migrations
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue components
│   │   ├── views/        # Page views
│   │   ├── stores/       # Pinia stores
│   │   ├── services/     # API services
│   │   └── locales/      # i18n translations
│   └── public/           # Static assets
├── specs/                # Specification documents
└── docker-compose.yml    # Docker orchestration
```

---

## 🔐 الأمان

- ✅ **JWT Authentication** - توكنات ذات صلاحية محدودة (30 دقيقة)
- ✅ **bcrypt Hashing** - لتشفير كلمات المرور والرموز السرية
- ✅ **CORS Protection** - حماية طلبات المصدر المتقاطع
- ✅ **RBAC** - التحكم في الوصول المبني على الأدوار
- ✅ **Rate Limiting** - على نقاط نهاية المصادقة
- ✅ **CSP Headers** - سياسة أمان المحتوى

---

## 🧪 الاختبارات

```bash
# اختبارات الواجهة الخلفية
cd backend
pytest --cov=app --cov-report=html

# اختبارات الواجهة الأمامية
cd frontend
pnpm test

# اختبارات التكامل
pytest tests/integration/
```

---

## 📝 الترخيص

هذا المشروع مرخص بموجب [MIT License](LICENSE).

---

## 🤝 المساهمة

نرحب بمساهماتكم! يرجى قراءة [دليل المساهمة](CONTRIBUTING.md) أولاً.

---

<div align="center">
  
**بُنيت منصة إحسان لتكون "المرافق الرقمي الأول" للتلميذ الجزائري**

🌟 ليس كبديل وحيد، بل كسند يعيد أنسنة التعلم في العصر الرقمي 🌟

</div>