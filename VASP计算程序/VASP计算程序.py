import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage, ttk, simpledialog
import os
import shutil
import subprocess
import stat
import threading
from openai import OpenAI
import re

# 基于脚本文件的位置构建路径
app_root = os.path.dirname(__file__)

app = tk.Tk()
app.title('VASP自动化计算')
app.config(bg='white')
app.minsize(500, 600)
app.withdraw()  # 隐藏主界面直到封面结束

# 获取主界面宽高
main_app_width = 800  # 主界面的宽度
main_app_height = 500  # 主界面的高度

# 1. 添加封面函数
def show_cover_page():
    cover_window = tk.Toplevel()
    cover_window.title("欢迎使用VASP自动化计算工具")

    # 调整窗口尺寸
    cover_window_width = int(main_app_width * 1.2)
    cover_window_height = int(main_app_height * 1.2)
    screen_width = cover_window.winfo_screenwidth()
    screen_height = cover_window.winfo_screenheight()
    position_top = int(screen_height / 2 - cover_window_height / 2)
    position_right = int(screen_width / 2 - cover_window_width / 2)

    cover_window.geometry(f'{cover_window_width}x{cover_window_height}+{position_right}+{position_top}')
    cover_window.config(bg='#F4F6F7')  # 使用柔和的背景色

    # 添加标题，使用大字体并居中
    title_frame = tk.Frame(cover_window, bg='white')  # 使用单独的白色背景块
    title_frame.pack(fill='x', pady=5)

    cover_label = tk.Label(title_frame, text="VASP自动化计算", font=('Helvetica', 30, 'bold'), bg='white', fg='#5AC1EC')
    cover_label.pack(pady=10)

    # 添加半透明背景层，避免图片和文字重叠冲突
    image_frame = tk.Frame(cover_window, bg='#E8EAF6')  # 使用带颜色的背景框
    image_frame.pack(pady=10, fill='x')

    # 增大并居中图片
    logo_image = PhotoImage(file=os.path.join(app_root, 'assets', 'VASP程序内用图1.png'))
    logo_image = logo_image.subsample(1, 1)  # 调整图片大小
    logo_label = tk.Label(image_frame, image=logo_image, bg='#E8EAF6')
    logo_label.image = logo_image
    logo_label.pack(pady=5)  # 适当减少图片与下方文字的间距

    # 添加简短介绍文字，设置合适的字体和颜色
    intro_text = """欢迎使用VASP自动化计算工具，
    本工具旨在帮助您快速生成VASP计算所需文件，
    自动执行计算并分析结果。"""
    intro_label = tk.Label(cover_window, text=intro_text, font=('Helvetica', 14), bg='#F4F6F7', fg='#333333', wraplength=cover_window_width - 40)
    intro_label.pack(pady=10)  # 适当减少文字与下方的按钮间距

    # 美化按钮
    def start_main_app():
        cover_window.destroy()
        app.deiconify()  # 显示主界面

    start_button = tk.Button(cover_window, text="进入工具", font=('Helvetica', 14), bg='#4A90E2', fg='white',
                             activebackground='#3B7BBE', relief='raised', command=start_main_app)
    start_button.pack(pady=10)  # 减少按钮与进度条之间的距离




# 2. 在程序启动时调用封面
app.after(100, show_cover_page)

# 主窗口也需要设置权重
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)

# 创建Notebook
notebook = ttk.Notebook(app, style='My.TNotebook')
notebook.pack(expand=True, fill='both', side=tk.LEFT)

# 创建三个标签页
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)

notebook.add(tab1, text='文件生成')
notebook.add(tab2, text='自动计算')
notebook.add(tab3, text='文件分析')

# 使用更加美观的样式
style = ttk.Style()
style.configure('My.TNotebook.Tab', font=('Segoe UI', 12, 'bold'), padding=[20, 10], background='#5AC1EC', foreground='#5AC1EC')
style.configure('My.TNotebook', tabposition='wn', background='#5AC1EC')
style.configure('TLabel', font=('Helvetica', 12))
style.configure('TButton', font=('Helvetica', 12), borderwidth=1)
style.configure('TEntry', font=('Helvetica', 12), borderwidth=1)
style.configure('TText', font=('Helvetica', 12), borderwidth=1)

# 第一个标签页内容
def generate_vasp_files(material_name):
    status_label.config(text='文件生成')
    try:
        client = OpenAI(
            api_key='sk-aoLLexsH788Pi3YoC0158dEc6eB74211Ac1cCfAbD75670Cf',  # 替换为您的 OpenAI API 密钥
            base_url="https://api2.aigcbest.top/v1"  # 替换为您使用的 API base URL
        )

        response = client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=[
                {"role": "system", "content": "You are an assistant."},
                {"role": "user", "content": f"请你生成VASP用于计算{material_name}的INCAR、KPOINTS以及POSCAR文件。\
                     请注意，文件内容中不要出现注释。\
                     1.对于INCAR文件，生成时提供用于VASP计算的参数并注意格式正确，提供的参数进行适当取值，以加快VASP计算效率。\
                     2.对于KPOINTS文件，请在生成时提供以下参数并注意格式正确，提供的参数进行适当取值，以加快VASP计算效率：\
                     标题或注释：请提供一行描述该K点设置或实验的标题或注释。\
                     网格类型：请根据计算目标和晶体对称性选择适当的网格类型。\
                     K点网格密度：请选择合适的密度可以平衡计算精度和资源使用。并考虑晶体结构的对称性，以减少不必要的K点数目，从而优化计算时间。\
                     偏移量：选择是否使用偏移（通常为0 0 0或0.5 0.5 0.5）。对于非中心对称的晶格，使用偏移可以改善积分的准确性。\
                     3.对于POSCAR文件，请在生成时提供以下参数并注意格式正确，提供的参数进行适当取值，以加快VASP计算效率：\
                     标题或注释：请提供一行描述该结构或实验的标题或注释。\
                     缩放因子：请选择一个合理的缩放因子。\
                     晶胞基矢量：请确保基矢量与实际晶体对称性和维度相符，以避免不必要的计算负担。\
                     原子种类：请确保原子排序与计算效率和收敛性相匹配。\
                     原子数量：请为每种原子类型提供相应的数量。\
                     坐标类型：选择使用合适的坐标类型。\
                     原子坐标：请确保坐标精确无误，避免不必要的对称性破坏导致计算资源浪费。"},
            ],
        )
        result = response.choices[0].message.content
        vasp_content = extract_triple_backticks(result)
        if len(vasp_content) == 0:
            raise Exception("No VASP content found")

        # 将POSCAR内容写入文件
        poscar_path = "assets/生成POTCAR文件使用的文件/POSCAR"  # 使用相对路径
        with open(poscar_path, 'w') as f:
            f.write(vasp_content[2])  # 假设 vasp_content[2] 是 POSCAR 内容
            poscar = vasp_content[2]

        # 提取元素符号
        elements = extract_elements_from_poscar(poscar)

        # 生成 POTCAR 文件
        paw_pbe_path = "assets/PAW_PBE"  # 使用相对路径
        potcar_content, error_message = create_potcar(elements, paw_pbe_path)

        if error_message:
            raise Exception(error_message)

        # 将生成的 POTCAR 内容添加到返回列表
        vasp_content.append(potcar_content)

        return vasp_content
    except Exception as e:
        tk.messagebox.showerror("错误", str(e))



def extract_elements_from_poscar(poscar):
    elements = []
    # 假设元素符号在第六行
    element_line = poscar.split('\n')[6].strip()  # 直接获取第六行内容
    for element in element_line.split():  # 分割第六行，可能包含多个元素
        if element.isalpha():  # 确保只包含字母，排除数字和其他字符
            elements.append(element)
        else:
            # 如果元素行包含非字母字符，这通常不是标准的元素符号行
            break
    return elements



def create_potcar(elements, repo_path):
    potcar_combined = ""
    missing_elements = []
    for element in elements:
        element_path = os.path.join(repo_path, element, "POTCAR")
        try:
            with open(element_path, 'r') as file:
                potcar_combined += file.read()
        except FileNotFoundError:
            missing_elements.append(element)
    if missing_elements:
        return None, f"Error: POTCAR file not found for elements: {', '.join(missing_elements)}"
    return potcar_combined, None


def extract_triple_backticks(text):
    pattern = r'```(.*?)```'
    return re.findall(pattern, text, re.DOTALL)


def on_generate_button_clicked():
    material_name = simpledialog.askstring("输入", "请输入您需要计算的材料及其性质！")
    if material_name:
        thread = threading.Thread(target=lambda: run_vasp_task(material_name))
        thread.start()


def run_vasp_task(material_name):
    vasp_files = generate_vasp_files(material_name)
    if vasp_files:
        update_gui_with_results(vasp_files)


def update_gui_with_results(vasp_files):
    # 插入新内容
    incar, kpoints, poscar, potcar = vasp_files
    incar_text.insert(tk.END, incar.strip() + "\n")
    kpoints_text.insert(tk.END, kpoints.strip() + "\n")
    poscar_text.insert(tk.END, poscar.strip() + "\n")
    potcar_text.insert(tk.END, potcar.strip() + "\n")

def clear_all_text_areas():
    incar_text.delete("1.0", tk.END)
    kpoints_text.delete("1.0", tk.END)
    poscar_text.delete("1.0", tk.END)
    potcar_text.delete("1.0", tk.END)
    status_label.config(text='清除成功')


def save_files():
    status_label.config(text='保存中...')
    files = [('INCAR File', '*.INCAR'),
             ('KPOINTS File', '*.KPOINTS'),
             ('POSCAR File', '*.POSCAR'),
             ('POTCAR File', '*.POTCAR')]  # 新增 POTCAR 文件保存
    contents = [incar_text.get("1.0", tk.END), kpoints_text.get("1.0", tk.END),
                poscar_text.get("1.0", tk.END), potcar_text.get("1.0", tk.END)]
    for content, filetype in zip(contents, files):
        file = filedialog.asksaveasfilename(filetypes=[filetype], defaultextension=filetype)
        if file:
            with open(file, 'w') as f:
                f.write(content)
    app.after(1000, lambda: status_label.config(text='保存成功'))

# 设置tab1的布局自适应
tab1.grid_columnconfigure(0, weight=1)
tab1.grid_columnconfigure(1, weight=1)
tab1.grid_rowconfigure(0, weight=1)
tab1.grid_rowconfigure(1, weight=1)

# Setting up text areas for output in a grid to form a 2x2 layout
incar_text = tk.Text(tab1, height=10, width=50)
incar_text.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

kpoints_text = tk.Text(tab1, height=10, width=50)
kpoints_text.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

poscar_text = tk.Text(tab1, height=10, width=50)
poscar_text.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

potcar_text = tk.Text(tab1, height=10, width=50)
potcar_text.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')

# 状态标签
status_label = tk.Label(tab1, text="准备就绪", fg='green')
status_label.grid(row=2, column=0, columnspan=2, sticky='ew')

# Set up a frame for buttons to ensure alignment
button_frame = tk.Frame(tab1)
button_frame.grid(row=3, column=0, columnspan=2, sticky='ew')

# Configure buttons to be in the button frame
button_width = 20  # Uniform button width

generate_button = tk.Button(button_frame, text="生成VASP文件", command=on_generate_button_clicked, bg='#add8e6', width=button_width)
generate_button.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)

save_button = tk.Button(button_frame, text="保存文件", command=save_files, bg='#add8e6', width=button_width)
save_button.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)

clear_button = tk.Button(button_frame, text="清空输出", command=clear_all_text_areas, bg='#add8e6', width=button_width)
clear_button.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)


# 第二个标签页内容
# tab2 中的组件设置
def open_folder():
    folder_path = os.path.join(app_root, 'assets', 'VASP_files')
    os.startfile(folder_path)

def upload_files():
    files = filedialog.askopenfilenames(title="Select files to upload")
    base_destination_folder = os.path.join(app_root, 'assets', 'VASP_files')
    for file in files:
        # 获取文件名和扩展名
        base_name = os.path.basename(file)
        # 截取文件扩展名作为新文件名（包括点）
        new_file_name = base_name.split('.')[-1] if '.' in base_name else base_name
        # 构建目标文件的完整路径
        destination_path = os.path.join(base_destination_folder, new_file_name)
        try:
            shutil.copy(file, destination_path)
            message_label.config(text="上传成功", fg='green')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload files: {e}")

def clear_files():
    folder_path = os.path.join(app_root, 'assets', 'VASP_files')
    exclude_files = ["run.sh"]
    try:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if file not in exclude_files:
                os.chmod(file_path, stat.S_IWRITE)
                os.remove(file_path)
        message_label.config(text="清除成功", fg='green')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to clear files: {e}")

def run_vasp_calculation():
    script_path = os.path.join(app_root, 'assets', 'complete_vasp_workflow.sh')
    bash_path = os.path.join(app_root, 'assets', 'Git', 'bin', 'bash.exe')
    message_label.config(text="VASP计算已启动", fg='blue')
    app.update()
    try:
        subprocess.run([bash_path, script_path], cwd=os.path.join(app_root, 'assets'), check=True)
        message_label.config(text="VASP计算已完成", fg='green')
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"VASP calculation failed: {e}")


font_style = ('Verdana', 10)
button_width = 20  # 可以根据需要调整宽度

# 设置每一列的权重，允许他们随窗口宽度变化
tab2.grid_columnconfigure(0, weight=1)
tab2.grid_columnconfigure(1, weight=1)
tab2.grid_columnconfigure(2, weight=1)
tab2.grid_columnconfigure(3, weight=1)

# 加载图片
photo = PhotoImage(file = os.path.join(app_root, 'assets', 'VASP程序内用图2.png'))  # 确保路径正确

# 创建图片显示标签
image_label = tk.Label(tab2, image=photo)
image_label.photo = photo  # 保持对图片的引用
image_label.grid(row=2, column=0, columnspan=4, sticky='nsew', padx=20, pady=10)

# 上传按钮
upload_button = tk.Button(tab2, text="上传并重命名文件", command=upload_files, font=font_style, bg='lightblue', activebackground='blue', pady=5, width=button_width)
upload_button.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

# 清除按钮
clear_button = tk.Button(tab2, text="清除VASP文件", command=clear_files, font=font_style, bg='lightblue', activebackground='blue', pady=5, width=button_width)
clear_button.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)

# 运行计算按钮
run_button = tk.Button(tab2, text="VASP自动化计算", command=run_vasp_calculation, font=font_style, bg='lightblue', activebackground='blue', pady=5, width=button_width)
run_button.grid(row=0, column=2, sticky='nsew', padx=20, pady=20)

# 打开文件夹按钮
open_folder_button = tk.Button(tab2, text="打开VASP文件夹", command=open_folder, font=font_style, bg='lightblue', activebackground='blue', pady=5, width=button_width)
open_folder_button.grid(row=0, column=3, sticky='nsew', padx=20, pady=20)

# 消息显示框
message_label = tk.Label(tab2, text="", bg='lightgrey', font=font_style, width=button_width)
message_label.grid(row=1, column=0, columnspan=4, sticky='nsew', padx=20, pady=20)

# 第三个标签页(tab3)可以用于上传分析结果的功能
chat_frame = tk.Frame(tab3, bg='#FAFAFA')
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_area = tk.Text(chat_frame, font=font_style)
chat_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(chat_frame, command=chat_area.yview, bg='#FAFAFA')
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

chat_area['yscrollcommand'] = scrollbar.set

# Prevent the user from typing in the conversation box
chat_area.config(state=tk.DISABLED)

input_frame = tk.Frame(tab3, bg='#FAFAFA')
input_frame.pack(padx=10, pady=10, fill=tk.X)


# 上传按钮
def upload_vasp_files():
    status_label.config(text='上传中...')
    files = [('INCAR File', '*.INCAR'),
             ('KPOINTS File', '*.KPOINTS'),
             ('POSCAR File', '*.POSCAR'),
             ('POTCAR File', '*.POTCAR')]  # 新增 POTCAR 文件保存
    # 依次上传四个文件
    contents = ['', '', '']
    potcarFilePath = ''
    for file_type in files:
        file = filedialog.askopenfilename(filetypes=[file_type])
        if file:
            with open(file, 'r') as f:
                content = f.read()
                if file_type[0] == 'INCAR File':
                    contents[0] = content
                elif file_type[0] == 'KPOINTS File':
                    contents[1] = content
                elif file_type[0] == 'POSCAR File':
                    contents[2] = content
                elif file_type[0] == 'POTCAR File':
                    potcarFilePath = file
                f.close()

    if len(potcarFilePath) == 0:
        print("POTCAR文件不存在")

    try:
        client = OpenAI(
            api_key="sk-ysfmTMyaR0sACpKMSNLEh0Qw4cxN5H4l8FTATZOI0NHsdL4m",
            base_url="https://api.moonshot.cn/v1"  # 替换为您使用的 API base URL
        )

        # 复制potcar文件，后缀改为txt
        tmpPotcarFilePath = potcarFilePath.replace(".POTCAR", ".txt")
        shutil.copyfile(potcarFilePath, tmpPotcarFilePath)

        # 上传文件到openai
        # uploadFileInfo = client.files.create(
        #     file=open(tmpPotcarFilePath, "rb"),
        #     purpose="file-extract")
        # print(uploadFileInfo)
        tmpFileId = 'cqdnrtpr6kjbs01q0v40'  # uploadFileInfo.id
        file_content = client.files.content(file_id=tmpFileId).text
        cutFileContent = file_content[:2000]  # 截取文件内容的前1000个字符

        # 分析vasp文件内容
        response = client.chat.completions.create(
            model="moonshot-v1-128k",
            messages=[
                {"role": "system", "content": "You are an assistant."},
                {"role": "user",
                 "content": f"请你分析文件内容并修改上传的INCAR文件、KPOINTS文件和POSCAR文件中存在问题的部分，其中INCAR文件内容为：{contents[0]}，KPOINTS文件内容为：{contents[1]}，POSCAR文件内容为：{contents[2]}。"},
                {"role": "user", "content": f"POTCAR文件内容为：{cutFileContent}"}
            ])
        result = response.choices[0].message.content
        print(result)
        chat_area.config(state=tk.NORMAL)  # allow editing of the chat area
        chat_area.insert(tk.END, "Alex: " + result + "\n")  # add the response to the chat area
        chat_history.append({"role": "assistant", "content": result})  # add the AI's response to the chat history
        chat_area.yview(tk.END)  # automatically scroll to the end of the chat
        chat_area.config(state=tk.DISABLED)  # prevent editing of the chat area
    except Exception as e:
        tk.messagebox.showerror("错误", str(e))


upload_button1 = tk.Button(input_frame, text="上传文件并分析", command=upload_vasp_files, font=font_style,
                           bg='lightblue', activebackground='blue', pady=5, width=button_width)
upload_button1.pack(padx=20, pady=20, fill=tk.X, expand=True)

user_input = tk.Entry(input_frame, bg='#FAFAFA', fg='#9BC53D', font=font_style)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)

# Set focus to the input box
user_input.focus()

# The chat history is a list of dictionaries, where each dictionary has two keys: "role" and "content".
chat_history = [
    {"role": "system", "content": "You are a helpful assistant."},
]


def clear_chat():
    chat_area.delete('1.0', tk.END)


def send_message(event=None):
    message = user_input.get().strip()  # get the user's input and strip whitespace

    if not message:
        tk.messagebox.showwarning("Warning", "Message cannot be empty.")
        return

    user_input.delete(0, tk.END)  # clear the input box
    chat_area.config(state=tk.NORMAL)  # allow editing of the chat area
    chat_area.insert(tk.END, "User: " + message + "\n")  # add the user's message to the chat area
    chat_history.append({"role": "user", "content": message})  # add the user's message to the chat history

    response = None
    try:
        client = OpenAI(
            api_key="sk-ysfmTMyaR0sACpKMSNLEh0Qw4cxN5H4l8FTATZOI0NHsdL4m",
            base_url="https://api.moonshot.cn/v1"  # 替换为您使用的 API base URL
        )

        response = client.chat.completions.create(
            model="moonshot-v1-128k",
            messages=chat_history
        )
    except Exception as e:
        chat_area.insert(tk.END, "Alex: " + "I'm sorry, I encountered an error: " + str(e) + "\n")
        return

    response_content = response.choices[0].message.content
    print(response_content)
    chat_area.insert(tk.END, "Alex: " + response_content + "\n")  # add the response to the chat area
    chat_history.append({"role": "assistant", "content": response_content})  # add the AI's response to the chat history
    chat_area.yview(tk.END)  # automatically scroll to the end of the chat
    chat_area.config(state=tk.DISABLED)  # prevent editing of the chat area


clear_button = tk.Button(input_frame, text="Clear Chat", bg='#323031', fg='#8BCD51', command=clear_chat,
                         font=font_style, relief='groove')
clear_button.pack(side=tk.RIGHT, ipadx=5, ipady=5)

send_button = tk.Button(input_frame, text="Send", bg='#323031', fg='#8BCD51', command=send_message, font=font_style,
                        relief='groove')
send_button.pack(side=tk.RIGHT, ipadx=5, ipady=5)
tab3.bind("<Return>", send_message)

app.mainloop()
