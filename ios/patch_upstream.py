#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])
cmake = root / "CMakeLists.txt"
text = cmake.read_text()

text = text.replace("project(AbyssEngine)", "project(AbyssEngine C)", 1)
text = text.replace(
    "set(CMAKE_C_STANDARD 99)",
    """set(CMAKE_C_STANDARD 99)

option(ABYSS_IOS "Build Abyss Engine for iOS" OFF)
if(ABYSS_IOS)
    set(CMAKE_SYSTEM_NAME iOS)
    set(CMAKE_OSX_SYSROOT iphoneos CACHE STRING "" FORCE)
    set(CMAKE_OSX_ARCHITECTURES arm64 CACHE STRING "" FORCE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET 15.0 CACHE STRING "" FORCE)
endif()""",
    1,
)

darwin = "if (" + "$" + "{CMAKE_SYSTEM_NAME} MATCHES \"Darwin\")"
text = text.replace(
    darwin,
    "if (" + "$" + "{CMAKE_SYSTEM_NAME} MATCHES \"Darwin\" AND NOT ABYSS_IOS)",
    1,
)
text = text.replace(
    "if (APPLE)\n    if (NOT DEFINED GITHUB_ACTIONS)",
    "if (APPLE AND NOT ABYSS_IOS)\n    if (NOT DEFINED GITHUB_ACTIONS)",
    1,
)

if "target_link_libraries(AbyssEngine" not in text:
    raise SystemExit("target_link_libraries(AbyssEngine) not found")

dollar = "$"
text += f"""
if (ABYSS_IOS)
    set_target_properties(AbyssEngine PROPERTIES
        MACOSX_BUNDLE TRUE
        MACOSX_BUNDLE_GUI_IDENTIFIER "com.anch.d2ios"
        MACOSX_BUNDLE_BUNDLE_NAME "D2 iOS"
        MACOSX_BUNDLE_BUNDLE_VERSION "1.0"
        XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER "com.anch.d2ios"
        XCODE_ATTRIBUTE_IPHONEOS_DEPLOYMENT_TARGET "15.0"
        XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED "NO"
        XCODE_ATTRIBUTE_CODE_SIGNING_REQUIRED "NO"
        XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY ""
    )

    find_library(IOS_UIKIT UIKit REQUIRED)
    find_library(IOS_QUARTZCORE QuartzCore REQUIRED)
    find_library(IOS_AVFOUNDATION AVFoundation REQUIRED)
    target_link_libraries(AbyssEngine PRIVATE
        {dollar}{{IOS_UIKIT}}
        {dollar}{{IOS_QUARTZCORE}}
        {dollar}{{IOS_AVFOUNDATION}}
    )
endif()
"""
cmake.write_text(text)
print("Patched", cmake)
