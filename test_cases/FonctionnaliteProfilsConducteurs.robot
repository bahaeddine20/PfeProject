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
${Device}              emulator-5556
${Setting_system}      com.android.car.settings:id/fragment_container
${System}               System
*** Test Cases ***


Test Ajouter Utilisateur
    ${driver}    setup driver       ${Device}

    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=    Set Variable     Système
        ${Setting}    Set Variable     Paramètres
        ${Profils}    Set Variable     Profils et comptes
        ${Ajouter}    Set Variable     Ajouter un profil
        ${Ok}         Set Variable     OK
    ELSE
        ${System}=    Set Variable    System
        ${Setting}=    Set Variable    Settings
        ${Profils}    Set Variable    Profils et comptes
        ${Ajouter}    Set Variable    Add Profile
        ${Ok}         Set Variable    OK
    END

    # Récupérer la liste des utilisateurs avant l'ajout
    ${old_users}=       Get Android Users     ${driver}

    Revenir A La Home Page    ${driver}

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s

    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Run Keyword And Continue On Failure  Should Be True    ${Verfier}        Setting n'est pas affiché.

    Run Keyword And Continue On Failure      Clique Sur Setting       ${driver}      ${Profils}        ${Setting_menu}
    Click Element By Text Att    ${driver}       ${Ajouter}

    Sleep    2s
    Click Element By Text Att    ${driver}         ${Ok}
    Sleep    5s

    # Récupérer la liste des utilisateurs après l'ajout
    ${new_users}=       Get Android Users     ${driver}

    # Vérifier si un utilisateur a été ajouté
    ${verifie_adb_add_user}=    Get Added User       ${old_users}    ${new_users}

    # Vérification et validation du test
    Run Keyword And Continue On Failure  Should Not Be Equal    ${verifie_adb_add_user}    ${None}   Aucun utilisateur n'a été ajouté.

    # Log des informations
    Log    Utilisateur ajouté : ${verifie_adb_add_user}




Test renommer Utilisateur
    ${driver}    setup driver       ${Device}

    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=    Set Variable     Système
        ${Setting}    Set Variable     Paramètres
        ${Profils}    Set Variable     Profils et comptes
        ${Ajouter}    Set Variable     Ajouter un profil
        ${Ok}         Set Variable     OK
    ELSE
        ${System}=    Set Variable    System
        ${Setting}=    Set Variable    Settings
        ${Profils}    Set Variable    Profils et comptes
        ${Ajouter}    Set Variable    Add Profile
        ${Ok}         Set Variable    OK
    END

    # Récupérer la liste des utilisateurs avant l'ajout
    ${old_users}=       Get Android Users     ${driver}

    Revenir A La Home Page    ${driver}

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s

    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Run Keyword And Continue On Failure  Should Be True    ${Verfier}        Setting n'est pas affiché.

    Run Keyword And Continue On Failure      Clique Sur Setting       ${driver}      ${Profils}        ${Setting_menu}
