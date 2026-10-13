[app]
title = Syobon Action 0
package.name = syobon0
package.domain = org.yourname
source.dir = .
# 読み込む拡張子に、ゲームで使うものをすべて指定します（xlsxも含む）
source.include_exts = py,png,jpg,wav,mp3,xlsx,ico,ttf

version = 0.1
orientation = landscape
fullscreen = 1

# 必要なライブラリをカンマ区切りで指定（pygame, xlrd, numpy）
requirements = python3,pygame,xlrd,numpy

android.archs = arm64-v8a
android.allow_backup = True
