from customtkinter import *
from PIL import Image
from socket import *
import threading
import base64
import io
import os


bg = Image.open('bg.png')
setting = Image.open('setting.png')


class AuthWindow(CTk):
    def __init__(self):
        super().__init__()
        self.title('Вхід')
        self.resizable(True, False)
        self.minsize(700, 400)




        self.butt = CTkButton(self, width=50, height=50, text='')
        self.butt.place(x=0, y=0)


        main_font = ('Helvetica', 20, 'bold')
        self.left_frame = CTkFrame(self)
        self.left_frame.pack(side='left', fill='both')
        bg_image = CTkImage(bg, size=(450, 400))
        self.label_welcome = CTkLabel(self.left_frame, text = 'Welcome', font=main_font, image=bg_image, text_color='white')
        self.label_welcome.pack()


        self.right_frame = CTkFrame(self, fg_color='white')
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side='right', fill = 'both', expand='True')


        CTkLabel(self.right_frame, text='LogiTalk', font=main_font, text_color="#6753cc").pack(pady=50)


        self.entry_name = CTkEntry(self.right_frame, placeholder_text="☻Ім'я", font=main_font, height=45, corner_radius=25,fg_color='#eae6ff', border_color='#eae6ff', text_color='#6753cc', placeholder_text_color='#6753cc')
        self.entry_name.pack(pady=5, padx=10, fill='x')

        self.entry_ip = CTkEntry(self.right_frame, placeholder_text="IP", font=main_font, height=45, corner_radius=25,fg_color='#eae6ff', border_color='#eae6ff', text_color='#6753cc', placeholder_text_color='#6753cc')
        self.entry_ip.pack(pady=5, padx=10, fill='x')

        self.entry_port = CTkEntry(self.right_frame, placeholder_text="port", font=main_font, height=45, corner_radius=25,fg_color='#eae6ff', border_color='#eae6ff', text_color='#6753cc', placeholder_text_color='#6753cc')
        self.entry_port.pack(pady=5, padx=10, fill='x')

        self.connect_btn = CTkButton(self.right_frame, height=45, text='УВІЙТИ', font=main_font, text_color='white', fg_color='#d06fc0', border_color='#d06fc0', hover_color="#b45da6", corner_radius=25, command=self.open_chat)
        self.connect_btn.pack(fill='x', pady=20, padx=50)

    def open_chat(self):
        name = self.entry_name.get().strip() or 'user'
        ip = self.entry_ip.get().strip() or 'localhost'
        try:
            port = int(self.entry_port.get().strip())
        except:
            port = 8080

        self.destroy()
        window = ChatWindow(name, ip, port)
        window.mainloop()



class ChatWindow(CTk):
    def __init__(self, name, ip, port):
        super().__init__()

        self.user_name = name

        self.resizable(True, True)
        self.minsize(700, 400)
        self.title('LogiTalk')


        self.current_theme = 'dark'
        set_appearance_mode('dark')

        self.bind('<Configure>', self.adaptive_ui)
        self.bind('<Return>', self.send_message)


        #меню


        self.setting_frame = CTkFrame(self, width=200, height=self.winfo_height())
        self.setting_frame.pack_propagate(False)
        self.setting_frame.configure(width=0)
        self.frame_width = 0
        self.setting_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.menu_show_speed = 20


        #основне поле чату


        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=100, y=0)


        self.btn = CTkButton(self, width=30, text='>', command=self.toggle_show_menu)
        self.btn.place(x=0, y=0)


        self.label = CTkLabel(self.setting_frame, text="Ваше Ім'я")
        self.label.pack(pady=30)
        self.entry = CTkEntry(self.setting_frame, placeholder_text=name)
        self.entry.pack()


        self.save_btn = CTkButton(self.setting_frame, text='Зберегти', command=self.save_name)
        self.save_btn.pack()


        self.theme_btn = CTkButton(self.setting_frame, text=f'тема: {self.current_theme}', command=self.change_theme)
        self.theme_btn.pack(side='top', pady=60)


        #поле введеня та кнопки
        self.message_entry = CTkEntry(self, placeholder_text='ведіть повідомлення', height=40)
        self.message_entry.place(x=0, y=300)


        self.send_btn = CTkButton(self, text='>', width=50, height=40, command = self.send_message)
        self.send_btn.place(x=200, y=300)


        self.open_img_btn = CTkButton(self, text='📂', width=50, height=40, command=self.open_img)
        self.open_img_btn.place(x=250, y=300)


        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((ip, port))
            hello = f'TEXT@{self.user_name}@[SYSTEM] {self.user_name} приєднався(лась)\n'
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f'не вдалось підключитись до сервера {e}')


        self.adaptive_ui()


    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()


    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += self.menu_show_speed
            self.setting_frame.configure(width = self.frame_width, height=self.winfo_height())
            if self.frame_width >=30:
                self.btn.configure(width=self.frame_width, text='<')
            if self.is_show_menu:
                self.show_menu()
           
    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= self.menu_show_speed
            self.setting_frame.configure(width = self.frame_width)
            if self.frame_width >=30:
                self.btn.configure(width=self.frame_width, text='>')
            if not self.is_show_menu:
                self.close_menu()


    def change_theme(self):
        if self.current_theme == 'light':
            set_appearance_mode('dark')
            self.current_theme = 'dark'
        else:
            set_appearance_mode('light')
            self.current_theme = 'light'
        self.theme_btn.configure(text=f'тема: {self.current_theme}')


    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            self.add_message(f'{self.user_name}: {message}')
            data = f'TEXT@{self.user_name}@{message}\n'
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)


    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_field, fg_color='gray')
        message_frame.pack(pady=5, anchor='w')
        wraplenght_size = self.winfo_width() - self.setting_frame.winfo_width() - 40
        if not img:
            CTkLabel(message_frame, text=message, wraplength=wraplenght_size, justify='left').pack(padx=10, pady=5)
        else:
            CTkLabel(message_frame, text=message, wraplength=wraplenght_size, justify='left', image=img, compound='top').pack(padx=10, pady=5)


    def open_img(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, 'rb') as f:
                raw = f.read()
            b64 = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f'IMAGE@{self.user_name}@{short_name}@{b64}'
            self.sock.sendall(data.encode())
            self.add_message('', CTkImage(light_image=Image.open(file_name), size=(300, 300)))
        except Exception as e:
            print(f'Не вдалось надіслати зображення {e}')




    def handle_line(self, line):
        if not line:
            return
        parts = line.split('@', 3)
        msg_type = parts[0]


        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img, size=(300, 300))
                    self.add_message(
                        f"{author} надіслав(ла) зображення: {filename}", img=ctk_img
                    )
                except Exception as e:
                    self.add_message(f"Помилка відображення зображення: {e}")
        else:
            self.add_message(line)


    def recv_message(self):
        buffer = ''
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='ignore')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.handle_line(line.strip())
            except:
                break


        self.sock.close()


    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.add_message(f"{self.user_name} змінив ім'я на {new_name}")
            self.user_name = new_name
            self.entry.configure(placeholder_text=self.user_name)
            self.entry.delete(0, END)
            self.focus()


    def adaptive_ui(self, event=None):
        self.setting_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.setting_frame.winfo_width())
        self.chat_field.configure(
            width=self.winfo_width() - self.setting_frame.winfo_width() - 20,
            height = self.winfo_height() - 40)
        self.send_btn.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.setting_frame.winfo_width(), y=self.winfo_height() - 40)
        self.message_entry.configure(width = self.winfo_width() - self.setting_frame.winfo_width() - 110)
        self.open_img_btn.place(x=self.winfo_width() - 105, y=self.winfo_height() - 40)



window = AuthWindow()


window.mainloop()