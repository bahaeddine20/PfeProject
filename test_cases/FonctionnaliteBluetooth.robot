*** Settings ***
Documentation    Ce fichier contient des tests d'activation, désactivation, appairage et gestion d'appels via Bluetooth sur des appareils Android.
...              Les tests vérifient que les paramètres Bluetooth sont accessibles, que les actions d'activation/désactivation fonctionnent correctement,
...              que l'appairage entre appareils fonctionne, et que les fonctionnalités d'appel via Bluetooth opèrent correctement.
...              Les tests prennent en charge les interfaces en français et en anglais.Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Library    script_mobile.py
Library    script_IA.py
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
${name_bluetooth_mobile}        ${null}
*** Keywords ***

Démarrer Driver
    ${driver}=    Setup Driver    ${Device}
    Log    Driver for ${Device}: ${driver}
    ${driver_mobile}=    Setup Driver Mobile    ${Device_mobile}

    Set Suite Variable    ${driver}
    Set Suite Variable    ${driver_mobile}

Fermer Driver
    Close Driver    ${driver}
    Close Driver   ${driver_mobile}


*** Test Cases ***

Test Ouvrir Bluetooth
    [Documentation]    Teste l'activation du Bluetooth sur l'appareil principal
    ...                - Vérifie la langue du système
    ...                - Ouvre les paramètres
    ...                - Accède aux paramètres Bluetooth
    ...                - Active le Bluetooth s'il est désactivé
    ...                - Vérifie que le Bluetooth est bien activé (UI et ADB)

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
    [Documentation]    Teste l'appairage Bluetooth entre les deux appareils
    ...                - Vérifie la langue du système
    ...                - Ouvre les paramètres Bluetooth
    ...                - Récupère le nom Bluetooth du mobile
    ...                - Vérifie si l'appairage existe déjà
    ...                - Si non, initie le processus d'appairage
    ...                - Valide l'appairage des deux côtés
    ...                - Vérifie que l'appairage est effectif via ADB

    ${lang}=    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=      Set Variable    Système
        ${Setting}=     Set Variable    Paramètres
        ${apps}=        Set Variable    Applis
        ${Consulter_allapps}=    Set Variable    Voir les
        ${DesButton}=   Set Variable    Désinstaller
        ${confirme}=    Set Variable    OK
        ${pairing}=     Set Variable    Associer un nouvel appareil
        ${pairing_conf}=    Set Variable    Associer
        ${pairing_conf2}=   Set Variable    Continuer
    ELSE
        ${System}=      Set Variable    System
        ${Setting}=     Set Variable    Settings
        ${apps}=        Set Variable    Apps
        ${Consulter_allapps}=    Set Variable    See all
        ${DesButton}=   Set Variable    Uninstall
        ${confirme}=    Set Variable    OK
        ${pairing}=     Set Variable    Pair new device
        ${pairing_conf}=    Set Variable    Pair
        ${pairing_conf2}=   Set Variable    Continue
    END

    ${resultat}=    Open Application With Click      ${driver}    ${Setting}
    Clique Sur Setting       ${driver}      Bluetooth       ${Setting_menu}

    ${name_bluetooth_mobile}=    Get Bluetooth Name    ${driver_mobile}
    Log    ${name_bluetooth_mobile}

    ${verif_adb}=    Is Bluetooth Connected    ${driver}    ${name_bluetooth_mobile}

    IF    not ${verif_adb}
        Press Key    ${driver_mobile}    4
        Press Key    ${driver_mobile}    176

        Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver_mobile}    Bluetooth, pairing
        Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver}    ${pairing}
        Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver}    ${name_bluetooth_mobile}
        Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver_mobile}    Pair
        Wait Until Keyword Succeeds    10s    2s    Click Element By Text Att    ${driver}    ${pairing_conf}
        Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver_mobile}    Allow
        Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver}    ${pairing_conf2}
    END

    ${verif_adb}=    Is Bluetooth Connected    ${driver}    ${name_bluetooth_mobile}
    Should Be True    ${verif_adb}    Le Bluetooth n'est pas connecté (via ADB).


Test Call Bluetooth
    [Documentation]    Teste la réception d'un appel via Bluetooth
    ...                - Simule un appel entrant sur le mobile
    ...                - Vérifie que le numéro appelant est affiché à l'écran
    ...                - Continue l'exécution même en cas d'échec partiel
    ${call}=    Run Keyword And Continue On Failure       Simulate Incoming Call    ${driver_mobile}    52440030
    Sleep    5s
    ${bounds}=    Run Keyword And Continue On Failure        Wait Until Keyword Succeeds    30s    2s    Get Text Bounds Driver    ${driver_mobile}    52440030
    Run Keyword And Continue On Failure     Log    ${bounds}
    Run Keyword And Continue On Failure     Should Not Be Equal    ${bounds}    ${None}    Le numéro 52440030 n'a pas été trouvé à l'écran


Test Answer Call Bluetooth
    [Documentation]    Teste la réponse à un appel via Bluetooth
    ...                - Localise et clique sur le bouton "Répondre"
    ...                - Vérifie que l'interface d'appel est active
    ...                - Continue l'exécution même en cas d'échec partiel

        ${lang}=    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${answer}=      Set Variable    Répondre
        ${Setting}=     Set Variable    Paramètres
    ELSE
        ${answer}=      Set Variable    Answer
        ${Setting}=     Set Variable    Settings

    END

    ${bounds}=      Run Keyword          Wait Until Keyword Succeeds    30s    2s    Get Text Bounds Driver    ${driver_mobile}     ${answer}
    Log    ${bounds}
    Run Keyword      Click Sur Bound    ${driver_mobile}    ${bounds}
    Sleep       3s
    ${Verifcall}=       Run Keyword And Continue On Failure          Wait Until Keyword Succeeds    30s    2s       Find Icon Position      ${driver}           callsAnswer
    Run Keyword And Continue On Failure   Should Not Be Equal    ${Verifcall}    ${None}       problem lors de repondre

Test End Call Bluetooth
    [Documentation]    Teste la fin d'un appel via Bluetooth
    ...                - Ouvre l'application téléphone
    ...                - Localise et clique sur le bouton "Terminer l'appel"
    ...                - Continue l'exécution même en cas d'échec partiel


    ${lang}=    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${phone}=       Set Variable     Téléphone
        ${Setting}=     Set Variable    Paramètres
    ELSE
        ${phone}=       Set Variable    Phone
        ${Setting}=     Set Variable    Settings

    END

    ${resultat}=        Run Keyword         Open Application With Click      ${driver}          ${phone}
    Sleep       3s
    ${Verifcall}=       Run Keyword         Wait Until Keyword Succeeds    30s    2s       Click Icon Ia    ${driver}       endcall




Test Supprimer Bluetooth
    [Documentation]    Teste la suppression de l'appairage Bluetooth
    ...                - Vérifie la langue du système
    ...                - Ouvre les paramètres Bluetooth
    ...                - Récupère le nom Bluetooth du mobile
    ...                - Supprime l'appareil appairé
    ...                - Vérifie que l'appairage n'est plus actif via ADB
    ...                - Continue l'exécution même en cas d'échec partiel

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
        ${supp}        Set Variable       Supprimer

    ELSE
        ${System}   Set Variable    System
        ${Setting}    Set Variable    Settings
        ${apps}         Set Variable     Applis
        ${Consulter_allapps}         Set Variable      Voir les
        ${DesButton}        Set Variable    Désinstaller
        ${confirme}         Set Variable    OK
        ${pairing}        Set Variable       Pair new device
        ${pairing_conf}        Set Variable       Pair
        ${pairing_conf2}        Set Variable       Continue
        ${supp}        Set Variable       Forget


    END
        ${resultat}=        Run Keyword And Continue On Failure    Open Application With Click      ${driver}        ${Setting}

        Clique Sur Setting       ${driver}      Bluetooth       ${Setting_menu}

        ${name_bluetooth_mobile} =      Get Bluetooth Name      ${driver_mobile}
        Log   ${name_bluetooth_mobile}
        Press Key    ${driver_mobile}    4

        Press Key    ${driver_mobile}    176
        Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver_mobile}     Bluetooth, pairing

        Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver}      ${name_bluetooth_mobile}
        Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver}      ${supp}



        ${verif_adb}=        Is Bluetooth Connected   ${driver}      ${name_bluetooth_mobile}

        Run Keyword And Continue On Failure         Should Not Be True     ${verif_adb}   Le Bluetooth n'est pas connecté (via ADB).






Test Fermer Bluetooth

    [Documentation]    Teste la désactivation du Bluetooth sur l'appareil principal
    ...                - Vérifie la langue du système
    ...                - Ouvre les paramètres
    ...                - Accède aux paramètres Bluetooth
    ...                - Désactive le Bluetooth s'il est activé
    ...                - Vérifie que le Bluetooth est bien désactivé (UI et ADB)

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


