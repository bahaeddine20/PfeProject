*** Settings ***
Documentation    Ce fichier contient des tests pour vérifier l'activation, la désactivation et la gestion des notifications, la modification de la langue, la synchronisation de l'heure, etc. sur un appareil Android. Les tests prennent en charge les interfaces en français et en anglais.
Library    Process
*** Settings ***
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
${System}              System

*** Keywords ***
Démarrer Driver
    ${driver}=    setup driver    ${Device}
    Set Suite Variable    ${driver}

Fermer Driver
    Close Driver    ${driver}

*** Test Cases ***
Test Home_Button
    [Documentation]    Ce test vérifie si le bouton "Home" fonctionne correctement en revenant à la page d'accueil de l'appareil.
    Revenir A La Home Page    ${driver}

Test Ouvrir YouTube App
    [Documentation]    Ce test vérifie si l'application YouTube peut être ouverte et si son activité est correctement lancée sur l'appareil Android.
    Sleep    2
    ${resultat}=    Open Application With Click      ${driver}    YouTube
    Should Be True    ${resultat}      L'activité YouTube n'est pas trouvée.
    ${Activity}=          Print Activity2       ${driver}
    Sleep    5s
    Log    ${Activity}
    ${is_element_present}=     Check Element ExistsBy Id       ${driver}       com.google.android.apps.automotive.youtube:id/decor_content_parent
    Should Be True    ${is_element_present}    L'élément YouTube n'est pas affiché.

Test Modifier Languages
    [Documentation]    Ce test vérifie si la modification de la langue du système fonctionne correctement sur l'appareil, en fonction de la langue actuelle de l'appareil.
    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=    Set Variable     Système
        ${Setting}=    Set Variable     Paramètres
        ${Langue1}=    Set Variable      Langues et saisie
        ${Langue2}=    Set Variable      Langues
    ELSE
        ${System}=    Set Variable    System
        ${Setting}=    Set Variable    Settings
        ${Langue1}=    Set Variable      Languages & input
        ${Langue2}=    Set Variable      Languages
    END

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Settings n'est pas affiché.
    Clique Sur Setting       ${driver}      ${System}        ${Setting_menu}
    Clique Sur Setting       ${driver}     ${Langue1}     ${Setting_system}
    Clique Sur Setting       ${driver}      ${Langue2}       ${Setting_system}
    Clique Sur Setting       ${driver}      English        ${Setting_system}
    Clique Sur Setting       ${driver}      English (United States)       ${Setting_system}
    Sleep    4s
    ${verfieadb} =         Check Language Change      ${Device}       en-US
    Should Be True     ${verfieadb}  Modifier Languages ne s'active pas (via adb).

    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=    Set Variable     Système
        ${Setting}=    Set Variable     Paramètres
        ${Langue1}=    Set Variable      Langues et saisie
        ${Langue2}=    Set Variable      Langues
    ELSE
        ${System}=    Set Variable    System
        ${Setting}=    Set Variable    Settings
        ${Langue1}=    Set Variable      Languages & input
        ${Langue2}=    Set Variable      Languages
    END

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Settings n'est pas affiché.
    Clique Sur Setting       ${driver}      ${System}        ${Setting_menu}
    Clique Sur Setting       ${driver}     ${Langue1}     ${Setting_system}
    Clique Sur Setting       ${driver}      ${Langue2}       ${Setting_system}
    Clique Sur Setting       ${driver}      Français      ${Setting_system}
    Clique Sur Setting       ${driver}      Français (France)   ${Setting_system}
    Sleep    4s
    ${verfieadb} =         Check Language Change      ${Device}        fr-FR
    Should Be True     ${verfieadb}  Modifier Languages ne s'active pas (via adb).


Test Notification Réception
    [Documentation]    Ce test vérifie la réception d'une notification après l'activation des paramètres nécessaires et l'envoi de la notification depuis une application tierce.
    Install Apk     ${driver}         automotive-Notification_Test.apk
    ${isIns}=      Is App Installed      ${driver}        actia.pfe25.testnotificationapk
    Log    ${isIns}
    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}       Set Variable     Système
        ${Setting}     Set Variable     Paramètres
        ${Noti}         Set Variable     Notifications
    ELSE
        ${System}   Set Variable    System
        ${Setting}    Set Variable    Settings
        ${Noti}    Set Variable     Notifications
    END

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Settings n'est pas affiché.
    Clique Sur Setting       ${driver}      ${Noti}       ${Setting_menu}
    Clique Sur Setting       ${driver}     TestNotificationapk      ${Setting_system}

    Activer Notification Si Desactive         ${driver}     android:id/switch_widget
    ${resultat}=    Open Application With Click      ${driver}        TestNotificationapk
    click Element By Text Att   ${driver}       ENVOYER NOTIFICATION
    Sleep    2
    Afficher Notification        ${driver}
    Sleep    2s
    ${Verfier}=      Check Element ExistsBy Id      ${driver}        com.android.systemui:id/notifications
    Should Be True    ${Verfier}      Notification n'est pas affiché.

    ${VerfierNotif}=        Check Element Exists By Text         ${driver}      Bouton appuyé !

Test Notification Supprimer
    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}    Set Variable    Système
        ${Setting}    Set Variable    Paramètres
        ${Langue1}    Set Variable    Langues et saisie
        ${Langue2}    Set Variable    Langues
        ${Btn_clear}    Set Variable    Tout effacer
    ELSE
        ${System}    Set Variable    System
        ${Setting}    Set Variable    Settings
        ${Langue2}    Set Variable    Languages
        ${Btn_clear}    Set Variable    Clear all
    END

    Afficher Notification        ${driver}
    Sleep    2s   # Attendre que la notification apparaisse

    ${VerfierNotif}=        Check Element Exists By Text         ${driver}      Bouton appuyé !
    Should Be True    ${VerfierNotif}    La notification n'est pas affichée.
    Sleep    2s  # Attendre que l'élément soit visible et interactif
    Click Element By Text     ${driver}    ${Btn_clear}
    Sleep    1s



    ${VerfierNotif}=    Check Element Exists By Text    ${driver}    Bouton appuyé !
    Run Keyword If    '${VerfierNotif}' == 'False'    Log    La notification a été supprimée correctement.
    Run Keyword If    '${VerfierNotif}' == 'True'    Fail    La notification n'a pas été supprimée correctement.







Test Disable Notification

    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}       Set Variable     Système
        ${Setting}     Set Variable     Paramètres
        ${Noti}         Set Variable     Notifications


    ELSE
        ${System}   Set Variable    System
        ${Setting}    Set Variable    Settings
        ${Noti}    Set Variable     Notifications



    END


    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Settings n'est pas affiché.


    Clique Sur Setting       ${driver}      ${Noti}       ${Setting_menu}
    Clique Sur Setting       ${driver}     TestNotificationapk      ${Setting_system}

    #Activer Notification Si Desactive         ${driver}     android:id/switch_widget
    Desactive Notification Si Activer         ${driver}        android:id/switch_widget
    ${resultat}=    Open Application With Click      ${driver}        TestNotificationapk
    Click Element By Text       ${driver}       ENVOYER NOTIFICATION
    Sleep    2
    Afficher Notification        ${driver}
    Sleep    2s   # Attendre que la notification apparaisse

    ${VerfierNotif}=        Check Element Exists By Text         ${driver}      Bouton appuyé !

    Run Keyword If    '${VerfierNotif}' == 'True'    Fail    La notification a été supprimée correctement.
    Run Keyword If    '${VerfierNotif}' == 'False'     Log   La notification n'a pas été supprimée correctement.



Test Modifier Manuellement Date

        ${lang}    Get System Language       ${Device}

        IF    '${lang}' == 'fr'
            ${System}       Set Variable     Système
            ${Setting}     Set Variable     Paramètres
            ${Date}         Set Variable     Date et heure
            ${Btn_Heure}         Set Variable     Définir l'heure



        ELSE
            ${System}   Set Variable    System
            ${Setting}    Set Variable    Settings
            ${Date}    Set Variable     Date & time
            ${Btn_Heure}         Set Variable     Set time




        END


    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Setting n'est pas affiché.


    Clique Sur Setting       ${driver}      ${System}        ${Setting_menu}
    Clique Sur Setting       ${driver}     ${Date}     ${Setting_system}
    ${date_ini}=     Get Device Datetime Heure        ${driver}
    Sleep    1s
    Click Element By Text Att       ${driver}     ${Btn_Heure}
    ${heure_act}=   Compose Time        ${driver}
    Log     ${heure_act}
    ${random_heure}=    Heure Aleatoire
    Log    ${random_heure}
    Change Date          ${driver}      ${random_heure}

    PressKey   ${driver}     4
    ${date_ini}=     Get Device Datetime Heure        ${driver}
    Should Be Equal   ${date_ini}     ${random_heure}      La date n'a pas été modifiée !


Test Modifier Synchronisation Automatique Date

        ${lang}    Get System Language       ${Device}

        IF    '${lang}' == 'fr'
            ${System}       Set Variable     Système
            ${Setting}     Set Variable     Paramètres
            ${Date}         Set Variable     Date et heure
            ${Btn_Heure}         Set Variable     Définir l'heure



        ELSE
            ${System}   Set Variable    System
            ${Setting}    Set Variable    Settings
            ${Date}    Set Variable     Date & time
            ${Btn_Heure}         Set Variable     Définir l'heure




        END


    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Setting n'est pas affiché.


    Clique Sur Setting       ${driver}      ${System}        ${Setting_menu}
    Clique Sur Setting       ${driver}     ${Date}     ${Setting_system}
    ${date_ini}=     Get Device Datetime Heure        ${driver}
    Click Element By Text Att       ${driver}     ${Btn_Heure}
    ${heure_act}=   Compose Time        ${driver}
    Log     ${heure_act}
    ${random_heure}=    Heure Aleatoire
    Log    ${random_heure}
    Change Date          ${driver}      ${random_heure}

    PressKey   ${driver}     4
    ${date_ini}=     Get Device Datetime Heure        ${driver}
    Should Be Equal   ${date_ini}     ${random_heure}      La date n'a pas été modifiée !


