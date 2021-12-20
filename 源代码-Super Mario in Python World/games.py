from pgzero import clock, game, music
from pgzero.actor import Actor
from pgzero.loaders import sounds
import pgzrun
import numpy as np
import random
import copy
import time

WIDTH = 640
HEIGHT = 480
dx = (0, 0, -1, 1)
dy = (-1, 1, 0, 0)


# -----------------------------------maze-----------------------------------#
class MAZE:
    def __init__(self):
        self.l1, self.l2 = 32, 32
        self.W_1, self.H_1 = (
            (WIDTH * 2 // self.l1 - 1) // 2,
            (HEIGHT * 2 // self.l2 - 1) // 2,
        )
        self.player_static = Actor("mario1")
        self.player_move1 = Actor("mario3")
        self.player_move2 = Actor("mario1")
        self.water = Actor("water")
        self.rule_maze = Actor("rule_maze")
        self.start_button = Actor("begin")
        self.shadow = Actor("black")
        self.end_x, self.end_y = self.W_1 * 2 - 1, self.H_1 * 2 - 1
        self.mode = 1

    def main_maze(self):
        self.pos_flag = 1
        self.flag = 1
        self.start_time = time.time()
        self.count_time = 0
        self.score = 0
        self.action = 0

        self.pressed = False
        self.generated = False
        no_wall = np.zeros((self.W_1, self.H_1, 4), dtype=np.uint8)
        maps_vis = np.zeros((self.W_1, self.H_1), dtype=np.uint8)
        maps_content = np.zeros(
            (self.W_1 * 2 + 1, self.H_1 * 2 + 1)
        )  # 1表示没有东西可行走，0表示砖块， 2表示金币， -2表示终点
        self.ground_blocks = np.empty((self.W_1 * 2 + 1, self.H_1 * 2 + 1), Actor)

        self.player_static.pos = self.player_move1.pos = self.player_move2.pos = (
            2 * self.l1,
            2 * self.l2,
        )
        maps_content = self.prim_produce(no_wall, maps_vis, maps_content)  # 生成迷宫
        maps_content[self.end_x][self.end_y] = -2
        # 随机生成金币奖励
        cnt = 0
        temp = copy.deepcopy(maps_content)
        while cnt <= 15:
            maps_content = copy.deepcopy(temp)
            for i in range(self.W_1 * 2 + 1):
                for j in range(self.H_1 * 2 + 1):
                    if maps_content[i][j] == 1 and not (i == 1 and j == 1):
                        t = random.randint(1, 30)
                        if t % 7 == 0:
                            maps_content[i][j] = 2
                            cnt += 1
        self.maps_content = maps_content

    def prim_produce(self, no_wall, maps_vis, maps_content):
        vis_lis = [(0, 0)]  # 存储待处理的单元格
        while vis_lis:  # Prim随机生成迷宫
            x, y = random.choice(vis_lis)
            maps_vis[x][y] = 1
            vis_lis.remove((x, y))
            check = []
            for i in range(4):  # 检测四个方向是否相通
                xx = x + dx[i]
                yy = y + dy[i]
                if xx < 0 or yy < 0 or xx >= self.W_1 or yy >= self.H_1:
                    continue
                if maps_vis[xx][yy] == 1:
                    check.append(i)
                elif maps_vis[xx][yy] == 0:
                    vis_lis.append((xx, yy))
                    maps_vis[xx][yy] = 2
            if len(check):
                k = random.choice(check)
                no_wall[x][y][k] = 1
                k_ = -1
                if k == 0 or k == 2:
                    k_ = k + 1
                else:
                    k_ = k - 1
                no_wall[x + dx[k]][y + dy[k]][k_] = 1
        for i in range(self.W_1):  # 将原本只有单元格的数组转变成包含墙的数组
            for j in range(self.H_1):
                cell_data = no_wall[i][j]
                maps_content[i * 2 + 1][j * 2 + 1] = 1
                x = i * 2 + 1
                y = j * 2 + 1
                for k in range(4):
                    if cell_data[k] == 1:
                        maps_content[x + dx[k]][y + dy[k]] = 1
        return maps_content

    def show_ground(self):
        t1, t2, t3, t4 = 0, 0, 20, 15
        t5, t6 = 0, 0
        if self.pos_flag == 2:
            t1, t2, t3, t4 = 20, 0, 39, 15
            t5, t6 = 19, 0
        elif self.pos_flag == 3:
            t1, t2, t3, t4 = 0, 15, 20, 29
            t5, t6 = 0, 14
        elif self.pos_flag == 4:
            t1, t2, t3, t4 = 20, 15, 39, 29
            t5, t6 = 19, 14
        if self.generated == False:  # 当切换界面时才重新生成数组存储要展现的图像
            self.generated = True
            for i in range(39):
                for j in range(29):
                    if self.maps_content[i][j] == 0:
                        self.ground_blocks[i][j] = Actor("ground1")
                        self.ground_blocks[i][j].pos = (
                            (i - t1) * self.l1 + self.l1,
                            (j - t2) * self.l2 + self.l2,
                        )
                        self.ground_blocks[i][j].draw()
                    elif self.maps_content[i][j] == -2:
                        self.ground_blocks[i][j] = Actor("exit")
                        self.ground_blocks[i][j].pos = (
                            (i - t1) * self.l1 + self.l1,
                            (j - t2) * self.l2 + self.l2,
                        )
                        self.ground_blocks[i][j].draw()
                    elif self.maps_content[i][j] == 2:
                        self.ground_blocks[i][j] = Actor("coin")
                        self.ground_blocks[i][j].pos = (
                            (i - t1) * self.l1 + self.l1,
                            (j - t2) * self.l2 + self.l2,
                        )
                        self.ground_blocks[i][j].draw()
        else:
            for i in range(t5, t3):
                for j in range(t6, t4):
                    if self.maps_content[i][j] != 1 and self.maps_content[i][j] != -2:
                        self.ground_blocks[i][j].pos = (
                            (i - t1) * self.l1 + self.l1,
                            (j - t2) * self.l2 + self.l2,
                        )
                        self.ground_blocks[i][j].draw()
                    elif self.maps_content[i][j] == -2:
                        self.ground_blocks[i][j].pos = (
                            (i - t1) * self.l1 + self.l1,
                            (j - t2) * self.l2 + self.l2,
                        )
                        self.ground_blocks[i][j].draw()

    def move_player(self):  # 控制人物的移动
        self.x2 = self.x1 + dx[self.action] * self.l1
        self.y2 = self.y1 + dy[self.action] * self.l2
        self.player_static.x += dx[self.action] * self.l1
        self.player_static.y += dy[self.action] * self.l2
        if self.x1 <= WIDTH and self.x2 > WIDTH and self.action == 3:
            self.pos_flag += 1
            self.x1 = self.x2 = self.player_static.x = 0
        if self.x2 < 0 and self.x1 >= 0 and self.action == 2:
            self.pos_flag -= 1
            self.x1 = self.x2 = self.player_static.x = WIDTH
        if self.y2 > HEIGHT and self.y1 <= HEIGHT and self.action == 1:
            self.pos_flag += 2
            self.y1 = self.y2 = self.player_static.y = 0
        if self.y2 < 0 and self.y1 >= 0 and self.action == 0:
            self.pos_flag -= 2
            self.y1 = self.y2 = self.player_static.y = HEIGHT

    def animation(self):  # 实现移动的动画效果---通过位移
        if self.flag > 10:
            self.flag = -1
        if self.flag < -10:
            self.flag = 1
        while self.x1 != self.x2:
            if abs(self.x1 - self.x2) >= 3:
                self.x1 += dx[self.action] * 3
            else:
                self.x1 += dx[self.action]
            self.player_move1.x = self.x1
            self.player_move2.x = self.x1
            return False
        while self.y1 != self.y2:
            if abs(self.y1 - self.y2) >= 3:
                self.y1 += dy[self.action] * 3
            else:
                self.y1 += dy[self.action]
            self.player_move1.y = self.y1
            self.player_move2.y = self.y1
            return False
        return True

    def win(self):  # 如果赢了那先再持续播放4s（在外部函数的draw中判断）再结束
        global Win, end_time, Coins
        music.pause()
        sounds.pass_.play()
        Coins += self.score
        if not Win:
            pass_through[2] = pass_through[3] = True
            cases[3].image = "4"
            cases[4].image = "5"
            end_time = time.time()
            Win = True

    def play_maze(self):  # 感应键盘的操作
        if self.mode == 1:
            return
        if self.pressed:
            return
        self.x1, self.y1 = x, y = self.player_static.pos
        x_block, y_block = int(x // self.l1) - 1, int(y // self.l2) - 1
        if self.pos_flag == 2:
            x_block += 20
        elif self.pos_flag == 4:
            x_block += 20
            y_block += 15
        elif self.pos_flag == 3:
            y_block += 15
        if keyboard.left and x_block > 1:
            self.action = 2
            self.player_static.image = "mario1r"
            self.player_move1.image = "mario3r"
            self.player_move2.image = "mario1r"
            if self.maps_content[x_block - 1][y_block] != 0:
                self.pressed = True
                self.move_player()
            if self.maps_content[x_block - 1][y_block] == 2:
                self.maps_content[x_block - 1][y_block] = 1
                self.score += 1
                sounds.coin.play()
            if self.maps_content[x_block - 1][y_block] == -2:
                self.win()
        elif keyboard.right and x_block < self.end_x:
            self.action = 3
            self.player_static.image = "mario1"
            self.player_move1.image = "mario3"
            self.player_move2.image = "mario1"
            if self.maps_content[x_block + 1][y_block] != 0:
                self.pressed = True
                self.move_player()
            if self.maps_content[x_block + 1][y_block] == 2:
                self.maps_content[x_block + 1][y_block] = 1
                self.score += 1
                sounds.coin.play()
            if self.maps_content[x_block + 1][y_block] == -2:
                self.win()
        elif keyboard.up and y_block > 1:
            self.action = 0
            if self.maps_content[x_block][y_block - 1] != 0:
                self.pressed = True
                self.move_player()
            if self.maps_content[x_block][y_block - 1] == 2:
                self.maps_content[x_block][y_block - 1] = 1
                self.score += 1
                sounds.coin.play()
            if self.maps_content[x_block][y_block - 1] == -2:
                self.win()
        elif keyboard.down and y_block < self.end_y:
            self.action = 1
            if self.maps_content[x_block][y_block + 1] != 0:
                self.pressed = True
                self.move_player()
            if self.maps_content[x_block][y_block + 1] == 2:
                self.maps_content[x_block][y_block + 1] = 1
                self.score += 1
                sounds.coin.play()
            if self.maps_content[x_block][y_block + 1] == -2:
                self.win()
        if (
            keyboard.right
            and self.player_static.x == WIDTH
            and self.maps_content[x_block + 1][y_block] == 0
        ):
            self.pos_flag += 1
            self.x1 = (
                self.x2
            ) = self.player_static.x = self.player_move1.x = self.player_move2.x = 0
        elif (
            keyboard.left
            and self.player_static.x == 0
            and self.maps_content[x_block - 1][y_block] == 0
        ):
            self.pos_flag -= 1
            self.x1 = (
                self.x2
            ) = self.player_static.x = self.player_move1.x = self.player_move2.x = WIDTH
        elif (
            keyboard.up
            and self.player_static.y == HEIGHT
            and self.maps_content[x_block][y_block - 1] == 0
        ):
            self.pos_flag += 2
            self.y1 = (
                self.y2
            ) = self.player_static.y = self.player_move1.y = self.player_move2.y = 0
        elif (
            keyboard.down
            and self.player_static.y == 0
            and self.maps_content[x_block][y_block + 1] == 0
        ):
            self.pos_flag -= 2
            self.y1 = (
                self.y2
            ) = (
                self.player_static.y
            ) = self.player_move1.y = self.player_move2.y = HEIGHT

    def draw_maze(self):  # draw调用的对象，展示迷宫的要素
        screen.clear()
        screen.blit("bg", (0, 0))

        if self.mode == 1:
            self.rule_maze.pos = (WIDTH / 2 - 60, HEIGHT / 2 - 5)
            self.rule_maze.draw()
            self.start_button.pos = (570, 420)
            self.start_button.draw()
            Pause_reminder.draw()
        elif self.mode == 2:
            t = time.time() - self.start_time
            if not Win:
                self.count_time += t
            self.start_time = time.time()
            self.show_ground()
            if t > 180:
                self.lose()
            if not self.pressed:
                self.player_static.draw()
                self.shadow.pos = self.player_static.pos
            else:
                if self.animation():
                    self.pressed = False
                    self.player_static.draw()
                    self.shadow.pos = self.player_static.pos
                else:
                    if self.flag < 0:
                        self.player_move1.draw()
                        self.shadow.pos = self.player_move1.pos
                        self.flag -= 1
                    else:
                        self.player_move2.draw()
                        self.shadow.pos = self.player_move2.pos
                        self.flag += 1
            self.water.draw()
            self.shadow.draw()
            screen.draw.text("COIN:%d" % self.score, (540, 10), color="white")
            screen.draw.text(
                "COUNT DOWN:%.f" % (max(180 - self.count_time, 0)),
                (10, 10),
                color="white",
            )

    def lose(self):
        global Mode, Game_Over, end_time
        if not Game_Over:
            end_time = time.time()
            music.pause()
            sounds.time_out.play()
            Game_Over = True


# -----------------------------------maze-----------------------------------#
# -----------------------------------boss-----------------------------------#
class BOSS:
    def __init__(self):
        self.n = 1000
        self.GRAVITY = 0.2
        self.rule_boss = Actor("rule_boss")
        self.start_button = Actor("begin")
        self.mode = 1

    def main_boss(self):
        self.flame_num = 0 #记录火焰编号
        self.fireball_num = 0 #记录火球编号
        self.bullet_num = 0 #记录子弹编号
        self.magma2_num = 0 #记录岩浆火花编号
        self.boom_num = 0 #记录爆炸特效编号
        self.flame = [] #创建火焰列表
        self.fireball = [] #创建火球列表
        self.bullet = [] #创建子弹列表
        self.magma2 = [] #创建岩浆火花列表
        self.boom = [] #创建爆炸特效列表
        self.live = [] #创建马里奥生命值列表
        self.blood2 = [] #创建boss血条列表
        self.flash = 0 #记录马里奥受伤闪烁次数
        self.time = 0 #记录时间
        self.t = 0 #记录时间
        self.num = 0 #记录当前屏幕内的子弹个数
        self.Mario = self._Mario("mario_15", 0, 0, 0, 0, 0, 5, boss_game) #创建马里奥对象
        self.Koopa = self._Koopa("koopa1", 0, 1, 1, 0, 100, boss_game) #创建boss对象
        self.magma = self._magma("magma1", midbottom=(320, 480)) #创建岩浆对象
        self.death = self._death("mario_death", 0, 0, boss_game) #创建马里奥尸体对象
        self.blood1 = Actor("blood1", (512, 48)) #创建boss血条边框对象
        self.koopadeath = self._koopadeath("koopa_death1", 0, 0, boss_game) #创建boss尸体对象
        self.ship = self._ship("ship1") #创建飞船对象
        self.Mario.pos = (100, 100) #设置马里奥初始位置
        self.Koopa.pos = (500, 384) #设置boss初始位置
        for i in range(self.n): #创建各数目不定的对象保存到相应的数组中
            self.flame.append(self._flame("flame1", 0, 0, 0, boss_game))
            self.fireball.append(self._fireball("fireball1", 0, 0, 0, 0, boss_game))
            self.bullet.append(self._bullet("bullet", 0, 0, 0, boss_game))
            self.magma2.append(self._magma2("magma3", 0))
            self.boom.append(self._boom("boom1", 0))
        for i in range(5): #创建马里奥生命值对象
            self.live.append(self._live("live", 1))
            self.live[i].pos = (16 + 20 * i, 20)
        for i in range(100): #创建boss血条对象
            self.blood2.append(self._blood2("blood2", 1))
            self.blood2[i].pos = (493 + i, 51)
        self.magma.magma1() #执行岩浆的动画效果
        self.Koopa.Koopa1() #执行boss的动画效果
        self.ship.ship1() #执行飞船的动画效果

    def draw_boss(self):
        if self.mode == 1: #boss关说明
            screen.clear()
            screen.blit("background2", (0, 0))
            self.rule_boss.pos = (WIDTH / 2 - 60, HEIGHT / 2 - 5)
            self.rule_boss.draw()
            self.start_button.pos = (570, 420)
            self.start_button.draw()
            Pause_reminder.draw()
        elif self.mode == 2: #正式关卡
            global Game_Over, end_time
            screen.blit("background2", (0, 0))
            if self.Koopa.live > 0:
                self.Koopa.draw()
            if self.Mario.live > 0 and self.Mario.flag3 != 2:
                self.Mario.draw()
            self.ship.draw()
            for i in range(max(self.flame_num-10,0),self.flame_num):
                if self.flame[i].flag1 > 0:
                    self.flame[i].draw()
            for i in range(max(self.fireball_num-10,0),self.fireball_num):
                if self.fireball[i].flag1 > 0:
                    self.fireball[i].draw()
            for i in range(max(self.bullet_num-10,0),self.bullet_num):
                if self.bullet[i].flag > 0:
                    self.bullet[i].draw()
                    self.num += 1
            for i in range(max(self.magma2_num-10,0),self.magma2_num):
                if self.magma2[i].flag > 0:
                    self.magma2[i].draw()
            for i in range(max(self.boom_num-10,0),self.boom_num):
                if self.boom[i].flag > 0:
                    self.boom[i].draw()
            self.magma.draw()
            if self.death.flag > 0:
                self.death.draw()
                if not Game_Over:
                    end_time = time.time()
                Game_Over = True
            if self.koopadeath.flag > 0:
                self.koopadeath.draw()
            self.blood1.draw()
            for i in range(5):
                if self.live[i].flag > 0:
                    self.live[i].draw()
            for i in range(100):
                if self.blood2[i].flag > 0:
                    self.blood2[i].draw()

    def update_boss(self):
        if self.mode == 1:
            return
        self.key() #执行按键判定代码
        for i in range(max(self.flame_num - 10, 0), self.flame_num):
            if self.flame[i].flag1 > 0:
                self.flame[i].update()
        for i in range(max(self.fireball_num - 10, 0), self.fireball_num):
            if self.fireball[i].flag1 > 0:
                self.fireball[i].update()
        for i in range(max(self.bullet_num - 10, 0), self.bullet_num):
            if self.bullet[i].flag > 0:
                self.bullet[i].update()
        self.Mario.update()
        if self.Mario.live > 0:
            self.ship.midtop = self.Mario.midbottom
        self.Koopa.update()
        self.magma.update()
        self.time += 1
        if self.death.flag > 0:
            self.death.update()
        if self.koopadeath.flag > 0:
            self.koopadeath.update()
        for i in range(5):
            if i < self.Mario.live:
                self.live[i].flag = 1
            else:
                self.live[i].flag = 0
        for i in range(100):
            if 99 - i < self.Koopa.live:
                self.blood2[i].flag = 1
            else:
                self.blood2[i].flag = 0
        self.num = 0 #不断更新当前子弹数为0（方便其他地方改变并判定这个变量）

    # 按键操作
    def key(self):
        if keyboard.left:
            self.Mario.flag1 = 1
            self.Mario.Mario1()
            if self.Mario.vx > -3:
                self.Mario.vx -= 1
        if keyboard.right:
            self.Mario.flag1 = 0
            self.Mario.Mario1()
            if self.Mario.vx < 3:
                self.Mario.vx += 1
        if (keyboard.left and keyboard.right) or not (keyboard.left or keyboard.right):
            if self.Mario.flag1 == 1 and self.Mario.vx < 0:
                self.Mario.vx += 1
            if self.Mario.flag1 == 0 and self.Mario.vx > 0:
                self.Mario.vx -= 1
        if keyboard.up and self.Mario.vy > -3:
            self.Mario.vy -= 1
        if keyboard.down and self.Mario.vy < 3:
            self.Mario.vy += 1
        if (keyboard.up and keyboard.down) or not (keyboard.up or keyboard.down):
            if self.Mario.vy < 0:
                self.Mario.vy += 1
            if self.Mario.vy > 0:
                self.Mario.vy -= 1
        if keyboard.x: #发子弹判定，当前屏幕内子弹数<2时才能发子弹
            if self.Mario.flag2 == 0 and self.num < 2:
                sounds.shoot.play()
                self.Mario.Mario2()
                if self.Mario.flag1 == 0:
                    self.bullet[self.bullet_num].vx = 6
                    self.bullet[self.bullet_num].x = self.Mario.x + 3
                else:
                    self.bullet[self.bullet_num].vx = -6
                    self.bullet[self.bullet_num].x = self.Mario.x - 3
                self.bullet[self.bullet_num].flag = 1
                self.bullet[self.bullet_num].y = self.Mario.y + 5
                self.bullet[self.bullet_num].vy = 2
                self.bullet_num += 1
            self.Mario.flag2 = 1
        else:
            self.Mario.flag2 = 0

    # 马里奥
    class _Mario(Actor):
        # flag1控制朝向，flag2控制是否处于发子弹状态，flag3控制是否受伤
        def __init__(self, name, vx, vy, flag1, flag2, flag3, live, obj):
            super().__init__(name)
            self.vx = vx
            self.vy = vy
            self.flag1 = flag1
            self.flag2 = flag2
            self.flag3 = flag3
            self.live = live
            self.obj = obj

        def update(self):
            self.x += self.vx
            self.y += self.vy
            if self.flag3 == 1: #受伤与死亡判定
                if self.live == 0:
                    self.flag3 = 2
                    self.obj.death.pos = self.pos
                    self.obj.death.flag = 1
                    sounds.die.play()
                    music.pause()
                else:
                    self.attacked1()
                    sounds.hurt.play()
            # 马里奥不能出边界
            if self.x < 16:
                self.x = 16
                self.vx = 0
            if self.x > 624:
                self.x = 624
                self.vx = 0
            if self.y < 32:
                self.y = 32
                self.vy = 0
            if self.y > 416:
                self.y = 416
                self.vy = 0

        # 马里奥图像的变化
        def Mario1(self):
            if self.flag1 == 0:
                self.image = "mario_15"
            else:
                self.image = "mario_17"

        def Mario2(self):
            if self.flag1 == 0:
                self.image = "mario_16"
            else:
                self.image = "mario_18"
            clock.schedule_unique(self.Mario1, 0.1)

        # 受伤时闪烁10次，闪烁过程马里奥不会受伤
        def attacked1(self):
            self.flag3 = 2
            clock.schedule_unique(self.attacked2, 0.1)

        def attacked2(self):
            global flash
            self.flag3 = 3
            if self.obj.flash <= 10:
                clock.schedule_unique(self.attacked1, 0.1)
                self.obj.flash += 1
            else:
                self.flag3 = 0
                self.obj.flash = 0

    # boss
    class _Koopa(Actor):
        # flag1控制朝向，flag2控制移动方向，flag3控制攻击
        def __init__(self, name, vx, flag1, flag2, flag3, live, obj):
            super().__init__(name)
            self.vx = vx
            self.flag1 = flag1
            self.flag2 = flag2
            self.flag3 = flag3
            self.live = live
            self.obj = obj

        def update(self):
            self.x += self.vx
            if self.x < 32: #boss运动方向的改变
                self.flag2 = 0
            if self.x > 608:
                self.flag2 = 1
            # 平均移动速度随生命的减少递增
            if self.live > 0:
                if self.flag2 == 0:
                    self.vx = random.uniform(0, 2 + (100 - self.live) / 20)
                else:
                    self.vx = random.uniform(-2 - (100 - self.live) / 20, 0)
            else:
                # boss死亡时的相关处理
                self.vx = 0
                if self.obj.koopadeath.flag == 0:
                    sounds.koopadeath1.play()
                    music.pause()
                    self.obj.koopadeath.koopadeath1()
                    self.obj.koopadeath.pos = self.pos
                    clock.schedule_unique(self.obj.koopadeath.move, 3)
                    self.obj.koopadeath.flag = 1
            # 根据马里奥和Boss的相对x坐标确定朝向
            if self.x > self.obj.Mario.x:
                self.flag1 = 1
            else:
                self.flag1 = 0
            # 马里奥接触Boss则受伤
            if self.colliderect(self.obj.Mario) and self.obj.Mario.flag3 == 0:
                self.obj.Mario.flag3 = 1
                self.obj.Mario.live -= 1
            # 攻击模式
            if self.obj.time == 0:
                self.obj.t = random.randint(self.live, self.live + 100)
            if self.obj.time >= self.obj.t and self.live > 0:
                self.flag3 = 1
                self.Koopa3()
                self.obj.time = 0

        # 攻击方式1：喷火焰
        def attack1(self):
            if self.flag1 == 0:
                self.obj.flame[self.obj.flame_num].flag2 = 0
                self.obj.flame[self.obj.flame_num].vx = 2
                self.obj.flame[self.obj.flame_num].x = self.obj.Koopa.x + 10
            else:
                self.obj.flame[self.obj.flame_num].flag2 = 1
                self.obj.flame[self.obj.flame_num].vx = -2
                self.obj.flame[self.obj.flame_num].x = self.obj.Koopa.x - 10
            self.obj.flame[self.obj.flame_num].y = self.obj.Koopa.y - 10
            self.obj.flame[self.obj.flame_num].flag1 = 1
            self.obj.flame[self.obj.flame_num].flame1()
            self.obj.flame_num += 1

        # 攻击方式2：喷火球
        def attack2(self):
            if self.flag1 == 0:
                self.obj.fireball[self.obj.fireball_num].vx = random.uniform(2, 4)
                self.obj.fireball[self.obj.fireball_num].x = self.obj.Koopa.x + 10
            else:
                self.obj.fireball[self.obj.fireball_num].vx = random.uniform(-4, -2)
                self.obj.fireball[self.obj.fireball_num].x = self.obj.Koopa.x - 10
            self.obj.fireball[self.obj.fireball_num].vy = -2
            self.obj.fireball[self.obj.fireball_num].y = self.obj.Koopa.y - 10
            self.obj.fireball[self.obj.fireball_num].flag1 = 1
            self.obj.fireball[self.obj.fireball_num].fireball1()
            self.obj.fireball_num += 1

        # Boss图像的改变
        def Koopa1(self):
            if self.flag3 == 0:
                if self.flag1 == 0:
                    self.image = "koopa1"
                else:
                    self.image = "koopa5"
                clock.schedule_unique(self.Koopa2, 0.2)

        def Koopa2(self):
            if self.flag3 == 0:
                if self.flag1 == 0:
                    self.image = "koopa2"
                else:
                    self.image = "koopa6"
            clock.schedule_unique(self.Koopa1, 0.2)

        def Koopa3(self):
            if self.flag1 == 0:
                self.image = "koopa3"
            else:
                self.image = "koopa7"
            clock.schedule_unique(self.Koopa4, 1)

        def Koopa4(self):
            if self.flag1 == 0:
                self.image = "koopa4"
            else:
                self.image = "koopa8"
            choice = random.choice((1, 2))
            if choice == 1:
                self.attack1()
            else:
                self.attack2()
            self.flag3 = 0
            sounds.flame.play()
            clock.schedule_unique(self.Koopa1, 0.5)

    # 岩浆的动画效果
    class _magma(Actor):
        def update(self):
            if self.colliderect(boss_game.Mario) and boss_game.Mario.flag3 == 0:
                boss_game.Mario.flag3 = 1
                boss_game.Mario.live -= 1

        def magma1(self):
            self.image = "magma1"
            clock.schedule_unique(self.magma2, 0.3)

        def magma2(self):
            self.image = "magma2"
            clock.schedule_unique(self.magma1, 0.3)

    # 火焰
    class _flame(Actor):
        # flag1控制是否显示，flag2控制方向
        def __init__(self, name, vx, flag1, flag2, obj):
            super().__init__(name)
            self.vx = vx
            self.flag1 = flag1
            self.flag2 = flag2
            self.obj = obj

        def update(self):
            self.x += self.vx
            self.y -= 2
            # 火焰出屏消失
            if self.y < -16:
                self.flag1 = 0
            # 马里奥接触火焰受伤
            if self.colliderect(self.obj.Mario) and self.obj.Mario.flag3 == 0:
                self.obj.Mario.flag3 = 1
                self.obj.Mario.live -= 1

        # 火焰图像的改变
        def flame1(self):
            if self.flag2 == 0:
                self.image = "flame1"
            else:
                self.image = "flame3"
            clock.schedule_unique(self.flame2, 0.2)

        def flame2(self):
            if self.flag2 == 0:
                self.image = "flame2"
            else:
                self.image = "flame4"
            clock.schedule_unique(self.flame1, 0.2)

    # 火球
    class _fireball(Actor):
        # flag1控制是否显示，flag2控制是否已反弹
        def __init__(self, name, vx, vy, flag1, flag2, obj):
            super().__init__(name)
            self.vx = vx
            self.vy = vy
            self.flag1 = flag1
            self.flag2 = flag2
            self.obj = obj

        def update(self):
            self.x += self.vx
            self.y += self.vy
            self.vy += self.obj.GRAVITY
            if self.flag2 == 1:
                self.angle = 0
                if self.vy > 0:
                    self.angle = 180
            else:
                self.angle += 10
            # 马里奥接触火球受伤
            if self.colliderect(self.obj.Mario) and self.obj.Mario.flag3 == 0:
                self.obj.Mario.flag3 = 1
                self.obj.Mario.live -= 1
            # 火球接触岩浆反弹一次，并生成岩浆火花
            if self.colliderect(self.obj.magma):
                self.obj.magma2[self.obj.magma2_num].flag = 1
                self.obj.magma2[self.obj.magma2_num].pos = self.pos
                self.obj.magma2[self.obj.magma2_num].magma3()
                self.obj.magma2_num += 1
                if self.flag2 == 0:
                    self.flag2 = 1
                    self.vy = -12
                    self.vx = 0
                else:
                    self.flag1 = 0
            # 火球出屏消失
            if self.x < -16 or self.x > 656:
                self.flag1 = 0

        # 火球图像的改变
        def fireball1(self):
            self.image = "fireball1"
            clock.schedule_unique(self.fireball2, 0.2)

        def fireball2(self):
            self.image = "fireball2"
            clock.schedule_unique(self.fireball1, 0.2)

    # 子弹
    class _bullet(Actor):
        # flag控制是否显示
        def __init__(self, name, vx, vy, flag, obj):
            super().__init__(name)
            self.vx = vx
            self.vy = vy
            self.flag = flag
            self.obj = obj

        def update(self):
            self.x += self.vx
            self.y += self.vy
            self.vy += self.obj.GRAVITY
            self.angle += 10
            # 子弹打中boss使boss减血
            if self.colliderect(self.obj.Koopa) and self.obj.Koopa.live > 0:
                sounds.kick2.play()
                self.obj.Koopa.live -= 1
                self.flag = 0
                self.obj.boom[self.obj.boom_num].flag = 1
                self.obj.boom[self.obj.boom_num].pos = self.pos
                self.obj.boom[self.obj.boom_num].boom1()
                self.obj.boom_num += 1
            # 子弹出屏消失
            if self.y > 496:
                self.flag = 0

    # 岩浆火花的动画效果
    class _magma2(Actor):
        def __init__(self, name, flag):
            super().__init__(name)
            self.flag = flag

        def magma3(self):
            self.image = "magma3"
            clock.schedule_unique(self.magma4, 0.2)

        def magma4(self):
            self.image = "magma4"
            clock.schedule_unique(self.magma5, 0.2)

        def magma5(self):
            self.image = "magma5"
            clock.schedule_unique(self.destroy, 0.2)

        def destroy(self):
            self.flag = 0

    # 飞船的动画效果
    class _ship(Actor):
        def ship1(self):
            self.image = "ship1"
            clock.schedule_unique(self.ship2, 0.2)

        def ship2(self):
            self.image = "ship2"
            clock.schedule_unique(self.ship1, 0.2)

    # 子弹爆炸特效的动画效果
    class _boom(Actor):
        def __init__(self, name, flag):
            super().__init__(name)
            self.flag = flag

        def boom1(self):
            self.image = "boom1"
            clock.schedule_unique(self.boom2, 0.1)

        def boom2(self):
            self.image = "boom2"
            clock.schedule_unique(self.destroy, 0.1)

        def destroy(self):
            self.flag = 0

    # 马里奥尸体
    class _death(Actor):
        def __init__(self, name, flag, vy, obj):
            super().__init__(name)
            self.flag = flag
            self.vy = vy
            self.obj = obj

        def update(self):
            self.y += self.vy
            if self.flag == 3:
                self.vy += self.obj.GRAVITY
            else:
                if self.flag == 1:
                    self.stop()
            if self.y > 496:
                self.flag = 0

        def stop(self):
            self.flag = 2
            clock.schedule_unique(self.move, 1)

        def move(self):
            self.vy = -5
            self.flag = 3

    # boss尸体
    class _koopadeath(Actor):
        def __init__(self, name, vy, flag, obj):
            super().__init__(name)
            self.vy = vy
            self.flag = flag
            self.obj = obj

        def update(self):
            self.y += self.vy
            if self.flag > 1:
                self.vy += self.obj.GRAVITY

        def move(self):
            self.flag = 2
            sounds.koopadeath2.play()
            clock.schedule_unique(self.pass0, 3)

        def koopadeath1(self):
            if self.obj.Koopa.flag1 == 0:
                self.image = "koopa_death1"
            else:
                self.image = "koopa_death3"
            clock.schedule_unique(self.koopadeath2, 0.2)

        def koopadeath2(self):
            if self.obj.Koopa.flag1 == 0:
                self.image = "koopa_death2"
            else:
                self.image = "koopa_death4"
            clock.schedule_unique(self.koopadeath1, 0.2)

        def pass0(self):
            global Win, end_time, Coins
            sounds.pass0.play()
            if not Win:
                Coins += 100
                pass_through[4] = True
                end_time = time.time()
                Win = True

    # 马里奥生命
    class _live(Actor):
        def __init__(self, name, flag):
            super().__init__(name)
            self.flag = flag

    # boss血条
    class _blood2(Actor):
        def __init__(self, name, flag):
            super().__init__(name)
            self.flag = flag


# -----------------------------------boss-----------------------------------#
# -----------------------------------MVL------------------------------------#
class MARIO_VS_LAKITU:
    def __init__(self):
        self.n = 1000
        self.GRAVITY = 0.2
        self.rule_MVL = Actor("rule_mvl")
        self.start_button = Actor("begin")
        self.mode = 1
        self.paused = False

    def main_MVL(self):
        self.flash = 0
        self.paused = False
        self.mushroom_time = 0 #记录蘑菇生成时间
        self.TIME = 7200 #关卡总时间
        self.Goomba_num = 0 #记录板栗仔编号
        self.coin_num = 0 #记录金币编号
        self.spiny_num = 0 #记录刺球编号
        self.mushroom_num = 0 #记录蘑菇编号
        self.COIN = 0 #记录当前关卡金币数
        self.Goomba = [] #创建板栗仔列表
        self.coin = [] #创建金币列表
        self.spiny = [] #创建刺球列表
        self.mushroom = [] #创建蘑菇列表
        self.FLAG = 0 #判断是否过关
        for i in range(self.n): #创建各数目不定的对象保存到相应数组中
            self.Goomba.append(self._Goomba("chestnut1", 1, 0, 0))
            self.coin.append(self._coin("coin1", 0, 0))
            self.spiny.append(self._spiny("acanthosphere", 0, 0, 0))
            self.mushroom.append(self._mushroom("mushroom", 0, 0))
        self.ground = Actor("ground", bottomright=(WIDTH, HEIGHT)) #创建地面对象
        self.Mario = self._Mario("mario_4", 0, 0, 0, 0, 1, 0) #创建马里奥对象
        self.Lakitu = self._Lakitu("hedgehog_cloud1", 0, 0) #创建刺猬云对象
        self.death = self._death("mario_death", 0, 0) #创建马里奥尸体对象
        self.Lakitu.pos = (640, 80) #设置刺猬云初始位置
        self.Mario.midbottom = (320, 416) #设置马里奥初始位置
        self.coin_create() #开始随机生成金币
        self.Lakitu.Lakitu2() #刺猬云动画效果启动

    # 板栗仔
    class _Goomba(Actor):
        # flag控制板栗仔的状态，0表示未创建，1表示向左未落地，2表示向右未落地，3表示向左已落地，4表示向右未落地，5表示已死亡
        def __init__(self, name, vx, vy, flag):
            super().__init__(name)
            self.flag = flag
            self.vx = vx
            self.vy = vy

        def update(self):
            self.y += self.vy
            if self.flag % 2 == 0:#判断板栗仔被创建时的朝向
                self.x += self.vx
            else:
                self.x -= self.vx
            if 2 < self.flag < 5:
                self.vy += MVL_game.GRAVITY
            # 板栗仔落地
            if self.colliderect(MVL_game.ground) and self.flag < 5:
                self.vy = 0
                self.flag -= 2
                self.y = MVL_game.ground.y - self.height / 2 - 32
            # 板栗仔出屏消失
            if self.x < -16 or self.x > 656:
                self.flag = 0
            # 马里奥碰到板栗仔时判定，踩到头顶则踩死板栗仔，否则马里奥受伤
            if self.colliderect(MVL_game.Mario) and self.flag < 5:
                if (
                    MVL_game.Mario.vy > 0
                    and MVL_game.Mario.y + MVL_game.Mario.height / 2
                    < self.y - self.height / 2 + 8
                ):
                    self.vx = 0
                    self.flag = 5
                    clock.schedule_unique(self.destroy, 1)
                    MVL_game.Mario.vy = -4
                    self.image = "chestnut_death"
                    self.y = MVL_game.ground.y - 38
                    sounds.goomba_death.play()
                else:
                    if MVL_game.Mario.flag4 == 0:
                        MVL_game.Mario.flag4 = 1

        # 板栗仔动画效果
        def Goomba1(self):
            if self.flag < 5:
                self.image = "chestnut1"
                clock.schedule_unique(self.Goomba2, 0.2)

        def Goomba2(self):
            if self.flag < 5:
                self.image = "chestnut2"
                clock.schedule_unique(self.Goomba1, 0.2)

        def destroy(self):
            self.flag = 0

    # 金币
    class _coin(Actor):
        # flag控制是否显示
        def __init__(self, name, flag, vx):
            super().__init__(name)
            self.flag = flag
            self.vx = vx

        def update(self):
            self.y += 2
            self.x += self.vx
            if self.y > 496: #金币出屏消失
                self.flag = 0
            if self.colliderect(MVL_game.Mario): #马里奥吃金币判定
                self.flag = 0
                MVL_game.COIN += 1
                sounds.coin.play()

        # 金币动画效果
        def coin1(self):
            self.image = "coin1"
            clock.schedule_unique(self.coin2, 0.1)

        def coin2(self):
            self.image = "coin2"
            clock.schedule_unique(self.coin3, 0.1)

        def coin3(self):
            self.image = "coin3"
            clock.schedule_unique(self.coin1, 0.1)

    # 刺球
    class _spiny(Actor):
        # flag控制是否显示
        def __init__(self, name, flag, vx, vy):
            super().__init__(name)
            self.flag = flag
            self.vx = vx
            self.vy = vy

        def update(self):
            if flag_pause:
                return
            self.x += self.vx
            self.y += self.vy
            self.vy += MVL_game.GRAVITY
            self.angle += 10
            # 刺球出屏消失
            if self.y > 496:
                self.flag = 0
            # 马里奥碰到刺球受伤
            if self.colliderect(MVL_game.Mario) and MVL_game.Mario.flag4 == 0:
                MVL_game.Mario.flag4 = 1

    # 刺猬云
    class _Lakitu(Actor):
        # flag控制是否显示
        def __init__(self, name, vx, flag):
            super().__init__(name)
            self.vx = vx
            self.flag = flag

        def update(self):
            self.x += self.vx
            if self.x >= 576: #改变刺猬云运动方向
                self.vx = -2
            if self.x <= 64:
                self.vx = 2

        # 攻击方式1：扔板栗仔
        def attack1(self):
            if flag_pause or Win:
                return
            MVL_game.Goomba[MVL_game.Goomba_num].flag = 3
            MVL_game.Goomba[MVL_game.Goomba_num].pos = (self.x, self.y - 32)
            MVL_game.Goomba[MVL_game.Goomba_num].vy = -3
            MVL_game.Goomba[MVL_game.Goomba_num].Goomba1()
            if MVL_game.Goomba[MVL_game.Goomba_num].x < MVL_game.Mario.x:
                MVL_game.Goomba[MVL_game.Goomba_num].flag += 1
            MVL_game.Goomba_num += 1

        # 攻击方式2：扔刺球
        def attack2(self):
            if flag_pause or Win:
                return
            MVL_game.spiny[MVL_game.spiny_num].flag = 1
            MVL_game.spiny[MVL_game.spiny_num].pos = (self.x, self.y - 32)
            MVL_game.spiny[MVL_game.spiny_num].vy = random.randint(-5, -2)
            MVL_game.spiny[MVL_game.spiny_num].vx = random.uniform(-1.5, 1.5)
            MVL_game.spiny_num += 1

        # 刺猬云图像改变
        def Lakitu1(self):
            global Game_Over
            if Game_Over or MVL_game.mode == 1 or flag_pause:
                MVL_game.paused = True
                return
            self.image = "hedgehog_cloud1"
            choice = random.choice((1, 2))
            if choice == 1:
                self.attack1()
                sounds.lakitu1.play()
            else:
                self.attack2()
                sounds.lakitu2.play()
            MVL_game.time = random.uniform(
                MVL_game.TIME / 14400, MVL_game.TIME / 14400 + 0.5
            )
            clock.schedule_unique(self.Lakitu2, MVL_game.time)

        def Lakitu2(self):
            if flag_pause or Win:
                return
            self.image = "hedgehog_cloud2"
            clock.schedule_unique(self.Lakitu1, 1)

    # 马里奥
    class _Mario(Actor):
        # flag1=0静止，flag1=1运动，flag1=2悬空，flag2控制左右朝向,flag3控制大小状态,flag4=0正常,flag4=1刚受伤，flag4=2,3无敌,flag4=2消失
        def __init__(self, name, vx, vy, flag1, flag2, flag3, flag4):
            super().__init__(name)
            self.vx = vx
            self.vy = vy
            self.flag1 = flag1
            self.flag2 = flag2
            self.flag3 = flag3
            self.flag4 = flag4

        def update(self):
            self.x += self.vx
            self.y += self.vy
            if self.flag1 == 2:
                self.vy += MVL_game.GRAVITY * 1.5
                # 马里奥落地
                if self.colliderect(MVL_game.ground):
                    self.vy = 0
                    self.flag1 = 1
                    self.Mario1()
                    self.y = MVL_game.ground.y - MVL_game.Mario.height / 2 - 32
            # 马里奥不能出屏
            if self.x < 16:
                self.x = 16
                self.vx = 0
            if self.x > 624:
                self.x = 624
                self.vx = 0
            # 根据朝向改变马里奥图像
            if self.flag1 == 0:
                self.Mario1()
            if self.flag1 == 2:
                self.Mario3()
            # 判断是受伤还是死亡
            if self.flag4 == 1:
                if self.flag3 == 0:
                    self.flag4 = 2
                    MVL_game.death.pos = self.pos
                    MVL_game.death.flag = 1
                    sounds.die.play()
                    music.pause()
                else:
                    self.flag3 = 0
                    self.y += 16
                    self.attacked1()
                    sounds.hurt.play()

        # 马里奥图像改变
        def Mario1(self):
            if self.flag3 == 0:
                if self.flag2 == 0:
                    self.image = "mario_1"
                else:
                    self.image = "mario_7"
            else:
                if self.flag2 == 0:
                    self.image = "mario_4"
                else:
                    self.image = "mario_10"
            if self.flag1 == 1:
                clock.schedule_unique(self.Mario2, 0.1)

        def Mario2(self):
            if self.flag3 == 0:
                if self.flag2 == 0:
                    self.image = "mario_2"
                else:
                    self.image = "mario_8"
            else:
                if self.flag2 == 0:
                    self.image = "mario_5"
                else:
                    self.image = "mario_11"
            clock.schedule_unique(self.Mario1, 0.1)

        def Mario3(self):
            if self.flag3 == 0:
                if self.flag2 == 0:
                    self.image = "mario_3"
                else:
                    self.image = "mario_9"
            else:
                if self.flag2 == 0:
                    self.image = "mario_6"
                else:
                    self.image = "mario_12"

        # 受伤时闪烁10次，闪烁时不会受伤
        def attacked1(self):
            self.flag4 = 2
            clock.schedule_unique(self.attacked2, 0.1)

        def attacked2(self):
            self.flag4 = 3
            if MVL_game.flash <= 10:
                clock.schedule_unique(self.attacked1, 0.1)
                MVL_game.flash += 1
            else:
                self.flag4 = 0
                MVL_game.flash = 0

    # 蘑菇
    class _mushroom(Actor):
        # flag=0未创建，flag=1未落地，flag=2已落地
        def __init__(self, name, flag, vy):
            super().__init__(name)
            self.flag = flag
            self.vy = vy

        def update(self):
            self.x -= 2
            self.y += self.vy
            if self.flag == 1:
                self.vy += MVL_game.GRAVITY
            # 蘑菇落地
            if self.colliderect(MVL_game.ground):
                self.flag = 2
                self.vy = 0
                self.y = MVL_game.ground.y - 48
            # 蘑菇出屏消失
            if self.x < -16:
                self.flag = 0
            if self.colliderect(MVL_game.Mario):
                self.flag = 0
                MVL_game.Mario.flag3 = 1
                MVL_game.Mario.y -= 16
                sounds.mushroom.play()

    # 马里奥尸体
    class _death(Actor):
        def __init__(self, name, flag, vy):
            super().__init__(name)
            self.flag = flag
            self.vy = vy

        def update(self):
            self.y += self.vy
            if self.flag == 3:
                self.vy += MVL_game.GRAVITY
            else:
                if self.flag == 1:
                    self.stop()
            if self.y > 496:
                self.flag = 0

        def stop(self):
            self.flag = 2
            clock.schedule_unique(self.move, 1)

        def move(self):
            self.vy = -5
            self.flag = 3

    def draw_MVL(self):
        if self.mode == 1:
            screen.clear()
            screen.blit("background", (0, 0))
            self.rule_MVL.pos = (WIDTH / 2 - 60, HEIGHT / 2 - 5)
            self.rule_MVL.draw()
            self.start_button.pos = (570, 420)
            self.start_button.draw()
            Pause_reminder.draw()
        elif self.mode == 2:
            global Game_Over, end_time
            screen.blit("background", (0, 0))
            screen.draw.text("TIME:%d" % (self.TIME / 60,), (10, 10), color="blue")
            screen.draw.text("COIN:%d" % (self.COIN,), (560, 10), color="blue")
            self.ground.draw()
            self.Lakitu.draw()
            if self.Mario.flag4 != 2:
                self.Mario.draw()
            for i in range(max(self.Goomba_num-10,0),self.Goomba_num):
                if self.Goomba[i].flag > 0:
                    self.Goomba[i].draw()
            for i in range(max(self.spiny_num-10,0),self.spiny_num):
                if self.spiny[i].flag > 0:
                    self.spiny[i].draw()
            for i in range(max(self.coin_num-10,0),self.coin_num):
                if self.coin[i].flag > 0:
                    self.coin[i].draw()
            for i in range(max(self.mushroom_num-10,0),self.mushroom_num):
                if self.mushroom[i].flag > 0:
                    self.mushroom[i].draw()
            if self.death.flag > 0:
                self.death.draw()
                if not Game_Over:
                    Game_Over = True
                    end_time = time.time()

    def update_MVL(self):
        if self.mode == 1:
            return
        if not flag_pause and self.paused:
            MVL_game.paused = False
            clock.schedule_unique(self.Lakitu.Lakitu2, self.time)
            clock.schedule_unique(self.coin_create, 1.5)

        self.Lakitu.update()
        for i in range(max(self.Goomba_num - 10, 0), self.Goomba_num):
            if self.Goomba[i].flag > 0:
                self.Goomba[i].update()
        for i in range(max(self.spiny_num - 10, 0), self.spiny_num):
            if self.spiny[i].flag > 0:
                self.spiny[i].update()
        for i in range(max(self.coin_num - 10, 0), self.coin_num):
            if self.coin[i].flag > 0:
                self.coin[i].update()
        for i in range(max(self.mushroom_num - 10, 0), self.mushroom_num):
            if self.mushroom[i].flag > 0:
                self.mushroom[i].update()
        self.key()
        self.Mario.update()
        if self.death.flag > 0:
            self.death.update()
        self.mushroom_create()
        self.mushroom_time += 1
        if self.TIME > 0:
            self.TIME -= 1
        self.pass0()

    # 生成随机金币
    def coin_create(self):
        if flag_pause:
            return
        self.coin[self.coin_num].flag = 1
        self.coin[self.coin_num].x = random.randint(120, 520)
        self.coin[self.coin_num].y = -32
        self.coin[self.coin_num].vx = random.uniform(-1, 1)
        self.coin[self.coin_num].coin1()
        self.coin_num += 1
        clock.schedule_unique(self.coin_create, 1.5)

    # 生成蘑菇，条件是与上一次生成间隔至少20s且马里奥是小个子
    def mushroom_create(self):
        if flag_pause or Win:
            return
        if (
            self.mushroom_time >= 1200
            and self.Mario.flag3 == 0
            and self.Mario.flag4 != 2
        ):
            self.mushroom_time = 0
            self.mushroom[self.mushroom_num].pos = (640, -32)
            self.mushroom[self.mushroom_num].flag = 1
            self.mushroom_num += 1

    # 按键控制
    def key(self):
        if keyboard.left:
            if self.Mario.flag1 == 0:
                self.Mario.flag1 = 1
                self.Mario.Mario2()
            if self.Mario.flag2 == 0:
                self.Mario.flag2 = 1
                self.Mario.Mario2()
            if self.Mario.flag1 < 2:
                self.Mario.flag1 = 1
            if self.Mario.vx > -3:
                self.Mario.vx -= 1
        if keyboard.right:
            if self.Mario.flag1 == 0:
                self.Mario.flag1 = 1
                self.Mario.Mario2()
            if self.Mario.flag2 == 1:
                self.Mario.flag2 = 0
                self.Mario.Mario2()
            if self.Mario.flag1 < 2:
                self.Mario.flag1 = 1
            if self.Mario.vx < 3:
                self.Mario.vx += 1
        if keyboard.z and self.Mario.flag1 < 2:
            sounds.jump.play()
            self.Mario.vy = -10
            self.Mario.flag1 = 2
        if (keyboard.left and keyboard.right) or not (keyboard.left or keyboard.right):
            if self.Mario.flag2 == 1 and self.Mario.vx < 0:
                self.Mario.vx += 1
            if self.Mario.flag2 == 0 and self.Mario.vx > 0:
                self.Mario.vx -= 1
            if self.Mario.vx == 0 and self.Mario.flag1 == 1:
                self.Mario.flag1 = 0

    # 过关判定
    def pass0(self):
        global end_time, Win, Coins
        if self.TIME == 0 and self.FLAG == 0:
            self.FLAG = 1
            sounds.pass0.play()
            music.pause()
            Coins += self.coin_num
            if not Win:
                pass_through[0] = pass_through[1] = True
                cases[1].image = "2"
                cases[2].image = "3"
                end_time = time.time()
                Win = True


# -----------------------------------MVL------------------------------------#
# -----------------------------------SHIP-----------------------------------#
class BattleShips:
    # 初始化函数
    def __init__(self):
        self.rule_ship = Actor("rule_ship")
        self.start_button = Actor("begin")
        self.mode = 1
        self.player = Actor("neutral", center=(320, 25))  # 玩家表情
        self.sea = np.zeros((10, 10))  # 海面上的舰艇位置
        self.con = np.zeros((10, 10))  # 各方格情况

        self.lose = False  # 是否失败
        self.win = False  # 是否胜利
        self.score = 0  # 玩家得分
        self.step = 40  # 玩家剩余步数
        self.coin = 0  # 玩家金币数
        self.ruined = 0  # 玩家摧毁敌舰数
        self.flag = 0  # 攻击状态显示标志

        # Ship类，用于保存敌舰状态
        class Ship:
            def __init__(self):
                self.pos = list()
                self.life = 0
                self.sunk = False

        self.ships = [Ship(), Ship(), Ship(), Ship(), Ship()]  # 敌舰对象
        self.length = (5, 4, 3, 3, 2)  # 敌舰长度

    # 敌舰生成函数，用于在海面上随机生成5艘位置合法的敌舰
    def generate_ships(self):
        num = 0
        while num < 5:
            x = random.randint(0, 9)
            y = random.randint(0, 9)
            if self.sea[x][y]:
                continue
            direct = [0, 1, 2, 3]
            while len(direct):
                d = 1
                k = random.choice(direct)
                direct.remove(k)
                while d < self.length[num]:
                    if (
                        x + dx[k] * d < 0
                        or x + dx[k] * d > 9
                        or y + dy[k] * d < 0
                        or y + dy[k] * d > 9
                    ):
                        break
                    if self.sea[x + dx[k] * d][y + dy[k] * d]:
                        break
                    d += 1
                else:
                    for i in range(self.length[num]):
                        self.sea[x + dx[k] * i][y + dy[k] * i] = num + 1
                        self.ships[num].pos.append((x + dx[k] * i, y + dy[k] * i))
                    self.ships[num].life = self.length[num]
                    num += 1
                    break

    # 设置玩家表情为正常
    def set_player_neutral(self):
        self.player.image = "neutral"

    # 设置玩家表情为开心，1s后恢复
    def set_player_happy(self):
        self.player.image = "happy"
        clock.schedule_unique(self.set_player_neutral, 1.0)

    # 设置玩家表情为伤心，1s后恢复
    def set_player_sad(self):
        self.player.image = "sad"
        clock.schedule_unique(self.set_player_neutral, 1.0)

    # 设置玩家表情为点击，0.5s后恢复（彩蛋）
    def set_player_beaten(self):
        self.player.image = "beaten"
        clock.schedule_unique(self.set_player_neutral, 0.5)

    # 设置攻击状态为正常
    def set_flag_0(self):
        self.flag = 0

    # 设置攻击状态为击中，1s后恢复
    def set_flag_1(self):
        self.flag = 1
        clock.schedule_unique(self.set_flag_0, 1.0)

    # 设置攻击状态为击沉，1s后恢复
    def set_flag_2(self):
        self.flag = 2
        clock.schedule_unique(self.set_flag_0, 1.0)

    # 画面绘制函数
    def draw_ships(self):
        if self.mode == 1:
            screen.clear()
            screen.blit("bg2", (0, 0))
            self.rule_ship.pos = (WIDTH / 2 - 60, HEIGHT / 2 - 5)
            self.rule_ship.draw()
            self.start_button.pos = (570, 420)
            self.start_button.draw()
            Pause_reminder.draw()
        elif self.mode == 2:
            # 清空界面
            screen.clear()
            # 填充背景
            screen.blit("bg2", (0, 0))
            # 根据状态绘制各方格
            for i in range(10):
                for j in range(10):
                    if self.con[i][j] == 0:
                        if (i + j) % 2:
                            screen.blit("normal", (160 + 32 * i, 128 + 32 * j))
                        else:
                            screen.blit("middle", (160 + 32 * i, 128 + 32 * j))
                    elif self.con[i][j] == -1:
                        screen.blit("click", (160 + 32 * i, 128 + 32 * j))
                    elif self.con[i][j] == 1:
                        screen.blit("blank", (160 + 32 * i, 128 + 32 * j))
                    elif self.con[i][j] == 2:
                        screen.blit("fired", (160 + 32 * i, 128 + 32 * j))
                    elif self.con[i][j] == 3:
                        screen.blit("ruined", (160 + 32 * i, 128 + 32 * j))
                    elif self.con[i][j] == 4:
                        screen.blit("blank", (160 + 32 * i, 128 + 32 * j))
                        screen.blit("coin", (160 + 32 * i, 128 + 32 * j))
            # 根据攻击状态显示文本
            if self.flag == 1:
                screen.draw.text("Boom!", (270, 80), color="red", fontsize=50)
            elif self.flag == 2:
                screen.draw.text("Destroy!", (260, 80), color="black", fontsize=50)
            # 绘制玩家表情、得分、剩余步数、金币
            self.player.draw()
            screen.draw.text(
                "Scores: %d" % self.score, (15, 10), color="yellow", fontsize=40
            )
            screen.draw.text(
                "Steps: %d" % self.step, (510, 10), color="yellow", fontsize=40
            )
            screen.draw.text(
                "Coins: %d" % self.coin, (510, 40), color="yellow", fontsize=40
            )
            # 显示胜利或失败文本
            if self.lose:
                screen.draw.text("Game Over!", (220, 270), color="orange", fontsize=50)
                self.exit_ships_lose()
            if self.win and not self.step:
                screen.draw.text("You win!", (250, 270), color="blue", fontsize=50)
                self.exit_ships_win()  # 若游戏已经结束

    # 画面更新函数
    def update_ships(self):
        if self.mode == 1:
            return
        # 循环播放背景音乐
        if not self.lose and not self.win and not music.is_playing("bgm4"):
            music.play("bgm4")
        # 实时更新战舰损毁状态
        for i in range(5):
            if not self.ships[i].life:
                for j in self.ships[i].pos:
                    self.con[j[0]][j[1]] = 3
                self.score += 10
                self.ships[i].life = -1
                self.ruined += 1
                self.set_flag_2()
        # 根据胜利或失败情况更改玩家表情
        if self.lose:
            self.player.image = "dead"
        if self.win:
            self.player.image = "win"
        # 根据胜利或失败情况播放相应音乐
        if not self.step and not self.win and not self.lose:
            self.lose = True
            self.coin += self.score // 10
            music.stop()
            sounds.lose.play()
        if self.ruined == 5 and not self.win:
            self.win = True
            self.coin += self.score // 10
            music.stop()
            sounds.win.play()

    # 鼠标移动捕捉函数
    def on_mouse_move_ships(self, pos):
        # 将所有未知方格恢复正常
        for i in range(10):
            for j in range(10):
                if self.con[i][j] == -1:
                    self.con[i][j] = 0
        # 将鼠标所在的未知方格高亮显示
        if 160 <= pos[0] < 480 and 128 <= pos[1] < 448 and not self.lose and self.step:
            ii, jj = (pos[0] - 160) // 32, (pos[1] - 128) // 32
            if self.con[ii][jj] == 0:
                self.con[ii][jj] = -1

    # 鼠标点击捕捉函数
    def on_mouse_down_ships(self, pos, button):
        # 只捕捉左键点击
        global Coins
        if button == mouse.LEFT:
            # 若游戏尚未结束
            if not self.lose and not self.win:
                if 160 <= pos[0] < 480 and 128 <= pos[1] < 448:
                    ii, jj = (pos[0] - 160) // 32, (pos[1] - 128) // 32
                    # 鼠标处于海面范围且所在方格未知
                    if self.con[ii][jj] == 0 or self.con[ii][jj] == -1:
                        self.step -= 1
                        # 为敌舰
                        if self.sea[ii][jj]:
                            self.con[ii][jj] = 2
                            sounds.hit.play()  # 播放击中音效
                            self.set_player_happy()  # 更改玩家表情为开心
                            self.set_flag_1()  # 更改攻击状态标志
                            self.step += 1  # 奖励步数
                            for i in range(5):
                                if (ii, jj) in self.ships[i].pos:
                                    self.ships[i].life -= 1  # 敌舰生命减少
                                    break
                        # 为空白
                        else:
                            self.con[ii][jj] = 1
                            sounds.miss.play()  # 播放击空音效
                            self.set_player_sad()  # 更改玩家表情为伤心
                # 鼠标处于玩家表情上
                elif self.player.collidepoint(pos):
                    self.set_player_beaten()  # 更改玩家表情为点击（彩蛋）
            # 若已获胜但步数尚未用尽
            elif self.win and self.step:
                if 160 <= pos[0] < 480 and 128 <= pos[1] < 448:
                    ii, jj = (pos[0] - 160) // 32, (pos[1] - 128) // 32
                    # 鼠标处于海面范围且所在方格未知
                    if self.con[ii][jj] == 0 or self.con[ii][jj] == -1:
                        self.step -= 1
                        if not self.step:
                            Coins += self.coin + 5
                        # 随机产生金币
                        if random.randint(0, 2):
                            self.con[ii][jj] = 4
                            self.coin += random.randint(2, 6)
                            sounds.coin.play()  # 播放获得金币音效
                        else:
                            self.con[ii][jj] = 1
                            sounds.miss.play()  # 播放击空音效

    # 退出游戏函数
    def exit_ships_win(self):
        global Win, end_time
        music.pause()
        if not Win:
            pass_through[3] = True
            cases[4].image = "5"
            end_time = time.time()
            Win = True

    def exit_ships_lose(self):
        global Game_Over, end_time
        music.pause()
        if not Game_Over:
            end_time = time.time()
            Game_Over = True


# -----------------------------------SHIP-----------------------------------#
# -----------------------------------Music----------------------------------#
class ImitateMusic:
    # 初始化函数
    def __init__(self):
        self.mode = 1
        self.rule_music = Actor("rule_music")
        self.start_button = Actor("begin")

        self.dires = ["left", "right", "up", "down"]  # 方向列表
        self.props = ["life", "score", "slow", "distance", "bomb", "bomb"]  # 道具列表
        self.combo_colors = [
            "orange",
            "hot pink",
            "lawn green",
            "light slate blue",
            "yellow",
        ]  # 连击颜色显示列表

        self.items = []  # 存储当前屏幕上的全部项目
        self.s = 0  # 随帧数更新的时间
        self.distance = 30  # 判定距离
        self.speed = 3  # 下落速度
        self.score = 0  # 玩家得分
        self.now = Actor("dirc", center=(random.randrange(16, 624), 10))  # 当前需要拾取的项目
        self.condition = -2  # 当前拾取状态
        self.life = 3  # 玩家生命
        self.combo = 0  # 当前连击数
        self.get = False  # 是否拾取当前项目
        self.flag = True  # 速度正常标记
        self.lose = False  # 是否失败
        self.music = False  # 失败音乐标记

    # 得分处理函数
    def deal(self):
        # 判断是否属于有效判定距离
        if 480 - self.items[0].bottom <= self.distance:
            self.get = True  # 更改拾取标记
            self.combo += 1  # 更新连击数
            if self.combo > 2:
                self.score += self.combo * 10
            if 480 - self.items[0].top <= self.distance / 3:  # Perfect
                self.score += 100
                self.condition = 5
            elif 480 - self.items[0].top <= self.distance - 10:  # Great
                self.score += 85
                self.condition = 4
            elif 480 - self.items[0].bottom <= self.distance / 3:  # Good
                self.score += 60
                self.condition = 3
            else:  # Normal
                self.score += 30
                self.condition = 2
        else:  # Miss
            self.get = False  # 更改拾取标记
            self.combo = 0  # 连击数归零
            self.score -= 100
            self.condition = 1

    # 设置下落速度为正常
    def set_speed_normal(self):
        self.flag = True
        self.speed = 3 + self.score * 0.02 / 100

    # 设置判定距离为正常
    def set_distance_normal(self):
        self.distance = 30

    # 画面绘制函数
    def draw_music(self):
        global Coins
        if self.mode == 1:
            screen.clear()
            screen.blit("bgp", (0, 0))
            self.rule_music.pos = (WIDTH / 2 - 60, HEIGHT / 2 - 5)
            self.rule_music.draw()
            self.start_button.pos = (570, 420)
            self.start_button.draw()
            Pause_reminder.draw()
        elif self.mode == 2:
            # 清空界面
            screen.clear()
            # 填充背景
            screen.blit("bgp", (0, 0))
            # 绘制判定距离界限
            screen.draw.line(
                (0, 480 - self.distance), (640, 480 - self.distance), "orange"
            )

            # 绘制各项目
            for i in self.items:
                i.draw()

            # 根据拾取状态显示文本
            if self.condition == 5:
                screen.draw.text(
                    "Perfect!", (self.now.left, self.now.top), color="gold", fontsize=30
                )
            elif self.condition == 4:
                screen.draw.text(
                    "Great!", (self.now.left, self.now.top), color="purple", fontsize=30
                )
            elif self.condition == 3:
                screen.draw.text(
                    "Good!",
                    (self.now.left, self.now.top),
                    color="deep sky blue",
                    fontsize=30,
                )
            elif self.condition == 2:
                screen.draw.text(
                    "Normal!",
                    (self.now.left, self.now.top),
                    color="spring green",
                    fontsize=30,
                )
            elif self.condition == 1:
                if len(self.items):
                    screen.draw.text(
                        "Miss!",
                        (self.items[0].left, 460),
                        color="dim gray",
                        fontsize=30,
                    )
                else:
                    screen.draw.text(
                        "Miss!", (self.now.left, 460), color="dim gray", fontsize=30
                    )
            elif self.condition == 0:
                if len(self.items):
                    screen.draw.text(
                        "Wrong!", (self.items[0].left, 460), color="red", fontsize=30
                    )
                else:
                    screen.draw.text(
                        "Wrong!", (self.now.left, 460), color="red", fontsize=30
                    )
            elif self.condition == -1:
                screen.draw.text(
                    "Miss!", (self.now.left, self.now.top), color="orange ", fontsize=30
                )

            if self.combo > 2:
                screen.draw.text(
                    "Combo × %d" % self.combo,
                    (265, 10),
                    color=random.choice(self.combo_colors),
                    fontsize=40,
                )
            if self.score < 0:
                self.score = 0
            # 绘制玩家得分、生命
            screen.draw.text("Score: %d" % self.score, (15, 10), fontsize=40)
            screen.draw.text("Life: %d" % self.life, (530, 10), fontsize=40)
            # 显示失败文本并播放失败音乐
            if self.lose:
                screen.draw.text("Game Over!", (240, 150), fontsize=50)
                self.exit_music_lose()
                if self.music:
                    Coins += self.score // 500
                    sounds.win_music.play()
                    self.music = False

    # 画面更新函数
    def update_music(self):
        if self.mode == 1:
            return
        self.s += 1  # 更新时间
        # 随分数调整固定间隔
        d1 = 60 - self.score // 200
        if d1 < 10:
            d1 = 10
        # 随分数调整随机间隔
        d2 = 60 - self.score // 300
        if d2 < 20:
            d2 = 20
        # 随机生成新项目
        if self.s > d1 and random.randrange(d2) == 0 and self.lose == False:
            name = "unknown"
            if random.randrange(10) != 0:
                name = random.choice(self.dires)
            t = Actor(name, center=(random.randrange(16, 624), 10))
            t.name = name
            self.items.append(t)
            self.s = 0
        # 各项目下落
        for i in self.items:
            # 随分数调整下落速度
            if self.flag:
                self.speed = 3 + self.score * 0.02 / 100
            if i.name == "unknown":
                i.y += self.speed * 1.2
                if i.bottom >= 240:
                    i.name = random.choice(self.props)
                    i.image = i.name
            else:
                i.y += self.speed
        # 若带有方向项目在掉出屏幕前未被拾取，则扣除分数和生命
        if len(self.items) and self.items[0].top > 480 and self.get == False:
            if self.items[0].name in self.dires:
                sounds.lose_music.play()
                self.combo = 0
                self.score -= 100
                self.life -= 1
                self.condition = -1
            else:
                self.condition = -2
            # 更新当前需要拾取的项目
            self.now = Actor(
                self.items[0].name, topleft=(self.items[0].left, self.items[0].top)
            )
            if self.now.top > 455:
                self.now.top = 455
            self.now.name = self.items[0].name
            self.items.pop(0)
            # 判定是否失败
            if not self.life:
                self.music = True
                self.lose = True
                self.combo = 0
                self.items.clear()
        # 若成功拾取当前项目，则奖励对应分数或实现相应道具效果
        if self.get == True:
            if self.items[0].name != "bomb":
                sounds.get.play()  # 播放拾取音效
            else:
                sounds.lose_music.play()  # 播放漏拾音效
            if self.items[0].name in self.props:
                if self.items[0].name == "life":  # 生命道具增加1条生命
                    self.life += 1
                elif self.items[0].name == "bomb":  # 炸弹道具损失1条生命
                    self.life -= 1
                elif self.items[0].name == "score":  # 礼物道具增加500得分
                    self.score += 500
                elif self.items[0].name == "slow":  # 时钟道具使方块掉落速度变慢
                    self.speed *= 0.5
                    self.flag = False
                    clock.schedule_unique(self.set_speed_normal, 10.0)  # 10s后恢复正常下落速度
                elif self.items[0].name == "distance":  # 距离道具增长判定距离
                    self.distance = 60
                    clock.schedule_unique(
                        self.set_distance_normal, 15.0
                    )  # 15s后恢复正常判定距离
            # 更新当前需要拾取的项目
            self.now = Actor(
                self.items[0].name, topleft=(self.items[0].left, self.items[0].top)
            )
            if self.now.top > 455:
                self.now.top = 455
            self.now.name = self.items[0].name
            self.items.pop(0)
            self.get = False

    # 键盘操作捕捉函数
    def on_key_down_music(self, key):
        # 若空中没有项目则判定为Wrong
        if len(self.items) == 0:
            self.get = False
            self.combo = 0
            self.score -= 150
            self.condition = 0
            return
        if key == keys.LEFT:
            # LEFT对应拾取'←'
            if self.items[0].name == "left":
                self.deal()
            # 错误拾取判定为Wrong
            else:
                self.get = False
                self.combo = 0
                self.score -= 150
                self.condition = 0
        elif key == keys.RIGHT:
            # RIGHT对应拾取'→'
            if self.items[0].name == "right":
                self.deal()
            # 错误拾取判定为Wrong
            else:
                self.get = False
                self.combo = 0
                self.score -= 150
                self.condition = 0
        elif key == keys.UP:
            # UP对应拾取'↑'
            if self.items[0].name == "up":
                self.deal()
            # 错误拾取判定为Wrong
            else:
                self.get = False
                self.combo = 0
                self.score -= 150
                self.condition = 0
        elif key == keys.DOWN:
            # DOWN对应拾取'↓'
            if self.items[0].name == "down":
                self.deal()
            # 错误拾取判定为Wrong
            else:
                self.get = False
                self.combo = 0
                self.score -= 150
                self.condition = 0
        elif key == keys.SPACE:
            # 若游戏已结束，按下空格退出游戏
            if self.lose:
                self.exit_music_lose()
            # 空格对应拾取道具
            if self.items[0].name in self.props:
                if 480 - self.items[0].bottom <= self.distance:
                    self.get = True
                    self.condition = -2
                else:
                    self.get = False
                    self.score -= 100
                    self.condition = 1
            # 错误拾取判定为Wrong
            else:
                self.get = False
                self.score -= 150
                self.condition = 0
        # 错误拾取判定为Wrong
        else:
            self.get = False
            self.combo = 0
            self.score -= 150
            self.condition = 0

    def exit_music_win(self):
        global Win, end_time
        music.pause()
        if not Win:
            end_time = time.time()
            Win = True

    def exit_music_lose(self):
        global Game_Over, end_time
        music.pause()
        if not Game_Over:
            end_time = time.time()
            Game_Over = True


# -----------------------------------Music----------------------------------#

# -----------------------------------Store----------------------------------#
class STORE():
    def __init__(self):  # 初始化卡牌的名称以及文件名
        self.cards = []
        self.choose_card = [(64, 60), (192, 60), (320, 60), (448, 60), (576, 60), (576, 180), (576, 300), (576, 420),
                       (448, 420), (320, 420), (192, 420), (64, 420), (64, 300), (64, 180)]
        self.prizes = ["card_back", "card_back", "card_back", "card_back", "card_back", "card_back",
                       "card_back", "card_back", "card_back", "card_back", "card_back", "card_back",
                       "card_back", "card_back"]  # 放大奖励
        self.prizes_bigger = ['card2', 'card1', 'card5', 'card3', 'card6', 'card7', 'card4', 'card8', 'card9',
                         'card10', 'card11', 'card12', 'card13', 'card14']
        self.coin_20 = [9, 10, 12, 13, 8]
        self.coin_50 = [11, 7]
        for i in range(0, 14):
            t = Actor(self.prizes[i])
            t.pos = self.choose_card[i]
            self.cards.append(t)
        self.choose = Actor('choose')
        self.choose.pos = (64, 60)
        self.choose.pos_i = 0
        self.choose.showtime = 0
        self.choose.move_flag = True
        self.pressed = False

        self.roll_button = Actor('roll_button', (260, 280))
        self.return_button = Actor('home_page', (440, 280))

        self.tick = Actor('tick')
        self.tick.flag = False

        self.prize = Actor('tick')
        self.prize.flag = False
        self.prize.showtime = 0

    def draw_store(self):  # 绘制商店界面
        global Coins
        screen.clear()
        screen.blit('bg2', (0, 0))
        for i in self.cards:
            i.draw()
        self.choose.draw()
        self.roll_button.draw()
        self.return_button.draw()
        screen.draw.text("You have:", (200, 150), color='white', fontsize=40)
        if Coins >= 50:
            screen.draw.text("%d" % Coins, (350, 150), color='white', fontsize=40)
        else:
            screen.draw.text("%d" % Coins, (350, 150), color='yellow', fontsize=40)
        Coin_pic2.draw()
        if self.tick.flag == True:
            self.tick.draw()
            if self.prize.flag:
                self.prize.image = self.prizes_bigger[self.choose.pos_i]
                self.prize.pos = (320, 240)
                self.prize.draw()
                if self.prize.showtime < 70:
                    self.prize.showtime += 1
                    clock.schedule(self.hide_prize, 0.5)
                    clock.schedule(self.show_prize, 1)
                else:
                    self.prize.flag = True
        if self.choose.move_flag == True:
            if self.choose.showtime < 20:
                self.choose.showtime += 1
            else:
                self.choose.showtime = 0
                self.choose.pos_i = (self.choose.pos_i + 1) % 14
                self.choose.pos = self.choose_card[self.choose.pos_i]

    def set_tick(self):  # 给最终抽中的卡牌标记
        global Coins
        self.tick.pos = self.choose.pos
        if self.choose.pos_i < 7:
            Collection[self.choose.pos_i] = True
        elif self.choose.pos_i in self.coin_20:
            Coins += 20
        elif self.choose.pos_i in self.coin_50:
            Coins += 50
        save()
        self.tick.flag = True
        self.pressed = False

    def set_flag(self):
        self.flag = False

    def move_choose(self):  # 移动高亮选框
        self.choose.pos_i = (self.choose.pos_i + 1) % 14
        self.choose.pos = self.choose_card[self.choose.pos_i]
        self.tick_flag = True

    def on_mouse_down_store(self, pos):  # 感应鼠标左键是否按下按钮
        global Coins
        if self.pressed:
            return
        self.prize.flag = False
        self.tick.flag = False
        self.choose.move_flag = True
        if self.roll_button.collidepoint(pos) and Coins >= 50:  # 抽卡
            sounds.card.play()
            self.pressed = True
            x = random.randint(1, 15)
            Coins -= 50
            self.choose.move_flag = False
            self.tick.flag = False
            for i in range(1, x + 20):
                clock.schedule(self.move_choose, i / 4)
            clock.schedule(self.move_choose, x / 4 + 5)
            clock.schedule(self.move_choose, x / 4 + 6)
            clock.schedule(self.move_choose, x / 4 + 7.5)
            clock.schedule(self.move_choose, x / 4 + 9.5)
            clock.schedule(self.set_tick, x / 4 + 9.7)
            clock.schedule(self.show_prize, x / 4 + 9.8)

        elif self.return_button.collidepoint(pos):  # 返回主界面
            global Mode
            Mode = 1
            music.play('main_bgm')

    def show_prize(self):
        self.prize.flag = True

    def hide_prize(self):
        self.prize.flag = False
# -----------------------------------Store----------------------------------#


# -----------------------------------main-----------------------------------#

def save():
    f = open("history.txt", "w")
    # 存档，包括每个关卡的过关情况，积分数，商场人物的购买、解锁情况
    for i in range(5):
        f.write(str(pass_through[i]))
        f.write("\n")
    for i in range(7):
        f.write(str(Collection[i]))
        f.write("\n")
    f.write(str(Coins))
    f.write("\n")
    f.close()


def read():
    global Coins
    try:
        with open("history.txt", "r") as f:
            i = 0
            for a in f:
                if i < 5:
                    if a == "False\n":
                        pass_through[int(i)] = False
                    else:
                        pass_through[int(i)] = True
                elif i < 12:
                    if a == "False\n":
                        Collection[int(i - 5)] = False
                    else:
                        Collection[int(i - 5)] = True
                else:
                    Coins = int(a)
                i += 1
    except:
        pass


pass_through = [False, False, False, False, False]
# pass_through = [True, True, True, True, True]
Collection = [False, False, False, False, False, False, False]
# Collection = [True, True, True, True, True, True, True]
Coins = 0
read()
maze_game = boss_game = MVL_game = Music_game = Ship_game = None

Game_Over = False
end_time = 0
Win = False
cases = [
    Actor("1", (102, 165)),
    Actor("2", (220, 318)),
    Actor("3", (285, 237)),
    Actor("4", (337, 180)),
    Actor("5", (477, 260)),
]
Mode = 0
music.play('main_bgm')
Main_menu = Actor("home_page", (WIDTH / 2, 300))
Main_menu2 = Actor("home_page", (580, 450))
Restart = Actor("restart", (WIDTH / 2, 180))
Store = Actor("store", (470, 50))
Help = Actor("help", (590, 50))
Help_doc = Actor("help_doc", (WIDTH / 2, HEIGHT / 2))
Coin_pic = Actor("coin", (25, 30))
Coin_pic2 = Actor("coin", (440, 160))
Quit = Actor("quit", (WIDTH - 40, 460))
Delete = Actor("delete_history", (530, 50))
Pause_reminder = Actor('pause_reminder', (470, 50))
store = STORE()
flag_pause = False
Cover_start = Actor('cover_start', (540, 440))
for i in range(4):
    if not pass_through[i]:
        cases[i + 1].image = "locked"

# 背包的代码构想---package
Package = Actor('package', (410, 50))
Pics = [Actor('s_card2', (120, 120)), Actor('s_card1', (330, 160)),
        Actor('s_card5', (540, 140)), Actor('s_card3', (120, 240)),
        Actor('s_card6', (120, 360)), Actor('s_card7', (330, 360)),
        Actor('s_card4', (540, 340))]
Orig_pics = ['s_card2', 's_card1', 's_card5', 's_card3', 's_card6', 's_card7', 's_card4']
Locked_pic = ['locked2', 'locked1', 'locked5', 'locked3',
              'locked6', 'locked7', 'locked4']

def loading_menu():
    cases[0].draw()
    cases[1].draw()
    cases[2].draw()
    cases[3].draw()
    cases[4].draw()
    Store.draw()
    Coin_pic.draw()
    Package.draw()
    screen.draw.text("%d" % Coins, (45, 15), color="yellow", fontsize=50)
    Quit.draw()
    Delete.draw()
    Help.draw()


def pause_menu():  # 在游戏中间的pause
    Main_menu.draw()
    Restart.draw()

# 根据Mode切换要展示的界面，调用对应的类的成员函数
def draw():
    global Game_Over, end_time, Mode, Win, maze_game, MVL_game, Ship_game, boss_game, Music_game
    hour = time.localtime()[3]
    if 5 <= hour < 7:
        time_mode = 1
    elif 7 <= hour < 18:
        time_mode = 2
    elif 18 <= hour < 20:
        time_mode = 3
    else:
        time_mode = 4
    if flag_pause:
        Main_menu.draw()
        Restart.draw()
        if Mode == 2:
            maze_game.start_time = time.time()
        return
    if Game_Over:
        # 要更换为显示通关、分数、下一关等的界面
        t = time.time() - end_time
        if t > 4:
            Game_Over = False
            music.stop()
            Mode = 1
            del maze_game, boss_game, MVL_game, Music_game, Ship_game
            maze_game = boss_game = MVL_game = Music_game = Ship_game = None
            music.play('main_bgm')
    if Win:
        t = time.time() - end_time
        if t > 4:
            save()
            Win = False
            Mode = 1
            del maze_game, boss_game, MVL_game, Music_game, Ship_game
            maze_game = boss_game = MVL_game = Music_game = Ship_game = None
            music.stop()
            music.play('main_bgm')
    if Mode == 0:
        screen.blit('cover', (0, 0))
        Cover_start.draw()
    if Mode == -1:
        Help_doc.draw()
        Main_menu2.draw()
        return
    if Mode == 1 and not Game_Over:
        if time_mode == 1:
            screen.blit("main_dawn", (0, 0))
        elif time_mode == 2:
            screen.blit("main_daytime", (0, 0))
        elif time_mode == 3:
            screen.blit("main_dusk", (0, 0))
        elif time_mode == 4:
            screen.blit("main_night", (0, 0))
        loading_menu()
    elif Mode == -3:
        screen.blit("main", (0, 0))
        for i in range(7):
            if not Collection[i]:
                Pics[i].image = Locked_pic[i]
            else:
                Pics[i].image = Orig_pics[i]
            Pics[i].draw()
        Main_menu2.draw()
    elif Mode == 2:
        maze_game.draw_maze()
    elif Mode == 3:
        boss_game.draw_boss()
    elif Mode == 4:
        MVL_game.draw_MVL()
    elif Mode == 5:
        Ship_game.draw_ships()
    elif Mode == 6:
        Music_game.draw_music()


def update():
    if flag_pause:
        return
    if Mode == -2:
        store.draw_store()
    elif Mode == 2:
        maze_game.play_maze()
    elif Mode == 3:
        boss_game.update_boss()
    elif Mode == 4:
        MVL_game.update_MVL()
    elif Mode == 5:
        Ship_game.update_ships()
    elif Mode == 6:
        Music_game.update_music()


def on_mouse_down(pos, button=None):
    global Mode, Game_Over, Ship_game, Music_game, pass_through, Collection
    global maze_game, MVL_game, boss_game, flag_pause, Coins
    if Mode == 0 and Cover_start.collidepoint(pos):
        Mode = 1
    # 如果在主菜单界面---选择游戏/商城/存档/读档/退出
    if Mode == 1:
        if cases[2].collidepoint(pos) and pass_through[1]:
            Mode = 2
            maze_game = MAZE()
            maze_game.mode = 1
            music.play("bgm3")
        elif cases[4].collidepoint(pos) and pass_through[3]:
            Mode = 3
            boss_game = BOSS()
            boss_game.mode = 1
            music.play("bgm2")
        elif cases[0].collidepoint(pos):
            Mode = 4
            MVL_game = MARIO_VS_LAKITU()
            MVL_game.mode = 1
            music.play("bgm")
        elif cases[3].collidepoint(pos) and pass_through[2]:
            Mode = 5
            Ship_game = BattleShips()
            Ship_game.mode = 1
            music.play("bgm4")  # 播放背景音乐
        elif cases[1].collidepoint(pos) and pass_through[0]:
            Mode = 6
            Music_game = ImitateMusic()
            Music_game.mode = 1
            music.play("bgm_music")
        elif Quit.collidepoint(pos):
            game.exit()
        elif Delete.collidepoint(pos):
            pass_through = [False, False, False, False, False]
            Collection = [False, False, False, False, False, False, False]
            Coins = 0
            for i in range(4):
                if not pass_through[i]:
                    cases[i + 1].image = "locked"
            save()
        elif Help.collidepoint(pos):
            Mode = -1
        elif Store.collidepoint(pos):
            Mode = -2
            music.play('store_bgm')
        elif Package.collidepoint(pos):
            Mode = -3
    elif Mode == -1 or Mode == -3:
        if Main_menu2.collidepoint(pos):
            Mode = 1
    elif Mode == -2:
        store.on_mouse_down_store(pos)
    # 如果是在游戏中并且在规则界面点击了开始---游戏正式开始
    if Mode == 2 and maze_game.start_button.collidepoint(pos) and maze_game.mode == 1:
        maze_game.mode = 2
        maze_game.main_maze()
    elif Mode == 3 and boss_game.start_button.collidepoint(pos) and boss_game.mode == 1:
        boss_game.mode = 2
        boss_game.main_boss()
    elif Mode == 4 and MVL_game.start_button.collidepoint(pos) and MVL_game.mode == 1:
        MVL_game.mode = 2
        MVL_game.main_MVL()
    elif Mode == 5 and Ship_game.start_button.collidepoint(pos) and Ship_game.mode == 1:
        Ship_game.mode = 2
        Ship_game.generate_ships()  # 生成敌舰
    elif Mode == 5 and Ship_game.mode == 2:
        Ship_game.on_mouse_down_ships(pos, button)
    elif (Mode == 6 and Music_game.start_button.collidepoint(pos) and Music_game.mode == 1):
        Music_game.mode = 2
    if flag_pause:
        if Main_menu.collidepoint(pos):
            music.stop()
            Mode = 1
            loading_menu()
            flag_pause = False
        elif Restart.collidepoint(pos):
            flag_pause = False
            if Mode == 2:
                del maze_game
                maze_game = MAZE()
                music.play("bgm3")
                maze_game.main_maze()
            elif Mode == 3:
                del boss_game
                boss_game = BOSS()
                music.play("bgm2")
                boss_game.main_boss()
            elif Mode == 4:
                del MVL_game
                MVL_game = MARIO_VS_LAKITU()
                music.play("bgm")
                MVL_game.main_MVL()
            elif Mode == 5:
                del Ship_game
                Ship_game = BattleShips()
                music.play("bgm4")  # 播放背景音乐
                Ship_game.generate_ships()  # 生成敌舰
            elif Mode == 6:
                del Music_game
                music.play("bgm_music")
                Music_game = ImitateMusic()




def on_mouse_move(pos):
    if Mode == 5 and not Game_Over and not flag_pause:
        Ship_game.on_mouse_move_ships(pos)


def on_key_down(key):
    global flag_pause
    if flag_pause and key == keys.P:
        flag_pause = False
        return
    if Mode != 1 and not flag_pause:
        if key == keys.P:
            flag_pause = True
            if Mode == 4:
                MVL_game.paused = True
    if Mode == 6 and not flag_pause:
        Music_game.on_key_down_music(key)


pgzrun.go()

# Mode:1主菜单，2迷宫，3boss，4MVL，5ship，6music，7store，-1Help，-2Store，-3package
