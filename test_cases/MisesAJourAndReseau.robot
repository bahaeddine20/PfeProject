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
# Configuration des retries
${MAX_RETRIES}    3
${RETRY_DELAY}    2s
${QUICK_WAIT}     0.5s

# Language Configuration
&{LANG_FR}    System=Système    Setting=Paramètres    System_update=Mise à jour du système    System_update_check=Rechercher les mises à jour
&{LANG_EN}    System=System    Setting=Settings    System_update=System update    System_update_check=Check for update

*** Keywords ***
Démarrer Driver
    ${driver}=    setup driver    ${Device}
    Set Suite Variable    ${driver}

Fermer Driver
    Close Driver    ${driver}

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

Initialize Language Settings
    ${lang}=    Get System Language    ${Device}
    ${lang_dict}=    Set Variable If    '${lang}' == 'fr'    ${LANG_FR}    ${LANG_EN}
    Set Suite Variable    ${LANG_DICT}    ${lang_dict}

Get Localized Text
    [Arguments]    ${key}
    RETURN    ${LANG_DICT.${key}}

Aller Dans Paramètres
    ${setting}=    Get Localized Text    Setting
    Open Application With Click    ${driver}    ${setting}
    Clique Sur Setting    ${driver}    ${System}    ${Setting_menu}

Aller Dans Mise A Jour
    ${system}=    Get Localized Text    System
    Clique Sur Setting    ${driver}    ${system}    ${Setting_menu}
    ${system_update}=    Get Localized Text    System_update
    Clique Sur Setting Include    ${driver}    ${system_update}    ${Setting_system}

Lancer Recherche Mise A Jour
    ${system_update_check}=    Get Localized Text    System_update_check
    Click Element By Text    ${driver}    ${system_update_check}

Vérifier Mise A Jour System
    Initialize Language Settings
    Aller Dans Paramètres
    Aller Dans Mise A Jour
    Lancer Recherche Mise A Jour

*** Test Cases ***
Test Verfier Mise A Jour System
    [Documentation]    Verifies system update functionality
    ...                - Navigates to system update section
    ...                - Checks for available updates
    ...                - Supports both French and English interfaces
    [Tags]    update    system
    Execute Test With Retry    Vérifier Mise A Jour System    Test Verfier Mise A Jour System
