*** Settings ***
Documentation    Tests de fonctionnalité GPS pour appareil Android
...              - Vérification de la modification de position GPS
...              - Utilisation des commandes ADB pour contrôler l'émulateur

Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Library    script_mobile.py
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
${Device_mobile}       emulator-5554
${Setting_system}      com.android.car.settings:id/fragment_container
${System}               System
${Longitude}           -74.0060
${Latitude}            40.7128
*** Keywords ***
Démarrer Driver
    ${driver}=    setup driver    ${Device}
    Set Suite Variable    ${driver}

Fermer Driver
    Close Driver    ${driver}

*** Test Cases ***

Test Ouvrir Gps
        ${lang}    Get System Language       ${Device}

        IF    '${lang}' == 'fr'
            ${System}       Set Variable     Système
            ${Setting}     Set Variable     Paramètres
            ${Gps}         Set Variable     Position
            ${use_loc}         Set Variable     Utiliser la localisation
            ${acces}       Set Variable     Accès à la position



        ELSE
            ${System}   Set Variable    System
            ${Setting}    Set Variable    Settings
            ${Gps}         Set Variable      Position
            ${use_loc}         Set Variable     Utiliser la localisation
            ${acces}       Set Variable     Accès à la position

            ${System_update}       Set Variable     System update
            ${System_update_check}       Set Variable     Check for update





        END


    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s

    Clique Sur Setting Include      ${driver}             ${Gps}        ${Setting_menu}
    Clique Sur Setting Include   ${driver}         ${acces}        ${Setting_system}
    Activer Toggle Si Desactive      ${driver}      ${use_loc}
    ${verfier_gps_adb}=  Is Gps Enabled Adb       ${driver}
    Run Keyword And Continue On Failure     Should Be True     ${verfier_gps_adb}   Le gps ne s'active pas (via adb).

Test GPS Location Functionality
    [Documentation]    Teste la fonctionnalité de modification de position GPS
    ...                - Définit une position GPS spécifique via ADB
    ...                - Vérifie que la position a bien été mise à jour
    ...                - Tolère les échecs partiels avec continuation du test
    [Tags]    gps
    # Appeler set_location pour définir la position GPS
    Set Location ViaAdb     ${Device}    ${Longitude}    ${Latitude}

    # Attendre que la position soit définie (ajustez selon vos besoins)
    Sleep    2s

    # Vérifier si la position GPS a été mise à jour
    ${current_latitude}    ${current_longitude}       Get Location ViaAdb        ${Device}

    # Vérifier que les valeurs sont correctes
    Run Keyword And Continue On Failure     Should Be Equal As Numbers    ${current_latitude}    ${Latitude}
    Run Keyword And Continue On Failure     Should Be Equal As Numbers    ${current_longitude}    ${Longitude}
