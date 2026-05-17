[app]
title = Gestion Tienda
package.name = gestiontienda
package.domain = org.miralles

source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas,db

version = 1.0

requirements = python3,kivy,pillow

orientation = portrait
fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2