*** Settings ***
Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py

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

*** Test Cases ***
Test Home_Button
    ${driver}    setup driver        ${Device}
    Revenir A La Home Page    ${driver}

Test Ouvrir YouTube App
    ${driver}    setup driver       ${Device}
    Sleep    2
    Revenir A La Home Page    ${driver}
    ${resultat}=    Open Application With Click      ${driver}    YouTube
    Should Be True    ${resultat}      L'activité YouTube n'est pas trouver .
    ${Activity}=          Print Activity2       ${driver}
    Sleep    5s
    Log    ${Activity}
    ${is_element_present}=     Check Element ExistsBy Id       ${driver}       com.google.android.apps.automotive.youtube:id/decor_content_parent
    Should Be True    ${is_element_present}    L'élément YouTube n'est pas affiché.



Test Affiche Notification
    Sleep    2
    ${driver}    setup driver       ${Device}
    Afficher Notification        ${driver}
    ${Verfier}=      Check Element ExistsBy Id      ${driver}        com.android.systemui:id/notifications
    Should Be True    ${Verfier}      Notification n'est pas affiché.


Test Ouvrir Bluetooth
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
    ${allsetting}=    all_setting_list    ${driver}     ${Setting_menu}
    ${elementexist}=    Run Keyword And Return Status    Should Contain    ${allsetting}    Bluetooth
    Should Be True    ${elementexist}    Bluetooth should exist in the list.
    Log    ${allsetting}
    Clique Sur Setting       ${driver}      Bluetooth       ${Setting_menu}
    ${ble}=  Element Existe Par Accessibility Id       ${driver}     Bluetooth toggle switch
    Should Be True    ${ble}    Les paramètres de Bluetooth ne s'affichent pas.
    Activer Bluetooth Si Desactive       ${driver}     android:id/switch_widget
    Sleep    3s
    ${verifier_ble_ui}=   Verfier Bluetooth Activer       ${driver}     android:id/switch_widget
    Should Be True     ${verifier_ble_ui}   Le Bluetooth ne s'active pas (ui).
    
    ${verfier_ble_adb}=  Est Bluetooth Active       ${Device}
    Should Be True     ${verfier_ble_adb}   Le Bluetooth ne s'active pas (via adb).





    





Test Fermer Bluetooth
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
    ${allsetting}=    all_setting_list    ${driver}     ${Setting_menu}
    ${elementexist}=    Run Keyword And Return Status    Should Contain    ${allsetting}    Bluetooth
    Should Be True    ${elementexist}    Bluetooth should exist in the list.
    Log    ${allsetting}
    Clique Sur Setting       ${driver}      Bluetooth       ${Setting_menu}
    ${ble}=  Element Existe Par Accessibility Id       ${driver}     Bluetooth toggle switch
    Should Be True    ${ble}    Les paramètres de Bluetooth ne s'affichent pas.
    Desactive Bluetooth Si Activer       ${driver}     android:id/switch_widget
    Sleep    3s
    ${verifier_ble_ui}=   Verfier Bluetooth Activer       ${driver}     android:id/switch_widget
    Should Not Be True     ${verifier_ble_ui}   Le Bluetooth ne desactive pas (ui).

    ${verfier_ble_adb}=  Est Bluetooth Active       ${Device}
    Should Not Be True     ${verfier_ble_adb}   Le Bluetooth ne desactive pas (via adb).








Test Modifier Languages
    ${driver}    setup driver       ${Device}

    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=    Set Variable     Système
        ${Setting}    Set Variable     Paramètres
        ${Langue1}    Set Variable      Langues et saisie
        ${Langue2}    Set Variable      Langues

    ELSE
        ${System}=    Set Variable    System
        ${Setting}=    Set Variable    Settings
        ${Langue1}    Set Variable      Languages & input
        ${Langue2}    Set Variable      Languages

    END

    Revenir A La Home Page    ${driver}
    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Run Keyword And Continue On Failure  Should Be True    ${Verfier}        Setting n'est pas affiché.


    Run Keyword And Continue On Failure      Clique Sur Setting       ${driver}      ${System}        ${Setting_menu}

    Run Keyword And Continue On Failure     Clique Sur Setting       ${driver}     ${Langue1}     ${Setting_system}

    Run Keyword And Continue On Failure     Clique Sur Setting       ${driver}      ${Langue2}       ${Setting_system}

    Run Keyword And Continue On Failure     Clique Sur Setting       ${driver}      English        ${Setting_system}
    Run Keyword And Continue On Failure      Clique Sur Setting       ${driver}      English (United States)       ${Setting_system}
    Sleep    4s
    ${verfieadb} =         Check Language Change      ${Device}       en-US
    Run Keyword And Continue On Failure     Should Be True     ${verfieadb}  Modifier Languages ne s'active pas (via adb).


    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=    Set Variable     Système
        ${Setting}    Set Variable     Paramètres
        ${Langue1}    Set Variable      Langues et saisie
        ${Langue2}    Set Variable      Langues

    ELSE
        ${System}=    Set Variable    System
        ${Setting}=    Set Variable    Settings
        ${Langue1}    Set Variable      Languages & input
        ${Langue2}    Set Variable      Languages

    END

    Revenir A La Home Page    ${driver}
    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Setting n'est pas affiché.


    Clique Sur Setting       ${driver}      ${System}        ${Setting_menu}

    Clique Sur Setting       ${driver}     ${Langue1}     ${Setting_system}

    Clique Sur Setting       ${driver}      ${Langue2}       ${Setting_system}

    Clique Sur Setting       ${driver}      Français      ${Setting_system}
    Clique Sur Setting       ${driver}      Français (France)   ${Setting_system}
    Sleep    4s
    ${verfieadb} =         Check Language Change      ${Device}        fr-FR
    Run Keyword And Continue On Failure     Should Be True     ${verfieadb}  Modifier Languages ne s'active pas (via adb).





Test Notification Réception
    ${driver}    setup driver       ${Device}
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
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Settings n'est pas affiché.


    Clique Sur Setting       ${driver}      ${Noti}       ${Setting_menu}
    Clique Sur Setting       ${driver}     TestNotificationapk      ${Setting_system}

    Activer Notification Si Desactive         ${driver}     android:id/switch_widget
    #Desactive Notification Si Activer         ${driver}        android:id/switch_widget
    ${resultat}=    Open Application With Click      ${driver}        TestNotificationapk
    click Element By Text Att   ${driver}       ENVOYER NOTIFICATION
    Sleep    2
    Afficher Notification        ${driver}
    ${Verfier}=      Check Element ExistsBy Id      ${driver}        com.android.systemui:id/notifications
    Should Be True    ${Verfier}      Notification n'est pas affiché.

    ${VerfierNotif}=        Check Element Exists By Text         ${driver}      Bouton appuyé !

Test Notification Supprimer
    ${driver}    setup driver       ${Device}
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
    ${driver}    setup driver       ${Device}

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
     ${driver}    setup driver       ${Device}

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


    Revenir A La Home Page    ${driver}
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




Test Install Apk
      ${driver}    setup driver       ${Device}
      ${isInsUi}=   Search Application     ${driver}        TestNotificationapk
      Log    ${isInsUi}
      ${isIns}=      Is App Installed      ${driver}        actia.pfe25.testnotificationapk
      Log    ${isIns}
      Install Apk     ${driver}         automotive-Notification_Test.apk
      ${isIns}=      Is App Installed      ${driver}        actia.pfe25.testnotificationapk
      Log    ${isIns}
      Run Keyword And Continue On Failure      Should Be True    ${isIns}      The application is not installed via adb

      ${isInsUi}=   Search Application     ${driver}        TestNotificationapk
      Run Keyword And Continue On Failure        Should Be True    ${isInsUi}      The installed application is not displayed (via adb)



Test Uninstall Application
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
        ${apps}         Set Variable     Apps
        ${Consulter_allapps}         Set Variable      View all
        ${DesButton}        Set Variable    Uninstall
        ${confirme}         Set Variable    OK
    END

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s
    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Should Be True    ${Verfier}        Settings is not displayed.

    Clique Sur Setting         ${driver}      ${apps}       ${Setting_menu}
    Clique Sur Setting Include      ${driver}     ${Consulter_allapps}     ${Setting_system}
    Clique Sur Setting         ${driver}     TestNotificationapk      ${Setting_system}
    click Element By Text Att     ${driver}     ${DesButton}
    Sleep    1s
    click Element By Text     ${driver}     ${confirme}

    ${isInsUi}=   Search Application     ${driver}        TestNotificationapk
    Run Keyword And Continue On Failure    Should Not Be True    ${isInsUi}       The uninstalled application is displayed

    ${isIns}=      Is App Installed      ${driver}        actia.pfe25.testnotificationapk
    Log    ${isIns}
    Run Keyword And Continue On Failure     Should Not Be True     ${isIns}      The application is not uninstalled correctly (via adb)




