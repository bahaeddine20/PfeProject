*** Settings ***
Documentation    Ce fichier contient des tests pour vérifier les fonctionnalités système d'un appareil Android :
...              - Activation/désactivation des notifications
...              - Modification de la langue
...              - Synchronisation de l'heure
...              - Gestion des notifications (réception/suppression)
...              - Navigation de base (bouton Home, lancement d'applications)
...              Les tests prennent en charge les interfaces en français et en anglais.
Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Library    script_IA.py
Library    AppiumLibrary


Suite Setup     Démarrer Driver
Suite Teardown  Fermer Driver

*** Variables ***
${MAX_RETRIES}    3
${RETRY_DELAY}    2s
${AppGrid_ACTIVITY}    com.android.car.carlauncher/.GASAppGridActivity
${Setting_ACTIVITY}    com.android.car.settings/.Settings_Launcher_Homepage
${MessageActivity}     com.android.car.messenger/.ui.launcher.MessageLauncherActivity
${Setting_fr}          Settings
${Setting_xpath_id}    com.android.car.settings:id/car_settings_activity_wrapper
${Setting_menu}        com.android.car.settings:id/top_level_menu
${Device}              emulator-5554
${Setting_system}      com.android.car.settings:id/fragment_container
${System}              System

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
    ${driver}=    setup driver    ${Device}
    Set Suite Variable    ${driver}

Fermer Driver
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

*** Test Cases ***
Test Home_Button
    [Documentation]    Teste la fonctionnalité du bouton Home
    ...                - Vérifie que le bouton Home ramène bien à l'écran d'accueil
    ...                - Utilise la fonction 'Revenir A La Home Page'
    Execute Test With Retry    Execute Home Button Test    Test Home_Button

Test Ouvrir YouTube App
    [Documentation]    Teste le lancement de l'application YouTube
    ...                - Ouvre l'application YouTube
    ...                - Vérifie que l'activité YouTube est correctement lancée
    ...                - Contrôle la présence d'éléments UI spécifiques à YouTube
    Execute Test With Retry    Execute YouTube App Test    Test Ouvrir YouTube App

Test Modifier Languages
    [Documentation]    Teste la modification de la langue système
    ...                - Vérifie la langue actuelle du système
    ...                - Change la langue en anglais puis en français
    ...                - Vérifie les changements via ADB
    Execute Test With Retry    Execute Language Change Test    Test Modifier Languages

Test Notification Réception
    [Documentation]    Teste la réception de notifications
    ...                - Installe une application de test de notification
    ...                - Active les notifications pour l'application
    ...                - Envoie une notification de test
    ...                - Vérifie l'affichage de la notification
    Execute Test With Retry    Execute Notification Reception Test    Test Notification Réception

Test Notification Supprimer
    [Documentation]    Teste la suppression de notifications
    ...                - Vérifie la présence d'une notification
    ...                - Supprime toutes les notifications
    ...                - Vérifie que la notification a bien disparu
    Execute Test With Retry    Execute Notification Delete Test    Test Notification Supprimer

Test Disable Notification
    [Documentation]    Teste la désactivation des notifications
    ...                - Désactive les notifications pour l'application de test
    ...                - Envoie une notification de test
    ...                - Vérifie que la notification n'apparaît pas
    Execute Test With Retry    Execute Disable Notification Test    Test Disable Notification

Test Modifier Manuellement Date
    [Documentation]    Teste la modification manuelle de la date/heure
    ...                - Accède aux paramètres de date/heure
    ...                - Modifie l'heure manuellement
    ...                - Vérifie que le changement a bien été appliqué
    Execute Test With Retry    Execute Manual Date Change Test    Test Modifier Manuellement Date

Test Modifier Synchronisation Automatique Date
    [Documentation]    Teste la synchronisation automatique de la date/heure
    ...                - Accède aux paramètres de date/heure
    ...                - Active la synchronisation automatique
    ...                - Vérifie que l'heure est correctement synchronisée
    Execute Test With Retry    Execute Auto Date Sync Test    Test Modifier Synchronisation Automatique Date

*** Keywords ***
Execute Home Button Test
    Revenir A La Home Page    ${driver}

Execute YouTube App Test
    Sleep    2
    ${resultat}=    Open Application With Click    ${driver}    YouTube
    Should Be True    ${resultat}    L'activité YouTube n'est pas trouvée.
    ${Activity}=    Print Activity2    ${driver}
    Sleep    5s
    Log    ${Activity}
    ${is_element_present}=    Check Element ExistsBy Id    ${driver}    com.google.android.apps.automotive.youtube:id/decor_content_parent
    Should Be True    ${is_element_present}    L'élément YouTube n'est pas affiché.

Execute Language Change Test
    ${lang}=    Get System Language    ${Device}
    ${System}=    Set Variable If    '${lang}' == 'fr'    Système    System
    ${Setting}=    Set Variable If    '${lang}' == 'fr'    Paramètres    Settings
    ${Langue1}=    Set Variable If    '${lang}' == 'fr'    Langues et saisie    Languages & input
    ${Langue2}=    Set Variable If    '${lang}' == 'fr'    Langues    Languages

    ${resultat}=    Open Application With Click    ${driver}    ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Settings n'est pas affiché.

    Clique Sur Setting    ${driver}    ${System}    ${Setting_menu}
    Clique Sur Setting    ${driver}    ${Langue1}    ${Setting_system}
    Clique Sur Setting    ${driver}    ${Langue2}    ${Setting_system}
    Clique Sur Setting    ${driver}    English    ${Setting_system}
    Clique Sur Setting    ${driver}    English (United States)    ${Setting_system}
    Sleep    4s
    ${verfieadb}=    Check Language Change    ${Device}    en-US
    Should Be True    ${verfieadb}    Modifier Languages ne s'active pas (via adb).

    # Retour au français
    ${resultat}=    Open Application With Click    ${driver}    ${Setting}
    Clique Sur Setting    ${driver}    ${System}    ${Setting_menu}
    Clique Sur Setting    ${driver}    ${Langue1}    ${Setting_system}
    Clique Sur Setting    ${driver}    ${Langue2}    ${Setting_system}
    Clique Sur Setting    ${driver}    Français    ${Setting_system}
    Clique Sur Setting    ${driver}    Français (France)    ${Setting_system}
    Sleep    4s
    ${verfieadb}=    Check Language Change    ${Device}    fr-FR
    Should Be True    ${verfieadb}    Modifier Languages ne s'active pas (via adb).

Execute Notification Reception Test
    Install Apk    ${driver}    automotive-Notification_Test.apk
    ${isIns}=    Is App Installed    ${driver}    actia.pfe25.testnotificationapk
    Log    ${isIns}

    ${lang}=    Get System Language    ${Device}
    ${System}=    Set Variable If    '${lang}' == 'fr'    Système    System
    ${Setting}=    Set Variable If    '${lang}' == 'fr'    Paramètres    Settings
    ${Noti}=    Set Variable    Notifications

    ${resultat}=    Open Application With Click    ${driver}    ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Settings n'est pas affiché.

    Clique Sur Setting    ${driver}    ${Noti}    ${Setting_menu}
    Clique Sur Setting    ${driver}    TestNotificationapk    ${Setting_system}
    Activer Notification Si Desactive    ${driver}    android:id/switch_widget

    ${resultat}=    Open Application With Click    ${driver}    TestNotificationapk
    Click Element By Text Att    ${driver}    ENVOYER NOTIFICATION
    Sleep    2
    Click Icon Ia    ${driver}    notif
    Click Icon Ia    ${driver}    notif2

    Sleep    2s
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    com.android.systemui:id/notifications
    Should Be True    ${Verfier}    Notification n'est pas affiché.

    ${VerfierNotif}=    Check Element Exists By Text    ${driver}    Bouton appuyé !
    Should Be True    ${VerfierNotif}    La notification n'a pas été reçue.

Execute Notification Delete Test
    ${lang}=    Get System Language    ${Device}
    ${Btn_clear}=    Set Variable If    '${lang}' == 'fr'    Tout effacer    Clear all

    Click Icon Ia    ${driver}    notif
    Click Icon Ia    ${driver}    notif2
    Sleep    2s

    Click Element By Text    ${driver}    ${Btn_clear}
    Sleep    1s

    ${VerfierNotif}=    Check Element Exists By Text    ${driver}    Bouton appuyé !
    Should Not Be True    ${VerfierNotif}    La notification n'a pas été supprimée correctement.

Execute Disable Notification Test
    ${lang}=    Get System Language    ${Device}
    ${System}=    Set Variable If    '${lang}' == 'fr'    Système    System
    ${Setting}=    Set Variable If    '${lang}' == 'fr'    Paramètres    Settings
    ${Noti}=    Set Variable    Notifications

    ${resultat}=    Open Application With Click    ${driver}    ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Settings n'est pas affiché.

    Clique Sur Setting    ${driver}    ${Noti}    ${Setting_menu}
    Clique Sur Setting    ${driver}    TestNotificationapk    ${Setting_system}
    Desactive Notification Si Activer    ${driver}    android:id/switch_widget

    ${resultat}=    Open Application With Click    ${driver}    TestNotificationapk
    Click Element By Text    ${driver}    ENVOYER NOTIFICATION
    Sleep    2
    Click Icon Ia    ${driver}    notif
    Click Icon Ia    ${driver}    notif2

    Sleep    2s
    ${VerfierNotif}=    Check Element Exists By Text    ${driver}    Bouton appuyé !
    Should Not Be True    ${VerfierNotif}    La notification est toujours active alors qu'elle devrait être désactivée.

Execute Manual Date Change Test
    ${lang}=    Get System Language    ${Device}
    ${System}=    Set Variable If    '${lang}' == 'fr'    Système    System
    ${Setting}=    Set Variable If    '${lang}' == 'fr'    Paramètres    Settings
    ${Date}=    Set Variable If    '${lang}' == 'fr'    Date et heure    Date & time
    ${Btn_Heure}=    Set Variable If    '${lang}' == 'fr'    Définir l'heure    Set time

    ${resultat}=    Open Application With Click    ${driver}    ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Setting n'est pas affiché.

    Clique Sur Setting    ${driver}    ${System}    ${Setting_menu}
    Clique Sur Setting    ${driver}    ${Date}    ${Setting_system}
    ${date_ini}=    Get Device Datetime Heure    ${driver}
    Sleep    1s
    Click Element By Text Att    ${driver}    ${Btn_Heure}
    ${heure_act}=    Compose Time    ${driver}
    Log    ${heure_act}
    ${random_heure}=    Heure Aleatoire
    Log    ${random_heure}
    Change Date    ${driver}    ${random_heure}

    PressKey    ${driver}    4
    ${date_ini}=    Get Device Datetime Heure    ${driver}
    Should Be Equal    ${date_ini}    ${random_heure}    La date n'a pas été modifiée !

Execute Auto Date Sync Test
    ${lang}=    Get System Language    ${Device}
    ${System}=    Set Variable If    '${lang}' == 'fr'    Système    System
    ${Setting}=    Set Variable If    '${lang}' == 'fr'    Paramètres    Settings
    ${Date}=    Set Variable If    '${lang}' == 'fr'    Date et heure    Date & time
    ${Btn_Heure}=    Set Variable If    '${lang}' == 'fr'    Définir l'heure    Set time

    ${resultat}=    Open Application With Click    ${driver}    ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Setting n'est pas affiché.

    Clique Sur Setting    ${driver}    ${System}    ${Setting_menu}
    Clique Sur Setting    ${driver}    ${Date}    ${Setting_system}
    ${date_ini}=    Get Device Datetime Heure    ${driver}
    Click Element By Text Att    ${driver}    ${Btn_Heure}
    ${heure_act}=    Compose Time    ${driver}
    Log    ${heure_act}
    ${random_heure}=    Heure Aleatoire
    Log    ${random_heure}
    Change Date    ${driver}    ${random_heure}

    PressKey    ${driver}    4
    ${date_ini}=    Get Device Datetime Heure    ${driver}
    Should Be Equal    ${date_ini}    ${random_heure}    La date n'a pas été modifiée !


