*** Settings ***
Documentation    Ce fichier contient des tests d'activation et de désactivation du Bluetooth sur un appareil Android. Les tests vérifient que les paramètres Bluetooth sont accessibles et que les actions d'activation/désactivation fonctionnent correctement. Les tests prennent en charge les interfaces en français et en anglais.
Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Library    script_mobile.py


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

*** Test Cases ***

Test Ouvrir Bluetooth
    [Documentation]    Ce test vérifie si le Bluetooth peut être activé sur l'appareil en accédant aux paramètres.  Il vérifie que l'élément Bluetooth est bien présent, puis tente de activer Bluetooth et de vérifier son statut.
    ${driver}    setup driver       ${Device}
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
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable      Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${confirme}         Set Variable    OK
    END

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    2s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Setting n'est pas affiché.
    Clique Sur Setting       ${driver}      Bluetooth       ${Setting_menu}
    ${ble}=  Element Existe Par Accessibility Id       ${driver}     Bluetooth toggle switch
    Should Be True    ${ble}    Les paramètres de Bluetooth ne s'affichent pas.
    Activer Bluetooth Si Desactive       ${driver}     android:id/switch_widget
    Sleep    3s
    ${verifier_ble_ui}=   Verfier Bluetooth Activer       ${driver}     android:id/switch_widget
    Should Be True     ${verifier_ble_ui}   Le Bluetooth ne s'active pas (ui).
    ${verfier_ble_adb}=  Est Bluetooth Active       ${Device}
    Should Be True     ${verfier_ble_adb}   Le Bluetooth ne s'active pas (via adb).


Test Pairing Bluetooth
        ${driver}    setup driver       ${Device}
        ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}       Set Variable     Système
        ${Setting}     Set Variable     Paramètres
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable     Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${confirme}         Set Variable    OK
        ${pairing}        Set Variable       Associer un nouvel appareil
        ${pairing_conf}        Set Variable       Associer
        ${pairing_conf2}        Set Variable       Continuer

    ELSE
        ${System}   Set Variable    System
        ${Setting}    Set Variable    Settings
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable      Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${confirme}         Set Variable    OK
        ${pairing}        Set Variable       Associer un nouvel appareil
        ${pairing_conf}        Set Variable       Associer
        ${pairing_conf2}        Set Variable       Continuer


    END
        ${driver_mobile}    setup driver Mobile      ${Device_mobile}

        ${name_bluetooth_mobile} =      Get Bluetooth Name      ${driver_mobile}
        Log   ${name_bluetooth_mobile}
        Press Key    ${driver_mobile}    176
        Click Element By Text Att    ${driver_mobile}     Bluetooth, pairing

        Sleep    2s
        Click Element By Text Att     ${driver}      ${pairing}
        Sleep    4s
        Click Element By Text Att     ${driver}      ${name_bluetooth_mobile}
        Sleep    2s
        Click Element By Text Att    ${driver_mobile}     Pair
        Click Element By Text Att     ${driver}      ${pairing_conf}
        Sleep    2s
        Click Element By Text Att     ${driver_mobile}      Allow
        Click Element By Text Att     ${driver}      ${pairing_conf2}
        Sleep    2s
        ${verif_adb}=        Is Bluetooth Connected   ${driver}      ${name_bluetooth_mobile}

        Should Be True     ${verif_adb}   Le Bluetooth n'est pas connecté (via ADB).









Test Fermer Bluetooth
    [Documentation]    Ce test vérifie si le Bluetooth peut être désactivé sur l'appareil en accédant aux paramètres.  Il vérifie que l'élément Bluetooth est bien présent, puis tente de désactiver Bluetooth et de vérifier son statut.
    ${driver}    setup driver       ${Device}
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
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable      Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${confirme}         Set Variable    OK
    END

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    2s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Setting n'est pas affiché.
    Clique Sur Setting       ${driver}      Bluetooth       ${Setting_menu}
    ${ble}=  Element Existe Par Accessibility Id       ${driver}     Bluetooth toggle switch
    Should Be True    ${ble}    Les paramètres de Bluetooth ne s'affichent pas.
    Desactive Bluetooth Si Activer       ${driver}     android:id/switch_widget
    Sleep    3s
    ${verifier_ble_ui}=   Verfier Bluetooth Activer       ${driver}     android:id/switch_widget
    Should Not Be True     ${verifier_ble_ui}   Le Bluetooth ne desactive pas (ui).
    ${verfier_ble_adb}=  Est Bluetooth Active       ${Device}
    Should Not Be True     ${verfier_ble_adb}   Le Bluetooth ne desactive pas (via adb).
