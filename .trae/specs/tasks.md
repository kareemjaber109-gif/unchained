# خطة تنفيذ مشروع kopo (KOPO)

مشتقة من spec.md بتاريخ 30 سبتمبر 2026

---

## Task 1: إعدادات الأمان الأساسية في settings.py + إعداد مسار Admin جديد

**الأولوية:** عالي
**الحالة:** pending
**يغطي:** AC-6, AC-10, SEC-1, SEC-2, SEC-5

### الوصف
تعديل ملف config/settings.py ليتضمن:
1. توليد SECRET_KEY جديد عشوائي وطويل (بدون django-insecure-) — يُحفظ في نفس الملف
2. تغيير مسار الـ Admin من `/admin/` إلى `/kopo-manage/` (مع تعديل urls.py الجذري أيضاً)
3. إضافة إعدادات الأمان:
   - CSRF_COOKIE_HTTPONLY = True
   - SESSION_COOKIE_HTTPONLY = True
   - SESSION_COOKIE_AGE = 3600
   - SESSION_EXPIRE_AT_BROWSER_CLOSE = True
   - SECURE_CONTENT_TYPE_NOSNIFF = True
   - X_FRAME_OPTIONS = 'DENY' (موجودة فعلاً تأكيد)
   - LOGIN_URL = '/accounts/login/'
   - LOGIN_REDIRECT_URL = '/'
   - LOGOUT_REDIRECT_URL = '/'
   - AUTH_PASSWORD_VALIDATORS — تأكيد وجودهم أو زيادة صرامة (MinLengthValidator 8)
4. إضافة ميدلوير أمان مخصص (Middleware) لHeaders الأمنية الإضافية:
   - Referrer-Policy: strict-origin-when-cross-origin
   - Permissions-Policy: geolocation=(), microphone=(), camera=()
   - X-Permitted-Cross-Domain-Policies: none
   - مع شرط على كل هيدر حسب الحاجة
   (تُنفذ كـ Middleware class جديد في ملف devices/middleware.py)

### متطلبات الاختبار المحلي (TRs):
- **TR-1.1 (rule):** تشغيل `python manage.py check` بدون أخطاء
- **TR-1.2 (rule):** فتح /kopo-manage/ يعرض صفحة تسجيل دخول Django Admin
- **TR-1.3 (rule):** فتح /admin/ لا يعمل (لا يطابق أي URL)
- **TR-1.4 (rubric):** إعدادات الأمان المضافة: 0-1 (0 = ناقص كثيرة، 0.5 = بعضها، 1 = الكل موجودة). العتبة: >= 0.8

---

## Task 2: حماية كل الواجهات بـ Login Required

**الأولوية:** عالي
**الحالة:** pending
**يغطي:** FR-1, AC-1

### الوصف
تعديل ملف devices/views.py ليعكس كل الـ Views تتطلب تسجيل دخول:
- DeviceListView: LoginRequiredMixin
- DeviceCreateView: LoginRequiredMixin
- DeviceUpdateView: LoginRequiredMixin
- DeviceDeleteView: LoginRequiredMixin
- _MessageMixin: يظل كما هو

إضافة إعداد urls.py لـ Django auth (accounts/login/logout) في config/urls.py.

### متطلبات الاختبار المحلي (TRs):
- **TR-2.1 (rule):** طلب GET على "/" بدون تسجيل → HTTP 302 redirect إلى صفحة تسجيل الدخول
- **TR-2.2 (rule):** طلب GET على "/add/" بدون تسجيل → HTTP 302 redirect
- **TR-2.3 (rule):** طلب GET على "/1/edit/" بدون تسجيل → HTTP 302 redirect
- **TR-2.4 (rule):** طلب POST على "/1/delete/" بدون تسجيل → HTTP 302 redirect

---

## Task 3: إضافة حقل VLAN لنموذج Device + الهجرة + تحديث Forms/Admin/Tests

**الأولوية:** عالي
**الحالة:** pending
**يغطي:** FR-2, AC-2, AC-8, AC-9

### الوصف
1. تعديل devices/models.py وإضافة:
   - `vlan_id = models.PositiveIntegerField("VLAN ID", null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(4094)])`
2. إنشاء هجرة جديدة: `0002_device_vlan_id.py`
3. تعديل devices/forms.py حقل fields ليضيف "vlan_id" مع widget مناسب (NumberInput) + placeholder
4. تعديل devices/admin.py ليضيف vlan_id في list_display و search_fields أو list_filter حسب المناسب
5. تعديل devices/templates/devices/device_list.html الجدول يضيف عمود جديد "VLAN" بين IP و Type أو بعد Status (أي مكان مناسب)
6. تعديل devices/tests.py ليتضمن:
   - إنشاء جهاز مع vlan_id = 10
   - اختبار التحديث مع VLAN
   - التأكد من أن البحث والقائمة يعرضون القيمة
7. تشغيل `python manage.py migrate` لتطبيق الهجرة
8. تشغيل `python manage.py test devices` وتمرير كل الاختبارات

### متطلبات الاختبار المحلي (TRs):
- **TR-3.1 (rule):** تطبيق الهجرة بنجاح
- **TR-3.2 (rule):** `python manage.py test devices` يمر بنجاح
- **TR-3.3 (rule):** النموذج Device يحتوي فعلياً على vlan_id ويمكن تخزين قيمة صحيحة
- **TR-3.4 (rule):** حقل vlan_id ظاهر في الفورم (Add/Edit) والجدول الرئيسي وصفحة Admin

---

## Task 4: إعادة تسمية المشروع إلى "kopo" في الواجهة

**الأولوية:** متوسطة
**الحالة:** pending
**يغطي:** FR-3, AC-3

### الوصف
تعديل ملفات القوالب:
1. devices/templates/devices/base.html
   - Navbar brand يصبح "🖧 kopo" أو "🖧 KOPO"
   - Title tag: `{% block title %}kopo — Device Inventory{% endblock %}`
2. devices/templates/devices/device_list.html
   - العنوان الرئيسي: "Devices <badge>" يبقى أو يصبح "kopo Devices" حسب الرغبة
3. (اختياري) عنوان Admin: `admin.site.site_header = "kopo Administration"` و `admin.site.site_title = "kopo Admin"` في devices/apps.py أو devices/admin.py

### متطلبات الاختبار المحلي (TRs):
- **TR-4.1 (rule):** فتح الصفحة الرئيسية يعرض في الـ Navbar كلمة "kopo" واضحة وليس "Network Inventory" القديم
- **TR-4.2 (rule):** عنوان الصفحة (Browser tab) يحتوي على "kopo"

---

## Task 5: إضافة قسم معلومات Packet Tracer (راوترات + سويتشات + فروقات)

**الأولوية:** متوسطة
**الحالة:** pending
**يغطي:** FR-4, AC-4

### الوصف
تعديل devices/templates/devices/device_list.html لإضافة قسم معلومات بعد الجدول (أو Sidebar إذا كان العمود مناسب — أسهل يكون أسفل الجدول مباشرة):
- تصميم كارد Bootstrap 5 أو Accordion
- المحتوى:
  1. **أنواع الراوترات في Packet Tracer** (كروت شائعة):
     - Cisco 1841 — راوتر صغير للـ SOHO (مكاتب صغيرة)
     - Cisco 1941 — راوتر متوسط للأعمال ISR الجيل الثاني
     - Cisco 2811 — راوتر ISR جيل قديم، شائع في المختبرات
     - Cisco 2901 / 2911 — ISR G2 قوي، يدعم وحدات إضافية كثيرة
     - ISR 4331 — الجيل الأحدث ISR 4000، أداء عالٍ
  2. **أنواع السويتشات في Packet Tracer:**
     - Catalyst 2950 — سويتش قديم Layer 2، شائع في الدروس
     - Catalyst 2960 — Layer 2 الأكثر استخداماً في المختبرات، يدعم VLANs و STP
     - Catalyst 3560 — Layer 3، يدعم Inter-VLAN Routing
     - Catalyst 3650 — Layer 3 أحدث، أفضل أداء
  3. **الفرق بين الراوتر والسويتش (نقاط سريعة):**
     - **الطبقة:** الراوتر Layer 3 (Network) | السويتش عادةً Layer 2 (Data Link) إلا إذا كان MLS Layer 3
     - **الوظيفة:** الراوتر يربط شبكات مختلفة + الـ Routing بينها | السويتش يربط أجهزة داخل نفس الشبكة (VLAN)
     - **العناوين:** الراوتر يستخدم IP Address | السويتش يستخدم MAC Address
     - **مثال:** منزلك الراوتر يربطك بالإنترنت (ISP ← منزلك) | السويتش بيوصل الكمبيوتر والطابعة والـ TV ببعض في البيت

### متطلبات الاختبار المحلي (TRs):
- **TR-5.1 (rule):** صفحة device-list تعرض قسم معلومات Packet Tracer واضحاً يحتوي على 3 أقسام فرعية على الأقل
- **TR-5.2 (rubric):** جودة تصميم القسم: 0-2 (0 = مشوه/غير منظم، 1 = مقبول، 2 = منظم بBootstrap وجذاب بصرياً). العتبة: >= 1

---

## Task 6: إنشاء مستخدم Admin جديد باسم kopo_admin + التحقق منه

**الأولوية:** عالي
**الحالة:** pending
**يغطي:** FR-5, AC-5

### الوصف
1. إنشاء سكربت Python (مثل create_kopo_admin.py في الجذر) يقوم بـ:
   - إعداد Django
   - التحقق إذا كان المستخدم موجود
   - إنشاء SuperUser:
     - Username: `kopo_admin`
     - Password: `Kopo!Secure2026`
     - Email: `kopo@example.com`
   - حذف المستخدم القديم "admin" إذا كان موجود (اختياري أو فقط طباعة تحذير)
   - طباعة رسالة نجاح واضحة
2. تشغيل السكربت
3. التحقق يدوياً من تسجيل الدخول في المتصفح أو عبر اختبار

### متطلبات الاختبار المحلي (TRs):
- **TR-6.1 (rule):** المستخدم `kopo_admin` موجود في قاعدة البيانات وله صلاحيات is_superuser
- **TR-6.2 (rule):** يمكن تسجيل الدخول في /kopo-manage/ باستخدام كلمة المرور `Kopo!Secure2026`
