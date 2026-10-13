	# ---- kkk.py のファイルの一番上（関数の外）に追記します ----

# エンドロール用のグローバル変数を完全に一番外側で定義する
endroll_active = False
endroll_y = 600.0
endroll_font = None
endroll_text = [
    "〜 しょぼんのアクション 完結！ 〜",
    "",
    "オールクリア！ おめでとうございます！",
    "",
    "【 STAFF CREDIT 】",
    "",
    "企画・開発",
    "あなた",
    "",
    "グラフィック協力",
    "AI アシスタント",
    "",
    "スペシャルサンクス",
    "プレイしてくれたあなた",
    "",
    "",
    "Presented by Pygame",
    "",
    "THE END"
]

import sys
from time import sleep
import pygame
from pygame.locals import *

from Enemy import Enemy
from Image import LoadImage
from Sprite import SpritePlayer
from Sound import Sound
from Stage import Stage
from Player import Player
from Text import Text

pygame.init()

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 420
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("しょぼんのアクション0")
pygame.display.set_icon(pygame.image.load("res/icon.ico"))

clock = pygame.time.Clock()
FPS = 60
GAME_STATE = 0
REMAIN = 2

def main():
    LoadImage()
    Text()
    Sound()
    while True:
        # 【重要】一番外側で作ったエンドロール用の変数を、このループ内でも使うよ、とシステムに宣言する
        global endroll_active, endroll_y, endroll_font, endroll_text
        
        # フォントがまだ作られていなければ、ここで作成する
        if endroll_font is None:
            endroll_font = pygame.font.SysFont("msgothic", 30) or pygame.font.SysFont("notosanscjkjp", 30)

        # ----- エンドロール再生中の処理 -----
        if endroll_active:
            # 1. 画面を黒で塗りつぶす
            screen.fill((0, 0, 0))
            
            # 2. テキストを上に少しずつスクロール
            endroll_y -= 1.2
            
            # 3. 1行ずつ文字を描画
            current_y = endroll_y
            for line in endroll_text:
                if line:
                    text_surface = endroll_font.render(line, True, (255, 255, 255))
                    text_x = (screen.get_width() - text_surface.get_width()) // 2
                    if -40 < current_y < 600:
                        screen.blit(text_surface, (text_x, int(current_y)))
                current_y += 45  # 行間
                
            # 4. エンドロール中の終了イベント（×ボタン対応）
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            # 5. 画面を更新
            pygame.display.update()
            
            # 全テキストが消え去ったらゲームを自動終了
            if endroll_y < -(len(endroll_text) * 45):
                pygame.quit()
                sys.exit()
                
            continue  # 通常のゲーム進行を止めてループの先頭に戻る


        # ----- 通常プレイ中、新しく追加したエンドブロックに触れたかの判定を毎フレーム行う -----
        from Stage import Stage
        for block in list(Stage.block_object_list):
            # 新しいブロック「end_block」を探す
            if block.name == 'end_block':
                # プレイヤーの体がブロックに1ピクセルでも重なったら即作動！
                if Stage.player_object.rect.colliderect(block.rect):
                    # エンドロールを起動させる！
                    endroll_active = True
                    
                    # ぷよぷよのBGMを流す処理
                    try:
                        pygame.mixer.music.stop()  # 現在のBGMを停止
                        import os
                        bgm_path = os.path.join("res", "puyo_bgm.mp3")
                        pygame.mixer.music.load(bgm_path)
                        pygame.mixer.music.play(-1)  # ループ再生
                    except Exception as e:
                        print(f"ぷよぷよBGMの再生に失敗しました: {e}")



        if GAME_STATE == 0: Title()
        elif GAME_STATE == 1: Stage_1()
        elif GAME_STATE == 2: Stage_2()
        elif GAME_STATE == 3: Stage_3()
        elif GAME_STATE == 4: Stage_4()

def remain_show():
    global REMAIN
    screen.fill((0, 0, 0))
    img = LoadImage.image_list
    player = img['player1']
    player_rect = player.get_rect()
    player_rect.center = (200, 210)
    screen.blit(player, player_rect)
    
    sign = "-" if REMAIN < 0 else ""
    font = pygame.font.SysFont("sana", 20)
    tweak = 0
    for count, t in enumerate(f"× {sign}{abs(REMAIN)}"):
        text_x = 235 + count * 11
        if count == 1: tweak += 10
        elif count == 3: tweak += 1
        text = font.render(t, True, (255, 255, 255))
        screen.blit(text, [text_x + tweak, 200])
        screen.blit(text, [text_x + tweak + 1, 200])
    REMAIN -= 1
    pygame.display.update()
    for _ in range(100):
        sleep(0.005 if pygame.key.get_pressed()[K_SPACE] else 0.01)

def state_change(state_number):
    global GAME_STATE
    GAME_STATE = state_number
    SpritePlayer.initial_x = 55
    SpritePlayer.initial_y = 320
    SpritePlayer.initial_scroll_sum = 0

class Title:
    def __init__(self):
        global REMAIN
        REMAIN = 2
        self.goto_stage = 1
        img = LoadImage.image_list
        screen.fill((0, 0, 0))
        rect_title = img['title'].get_rect()
        rect_title.center = (239, 88)
        screen.blit(img['title'], rect_title)
        
        font = pygame.font.SysFont("sana", 20)
        for count, t in enumerate("Press Enter!!"):
            text_x = 160 + count * 11
            text = font.render(t, True, (255, 255, 255))
            screen.blit(text, [text_x, 249])
            screen.blit(text, [text_x + 1, 249])
            
        screen.blit(img['player1'], (60, 330))
        screen.blit(img['grass'], (180, 336))
        screen.blit(img['mountain'], (360, 278))
        for i in range(17):
            screen.blit(img['block5'], (29 * i, 365))
            screen.blit(img['block6'], (29 * i, 394))
        self.main()

    def main(self):
        while True:
            pygame.display.update()
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_1: self.goto_stage = 1
                    elif event.key == K_2: self.goto_stage = 2
                    elif event.key == K_3: self.goto_stage = 3
                    elif event.key == K_4: self.goto_stage = 4
                    elif event.key in (13, 122):
                        state_change(self.goto_stage)
                        return

class BaseStage:
    def __init__(self, world, stage_name, bgm_name, next_state):
        self.Stage = Stage(screen, world, stage_name)
        self.Player = Player(screen, self.Stage)
        self.Enemy = Enemy(screen)
        self.next_state = next_state
        remain_show()
        Sound.play_BGM(bgm_name)
        self.main()

    def main(self):
        while True:
            screen.fill((0, 0, 0))
            if self.Player.goal_animation():
                global REMAIN
                REMAIN += 1
                state_change(self.next_state)
                return
            if self.Player.dokan_animation() or self.Player.death_animation():
                return
            self.Player.update()
            self.Enemy.update()
            self.Player.item_animation()
            self.Stage.update()
            Text.update()
            variable_FPS = FPS * (2 if pygame.key.get_pressed()[K_SPACE] else 1)
            clock.tick(variable_FPS)
            pygame.display.update(Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_F1:
                        state_change(0)
                        return
                    if event.key == K_o:
                        Stage.player_object.isDeath = True

class Stage_1(BaseStage):
    def __init__(self): super().__init__(1, '1-1', 'puyo', 2)

class Stage_2(BaseStage):
    def __init__(self): super().__init__(1, '1-2', 'star4', 3)

class Stage_3(BaseStage):
    def __init__(self): super().__init__(1, '1-3', 'puyo', 4)

class Stage_4(BaseStage):
    def __init__(self): super().__init__(4, '1-4', 'makaimura', 0)

if __name__ == "__main__":
    main()
