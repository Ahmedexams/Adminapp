import flet as ft
import urllib.request
import json
import traceback
import threading

# بيانات الاتصال الخاصة بك
DB_URL = "https://ahmedexams-3e267-default-rtdb.firebaseio.com"
DB_SECRET = "nLDwjWapYWCVLHEyfZtLSqJrJAiBAhdNErDz3C8z"

def main(page: ft.Page):
    try:
        # إعدادات الواجهة الأساسية بألوان فخمة
        page.title = "إدارة المنصة"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#070B14"  # خلفية كحلي داكن جداً
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.scroll = "auto"
        
        def notify(msg, color="#2ea043"):
            page.snack_bar = ft.SnackBar(ft.Text(msg, weight="bold", color="white"), bgcolor=color)
            page.snack_bar.open = True
            page.update()

        # ==========================================
        # أدوات التصميم الجاهزة (آمنة تماماً بدون أوامر معقدة)
        # ==========================================
        def primary_button(text, on_click_func):
            # زر متدرج أنيق جداً بألوان سماوي وبنفسجي
            return ft.Container(
                content=ft.Text(text, color="#070B14", weight="900", size=16),
                alignment=ft.alignment.center,
                width=280,
                height=55,
                border_radius=15,
                gradient=ft.LinearGradient(colors=["#58e6e9", "#b388ff"]), 
                on_click=on_click_func,
                ink=True,
                shadow=ft.BoxShadow(blur_radius=15, color="#1a2b55") # ظل خفيف للزر
            )

        def secondary_button(text, on_click_func):
            # زر ثانوي رمادي داكن للرجوع والتحديث
            return ft.Container(
                content=ft.Text(text, color="#a8b3d9", weight="bold"),
                alignment=ft.alignment.center,
                width=280,
                height=50,
                border_radius=15,
                bgcolor="#111827",
                on_click=on_click_func,
                ink=True
            )

        def custom_textfield(label):
            return ft.TextField(
                label=label,
                text_align="center",
                bgcolor="#111827",
                border_radius=15,
                color="white",
                border_color="#1a2b55",
                focused_border_color="#58e6e9"
            )

        # اللوجو المضيء
        logo = ft.Container(
            content=ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, size=70, color="#58e6e9"),
            padding=10,
            bgcolor="#070B14",
            shape=ft.BoxShape.CIRCLE,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=25, color="#2a3f75") # تأثير النيون
        )

        # ===============================
        # 1. شاشة مراقبة المتصلين
        # ===============================
        def build_online_view(e=None):
            try:
                page.clean()
                table = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text("الطالب", color="#58e6e9")), ft.DataColumn(ft.Text("الجلسة", color="#58e6e9"))],
                    rows=[]
                )
                lbl_count = ft.Text("جاري التحميل...", size=14, color="#b388ff")
                
                def fetch_data():
                    try:
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
                        lbl_count.value = "فشل الاتصال"
                    page.update()

                def load_data():
                    threading.Thread(target=fetch_data).start()

                def kick_action():
                    user = input_kick.value.strip()
                    if user:
                        try:
                            req = urllib.request.Request(f"{DB_URL}/active_tickets/sessions/{user}.json?auth={DB_SECRET}", method='DELETE')
                            urllib.request.urlopen(req, timeout=10)
                            notify(f"تم طرد {user} بنجاح!")
                            input_kick.value = ""
                            load_data()
                        except:
                            notify("خطأ في الاتصال", "red")
                    else:
                        notify("أدخل اسم الطالب أولاً!", "red")

                def kick_student(e):
                    threading.Thread(target=kick_action).start()

                input_kick = custom_textfield("اسم الطالب لطرده")
                
                # الكارت الداخلي الشفاف
                card = ft.Container(
                    content=ft.Column([
                        lbl_count,
                        ft.Container(content=ft.Column([table], scroll="always"), height=200),
                        input_kick,
                        primary_button("طرد الطالب 👢", kick_student),
                        ft.Container(height=5),
                        secondary_button("تحديث البيانات 🔄", lambda _: load_data()),
                        secondary_button("رجوع للوحة التحكم", build_dashboard)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#0F1423",
                    padding=25,
                    border_radius=20,
                    width=340,
                    shadow=ft.BoxShadow(blur_radius=20, color="#04060c")
                )
                
                page.add(
                    ft.Container(height=20),
                    ft.Text("مراقبة المتصلين", size=26, color="white", weight="bold"),
                    ft.Container(height=10),
                    card
                )
                load_data()
            except Exception as ex:
                pass

        # ===============================
        # 2. شاشة الحسابات
        # ===============================
        def build_users_view(e=None):
            try:
                page.clean()
                table = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text("الطالب", color="#58e6e9")), ft.DataColumn(ft.Text("المرور", color="#58e6e9"))],
                    rows=[]
                )
                lbl_count = ft.Text("جاري التحميل...", size=14, color="#b388ff")
                
                def fetch_data():
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
                    except Exception as ex:
                        lbl_count.value = "فشل الاتصال"
                    page.update()

                def load_data():
                    threading.Thread(target=fetch_data).start()

                def delete_action():
                    user = input_del.value.strip()
                    if user:
                        try:
                            req = urllib.request.Request(f"{DB_URL}/credentials/{user}.json?auth={DB_SECRET}", method='DELETE')
                            urllib.request.urlopen(req, timeout=10)
                            notify(f"تم حذف {user} بنجاح!")
                            input_del.value = ""
                            load_data()
                        except:
                            notify("خطأ في الاتصال", "red")
                    else:
                        notify("أدخل اسم الطالب أولاً!", "red")

                def delete_student(e):
                    threading.Thread(target=delete_action).start()

                input_del = custom_textfield("اسم الطالب لحذفه")
                
                card = ft.Container(
                    content=ft.Column([
                        lbl_count,
                        ft.Container(content=ft.Column([table], scroll="always"), height=200),
                        input_del,
                        primary_button("حذف الحساب 🗑️", delete_student),
                        ft.Container(height=5),
                        secondary_button("تحديث البيانات 🔄", lambda _: load_data()),
                        secondary_button("رجوع للوحة التحكم", build_dashboard)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#0F1423",
                    padding=25,
                    border_radius=20,
                    width=340,
                    shadow=ft.BoxShadow(blur_radius=20, color="#04060c")
                )
                
                page.add(
                    ft.Container(height=20),
                    ft.Text("إدارة الحسابات", size=26, color="white", weight="bold"),
                    ft.Container(height=10),
                    card
                )
                load_data()
            except Exception as ex:
                pass

        # ===============================
        # 3. لوحة التحكم الأساسية
        # ===============================
        def build_dashboard(e=None):
            try:
                page.clean()
                
                card = ft.Container(
                    content=ft.Column([
                        primary_button("إدارة حسابات الطلاب", build_users_view),
                        ft.Container(height=10),
                        primary_button("مراقبة المتصلين الآن", build_online_view),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#0F1423",
                    padding=30,
                    border_radius=20,
                    width=340,
                    shadow=ft.BoxShadow(blur_radius=20, color="#04060c")
                )

                page.add(
                    ft.Container(height=40),
                    logo,
                    ft.Container(height=15),
                    ft.Text("لوحة تحكم المنصة", size=28, color="white", weight="900"),
                    ft.Text("أهلاً بك يا أدمن، اختر الإجراء للبدء", color="#a8b3d9", size=14),
                    ft.Container(height=25),
                    card,
                    ft.Container(height=25),
                    ft.Text("DEVELOPED BY AHMED HAMED", color="#b388ff", weight="bold", size=12)
                )
            except Exception as ex:
                pass

        build_dashboard()
        
    except Exception as e:
        page.clean()
        page.bgcolor = "black"
        page.add(ft.Text(f"Error:\n{traceback.format_exc()}", color="red", selectable=True))
        page.update()

ft.app(target=main)

