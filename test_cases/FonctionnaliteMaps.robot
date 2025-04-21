*** Settings ***
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
${Device}              emulator-5554
${Device_mobile}       emulator-5556
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
Test GPS Location Functionality
    [Documentation]    Ce test définit la localisation GPS et vérifie qu'elle est correcte.
    [Tags]    gps
    # Appeler set_location pour définir la position GPS
    Set Location ViaAdb     ${Device}    ${Longitude}    ${Latitude}

    # Attendre que la position soit définie (ajustez selon vos besoins)
    Sleep    2s

    # Vérifier si la position GPS a été mise à jour
    ${current_latitude}    ${current_longitude}       Get Location ViaAdb        ${Device}

    # Vérifier que les valeurs sont correctes
    Should Be Equal As Numbers    ${current_latitude}    ${Latitude}
    Should Be Equal As Numbers    ${current_longitude}    ${Longitude}
