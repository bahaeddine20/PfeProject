*** Settings ***
Documentation    Tests for system update verification
...              - Verifies system update functionality
...              - Supports both French and English interfaces
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
${Device}              emulator-5554
${Setting_system}      com.android.car.settings:id/fragment_container
${System}               System
*** Keywords ***
Démarrer Driver
    ${driver}=    setup driver    ${Device}
    Set Suite Variable    ${driver}

Fermer Driver
    Close Driver    ${driver}


*** Test Cases ***

Test Verfier Mise A Jour System
    [Documentation]    Verifies system update functionality
    ...                - Navigates to system update section
    ...                - Checks for available updates
    ...                - Supports both French and English interfaces
        ${lang}    Get System Language       ${Device}

        IF    '${lang}' == 'fr'
            ${System}       Set Variable     Système
            ${Setting}     Set Variable     Paramètres
            ${Date}         Set Variable     Date et heure
            ${Btn_Heure}         Set Variable     Définir l'heure
            ${System_update}       Set Variable     System update
            ${System_update_check}       Set Variable     Check for update



        ELSE
            ${System}   Set Variable    System
            ${Setting}    Set Variable    Settings
            ${Date}    Set Variable     Date & time
            ${Btn_Heure}         Set Variable     Set time
            ${System_update}       Set Variable     System update
            ${System_update_check}       Set Variable     Check for update





        END


    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s


    Clique Sur Setting       ${driver}      ${System}        ${Setting_menu}
    Clique Sur Setting Include      ${driver}      ${System_update}        ${Setting_system}
    Click Element By Text       ${driver}         ${System_update_check}
