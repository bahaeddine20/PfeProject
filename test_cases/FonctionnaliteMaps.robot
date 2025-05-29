*** Settings ***
Documentation    Tests de fonctionnalité GPS pour appareil Android
...              - Vérification de la modification de position GPS
...              - Utilisation des commandes ADB pour contrôler l'émulateur

Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Library    script_mobile.py
Library    AppiumLibrary

Suite Setup     Démarrer Driver
Suite Teardown  Fermer Driver

*** Variables ***
# Configuration des retries
${MAX_RETRIES}    3
${RETRY_DELAY}    2s
${QUICK_WAIT}     0.5s

# Application Activities
${AppGrid_ACTIVITY}    com.android.car.carlauncher/.GASAppGridActivity
${Setting_ACTIVITY}    com.android.car.settings/.Settings_Launcher_Homepage
${MessageActivity}     com.android.car.messenger/.ui.launcher.MessageLauncherActivity

# UI Element IDs
${Setting_fr}          Settings
${Setting_xpath_id}    com.android.car.settings:id/car_settings_activity_wrapper
${Setting_menu}        com.android.car.settings:id/top_level_menu
${Device}              emulator-5554
${Device_mobile}       emulator-5556
${Setting_system}      com.android.car.settings:id/fragment_container
${System}              System

# GPS Configuration
${Longitude}          -74.0060
${Latitude}           40.7128

# Language Configuration
&{LANG_FR}    System=Système    Setting=Paramètres    Gps=Position    use_loc=Utiliser la localisation    acces=Accès à la position
&{LANG_EN}    System=System    Setting=Settings    Gps=Location    use_loc=Use location    acces=Location access

# New York
${New_York_Latitude}    40.7128
${New_York_Longitude}    -74.0060

# Paris
${Paris_Latitude}        48.8566
${Paris_Longitude}       2.3522

# Tokyo
${Tokyo_Latitude}        35.6895
${Tokyo_Longitude}       139.6917

@{GPS_LOCATIONS}
...    40.7128    -74.0060    # New York
...    48.8566    2.3522      # Paris
...    35.6895    139.6917    # Tokyo

*** Keywords ***
Execute Test With Retry
    [Arguments]    ${test_keyword}    ${test_name}
    ${attempt}=    Set Variable    1
    ${test_status}=    Set Variable    ${FALSE}

    FOR    ${index}    IN RANGE    ${MAX_RETRIES}
        ${test_status}=    Run Keyword And Return Status    ${test_keyword}
        IF    ${test_status}
            Log    Test ${test_name} réussi
            Exit For Loop
        ELSE
            ${attempt}=    Evaluate    ${attempt} + 1
            IF    ${attempt} <= ${MAX_RETRIES}
                Log    Test ${test_name} échoué - Tentative ${attempt}/${MAX_RETRIES}
                Sleep    ${RETRY_DELAY}
            END
        END
    END

    IF    not ${test_status}
        Fail    Le test ${test_name} a échoué après ${MAX_RETRIES} tentatives
    END

Démarrer Driver
    [Documentation]    Initializes the test driver
    ${driver}=    setup driver    ${Device}
    Set Suite Variable    ${driver}
    Initialize Language Settings

Fermer Driver
    [Documentation]    Cleans up and closes the test driver
    TRY
        ${session_active}=    Run Keyword And Return Status    Get Source
        IF    ${session_active}
            Close Driver    ${driver}
            Log    Driver fermé avec succès
        ELSE
            Log    Le driver n'était pas actif
        END
    EXCEPT    AS    ${error}
        Log    Erreur lors de la fermeture du driver: ${error}
    END

Initialize Language Settings
    [Documentation]    Sets up language-specific variables based on system language
    ${lang}=    Get System Language    ${Device}
    ${lang_dict}=    Set Variable If    '${lang}' == 'fr'    ${LANG_FR}    ${LANG_EN}
    Set Suite Variable    ${LANG_DICT}    ${lang_dict}

Get Localized Text
    [Documentation]    Gets the localized text for a given key
    [Arguments]    ${key}
    RETURN    ${LANG_DICT.${key}}

Execute Open Gps Test
    [Documentation]    Tests GPS activation
    ${resultat}=    Open Application With Click    ${driver}    ${LANG_DICT.Setting}
    Sleep    ${QUICK_WAIT}

    Clique Sur Setting Include    ${driver}    ${LANG_DICT.Gps}    ${Setting_menu}
    Clique Sur Setting Include    ${driver}    ${LANG_DICT.acces}    ${Setting_system}
    Activer Toggle Si Desactive    ${driver}    ${LANG_DICT.use_loc}

    ${verfier_gps_adb}=    Is Gps Enabled Adb    ${driver}
    Should Be True    ${verfier_gps_adb}    Le GPS ne s'active pas (via ADB)

Execute Gps Location Test
    [Documentation]    Tests GPS location functionality
    # Set GPS location
    Set Location ViaAdb    ${Device}    ${Longitude}    ${Latitude}
    Sleep    ${QUICK_WAIT}

    # Verify GPS location
    ${current_latitude}    ${current_longitude}=    Get Location ViaAdb    ${Device}
    Should Be Equal As Numbers    ${current_latitude}    ${Latitude}    La latitude n'a pas été mise à jour correctement       precision=0.0001  
    Should Be Equal As Numbers    ${current_longitude}    ${Longitude}    La longitude n'a pas été mise à jour correctement    precision=0.0001

Test GPS Location For Coordinates
    [Arguments]    ${latitude}    ${longitude}
    Set Location ViaAdb    ${Device}    ${longitude}    ${latitude}
    Sleep    2s
    ${current_latitude}    ${current_longitude}=    Get Location ViaAdb    ${Device}
    Log    Vérification: attendu ${latitude}, obtenu ${current_latitude}
    Should Be Equal As Numbers    ${current_latitude}    ${latitude}    La latitude n'a pas été mise à jour correctement    precision=0.0001
    Should Be Equal As Numbers    ${current_longitude}    ${longitude}    La longitude n'a pas été mise à jour correctement    precision=0.0001

*** Test Cases ***
Test Ouvrir Gps
    [Documentation]    Teste l'activation du GPS
    ...                - Ouvre les paramètres
    ...                - Active le GPS
    ...                - Vérifie l'activation via ADB
    [Tags]    gps    smoke
    Execute Test With Retry    Execute Open Gps Test    Test Ouvrir Gps

Test GPS Location Functionality
    [Documentation]    Teste la fonctionnalité de modification de position GPS
    ...                - Définit une position GPS spécifique via ADB
    ...                - Vérifie que la position a bien été mise à jour
    [Tags]    gps    location
    Execute Test With Retry    Execute Gps Location Test    Test GPS Location Functionality

Test GPS Multi-Location
    [Documentation]    Teste la modification de position GPS pour plusieurs emplacements
    FOR    ${lat}    ${lon}    IN    @{GPS_LOCATIONS}
        Test GPS Location For Coordinates    ${lat}    ${lon}
    END
