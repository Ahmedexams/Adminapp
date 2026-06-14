import flet as ft
import requests

# بيانات الاتصال الخاصة بك
DB_URL = "https://ahmedexams-3e267-default-rtdb.firebaseio.com"
DB_SECRET = "nLDwjWapYWCVLHEyfZtLSqJrJAiBAhdNErDz3C8z"

def main(page: ft.Page):
    # إعدادات شاشة الموبايل
    page.title = "إدارة المنصة"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#070912"
    page.rtl = True # دعم اللغة العربية من اليمين لليسار تلقائياً
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = "auto"

    def notify(msg, color="green"):
        page.snack_bar = ft.SnackBar(ft.Text(msg, weight="bold", color="white"), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # ===============================
    # 1. شاشة مراقبة المتصلين
    # ===============================
    def build_online_view(e=None):
        page.clean()
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("اسم الطالب", color="#6ee7ff")),
                ft.DataColumn(ft.Text("الجلسة (Token)", color="#6ee7ff")),
            ],
            rows=[]
        )
        
        lbl_count = ft.Text("العدد الحالي: جاري التحميل...", color="#a8b3d9", size=16)
        
        def load_data():
            table.rows.clear()
            try:
                res = requests.get(f"{DB_URL}/active_tickets/sessions.json?auth={DB_SECRET}", timeout=10)
                if res.status_code == 200 and res.json():
                    data = res.json()
                    lbl_count.value = f"العدد الحالي: {len(data)} طالب"
                    for user, token in data.items():
                        table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(user)), ft.DataCell(ft.Text(token))]))
                else:
                    lbl_count.value = "العدد الحالي: 0"
                    notify("لا يوجد طلاب متصلين الآن.", "orange")
            except:
                notify("خطأ في الشبكة!", "red")
            page.update()

        def kick_student(e):
            user = input_kick.value.strip()
            if user:
                requests.delete(f"{DB_URL}/active_tickets/sessions/{user}.json?auth={DB_SECRET}")
                notify(f"تم طرد {user} بنجاح!")
                input_kick.value = ""
                lbl_count.value = "العدد الحالي: جاري التحديث..."
                page.update()
                load_data()
            else:
                notify("يرجى إدخال اسم الطالب!", "red")

        input_kick = ft.TextField(label="اسم الطالب لطرده", border_color="#1a2b55", text_align="center")
        
        # التعديل هنا: نقوم برسم الواجهة وعرضها للمستخدم أولاً
        page.add(
            ft.Text("مراقبة المتصلين الآن", size=25, color="#6ee7ff", weight="bold"),
            lbl_count,
            ft.Container(content=ft.Column([table], scroll="always"), height=250, border=ft.border.all(1, "#1a2b55"), border_radius=10, padding=10),
            input_kick,
            ft.ElevatedButton("طرد الطالب 👢", on_click=kick_student, bgcolor="#ef4444", color="white", width=300),
            ft.ElevatedButton("تحديث البيانات 🔄", on_click=lambda _: load_data(), bgcolor="#1a2b55", color="white", width=300),
            ft.ElevatedButton("رجوع للوحة التحكم 🔙", on_click=build_dashboard, bgcolor="#a8b3d9", color="#070912", width=300),
        )
        
        # ثم نقوم بجلب البيانات من الإنترنت في صمت
        load_data()

    # ===============================
    # 2. شاشة الحسابات
    # ===============================
    def build_users_view(e=None):
        page.clean()
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("اسم الطالب", color="#6ee7ff")),
                ft.DataColumn(ft.Text("كلمة المرور", color="#6ee7ff")),
            ],
            rows=[]
        )
        
        def load_data():
            table.rows.clear()
            try:
                res = requests.get(f"{DB_URL}/credentials.json?auth={DB_SECRET}", timeout=10)
                if res.status_code == 200 and res.json():
                    for user, info in res.json().items():
                        table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(user)), ft.DataCell(ft.Text(info.get("password", "N/A")))]))
                else:
                    notify("لا توجد حسابات.", "orange")
            except:
                notify("خطأ في الشبكة!", "red")
            page.update()

        def delete_student(e):
            user = input_del.value.strip()
            if user:
                requests.delete(f"{DB_URL}/credentials/{user}.json?auth={DB_SECRET}")
                notify(f"تم حذف {user} بنجاح!")
                input_del.value = ""
                page.update()
                load_data()
            else:
                notify("يرجى إدخال اسم الطالب!", "red")

        input_del = ft.TextField(label="اسم الطالب لحذفه", border_color="#1a2b55", text_align="center")
        
        # التعديل هنا: نقوم برسم الواجهة وعرضها للمستخدم أولاً
        page.add(
            ft.Text("إدارة الحسابات", size=25, color="#6ee7ff", weight="bold"),
            ft.Container(content=ft.Column([table], scroll="always"), height=250, border=ft.border.all(1, "#1a2b55"), border_radius=10, padding=10),
            input_del,
            ft.ElevatedButton("حذف الحساب 🗑️", on_click=delete_student, bgcolor="#ef4444", color="white", width=300),
            ft.ElevatedButton("تحديث البيانات 🔄", on_click=lambda _: load_data(), bgcolor="#1a2b55", color="white", width=300),
            ft.ElevatedButton("رجوع للوحة التحكم 🔙", on_click=build_dashboard, bgcolor="#a8b3d9", color="#070912", width=300),
        )
        
        # ثم نقوم بجلب البيانات من الإنترنت في صمت
        load_data()

    # ===============================
    # 3. لوحة التحكم الأساسية
    # ===============================
    def build_dashboard(e=None):
        page.clean()
        page.add(
            ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS, size=80, color="#6ee7ff"),
            ft.Text("لوحة تحكم المنصة", size=30, color="#6ee7ff", weight="bold"),
            ft.Text("أهلاً بك يا أدمن، اختر الإجراء المطلوب:", color="#a8b3d9"),
            ft.Container(height=30),
            ft.ElevatedButton("👥 إدارة حسابات الطلاب", on_click=build_users_view, bgcolor="#6ee7ff", color="#070912", width=300, height=50),
            ft.Container(height=10),
            ft.ElevatedButton("🟢 مراقبة المتصلين الآن", on_click=build_online_view, bgcolor="#6ee7ff", color="#070912", width=300, height=50),
        )

    # تشغيل الواجهة الأولى
    build_dashboard()

# السطر الأخير المخصص لتطبيقات الهاتف (بدون المتصفح)
ft.app(target=main)
