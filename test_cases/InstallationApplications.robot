*** Settings ***
Documentation    Tests for APK installation and uninstallation
...              - Verifies APK installation via ADB
...              - Checks application visibility in UI
...              - Tests complete uninstallation flow
Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Suite Setup     Démarrer Driver
Suite Teardown  Fermer Driver
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
*** Keywords ***
Démarrer Driver
    ${driver}=    setup driver    ${Device}
    Set Suite Variable    ${driver}

Fermer Driver
    Close Driver    ${driver}

*** Test Cases ***
Test Install Apk
    [Documentation]    Tests APK installation process
    ...                - Checks pre-installation state
    ...                - Installs the APK
    ...                - Verifies installation in system and UI
      ${isInsUi}=   Search Application     ${driver}        TestNotificationapk
      Log    ${isInsUi}
      ${isIns}=      Is App Installed      ${driver}        actia.pfe25.testnotificationapk
      Log    ${isIns}
      Install Apk     ${driver}         automotive-Notification_Test.apk
      ${isIns}=      Is App Installed      ${driver}        actia.pfe25.testnotificationapk
      Log    ${isIns}
      Run Keyword And Continue On Failure      Should Be True    ${isIns}      The application is not installed via adb

      ${isInsUi}=   Search Application     ${driver}        TestNotificationapk
      Run Keyword And Continue On Failure        Should Be True    ${isInsUi}      The installed application is not displayed (via adb)



Test Uninstall Application
    [Documentation]    Tests application uninstallation
    ...                - Navigates through settings
    ...                - Performs uninstallation
    ...                - Verifies complete removal
    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}       Set Variable     Système
        ${Setting}     Set Variable     Paramètres
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable     Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${confirme}         Set Variable    OK
    ELSE
        ${System}   Set Variable    System
        ${Setting}    Set Variable    Settings
        ${apps}         Set Variable     Apps
        ${Consulter_allapps}         Set Variable      View all
        ${DesButton}        Set Variable    Uninstall
        ${confirme}         Set Variable    OK
    END

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Settings is not displayed.

    Clique Sur Setting         ${driver}      ${apps}       ${Setting_menu}
    Clique Sur Setting Include      ${driver}     ${Consulter_allapps}     ${Setting_system}
    Clique Sur Setting         ${driver}     TestNotificationapk      ${Setting_system}
    click Element By Text Att     ${driver}     ${DesButton}
    Sleep    1s
    click Element By Text     ${driver}     ${confirme}

    ${isInsUi}=   Search Application     ${driver}        TestNotificationapk
    Run Keyword And Continue On Failure    Should Not Be True    ${isInsUi}       The uninstalled application is displayed

    ${isIns}=      Is App Installed      ${driver}        actia.pfe25.testnotificationapk
    Log    ${isIns}
    Run Keyword And Continue On Failure     Should Not Be True     ${isIns}      The application is not uninstalled correctly (via adb)




