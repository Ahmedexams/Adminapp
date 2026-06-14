import flet as ft
import urllib.request
import json
import traceback

# بيانات الاتصال الخاصة بك
DB_URL = "https://ahmedexams-3e267-default-rtdb.firebaseio.com"
DB_SECRET = "nLDwjWapYWCVLHEyfZtLSqJrJAiBAhdNErDz3C8z"

def main(page: ft.Page):
    try:
        # إعدادات شاشة الموبايل الأساسية (بدون إعدادات معقدة تسبب انهيار)
        page.title = "إدارة المنصة"
        page.theme_mode = ft.ThemeMode.DARK
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
                columns=[ft.DataColumn(ft.Text("الطالب")), ft.DataColumn(ft.Text("الجلسة (Token)"))],
                rows=[]
            )
            lbl_count = ft.Text("جاري التحميل...", size=16, color="#a8b3d9")
            
            def load_data():
                try:
                    # استخدمنا urllib المدمجة بدلاً من requests
                    req = urllib.request.Request(f"{DB_URL}/active_tickets/sessions.json?auth={DB_SECRET}")
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode())
                    
                    table.rows.clear()
                    if data:
                        lbl_count.value = f"العدد الحالي: {len(data)} طالب"
                        for user, token in data.items():
                            table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(user))), ft.DataCell(ft.Text(str(token)))]))
                    else:
                        lbl_count.value = "العدد الحالي: 0"
                        notify("لا يوجد طلاب متصلين الآن.", "orange")
                except Exception as ex:
                    lbl_count.value = "فشل الاتصال بقاعدة البيانات"
                    notify("خطأ في الشبكة", "red")
                page.update()

            def kick_student(e):
                user = input_kick.value.strip()
                if user:
                    try:
                        req = urllib.request.Request(f"{DB_URL}/active_tickets/sessions/{user}.json?auth={DB_SECRET}", method='DELETE')
                        urllib.request.urlopen(req, timeout=10)
                        notify(f"تم طرد {user} بنجاح!")
                        input_kick.value = ""
                        load_data()
                    except:
                        notify("خطأ في الاتصال أثناء الطرد", "red")
                else:
                    notify("أدخل اسم الطالب أولاً!", "red")

            input_kick = ft.TextField(label="اسم الطالب لطرده", text_align="center", border_color="#1a2b55")
            
            page.add(
                ft.Text("مراقبة المتصلين الآن", size=25, color="#6ee7ff", weight="bold"),
                lbl_count,
                ft.Container(content=ft.Column([table], scroll="always"), height=250, border=ft.border.all(1, "#1a2b55"), padding=10),
                input_kick,
                ft.ElevatedButton("طرد الطالب", on_click=kick_student, bgcolor="red", color="white", width=300),
                ft.ElevatedButton("تحديث البيانات", on_click=lambda _: load_data(), width=300),
                ft.ElevatedButton("رجوع للوحة التحكم", on_click=build_dashboard, width=300)
            )
            load_data()

        # ===============================
        # 2. شاشة الحسابات
        # ===============================
        def build_users_view(e=None):
            page.clean()
            table = ft.DataTable(
                columns=[ft.DataColumn(ft.Text("الطالب")), ft.DataColumn(ft.Text("كلمة المرور"))],
                rows=[]
            )
            lbl_count = ft.Text("جاري التحميل...", size=16, color="#a8b3d9")
            
            def load_data():
                try:
                    req = urllib.request.Request(f"{DB_URL}/credentials.json?auth={DB_SECRET}")
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode())
                    
                    table.rows.clear()
                    if data:
                        lbl_count.value = f"العدد الحالي: {len(data)} حساب"
                        for user, info in data.items():
                            table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(user))), ft.DataCell(ft.Text(str(info.get("password", ""))))]))
                    else:
                        lbl_count.value = "لا توجد حسابات مسجلة"
                        notify("لا توجد حسابات.", "orange")
                except Exception as ex:
                    lbl_count.value = "فشل الاتصال بقاعدة البيانات"
                    notify("خطأ في الشبكة", "red")
                page.update()

            def delete_student(e):
                user = input_del.value.strip()
                if user:
                    try:
                        req = urllib.request.Request(f"{DB_URL}/credentials/{user}.json?auth={DB_SECRET}", method='DELETE')
                        urllib.request.urlopen(req, timeout=10)
                        notify(f"تم حذف {user} بنجاح!")
                        input_del.value = ""
                        load_data()
                    except:
                        notify("خطأ في الاتصال أثناء الحذف", "red")
                else:
                    notify("أدخل اسم الطالب أولاً!", "red")

            input_del = ft.TextField(label="اسم الطالب لحذفه", text_align="center", border_color="#1a2b55")
            
            page.add(
                ft.Text("إدارة الحسابات", size=25, color="#6ee7ff", weight="bold"),
                lbl_count,
                ft.Container(content=ft.Column([table], scroll="always"), height=250, border=ft.border.all(1, "#1a2b55"), padding=10),
                input_del,
                ft.ElevatedButton("حذف الحساب", on_click=delete_student, bgcolor="red", color="white", width=300),
                ft.ElevatedButton("تحديث البيانات", on_click=lambda _: load_data(), width=300),
                ft.ElevatedButton("رجوع للوحة التحكم", on_click=build_dashboard, width=300)
            )
            load_data()

        # ===============================
        # 3. لوحة التحكم الأساسية
        # ===============================
        def build_dashboard(e=None):
            page.clean()
            page.add(
                ft.Text("لوحة تحكم المنصة", size=30, color="#6ee7ff", weight="bold"),
                ft.Container(height=30),
                ft.ElevatedButton("إدارة حسابات الطلاب", on_click=build_users_view, width=300, height=50),
                ft.Container(height=10),
                ft.ElevatedButton("مراقبة المتصلين الآن", on_click=build_online_view, width=300, height=50),
            )

        build_dashboard()
        
    except Exception as e:
        # إذا حدث أي خطأ برمجي، سيظهر هنا بدلاً من الشاشة السوداء!
        page.clean()
        page.bgcolor = "white"
        page.add(ft.Text(f"تفاصيل الخطأ:\n{traceback.format_exc()}", color="red", selectable=True, size=16))
        page.update()

ft.app(target=main)

