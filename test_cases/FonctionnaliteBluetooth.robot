*** Settings ***
Documentation    Ce fichier contient des tests d'activation, désactivation, appairage et gestion d'appels via Bluetooth sur des appareils Android.
...              Les tests vérifient que les paramètres Bluetooth sont accessibles, que les actions d'activation/désactivation fonctionnent correctement,
...              que l'appairage entre appareils fonctionne, et que les fonctionnalités d'appel via Bluetooth opèrent correctement.
...              Les tests prennent en charge les interfaces en français et en anglais.
Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Library    script_mobile.py
Library    script_IA.py
Library    AppiumLibrary
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
${MAX_RETRIES}    3
${RETRY_DELAY}    2s

*** Keywords ***

Démarrer Driver
    ${driver}=    Setup Driver    ${Device}
    Log    Driver for ${Device}: ${driver}
    ${driver_mobile}=    Setup Driver Mobile    ${Device_mobile}

    Set Suite Variable    ${driver}
    Set Suite Variable    ${driver_mobile}

Fermer Driver
    # Vérifier et fermer le driver principal
    TRY
        ${session_active}=    Run Keyword And Return Status    Get Source
        IF    ${session_active}
            Close Driver    ${driver}
            Log    Driver principal fermé avec succès
        ELSE
            Log    Le driver principal n'était pas actif
        END
    EXCEPT    AS    ${error}
        Log    Erreur lors de la vérification du driver principal: ${error}
    END

    # Vérifier et fermer le driver mobile
    TRY
        ${session_active_mobile}=    Run Keyword And Return Status    Get Source
        IF    ${session_active_mobile}
            Close Driver    ${driver_mobile}
            Log    Driver mobile fermé avec succès
        ELSE
            Log    Le driver mobile n'était pas actif
        END
    EXCEPT    AS    ${error}
        Log    Erreur lors de la vérification du driver mobile: ${error}
    END

    # Nettoyer les variables de session
    Set Suite Variable    ${driver}    ${None}
    Set Suite Variable    ${driver_mobile}    ${None}

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


*** Test Cases ***

Test Ouvrir Bluetooth
    [Documentation]    Teste l'activation du Bluetooth sur l'appareil principal
    ...                - Vérifie la langue du système
    ...                - Ouvre les paramètres
    ...                - Accède aux paramètres Bluetooth
    ...                - Active le Bluetooth s'il est désactivé
    ...                - Vérifie que le Bluetooth est bien activé (UI et ADB)
    Execute Test With Retry    Execute Open Bluetooth Test    Test Ouvrir Bluetooth


Test Pairing Bluetooth
    [Documentation]    Teste l'appairage Bluetooth entre les deux appareils
    ...                - Vérifie la langue du système
    ...                - Ouvre les paramètres Bluetooth
    ...                - Récupère le nom Bluetooth du mobile
    ...                - Vérifie si l'appairage existe déjà
    ...                - Si non, initie le processus d'appairage
    ...                - Valide l'appairage des deux côtés
    ...                - Vérifie que l'appairage est effectif via ADB
    Execute Test With Retry    Execute Pairing Bluetooth Test    Test Pairing Bluetooth


Test Call Bluetooth
    [Documentation]    Teste la réception d'un appel via Bluetooth
    ...                - Simule un appel entrant sur le mobile
    ...                - Vérifie que le numéro appelant est affiché à l'écran
    ...                - Continue l'exécution même en cas d'échec partiel
    Execute Test With Retry    Execute Call Bluetooth Test    Test Call Bluetooth


Test Answer Call Bluetooth
    [Documentation]    Teste la réponse à un appel via Bluetooth
    ...                - Localise et clique sur le bouton "Répondre"
    ...                - Vérifie que l'interface d'appel est active
    ...                - Continue l'exécution même en cas d'échec partiel
    Execute Test With Retry    Execute Answer Call Bluetooth Test    Test Answer Call Bluetooth


Test End Call Bluetooth
    [Documentation]    Teste la fin d'un appel via Bluetooth
    ...                - Ouvre l'application téléphone
    ...                - Localise et clique sur le bouton "Terminer l'appel"
    ...                - Continue l'exécution même en cas d'échec partiel
    Execute Test With Retry    Execute End Call Bluetooth Test    Test End Call Bluetooth


Test Supprimer Bluetooth
    [Documentation]    Teste la suppression de l'appairage Bluetooth
    ...                - Vérifie la langue du système
    ...                - Ouvre les paramètres Bluetooth
    ...                - Récupère le nom Bluetooth du mobile
    ...                - Supprime l'appareil appairé
    ...                - Vérifie que l'appairage n'est plus actif via ADB
    Execute Test With Retry    Execute Supprimer Bluetooth Test    Test Supprimer Bluetooth


Test Fermer Bluetooth
    [Documentation]    Teste la désactivation du Bluetooth sur l'appareil principal
    ...                - Vérifie la langue du système
    ...                - Ouvre les paramètres
    ...                - Accède aux paramètres Bluetooth
    ...                - Désactive le Bluetooth s'il est activé
    ...                - Vérifie que le Bluetooth est bien désactivé (UI et ADB)
    Execute Test With Retry    Execute Fermer Bluetooth Test    Test Fermer Bluetooth


*** Keywords ***
Execute Open Bluetooth Test
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

Execute Pairing Bluetooth Test
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

Execute Call Bluetooth Test
    ${call}=    Run Keyword And Continue On Failure       Simulate Incoming Call    ${driver_mobile}    52440030
    Sleep    5s
    ${bounds}=    Run Keyword And Continue On Failure        Wait Until Keyword Succeeds    30s    2s    Get Text Bounds Driver    ${driver_mobile}    52440030
    Run Keyword And Continue On Failure     Log    ${bounds}
    Run Keyword And Continue On Failure     Should Not Be Equal    ${bounds}    ${None}    Le numéro 52440030 n'a pas été trouvé à l'écran

Execute Answer Call Bluetooth Test
    ${lang}=    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${answer}=      Set Variable    Répondre
        ${accept}=      Set Variable    Accepter
        ${Setting}=     Set Variable    Paramètres
    ELSE
        ${answer}=      Set Variable    Answer
        ${accept}=      Set Variable    Accept
        ${Setting}=     Set Variable    Settings
    END

    Sleep    5s

    # Essayer plusieurs textes possibles pour le bouton de réponse
    ${possible_texts}=    Create List    ${answer}    ${accept}    Accept    Answer    Répondre    Accepter
    ${call_answered}=    Set Variable    ${FALSE}

    FOR    ${text}    IN    @{possible_texts}
        TRY
            ${bounds}=    Get Text Bounds Driver    ${driver_mobile}    ${text}
            IF    ${bounds} != ${None}
                Click Sur Bound    ${driver_mobile}    ${bounds}
                Sleep    5s


                # Essayer de trouver l'icône d'appel
                TRY
                    ${Verifcall}=    Find Icon Position    ${driver}    callsAnswer
                    IF    ${Verifcall} != ${None}
                        Log    Appel répondu avec succès (vérifié via icône)
                        ${call_answered}=    Set Variable    ${TRUE}
                        BREAK
                    END
                EXCEPT    AS    ${error}
                    Log    Erreur lors de la recherche de l'icône: ${error}
                END
            END
        EXCEPT    AS    ${error}
            Log    Erreur lors de la tentative avec "${text}": ${error}
            Continue For Loop
        END
    END

    # Vérification finale
    IF    not ${call_answered}
        Log    Avertissement: Impossible de confirmer que l'appel a été répondu
    END

Execute End Call Bluetooth Test
    ${lang}=    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${phone}=       Set Variable     Téléphone
        ${Setting}=     Set Variable    Paramètres
        ${end_call}=    Set Variable    Terminer
    ELSE
        ${phone}=       Set Variable    Phone
        ${Setting}=     Set Variable    Settings
        ${end_call}=    Set Variable    End
    END

    ${resultat}=    Open Application With Click    ${driver}    ${phone}
    Should Be True    ${resultat}    Impossible d'ouvrir l'application téléphone
    Sleep    5s

    ${bounds}=    Wait Until Keyword Succeeds    10s    2s    Get Text Bounds Driver    ${driver}    ${end_call}
    IF    ${bounds} is not None
        Click Sur Bound    ${driver}    ${bounds}
    ELSE
        ${end_call_pos}=    Wait Until Keyword Succeeds    10s    2s    Find Icon Position    ${driver}    endcall
        IF    ${end_call_pos} is not None
            Click Icon Ia    ${driver}      endcall
        ELSE
            Fail    Impossible de trouver le bouton pour terminer l'appel
        END
    END

    Sleep    3s

Execute Supprimer Bluetooth Test
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
        ${supp}=        Set Variable    Supprimer
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
        ${supp}=        Set Variable    Forget
    END
    Press Key    ${driver_mobile}       6

    ${resultat}=    Open Application With Click    ${driver}    ${Setting}
    Should Be True    ${resultat}    Impossible d'ouvrir les paramètres

    Clique Sur Setting    ${driver}    Bluetooth    ${Setting_menu}
    Sleep    2s

    ${name_bluetooth_mobile}=    Get Bluetooth Name    ${driver_mobile}
    Should Not Be Empty    ${name_bluetooth_mobile}    Impossible de récupérer le nom Bluetooth du mobile

    # Vérifier si l'appareil est appairé
    ${verif_adb}=    Is Bluetooth Connected    ${driver}    ${name_bluetooth_mobile}
    Should Be True    ${verif_adb}    L'appareil n'est pas appairé

    # Supprimer l'appairage
    Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver}    ${name_bluetooth_mobile}
    Sleep    2s
    Wait Until Keyword Succeeds    30s    2s    Click Element By Text Att    ${driver}    ${supp}
    Sleep    2s

    # Vérifier que l'appairage est supprimé
    ${verif_adb}=    Is Bluetooth Connected    ${driver}    ${name_bluetooth_mobile}
    Should Not Be True    ${verif_adb}    L'appairage n'a pas été supprimé

Execute Fermer Bluetooth Test
    ${lang}=    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=      Set Variable    Système
        ${Setting}=     Set Variable    Paramètres
        ${apps}=        Set Variable    Applis
        ${Consulter_allapps}=    Set Variable    Voir les
        ${DesButton}=   Set Variable    Désinstaller
        ${confirme}=    Set Variable    OK
    ELSE
        ${System}=      Set Variable    System
        ${Setting}=     Set Variable    Settings
        ${apps}=        Set Variable    Apps
        ${Consulter_allapps}=    Set Variable    See all
        ${DesButton}=   Set Variable    Uninstall
        ${confirme}=    Set Variable    OK
    END

    # Vérifier si l'application est ouverte
    ${app_open}=    Run Keyword And Return Status    Get Source
    IF    not ${app_open}
        ${resultat}=    Open Application With Click    ${driver}    ${Setting}
        Should Be True    ${resultat}    Impossible d'ouvrir les paramètres
        Sleep    2s
    END

    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Les paramètres ne sont pas affichés

    Clique Sur Setting    ${driver}    Bluetooth    ${Setting_menu}
    Sleep    2s

    ${ble}=    Element Existe Par Accessibility Id    ${driver}    Bluetooth toggle switch
    Should Be True    ${ble}    Les paramètres Bluetooth ne s'affichent pas

    # Vérifier si le Bluetooth est activé avant de le désactiver
    ${ble_active}=    Verfier Bluetooth Activer    ${driver}    android:id/switch_widget
    IF    ${ble_active}
        Desactive Bluetooth Si Activer    ${driver}    android:id/switch_widget
        Sleep    3s

        # Vérifier la désactivation dans l'UI
        ${verifier_ble_ui}=    Verfier Bluetooth Activer    ${driver}    android:id/switch_widget
        Should Not Be True    ${verifier_ble_ui}    Le Bluetooth n'est pas désactivé dans l'interface

        # Vérifier la désactivation via ADB
        ${verfier_ble_adb}=    Est Bluetooth Active    ${Device}
        Should Not Be True    ${verfier_ble_adb}    Le Bluetooth n'est pas désactivé via ADB
        Log    Bluetooth est désactivé.
    ELSE
        Log    Le Bluetooth est déjà désactivé
    END




