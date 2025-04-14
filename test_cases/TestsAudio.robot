*** Settings ***
Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    AppiumLibrary
Library    Integration.py

*** Variables ***
${AppGrid_ACTIVITY}    com.android.car.carlauncher/.GASAppGridActivity
${Setting_ACTIVITY}    com.android.car.settings/.Settings_Launcher_Homepage
${MessageActivity}     com.android.car.messenger/.ui.launcher.MessageLauncherActivity
${Setting_fr}          Settings
${Setting_xpath_id}    com.android.car.settings:id/car_settings_activity_wrapper
${Setting_menu}        com.android.car.settings:id/top_level_menu
${Device}              emulator-5556
${Setting_system}      com.android.car.settings:id/fragment_container
${System}               System
*** Test Cases ***