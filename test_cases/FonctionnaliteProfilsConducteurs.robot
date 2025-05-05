*** Settings ***
*** Settings ***
Documentation    Tests de gestion des utilisateurs Android
...              - Ajout d'un nouvel utilisateur
...              - Suppression d'un utilisateur
...              - Renommage d'un utilisateur
...              - Prend en charge les interfaces en français et en anglais
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
${Device}              emulator-5556
${Setting_system}      com.android.car.settings:id/fragment_container
${System}               System
${verifie_adb_add_user}     ${null}
*** Keywords ***
Démarrer Driver
    ${driver}=    Setup Driver       ${Device}
    Set Suite Variable    ${driver}

Fermer Driver
    Close Driver    ${driver}
*** Test Cases ***


Test Ajouter Utilisateur
    [Documentation]    Teste l'ajout d'un nouvel utilisateur
    ...                - Vérifie la langue du système
    ...                - Navigue dans les menus appropriés
    ...                - Ajoute un nouveau profil
    ...                - Vérifie que l'utilisateur a bien été ajouté
    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=    Set Variable     Système
        ${Setting}    Set Variable     Paramètres
        ${Profils}    Set Variable     Profils et comptes
        ${Mange}     Set Variable      Gérer d'autres profils

        ${Ajouter}    Set Variable     Ajouter un profil
        ${Ok}         Set Variable     OK
    ELSE
        ${System}=    Set Variable    System
        ${Setting}=    Set Variable    Settings
        ${Profils}    Set Variable    Profiles & accounts
        ${Mange}     Set Variable     Manage other profiles
        ${Ajouter}    Set Variable    Add profile
        ${Ajouter2}    Set Variable   Add a profile
        ${Ok}         Set Variable    OK
    END

    # Récupérer la liste des utilisateurs avant l'ajout
    ${old_users}=       Get Android Users     ${driver}

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s

    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Run Keyword And Continue On Failure  Should Be True    ${Verfier}        Setting n'est pas affiché.

    Run Keyword And Continue On Failure      Clique Sur Setting       ${driver}      ${Profils}        ${Setting_menu}
    Run Keyword And Continue On Failure      Clique Sur Setting       ${driver}      ${Mange}        ${Setting_system}
    Sleep    2s
    Run Keyword And Continue On Failure          Click Element By Text Att     ${driver}           ${Ajouter}
    Run Keyword And Continue On Failure          Click Element By Text Att      ${driver}           ${Ajouter2}



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
    Sleep    50s
    Switch Android User    ${Device}    10
    Sleep    20s

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}

Test Supprimer Utilisateur
    [Documentation]    Teste la suppression d'un utilisateur
    ...                - Vérifie la langue du système
    ...                - Navigue dans les menus appropriés
    ...                - Supprime le profil spécifié
    ...                - Vérifie que l'utilisateur a bien été supprimé
    ${lang}    Get System Language       ${Device}

    IF    '${lang}' == 'fr'
        ${System}=    Set Variable     Système
        ${Setting}    Set Variable     Paramètres
        ${Profils}    Set Variable     Profils et comptes
        ${Supp}     Set Variable      Supprimer ce profil

        ${Ajouter}    Set Variable     Ajouter un profil
        ${Ok}         Set Variable     OK
    ELSE
        ${System}=    Set Variable    System
        ${Setting}=    Set Variable    Settings
        ${Profils}    Set Variable    Profiles & accounts
        ${Supp}     Set Variable     Manage other profiles
        ${Ajouter}    Set Variable    Add Profile
        ${Ok}         Set Variable    OK
    END

    # Récupérer la liste des utilisateurs avant l'ajout
    ${old_users}=       Get Android Users     ${driver}

    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s

    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Run Keyword And Continue On Failure  Should Be True    ${Verfier}        Setting n'est pas affiché.

    Run Keyword And Continue On Failure      Clique Sur Setting       ${driver}      ${Profils}        ${Setting_menu}
    Run Keyword And Continue On Failure      Clique Sur Setting       ${driver}      ${Supp}        ${Setting_system}

    Sleep    20s

    # Récupérer la liste des utilisateurs après l'ajout
    ${new_users}=       Get Android Users     ${driver}

    # Vérifier si un utilisateur a été ajouté
    ${verifie_adb_add_user}=    Get Added User       ${old_users}    ${new_users}

    # Vérification et validation du test
    Run Keyword And Continue On Failure  Should Be Equal    ${verifie_adb_add_user}    ${None}   Aucun utilisateur n'a été ajouté.

    # Log des informations
    Log    Utilisateur ajouté : ${verifie_adb_add_user}




Test renommer Utilisateur
    [Documentation]    Teste le renommage d'un utilisateur
    ...                - Vérifie la langue du système
    ...                - Navigue dans les menus appropriés
    ...                - Modifie le nom du profil
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


    ${resultat}=    Open Application With Click      ${driver}        ${Setting}
    Sleep    1s

    ${Verfier}=    Check Element ExistsBy Id      ${driver}         ${Setting_xpath_id}
    Run Keyword And Continue On Failure  Should Be True    ${Verfier}        Setting n'est pas affiché.

    Run Keyword And Continue On Failure      Clique Sur Setting       ${driver}      ${Profils}        ${Setting_menu}
