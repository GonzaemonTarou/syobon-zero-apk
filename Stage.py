import pygame
import xlrd
import sys
import tkinter
from tkinter import messagebox

from Sprite import SpriteBlock, SpriteObject, SpritePlayer
from Image import LoadImage  # ← この行を新しく追加してください


class Stage:
    # プレイヤーオブジェクトを格納するリスト
    player_object = None
    # ブロックオブジェクトを格納するリスト
    block_object_list = []
    # 敵オブジェクトを格納するリスト
    enemy_object_list = []

    def __init__(self, screen, block_color, sheet_name):
        self.screen = screen
        
        # 【追加】現在残っている敵スプライトをすべて完全に消去して初期化する
        if hasattr(Stage, 'enemy_object_list') and Stage.enemy_object_list:
            for enemy in list(Stage.enemy_object_list):
                if hasattr(enemy, 'kill'):
                    enemy.kill() # Pygameのスプライトグループから完全に削除する
        
        # プレイヤーの再生成
        Stage.player_object = SpritePlayer(screen)
        
        # 現在のステージ名を保存
        self.sheet_name = sheet_name

        # オブジェクトリストの完全クリア
        Stage.block_object_list.clear()
        Stage.enemy_object_list.clear()


        # ステージのブロックの色 （1～4）
        self._mode = 7 * (block_color - 1)

        # Excelからステージデータを取得
        try:
            file = xlrd.open_workbook('res/ステージデータ.xlsx')
            sheet = file.sheet_by_name(sheet_name)
        except FileNotFoundError:
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("エラー", "ステージデータ.xlsxが見つかりませんでした")
            pygame.quit()
            sys.exit()
        except xlrd.biffh.XLRDError:
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("エラー", f"シート'{sheet_name}'が見つかりませんでした")
            pygame.quit()
            sys.exit()

        # ステージデータを読み込む
        sheet_data = [sheet.col_values(row) for row in range(sheet.ncols)]
        self.stage_data = [[item for item in row if item != ''] for row in sheet_data]
        self.draw()

    def update(self):
        # 画面外になったらオブジェクト削除
        for image in list(self.block_object_list):
            if image.rect.left < image.START_RANGE:
                image.remove()
                if image in self.block_object_list:
                    self.block_object_list.remove(image)

        # 各ブロックの描画やアニメーション更新
        for image in self.block_object_list:
            # 背景画像以外を描画
            if image.name not in SpriteBlock.BG:
                image.update()

            # 【マグマの処理】触れたら即死
            if image.name == 'magma':
                if Stage.player_object.rect.colliderect(image.rect):
                    if not Stage.player_object.isDeath:
                        Stage.player_object.isDeath = True

    def draw(self):
        # ステージデータから取得
        for x, list_data in enumerate(self.stage_data):
            for y, data in enumerate(list_data):


                # 一つ前のステージデータを取得
                try:
                    stage_position_up = self.stage_data[x][y - 1]
                    stage_position_down = self.stage_data[x][y + 1]
                    stage_position_left = self.stage_data[x - 1][y]
                    stage_position_right = self.stage_data[x + 1][y]
                except IndexError:
                    stage_position_up = 0
                    stage_position_down = 0
                    stage_position_left = 0
                    stage_position_right = 0

                # ---- 壊れるブロック（レンガブロック・数値1.1を含む）の処理 ----
                if data == 1 or data == 1.1 or data == 1.6 or (1.4 <= data <= 2.6 and data != 2.1):
                    # 2面（1-2）のときだけ見た目を専用画像に変更する
                    if self.sheet_name == '1-2':
                        import os
                        import pygame
                        if 'custom_stage2_brick_break' not in LoadImage.image_list:
                            try:
                                # ※ "stage2_block.png" を実際の画像ファイル名に書き換えてください
                                img_path = os.path.join("res", "block", "stage2_brick.png")
                                loaded_img = pygame.image.load(img_path).convert_alpha()
                                block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                                LoadImage.image_list['custom_stage2_brick_break'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                            except Exception as e:
                                print(f"2面専用レンガ画像の読み込みエラー: {e}")
                                if 'block1' in LoadImage.image_list:
                                    LoadImage.image_list['custom_stage2_brick_break'] = LoadImage.image_list['block1']
                        
                        self.block_add('custom_stage2_brick_break', data, x, y, color=False)
                    else:
                        # 【重要】2面以外の通常ステージ（1-1や1-3など）で元のレンガ（1.1含む）を復活させる処理
                        self.block_add('block1', data, x, y, start=1, end=1.2, color=True)
                        self.block_add('block1', data, x, y, start=1.4, end=2.6, color=True)

                # スターが出る特殊なレンガ（数値 2.1）の処理
                if data == 2.1:
                    if self.sheet_name == '1-2':
                        self.block_add('custom_stage2_brick_break', data, x, y, color=False)
                    else:
                        self.block_add('block1', data, x, y, color=True)


                # 近づくと落ちるブロック
                if data == 1.3:
                    group = 'end' if stage_position_right != 1.3 else ''
                    
                    # 2面（1-2）のときだけ見た目を専用画像に変更する
                    if self.sheet_name == '1-2':
                        import os
                        import pygame
                        if 'custom_stage2_nearfall' not in LoadImage.image_list:
                            try:
                                # ※ "stage2_block.png" を実際の画像ファイル名に書き換えてください
                                img_path = os.path.join("res", "block", "stage2_brick.png")
                                loaded_img = pygame.image.load(img_path).convert_alpha()
                                block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                                LoadImage.image_list['custom_stage2_nearfall'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                            except Exception as e:
                                print(f"2面専用・近づくと落ちるブロック画像の読み込みエラー: {e}")
                                if 'block1' in LoadImage.image_list:
                                    LoadImage.image_list['custom_stage2_nearfall'] = LoadImage.image_list['block1']
                        
                        self.block_add('custom_stage2_nearfall', data, x, y, group=group, color=False)
                    else:
                        # 【重要】2面以外の通常ステージで元のブロックを正常に復活させる
                        self.block_add('block1', data, x, y, group=group, color=True)


                # はてなブロック
                self.block_add('block2', data, x, y, start=3, end=4.1, color=True)

                # 隠しブロック
                self.block_add('block3', data, x, y, start=5, end=6.1, color=True, hide=True)

                # ---- Stage.py の「# 硬いブロック」の処理を以下に丸ごと書き換えます ----

                # ---- 硬いブロック（数値 7）の処理 ----
                if data == 7:
                    # 【追加】2面（1-2）のときだけ見た目を送られた画像に変更する
                    if self.sheet_name == '1-2':
                        import os
                        if 'custom_stage2_block7' not in LoadImage.image_list:
                            try:
                                # 【重要】"stage2_block.png" を実際の画像ファイル名に書き換えてください
                                img_path = os.path.join("res", "block", "stage2_block.png")
                                loaded_img = pygame.image.load(img_path).convert_alpha()
                                block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                                LoadImage.image_list['custom_stage2_block7'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                            except Exception as e:
                                print(f"2面専用ブロック画像の読み込みエラー: {e}")
                                if 'block4' in LoadImage.image_list:
                                    LoadImage.image_list['custom_stage2_block7'] = LoadImage.image_list['block4']
                        
                        self.block_add('custom_stage2_block7', data, x, y, color=False)
                    
                    # 1-4ステージの時
                    elif self._mode == 21:
                        import os
                        if 'custom_block7' not in LoadImage.image_list:
                            try:
                                img_path = os.path.join("res", "block", "block18.png")
                                loaded_img = pygame.image.load(img_path).convert_alpha()
                                block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                                LoadImage.image_list['custom_block7'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                            except Exception as e:
                                if 'block4' in LoadImage.image_list:
                                    LoadImage.image_list['custom_block7'] = LoadImage.image_list['block4']
                        self.block_add('custom_block7', data, x, y, color=False)
                    else:
                        self.block_add('block4', data, x, y, start=7, end=7.1, color=True)

                # ---- 足場ブロック（数値 8）の処理 ----
                if data == 8:
                    # 【修正】2面（1-2）のときだけ見た目を変更する
                    if self.sheet_name == '1-2':
                        import os
                        import pygame  # ここで確実にpygameをインポートする
                        
                        if 'custom_stage2_brick' not in LoadImage.image_list:
                            try:
                                # ※ "stage2_block.png" を実際の画像ファイル名に書き換えてください
                                img_path = os.path.join("res", "block", "stage2_block.png")
                                loaded_img = pygame.image.load(img_path).convert_alpha()
                                
                                # ブロックサイズに合わせてリサイズ
                                block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                                LoadImage.image_list['custom_stage2_brick'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                            except Exception as e:
                                print(f"2面専用足場画像の読み込みエラー: {e}")
                                # 【安全対策】画像が読み込めなかった場合は、1面の通常の足場（block1）を代わりに登録してエラー落ちを防ぐ
                                if 'block1' in LoadImage.image_list:
                                    LoadImage.image_list['custom_stage2_brick'] = LoadImage.image_list['block1']
                        
                        self.block_add('custom_stage2_brick', data, x, y, color=False)

                    # 1-4の時
                    elif self._mode == 21:
                        import os
                        import pygame
                        if 'custom_gray_brick' not in LoadImage.image_list:  # バグ防止のためimage_listに変更
                            try:
                                img_path = os.path.join("res", "gray_brick.png")
                                loaded_img = pygame.image.load(img_path).convert_alpha()
                                block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                                LoadImage.image_list['custom_gray_brick'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                            except Exception:
                                if 'block1' in LoadImage.image_list:
                                    LoadImage.image_list['custom_gray_brick'] = LoadImage.image_list['block1']
                        self.block_add('custom_gray_brick', data, x, y, color=False)
                    else:
                        if stage_position_up != 8:
                            self.block_add('block5', data, x, y, color=True)
                        else:
                            self.block_add('block6', data, x, y, color=True)

# ---- Stage.py の 剣(数値45) の処理を以下に丸ごと書き換えます ----

                # 剣（Excelデータ上の数値「45」に対応）
                if data == 45:
                    import os
                    if 'sword' not in LoadImage.image_list:
                        try:
                            # 読み込む画像の場所を res\block フォルダの中に修正
                            img_path = os.path.join("res", "block", "block34.png")
                            loaded_img = pygame.image.load(img_path).convert_alpha()
                            
                            # ブロックサイズに合わせて綺麗にリサイズ
                            block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                            LoadImage.image_list['sword'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                        except Exception as e:
                            print(f"剣画像の読み込みに失敗しました: {e}")
                            # 万が一のときのエラー落ち防止策
                            if 'block1' in LoadImage.image_list:
                                LoadImage.image_list['sword'] = LoadImage.image_list['block1']
                    
                    # color=False でオリジナルの色のまま配置
                    self.block_add('sword', data, x, y, color=False)


                # ---- 落ちる足場ブロック（数値 8.1）の処理 ----
                if data == 8.1:
                    # ブロックの繋がり（グループ）を判定する処理
                    if stage_position_up != 8.1:
                        group = 'start' if stage_position_left != 8.1 else ''
                    else:
                        group = 'end' if stage_position_right != 8.1 else ''

                    # 2面（1-2）のときだけ見た目を専用画像に変更する
                    if self.sheet_name == '1-2':
                        import os
                        import pygame
                        if 'custom_stage2_ridefall' not in LoadImage.image_list:
                            try:
                                # ※ "stage2_block.png" を実際の画像ファイル名に書き換えてください
                                img_path = os.path.join("res", "block", "stage2_block.png")
                                loaded_img = pygame.image.load(img_path).convert_alpha()
                                block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                                LoadImage.image_list['custom_stage2_ridefall'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                            except Exception as e:
                                print(f"2面専用・上に乗ったら落ちるブロックの画像読み込みエラー: {e}")
                                if 'block1' in LoadImage.image_list:
                                    LoadImage.image_list['custom_stage2_ridefall'] = LoadImage.image_list['block1']
                        
                        self.block_add('custom_stage2_ridefall', data, x, y, group=group, color=False)

                    # 1-4（四面）の時
                    elif self._mode == 21:
                        self.block_add('custom_gray_brick', data, x, y, group=group, color=False)
                    
                    # 【重要】それ以外の通常のステージ（一面、三面など）で元のブロックを復活させる
                    else:
                        if stage_position_up != 8.1:
                            self.block_add('block5', data, x, y, group=group, color=True)
                        else:
                            self.block_add('block6', data, x, y, group=group, color=True)


                # 針
                self.block_add('block7', data, x, y, 40, color=True)

                # ポール
                self.block_add('goal_pole', data, x, y, 9.1, tweak_x=3, tweak_y=-10)

                # ビーム
                self.block_add('beam', data, x, y, 9.3, tweak_x=-88, tweak_y=4, hide=True)

                # 顔付きの雲
                self.block_add('cloud2', data, x, y, start=19.1, end=19.2)

                # 透明のうめぇ
                self.block_add('cloud4', data, x, y, 19.3, hide=True)

                # 土管
                self.block_add('dokan1', data, x, y, 20)
                self.block_add('dokan1', data, x, y, start=20.2, end=20.5)

                if data == 20.1:
                    if stage_position_up == 20.2:
                        # グループ化
                        self.stage_data[x][y] = 20.2
                        self.block_add('dokan2', 20.2, x, y, tweak_x=0, tweak_y=1)
                    else:
                        self.block_add('dokan2', 20.1, x, y, tweak_x=0, tweak_y=1)

                # 草
                self.block_add('grass', data, x, y, 22)

# ---- Stage.py の 160行目付近（「山」の下あたり）に追記 ----

                # 山
                self.block_add('mountain', data, x, y, 22.1)

                # マグマブロック（Excelデータ上の数値「41」で配置）
                # color=False にすることで、ステージごとの色補正を無視してオリジナルの赤い画像を描画します。
                if data == 41:
                    import os
                    # まだ画像リストに登録されていない場合のみ読み込み処理を行う
                    if 'magma' not in LoadImage.image_list:
                        try:
                            # 画像の読み込み（ファイル名は適宜変更してください）
                            img_path = os.path.join("res", "image_uuwuNX.png")
                            loaded_img = pygame.image.load(img_path).convert_alpha()
                            
                            # 他のブロック（block1など）の幅に合わせて綺麗にリサイズ
                            block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                            # マグマの画像をブロックサイズに合わせてリサイズして登録
                            LoadImage.image_list['magma'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                        except Exception as e:
                            print(f"マグマ画像の読み込みエラー: {e}")
                    
                    # 当たり判定なしのブロックとして追加
                    self.block_add('magma', data, x, y, color=False)
# ---- Stage.py の draw メソッド内に追加 ----

                # エンドロール起動ブロック（Excelデータ上の数値「46」に対応）
                if data == 46:
                    import os
                    if 'end_block' not in LoadImage.image_list:
                        try:
                            # 見た目として分かりやすいように剣のグラフィックを使用（お好きな画像名に変更してください）
                            img_path = os.path.join("res", "block", "buhi.png")
                            loaded_img = pygame.image.load(img_path).convert_alpha()
                            
                            # ブロックサイズに合わせて綺麗にリサイズ
                            block_w = SpriteBlock(self.screen, 'block1', data, 0, 0).width
                            LoadImage.image_list['end_block'] = pygame.transform.smoothscale(loaded_img, (block_w, block_w))
                        except Exception as e:
                            print(f"エンドブロック画像の読み込みエラー: {e}")
                            if 'block1' in LoadImage.image_list:
                                LoadImage.image_list['end_block'] = LoadImage.image_list['block1']
                    
                    # 通常の「硬い壁・床」として配置する
                    self.block_add('end_block', data, x, y, color=False)


                # 中間地点
                self.block_add('halfway', data, x, y, 24)

                # ゴール塔
                self.block_add('end', data, x, y, 24.1)

                # まるい敵
                self.enemy_add('enemy', data, x, y, start=27, end=27.2)

                # 甲羅亀
                self.enemy_add('koura1', data, x, y, start=28, end=28.1, tweak_x=0, tweak_y=-12)

                # 飛ぶ魚
                self.enemy_add('fish1', data, x, y, 29, tweak_x=10)
                self.enemy_add('fish2', data, x, y, start=29.1, end=29.2, tweak_x=-10)

                # イベントポイント
                self.block_add('bg', data, x, y, start=39, end=39.2, hide=True)

    def block_add(self, img_name, data, img_x, img_y, match=0.0,
                  start=0.0, end=0.0, tweak_x=0, tweak_y=0, group='', color=False, hide=False):
        # ブロックの色を変更
        name = f'block{int(img_name[-1:]) + self._mode}' if color else img_name

        # block_object_listに追加
        sprite = SpriteBlock(self.screen, name, data, img_x, img_y, tweak_x, tweak_y, group, hide)
        # 【追記】ブロック自身に所属ステージ名を覚えさせておく
        sprite.sheet_name = self.sheet_name
        
        append = (lambda: self.block_object_list.append(sprite))

        self._add(append, data, match, start, end)


    def enemy_add(self, name, data, img_x, img_y, match=0.0, start=0.0, end=0.0, tweak_x=0, tweak_y=0):
        # enemy_object_listに追加
        append = (lambda: self.enemy_object_list.append(
            SpriteObject(self.screen, name, data, img_x, img_y, tweak_x, tweak_y)
        ))

        self._add(append, data,  match, start, end)

    def _add(self, append, data, match, start, end):
        # dataと一致しているか確認する場合
        if match != 0.0:
            if data == match:
                append()

        # 画像のパターンマッチング
        elif start != 0.0 or end != 0.0:
            start = int(start * 10)
            end = int(end * 10)
            for i in range(start, end + 1):
                if data == i / 10:
                    append()

        else:  # 呼び出し元でdataと一致しているか確認する場合
            append()
