[app]
title = PediMed Safe
package.name = pedimed
package.domain = org.kemko
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

requirements = python3==3.11.9,kivy==2.3.0,android,pyjnius

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# KLJUČNA LINIJA KOJA AUTOMATSKI PRIHVATA SVE LICENCE:
android.accept_sdk_license = True

android.api = 33
android.minapi = 24
android.ndk_api = 24
