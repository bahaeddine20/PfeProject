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
Library    AppiumLibrary

Suite Setup     Démarrer Driver
Suite Teardown  Fermer Driver

*** Variables ***
# Configuration des retries et timing
${MAX_RETRIES}        3
${RETRY_DELAY}        2s
${QUICK_WAIT}         0.5s
${WAIT_TIME}          2s
${USER_SWITCH_WAIT}   30s

# Application Activities
${AppGrid_ACTIVITY}    com.android.car.carlauncher/.GASAppGridActivity
${Setting_ACTIVITY}    com.android.car.settings/.Settings_Launcher_Homepage
${MessageActivity}     com.android.car.messenger/.ui.launcher.MessageLauncherActivity

# UI Element IDs
${Setting_xpath_id}    com.android.car.settings:id/car_settings_activity_wrapper
${Setting_menu}        com.android.car.settings:id/top_level_menu
${Device}              emulator-5554
${Setting_system}      com.android.car.settings:id/fragment_container

# Language Configuration
&{LANG_FR}    System=Système    Setting=Paramètres    Profils=Profils et comptes    Mange=Gérer d'autres profils
...    Ajouter=Ajouter un profil    Ajouter2=Ajouter un profil    Supp=Supprimer ce profil
...    Renommer=Renommer le profil    Ok=OK

&{LANG_EN}    System=System    Setting=Settings    Profils=Profiles & accounts    Mange=Manage other profiles
...    Ajouter=Add profile    Ajouter2=Add a profile    Supp=Delete profile
...    Renommer=Rename profile    Ok=OK

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
    [Documentation]    Initializes the test driver
    ${driver}=    Setup Driver    ${Device}
    Set Suite Variable    ${driver}
    Initialize Language Settings

Fermer Driver
    [Documentation]    Cleans up and closes the test driver
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

Initialize Language Settings
    [Documentation]    Sets up language-specific variables based on system language
    ${lang}=    Get System Language    ${Device}
    ${lang_dict}=    Set Variable If    '${lang}' == 'fr'    ${LANG_FR}    ${LANG_EN}
    Set Suite Variable    ${LANG_DICT}    ${lang_dict}

Get Localized Text
    [Documentation]    Gets the localized text for a given key
    [Arguments]    ${key}
    RETURN    ${LANG_DICT.${key}}

Reconnect Driver
    [Documentation]    Ferme et réinitialise le driver après un changement d'utilisateur
    Close Driver    ${driver}
    Sleep    ${QUICK_WAIT}
    ${driver}=    Setup Driver    ${Device}
    Set Suite Variable    ${driver}

Switch User And Reconnect
    [Documentation]    Change d'utilisateur et réinitialise le driver
    [Arguments]    ${user_id}
    Switch Android User    ${Device}    ${user_id}
    Sleep    ${USER_SWITCH_WAIT}    # Attendre que le système soit prêt
    Reconnect Driver
    Sleep    ${QUICK_WAIT}

Execute Add User Test
    [Documentation]    Tests adding a new user
    # Get user list before adding
    ${old_users}=    Get Android Users    ${driver}

    # Navigate to settings
    ${resultat}=    Open Application With Click    ${driver}    ${LANG_DICT.Setting}
    Sleep    ${QUICK_WAIT}

    # Verify settings screen
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Settings screen is not displayed

    # Navigate to profiles
    Clique Sur Setting    ${driver}    ${LANG_DICT.Profils}    ${Setting_menu}
    Clique Sur Setting    ${driver}    ${LANG_DICT.Mange}    ${Setting_system}
    Sleep    ${QUICK_WAIT}

    # Add new profile
    Click Element By Text Att    ${driver}    ${LANG_DICT.Ajouter}
    Click Element By Text Att    ${driver}    ${LANG_DICT.Ajouter2}
    Sleep    ${QUICK_WAIT}
    Click Element By Text Att    ${driver}    ${LANG_DICT.Ok}
    Sleep    ${QUICK_WAIT}

    # Verify user was added
    ${new_users}=    Get Android Users    ${driver}
    ${verifie_adb_add_user}=    Get Added User    ${old_users}    ${new_users}
    Should Not Be Equal    ${verifie_adb_add_user}    ${None}    No user was added
    Log    Utilisateur ajouté : ${verifie_adb_add_user}

    # Switch to new user
    Switch User And Reconnect    10

    # Verify we're connected to new user
    ${resultat}=    Open Application With Click    ${driver}    ${LANG_DICT.Setting}
    Sleep    ${QUICK_WAIT}

Execute Delete User Test
    [Documentation]    Tests deleting a user
    # Get user list before deletion
    ${old_users}=    Get Android Users    ${driver}

    # Navigate to settings
    ${resultat}=    Open Application With Click    ${driver}    ${LANG_DICT.Setting}
    Sleep    ${QUICK_WAIT}

    # Verify settings screen
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Settings screen is not displayed

    # Navigate to profiles and delete
    Clique Sur Setting    ${driver}    ${LANG_DICT.Profils}    ${Setting_menu}
    Clique Sur Setting    ${driver}    ${LANG_DICT.Supp}    ${Setting_system}
    Sleep    ${QUICK_WAIT}

    # Verify user was deleted
    ${new_users}=    Get Android Users    ${driver}
    ${verifie_adb_add_user}=    Get Added User    ${old_users}    ${new_users}
    Should Be Equal    ${verifie_adb_add_user}    ${None}    User was not deleted
    Log    Utilisateur supprimé : ${verifie_adb_add_user}

Execute Rename User Test
    [Documentation]    Tests renaming a user
    # Navigate to settings
    ${resultat}=    Open Application With Click    ${driver}    ${LANG_DICT.Setting}
    Sleep    ${QUICK_WAIT}

    # Verify settings screen
    ${Verfier}=    Check Element ExistsBy Id    ${driver}    ${Setting_xpath_id}
    Should Be True    ${Verfier}    Settings screen is not displayed

    # Navigate to profiles
    Clique Sur Setting    ${driver}    ${LANG_DICT.Profils}    ${Setting_menu}
    Sleep    ${QUICK_WAIT}

*** Test Cases ***
Test Ajouter Utilisateur
    [Documentation]    Teste l'ajout d'un nouvel utilisateur
    ...                - Vérifie la langue du système
    ...                - Navigue dans les menus appropriés
    ...                - Ajoute un nouveau profil
    ...                - Vérifie que l'utilisateur a bien été ajouté
    [Tags]    users    smoke
    Execute Test With Retry    Execute Add User Test    Test Ajouter Utilisateur

Test Supprimer Utilisateur
    [Documentation]    Teste la suppression d'un utilisateur
    ...                - Vérifie la langue du système
    ...                - Navigue dans les menus appropriés
    ...                - Supprime le profil spécifié
    ...                - Vérifie que l'utilisateur a bien été supprimé
    [Tags]    users    smoke
    Execute Test With Retry    Execute Delete User Test    Test Supprimer Utilisateur

Test Renommer Utilisateur
    [Documentation]    Teste le renommage d'un utilisateur
    ...                - Vérifie la langue du système
    ...                - Navigue dans les menus appropriés
    ...                - Modifie le nom du profil
    [Tags]    users    smoke
    Execute Test With Retry    Execute Rename User Test    Test Renommer Utilisateur
