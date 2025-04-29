*** Settings ***
Documentation    Ce fichier contient des tests d'activation et de désactivation du Bluetooth sur un appareil Android. Les tests vérifient que les paramètres Bluetooth sont accessibles et que les actions d'activation/désactivation fonctionnent correctement. Les tests prennent en charge les interfaces en français et en anglais.
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
${Device_mobile}       None

${Setting_system}      com.android.car.settings:id/fragment_container
${System}               System
${name_bluetooth_mobile}        ${null}
*** Keywords ***
Démarrer Driver
    ${driver}=    Setup Driver    ${Device}
    Set Suite Variable    ${driver}

Fermer Driver
    Run Keyword If    '${driver}' != 'None'    Close Driver    ${driver}
*** Test Cases ***

Test Ouvrir Wifi
    [Documentation]    Ce test vérifie si le Bluetooth peut être activé sur l'appareil en accédant aux paramètres.  Il vérifie que l'élément Bluetooth est bien présent, puis tente de activer Bluetooth et de vérifier son statut.

    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}       Set Variable     Système
        ${Setting}     Set Variable     Paramètres
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable     Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${ReseauMenu}         Set Variable    Réseau et Internet
    ELSE
        ${System}   Set Variable    System
        ${Setting}    Set Variable    Settings
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable      Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${confirme}         Set Variable    OK
        ${ReseauMenu}         Set Variable    Réseau et Internet

    END

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    2s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Setting n'est pas affiché.
    Clique Sur Setting       ${driver}      ${ReseauMenu}       ${Setting_menu}

    Activer Wifi Si Desactive       ${driver}
    Sleep    3s
    ${verifier_wifi_ui}=   Is Active Wifi Ui       ${driver}
    Run Keyword And Continue On Failure     Should Be True     ${verifier_wifi_ui}   Le Wifi ne s'active pas (ui).
    ${verfier_wifi_adb}=  Is Wifi Enabled Adb       ${driver}
    Run Keyword And Continue On Failure     Should Be True     ${verfier_wifi_adb}   Le Wifi ne s'active pas (via adb).




Test Fermer Wifi
    [Documentation]    Ce test vérifie si le Bluetooth peut être activé sur l'appareil en accédant aux paramètres.  Il vérifie que l'élément Bluetooth est bien présent, puis tente de activer Bluetooth et de vérifier son statut.

    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}       Set Variable     Système
        ${Setting}     Set Variable     Paramètres
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable     Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${ReseauMenu}         Set Variable    Réseau et Internet
    ELSE
        ${System}   Set Variable    System
        ${Setting}    Set Variable    Settings
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable      Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${confirme}         Set Variable    OK
        ${ReseauMenu}         Set Variable    Réseau et Internet

    END

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    2s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Setting n'est pas affiché.
    Clique Sur Setting       ${driver}      ${ReseauMenu}       ${Setting_menu}

    Desactiver Wifi Si Active       ${driver}
    Sleep    3s
    ${verifier_wifi_ui}=   Is Active Wifi Ui       ${driver}
    Run Keyword And Continue On Failure         Should Not Be True     ${verifier_wifi_ui}   Le Wifi ne s'active pas (ui).
    ${verfier_wifi_adb}=  Is Wifi Enabled Adb       ${driver}
    Run Keyword And Continue On Failure         Should Not Be True     ${verfier_wifi_adb}   Le Wifi ne s'active pas (via adb).

