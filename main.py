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
        # إعدادات بسيطة جداً وآمنة
        page.title = "إدارة المنصة"
        page.theme_mode = ft.ThemeMode.DARK
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.scroll = "auto"
        
        def notify(msg, color="green"):
            page.snack_bar = ft.SnackBar(ft.Text(msg, color="white"), bgcolor=color)
            page.snack_bar.open = True
            page.update()

        # ===============================
        # 1. شاشة مراقبة المتصلين
        # ===============================
        def build_online_view(e=None):
            try:
                page.clean()
                table = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text("الطالب")), ft.DataColumn(ft.Text("الجلسة"))],
                    rows=[]
                )
                lbl_count = ft.Text("جاري التحميل...", size=16)
                
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

                input_kick = ft.TextField(label="اسم الطالب لطرده", text_align="center")
                
                page.add(
                    ft.Text("مراقبة المتصلين", size=25, weight="bold"),
                    lbl_count,
                    table,
                    input_kick,
                    ft.ElevatedButton("طرد الطالب", on_click=kick_student, bgcolor="red", color="white"),
                    ft.ElevatedButton("تحديث البيانات", on_click=lambda _: load_data()),
                    ft.ElevatedButton("رجوع للوحة التحكم", on_click=build_dashboard)
                )
                load_data()
            except Exception as ex:
                page.add(ft.Text(f"Error in View:\n{ex}", color="red"))
                page.update()

        # ===============================
        # 2. شاشة الحسابات
        # ===============================
        def build_users_view(e=None):
            try:
                page.clean()
                table = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text("الطالب")), ft.DataColumn(ft.Text("المرور"))],
                    rows=[]
                )
                lbl_count = ft.Text("جاري التحميل...", size=16)
                
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

                input_del = ft.TextField(label="اسم الطالب لحذفه", text_align="center")
                
                page.add(
                    ft.Text("إدارة الحسابات", size=25, weight="bold"),
                    lbl_count,
                    table,
                    input_del,
                    ft.ElevatedButton("حذف الحساب", on_click=delete_student, bgcolor="red", color="white"),
                    ft.ElevatedButton("تحديث البيانات", on_click=lambda _: load_data()),
                    ft.ElevatedButton("رجوع للوحة التحكم", on_click=build_dashboard)
                )
                load_data()
            except Exception as ex:
                page.add(ft.Text(f"Error in View:\n{ex}", color="red"))
                page.update()

        # ===============================
        # 3. لوحة التحكم الأساسية
        # ===============================
        def build_dashboard(e=None):
            try:
                page.clean()
                page.add(
                    ft.Container(height=50),
                    ft.Text("لوحة تحكم المنصة", size=28, weight="bold"),
                    ft.Container(height=30),
                    ft.ElevatedButton("إدارة حسابات الطلاب", on_click=build_users_view, width=250, height=50),
                    ft.Container(height=10),
                    ft.ElevatedButton("مراقبة المتصلين الآن", on_click=build_online_view, width=250, height=50),
                    ft.Container(height=50),
                    ft.Text("DEVELOPED BY AHMED HAMED", size=12)
                )
            except Exception as ex:
                page.add(ft.Text(f"Error in Dashboard:\n{ex}", color="red"))
                page.update()

        build_dashboard()
        
    except Exception as e:
        page.clean()
        page.bgcolor = "black"
        page.add(ft.Text(f"Critical Error:\n{traceback.format_exc()}", color="red", selectable=True))
        page.update()

ft.app(target=main)

