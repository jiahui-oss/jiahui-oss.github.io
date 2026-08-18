from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.text import LabelBase
import os
from . import xuanjie_l
from datetime import datetime

# ========== 中文字体配置 ==========
字体候选列表 = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
]

中文字体路径 = None
for 字体路径 in 字体候选列表:
    if os.path.exists(字体路径):
        中文字体路径 = 字体路径
        break

if 中文字体路径:
    LabelBase.register(name="中文字体", fn_regular=中文字体路径)
    默认字体 = "中文字体"
else:
    默认字体 = "Roboto"


# ========== 加载页面 ==========
class 加载页面(Screen):
    """游戏启动时的加载页面，显示进度条"""

    def __init__(self, **参数):
        super().__init__(**参数)
        # 主布局：垂直排列
        布局 = BoxLayout(orientation="vertical", padding=40, spacing=20)
        # 游戏标题
        self.标题标签 = Label(text="泼天问道", font_size=32, font_name=默认字体)
        # 进度条
        self.进度条 = ProgressBar(max=100, value=0, size_hint=(1, 0.1))
        # 进入游戏按钮，初始不可用
        self.进入按钮 = Button(
            text="进入游戏",
            size_hint=(0.6, 0.15),
            pos_hint={"center_x": 0.5},
            font_name=默认字体
        )
        self.进入按钮.disabled = True
        self.进入按钮.bind(on_press=self.跳转菜单)
        # 组装布局
        布局.add_widget(self.标题标签)
        布局.add_widget(self.进度条)
        布局.add_widget(self.进入按钮)
        self.add_widget(布局)
        # 启动加载进度模拟
        self.加载生成器 = xuanjie_l.模拟加载()
        Clock.schedule_interval(self.加载进度更新, 0.15)

    def 加载进度更新(self, 时间间隔):
        """每帧更新进度条"""
        try:
            进度值 = next(self.加载生成器)
            self.进度条.value = 进度值
        except StopIteration:
            # 加载完成，启用进入按钮
            self.进入按钮.disabled = False
            return False

    def 跳转菜单(self, 实例):
        """跳转到主菜单页面"""
        self.manager.current = "菜单"


# ========== 主菜单页面 ==========
class 主菜单页面(Screen):
    """游戏主菜单，包含新游戏、继续游戏、存档管理、设置"""

    def __init__(self, **参数):
        super().__init__(**参数)
        # 主布局：垂直排列
        布局 = BoxLayout(orientation="vertical", padding=60, spacing=18)
        布局.add_widget(Label(text="主菜单", font_size=28, size_hint=(1, 0.2), font_name=默认字体))

        # 新游戏按钮
        新游戏按钮 = Button(text="新游戏", size_hint=(0.7, 0.12), pos_hint={"center_x": 0.5}, font_name=默认字体)
        # 继续游戏按钮
        self.继续游戏按钮 = Button(text="继续游戏", size_hint=(0.7, 0.12), pos_hint={"center_x": 0.5}, font_name=默认字体)
        # 存档管理按钮
        存档管理按钮 = Button(text="存档管理", size_hint=(0.7, 0.12), pos_hint={"center_x": 0.5}, font_name=默认字体)
        # 设置按钮
        设置按钮 = Button(text="设置", size_hint=(0.7, 0.12), pos_hint={"center_x": 0.5}, font_name=默认字体)

        # 绑定事件
        新游戏按钮.bind(on_press=self.跳转创建角色)
        self.继续游戏按钮.bind(on_press=self.继续游戏)
        存档管理按钮.bind(on_press=self.打开存档管理)

        # 根据存档存在与否决定是否禁用继续游戏按钮
        if not xuanjie_l.存在存档():
            self.继续游戏按钮.disabled = True

        # 组装布局
        布局.add_widget(新游戏按钮)
        布局.add_widget(self.继续游戏按钮)
        布局.add_widget(存档管理按钮)
        布局.add_widget(设置按钮)
        self.add_widget(布局)

    def on_enter(self):
        """每次进入菜单时刷新继续游戏按钮状态"""
        self.继续游戏按钮.disabled = not xuanjie_l.存在存档()

    def 跳转创建角色(self, 实例):
        """跳转到角色创建页面"""
        self.manager.current = "创建角色"

    def 继续游戏(self, 实例):
        """读取存档并显示"""
        存档 = xuanjie_l.读取存档()
        if 存档:
            self.显示存档弹窗("继续游戏", 存档)

    def 打开存档管理(self, 实例):
        """打开存档管理弹窗"""
        存档 = xuanjie_l.读取存档()
        if 存档:
            self.显示存档弹窗("存档管理", 存档)
        else:
            self.显示提示弹窗("暂无存档", "当前没有任何存档记录。")

    def 显示存档弹窗(self, 标题, 存档):
        """显示存档详细信息弹窗"""
        内容布局 = BoxLayout(orientation="vertical", padding=15, spacing=10)
        信息文本 = (
            f"道号：{存档.get('道号', '无名')}\n"
            f"种族：{存档.get('种族', '未知')}\n"
            f"性别：{存档.get('性别', '未知')}\n"
            f"灵根：{存档.get('灵根', '未知')}\n"
            f"创建时间：{存档.get('创建时间', '未知')}\n"
            f"最后保存：{存档.get('保存时间', '未知')}"
        )
        内容布局.add_widget(Label(text=信息文本, font_name=默认字体))
        关闭按钮 = Button(text="关闭", size_hint=(1, 0.18), font_name=默认字体)
        内容布局.add_widget(关闭按钮)
        弹窗 = Popup(title=标题, content=内容布局, size_hint=(0.8, 0.55), auto_dismiss=False)
        关闭按钮.bind(on_press=弹窗.dismiss)
        弹窗.open()

    def 显示提示弹窗(self, 标题, 消息):
        """显示简单的提示弹窗"""
        内容布局 = BoxLayout(orientation="vertical", padding=15)
        内容布局.add_widget(Label(text=消息, font_name=默认字体))
        确定按钮 = Button(text="知道了", size_hint=(1, 0.25), font_name=默认字体)
        内容布局.add_widget(确定按钮)
        弹窗 = Popup(title=标题, content=内容布局, size_hint=(0.5, 0.25), auto_dismiss=False)
        确定按钮.bind(on_press=弹窗.dismiss)
        弹窗.open()


# ========== 角色创建页面 ==========
class 角色创建页面(Screen):
    """角色创建页面，包含道号、种族、性别输入和灵根预览"""

    def __init__(self, **参数):
        super().__init__(**参数)
        # 根布局：垂直排列，适合手机竖屏
        根布局 = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # ===== 页面标题 =====
        根布局.add_widget(Label(
            text="创建角色 · 觉醒灵根",
            font_size=22,
            size_hint=(1, 0.06),
            font_name=默认字体
        ))

        # ===== 基础信息表单 =====
        表单布局 = GridLayout(cols=2, spacing=(10, 8), size_hint=(1, 0.22))

        # 道号输入
        表单布局.add_widget(Label(text="道号", font_name=默认字体, halign="right", size_hint_x=0.22))
        self.道号输入框 = TextInput(
            hint_text="请输入道号",
            multiline=False,
            font_name=默认字体,
            padding=(8, 8),
            size_hint_y=0.8
        )
        表单布局.add_widget(self.道号输入框)

        # 种族选择
        表单布局.add_widget(Label(text="种族", font_name=默认字体, halign="right"))
        种族按钮容器 = BoxLayout(orientation="horizontal", spacing=4)
        self.种族按钮字典 = {}
        for 种族名 in ["人族", "妖族", "灵族"]:
            按钮 = ToggleButton(text=种族名, group="种族", font_name=默认字体)
            if 种族名 == "人族":
                按钮.state = "down"
            self.种族按钮字典[种族名] = 按钮
            种族按钮容器.add_widget(按钮)
        表单布局.add_widget(种族按钮容器)

        # 性别选择
        表单布局.add_widget(Label(text="性别", font_name=默认字体, halign="right"))
        性别按钮容器 = BoxLayout(orientation="horizontal", spacing=4)
        self.性别按钮字典 = {}
        for 性别名 in ["男", "女"]:
            按钮 = ToggleButton(text=性别名, group="性别", font_name=默认字体)
            if 性别名 == "男":
                按钮.state = "down"
            self.性别按钮字典[性别名] = 按钮
            性别按钮容器.add_widget(按钮)
        表单布局.add_widget(性别按钮容器)

        # 先天灵根显示（只读，用于预览）
        表单布局.add_widget(Label(text="先天灵根", font_name=默认字体, halign="right"))
        self.灵根显示标签 = Label(
            text="尚未预览",
            font_name=默认字体,
            color=(0.6, 0.6, 0.6, 1)
        )
        表单布局.add_widget(self.灵根显示标签)

        根布局.add_widget(表单布局)

        # ===== 五行灵根预览按钮 =====
        根布局.add_widget(Label(
            text="灵根预览 · 点击五行查看",
            size_hint=(1, 0.04),
            font_name=默认字体,
            color=(0.8, 0.8, 0.8, 1)
        ))
        五行按钮容器 = BoxLayout(orientation="horizontal", size_hint=(1, 0.08), spacing=8)
        for 五行名 in ["木", "火", "土", "金", "水"]:
            按钮 = Button(
                text=五行名,
                font_name=默认字体,
                font_size=18
            )
            按钮.bind(on_press=lambda 实例, 五行=五行名: self.打开灵根预览(五行))
            五行按钮容器.add_widget(按钮)
        根布局.add_widget(五行按钮容器)

        # ===== 灵根详解区域 =====
        根布局.add_widget(Label(
            text="灵根详解",
            size_hint=(1, 0.04),
            font_name=默认字体,
            color=(0.8, 0.8, 0.8, 1)
        ))
        滚动区域 = ScrollView(size_hint=(1, 0.28))
        self.详解标签 = Label(
            text="点击上方五行按钮，预览该系灵根详情……",
            font_name=默认字体,
            valign="top",
            halign="left",
            padding=(10, 10),
            color=(0.85, 0.85, 0.85, 1)
        )
        # 绑定宽度变化以自动换行
        self.详解标签.bind(
            width=lambda *x: setattr(self.详解标签, 'text_size', (self.详解标签.width, None))
        )
        # 绑定文本大小变化以自动调整高度
        self.详解标签.bind(
            texture_size=lambda *x: setattr(self.详解标签, 'height', self.详解标签.texture_size[1])
        )
        滚动区域.add_widget(self.详解标签)
        根布局.add_widget(滚动区域)

        # ===== 底部操作按钮 =====
        底部按钮容器 = BoxLayout(orientation="horizontal", size_hint=(1, 0.08), spacing=10)
        保存按钮 = Button(
            text="踏入玄界（保存存档）",
            font_name=默认字体,
            background_color=(0.2, 0.6, 0.3, 1)
        )
        返回按钮 = Button(text="返回主菜单", font_name=默认字体)
        保存按钮.bind(on_press=self.保存并进入游戏)
        返回按钮.bind(on_press=self.返回主菜单)
        底部按钮容器.add_widget(保存按钮)
        底部按钮容器.add_widget(返回按钮)
        根布局.add_widget(底部按钮容器)

        self.add_widget(根布局)

    def 获取选中项(self, 按钮字典):
        """从一组ToggleButton中获取当前选中的项"""
        for 键, 值 in 按钮字典.items():
            if 值.state == "down":
                return 键
        return list(按钮字典.keys())[0]

    def 打开灵根预览(self, 五行名):
        """打开指定五行的灵根预览弹窗，显示阴、阳两种灵根"""
        # 更新当前预览的五行到显示标签
        self.灵根显示标签.text = f"{五行名}行灵根"
        self.灵根显示标签.color = (0.9, 0.7, 0.3, 1)

        # 构建弹窗内容
        弹窗内容 = BoxLayout(orientation="vertical", padding=15, spacing=10)

        # 弹窗标题区域
        弹窗内容.add_widget(Label(
            text=f"═══ {五行名}行灵根 ═══",
            font_name=默认字体,
            font_size=20,
            size_hint=(1, 0.06)
        ))

        # 阴灵根内容
        阴灵根数据 = xuanjie_l.灵根数据[五行名]["阴"]
        弹窗内容.add_widget(Label(
            text=f"◆ {阴灵根数据['名称']}【阴】",
            font_name=默认字体,
            color=(0.6, 0.8, 1, 1),
            halign="left",
            size_hint=(1, 0.04)
        ))
        阴描述标签 = Label(
            text=阴灵根数据['描述'],
            font_name=默认字体,
            halign="left",
            valign="top",
            padding=(8, 8),
            color=(0.9, 0.9, 0.9, 1)
        )
        阴描述标签.bind(width=lambda *x: setattr(阴描述标签, 'text_size', (阴描述标签.width, None)))
        弹窗内容.add_widget(阴描述标签)

        # 阳灵根内容
        阳灵根数据 = xuanjie_l.灵根数据[五行名]["阳"]
        弹窗内容.add_widget(Label(
            text=f"◆ {阳灵根数据['名称']}【阳】",
            font_name=默认字体,
            color=(1, 0.8, 0.6, 1),
            halign="left",
            size_hint=(1, 0.04)
        ))
        阳描述标签 = Label(
            text=阳灵根数据['描述'],
            font_name=默认字体,
            halign="left",
            valign="top",
            padding=(8, 8),
            color=(0.9, 0.9, 0.9, 1)
        )
        阳描述标签.bind(width=lambda *x: setattr(阳描述标签, 'text_size', (阳描述标签.width, None)))
        弹窗内容.add_widget(阳描述标签)

        # 关闭按钮
        关闭按钮 = Button(text="关闭", size_hint=(1, 0.08), font_name=默认字体)
        弹窗内容.add_widget(关闭按钮)

        # 创建并打开弹窗
        弹窗 = Popup(
            title=f"{五行名}行灵根预览",
            content=弹窗内容,
            size_hint=(0.92, 0.8),
            auto_dismiss=False
        )
        关闭按钮.bind(on_press=弹窗.dismiss)
        弹窗.open()

        # 同时更新主界面的详解区域
        主界面文本 = (
            f"═══【{五行名}行】═══\n\n"
            f"◆ {阴灵根数据['名称']}【阴】\n{阴灵根数据['描述']}\n\n"
            f"◆ {阳灵根数据['名称']}【阳】\n{阳灵根数据['描述']}"
        )
        self.详解标签.text = 主界面文本

    def 保存并进入游戏(self, 实例):
        """保存角色信息到存档并返回主菜单"""
        道号 = self.道号输入框.text.strip()
        if not 道号:
            self.显示错误弹窗("请填写道号")
            return

        存档数据 = {
            "道号": 道号,
            "种族": self.获取选中项(self.种族按钮字典),
            "性别": self.获取选中项(self.性别按钮字典),
            "灵根": self.灵根显示标签.text,
            "创建时间": datetime.now().isoformat()
        }
        xuanjie_l.保存存档(存档数据)

        # 显示保存成功弹窗
        内容布局 = BoxLayout(orientation="vertical", padding=15)
        内容布局.add_widget(Label(
            text=f"存档已保存\n{道号}，欢迎来到玄界。",
            font_name=默认字体
        ))
        确定按钮 = Button(text="确定", size_hint=(1, 0.25), font_name=默认字体)
        内容布局.add_widget(确定按钮)
        弹窗 = Popup(title="踏入玄界", content=内容布局, size_hint=(0.6, 0.3), auto_dismiss=False)

        def 关闭并跳转(*参数):
            弹窗.dismiss()
            self.manager.current = "菜单"

        确定按钮.bind(on_press=关闭并跳转)
        弹窗.open()

    def 显示错误弹窗(self, 消息):
        """显示错误提示弹窗"""
        内容布局 = BoxLayout(orientation="vertical", padding=15)
        内容布局.add_widget(Label(text=消息, font_name=默认字体, color=(1, 0.4, 0.4, 1)))
        确定按钮 = Button(text="知道了", size_hint=(1, 0.3), font_name=默认字体)
        内容布局.add_widget(确定按钮)
        弹窗 = Popup(title="提示", content=内容布局, size_hint=(0.5, 0.25), auto_dismiss=False)
        确定按钮.bind(on_press=弹窗.dismiss)
        弹窗.open()

    def 返回主菜单(self, 实例):
        """返回主菜单页面"""
        self.manager.current = "菜单"


# ========== 应用程序入口 ==========
class 泼天应用(App):
    """Kivy应用程序主类"""

    def build(self):
        """构建页面管理器并注册所有页面"""
        页面管理器 = ScreenManager()
        页面管理器.add_widget(加载页面(name="加载"))
        页面管理器.add_widget(主菜单页面(name="菜单"))
        页面管理器.add_widget(角色创建页面(name="创建角色"))
        return 页面管理器


if __name__ == "__main__":
    泼天应用().run()
