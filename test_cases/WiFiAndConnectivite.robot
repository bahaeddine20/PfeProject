*** Settings ***
Documentation    Tests de connectivité WiFi pour appareil Android
...              - Activation du WiFi
...              - Désactivation du WiFi
...              - Vérification de l'état via UI et ADB
...              - Prend en charge les interfaces en français et en anglais
Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Library    script_mobile.py
Library    AppiumLibrary


Suite Setup     Démarrer Driver
Suite Teardown  Fermer Driver

*** Variables ***
# Configuration des retries et timing
${MAX_RETRIES}        3
${RETRY_DELAY}        2s
${QUICK_WAIT}         0.5s
${WAIT_TIME}          2s

# Application Activities
${AppGrid_ACTIVITY}    com.android.car.carlauncher/.GASAppGridActivity
${Setting_ACTIVITY}    com.android.car.settings/.Settings_Launcher_Homepage
${MessageActivity}     com.android.car.messenger/.ui.launcher.MessageLauncherActivity

# UI Element IDs
${Setting_xpath_id}    com.android.car.settings:id/car_settings_activity_wrapper
${Setting_menu}        com.android.car.settings:id/top_level_menu
${Device}              emulator-5554
${Device_mobile}       emulator-5556
${Setting_system}      com.android.car.settings:id/fragment_container

# Language Configuration
&{LANG_FR}    System=Système    Setting=Paramètres    ReseauMenu=Réseau et Internet
&{LANG_EN}    System=System    Setting=Settings    ReseauMenu=Network & internet

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
    ${driver}=    Setup Driver    ${Device}
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

Execute Open Wifi Test
    [Documentation]    Tests WiFi activation
    # Navigate to settings
    ${resultat}=    Open Application With Click    ${driver}    ${LANG_DICT.Setting}
    Sleep    ${QUICK_WAIT}

    # Verify settings screen
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Settings screen is not displayed

    # Navigate to network settings
    Clique Sur Setting    ${driver}    ${LANG_DICT.ReseauMenu}    ${Setting_menu}

    # Activate WiFi
    Activer Wifi Si Desactive    ${driver}
    Sleep    ${WAIT_TIME}

    # Verify WiFi activation
    ${verifier_wifi_ui}=    Is Active Wifi Ui    ${driver}
    Run Keyword And Continue On Failure         Should Be True    ${verifier_wifi_ui}    WiFi is not active in UI
    ${verfier_wifi_adb}=    Is Wifi Enabled Adb    ${driver}
    Run Keyword And Continue On Failure         Should Be True    ${verfier_wifi_adb}    WiFi is not active via ADB

Execute Close Wifi Test
    [Documentation]    Tests WiFi deactivation
    # Navigate to settings
    ${resultat}=    Open Application With Click    ${driver}    ${LANG_DICT.Setting}
    Sleep    ${QUICK_WAIT}

    # Verify settings screen
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Settings screen is not displayed

    # Navigate to network settings
    Clique Sur Setting    ${driver}    ${LANG_DICT.ReseauMenu}    ${Setting_menu}

    # Deactivate WiFi
    Desactiver Wifi Si Active    ${driver}
    Sleep    ${WAIT_TIME}

    # Verify WiFi deactivation
    ${verifier_wifi_ui}=    Is Active Wifi Ui    ${driver}
    Should Not Be True    ${verifier_wifi_ui}    WiFi is still active in UI
    ${verfier_wifi_adb}=    Is Wifi Enabled Adb    ${driver}
    Should Not Be True    ${verfier_wifi_adb}    WiFi is still active via ADB

*** Test Cases ***
Test Ouvrir Wifi
    [Documentation]    Teste l'activation du WiFi
    ...                - Ouvre les paramètres
    ...                - Active le WiFi
    ...                - Vérifie l'activation via UI et ADB
    [Tags]    wifi    smoke
    Execute Test With Retry    Execute Open Wifi Test    Test Ouvrir Wifi

Test Fermer Wifi
    [Documentation]    Teste la désactivation du WiFi
    ...                - Ouvre les paramètres
    ...                - Désactive le WiFi
    ...                - Vérifie la désactivation via UI et ADB
    [Tags]    wifi    smoke
    Execute Test With Retry    Execute Close Wifi Test    Test Fermer Wifi

