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
        # إعدادات شاشة الموبايل
        page.title = "إدارة المنصة"
        page.theme_mode = ft.ThemeMode.DARK
        
        page.decoration = ft.BoxDecoration(
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), 
                end=ft.Alignment(0, 1),    
                colors=["#161c33", "#050710"]
            )
        )
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.scroll = "auto"
        
        def notify(msg, color="green"):
            page.snack_bar = ft.SnackBar(ft.Text(msg, weight="bold", color="white"), bgcolor=color)
            page.snack_bar.open = True
            page.update()

        def gradient_button(text, on_click_func, width=300):
            return ft.Container(
                content=ft.Text(text, color="black", weight="900", size=16),
                alignment=ft.Alignment(0, 0),
                width=width,
                height=55,
                border_radius=15,
                gradient=ft.LinearGradient(
                    colors=["#58e6e9", "#b388ff"],
                    begin=ft.Alignment(-1, 0),
                    end=ft.Alignment(1, 0),
                ),
                on_click=on_click_func,
                ink=True
            )

        def secondary_button(text, on_click_func, width=300):
            return ft.Container(
                content=ft.Text(text, color="#a8b3d9", weight="bold"),
                alignment=ft.Alignment(0, 0),
                width=width,
                height=50,
                border_radius=15,
                bgcolor="#0a0e1c",
                on_click=on_click_func,
                ink=True
            )

        def custom_textfield(label):
            return ft.TextField(
                label=label,
                text_align="center",
                border_color="#1a2b55",
                bgcolor="#0a0e1c",
                border_radius=15,
                color="white",
                focused_border_color="#58e6e9"
            )

        # التعديل الحاسم هنا: استخدام الأرقام فقط للمسافات (بدون symmetric أو only)
        footer = ft.Container(
            content=ft.Text("DEVELOPED BY AHMED HAMED", color="#b388ff", weight="bold", size=12),
            border_radius=25,
            padding=10, 
            margin=20,  
            bgcolor="#050710"
        )

        def build_online_view(e=None):
            try:
                page.clean()
                table = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text("الطالب", color="#58e6e9")), ft.DataColumn(ft.Text("الجلسة", color="#58e6e9"))],
                    rows=[]
                )
                lbl_count = ft.Text("جاري التحميل في الخلفية...", size=14, color="#b388ff")
                
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
                        lbl_count.value = "فشل الاتصال بقاعدة البيانات"
                        notify("خطأ في الشبكة", "red")
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
                
                main_card = ft.Container(
                    content=ft.Column([
                        lbl_count,
                        ft.Container(content=ft.Column([table], scroll="always"), height=200),
                        input_kick,
                        gradient_button("طرد الطالب", kick_student),
                        secondary_button("تحديث البيانات", lambda _: load_data()),
                        secondary_button("رجوع للوحة التحكم", build_dashboard)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#090d1a",
                    border_radius=20,
                    padding=20,
                    width=340
                )
                
                page.add(
                    ft.Text("مراقبة المتصلين", size=26, color="white", weight="bold"),
                    main_card
                )
                load_data()
            except Exception as ex:
                pass

        def build_users_view(e=None):
            try:
                page.clean()
                table = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text("الطالب", color="#58e6e9")), ft.DataColumn(ft.Text("المرور", color="#58e6e9"))],
                    rows=[]
                )
                lbl_count = ft.Text("جاري التحميل في الخلفية...", size=14, color="#b388ff")
                
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
                        lbl_count.value = "فشل الاتصال بقاعدة البيانات"
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
                
                main_card = ft.Container(
                    content=ft.Column([
                        lbl_count,
                        ft.Container(content=ft.Column([table], scroll="always"), height=200),
                        input_del,
                        gradient_button("حذف الحساب", delete_student),
                        secondary_button("تحديث البيانات", lambda _: load_data()),
                        secondary_button("رجوع للوحة التحكم", build_dashboard)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#090d1a",
                    border_radius=20,
                    padding=20,
                    width=340
                )
                
                page.add(
                    ft.Text("إدارة الحسابات", size=26, color="white", weight="bold"),
                    main_card
                )
                load_data()
            except Exception as ex:
                pass

        def build_dashboard(e=None):
            try:
                page.clean()
                
                # أزلنا التأثيرات المعقدة لضمان عدم الانهيار
                logo = ft.Container(
                    content=ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, size=70, color="#58e6e9"),
                    padding=10
                )

                main_card = ft.Container(
                    content=ft.Column([
                        gradient_button("إدارة حسابات الطلاب", build_users_view),
                        ft.Container(height=5),
                        gradient_button("مراقبة المتصلين الآن", build_online_view),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#090d1a",
                    border_radius=20,
                    padding=30,
                    width=340
                )

                page.add(
                    ft.Container(height=30),
                    logo,
                    ft.Container(height=10),
                    ft.Text("لوحة تحكم المنصة", size=28, color="white", weight="bold"),
                    ft.Text("أهلاً بك يا أدمن، اختر الإجراء للبدء", color="#a8b3d9", size=14),
                    ft.Container(height=20),
                    main_card,
                    footer
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

