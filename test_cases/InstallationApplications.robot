*** Settings ***
Documentation    Tests for APK installation and uninstallation
...              - Verifies APK installation via ADB
...              - Checks application visibility in UI
...              - Tests complete uninstallation flow
Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Library    Collections
Library    AppiumLibrary

Suite Setup     Démarrer Driver
Suite Teardown  Fermer Driver

*** Variables ***
# Application Activities
${AppGrid_ACTIVITY}    com.android.car.carlauncher/.GASAppGridActivity
${Setting_ACTIVITY}    com.android.car.settings/.Settings_Launcher_Homepage
${MessageActivity}     com.android.car.messenger/.ui.launcher.MessageLauncherActivity

# UI Element IDs
${Setting_xpath_id}    com.android.car.settings:id/car_settings_activity_wrapper
${Setting_menu}        com.android.car.settings:id/top_level_menu
${Device}              emulator-5554
${Setting_system}      com.android.car.settings:id/fragment_container

# Application Details
${TEST_APP_NAME}       TestNotificationapk
${TEST_APP_PACKAGE}    actia.pfe25.testnotificationapk
${TEST_APK_FILE}       automotive-Notification_Test.apk

# Timing Configuration
${WAIT_TIME}          2s
${MAX_RETRIES}        3
${RETRY_DELAY}        2s
${QUICK_WAIT}         0.5s

# Language Configuration
&{LANG_FR}    System=Système    Setting=Paramètres    apps=Applis    view_all=Voir les    uninstall=Désinstaller    confirm=OK
&{LANG_EN}    System=System    Setting=Settings    apps=Apps    view_all=View all    uninstall=Uninstall    confirm=OK

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
    ${driver}=    setup driver    ${Device}
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

Wait For Element
    [Documentation]    Waits for an element to be present with retry mechanism
    [Arguments]    ${driver}    ${locator}    ${timeout}=${WAIT_TIME}
    FOR    ${i}    IN RANGE    ${MAX_RETRIES}
        ${exists}=    Run Keyword And Return Status
        ...    Check Element ExistsBy Id    ${driver}    ${locator}
        IF    ${exists}
            RETURN    ${True}
        END
        Sleep    ${RETRY_DELAY}
    END
    RETURN    ${False}

Wait For App Visibility
    [Documentation]    Waits for the application to be visible in UI
    [Arguments]    ${driver}    ${app_name}
    FOR    ${i}    IN RANGE    ${MAX_RETRIES}
        ${is_visible}=    Search Application    ${driver}    ${app_name}
        IF    ${is_visible}
            RETURN    ${True}
        END
        Sleep    ${RETRY_DELAY}
    END
    RETURN    ${False}

Verify App Installation
    [Documentation]    Verifies if the application is properly installed
    [Arguments]    ${driver}    ${app_name}    ${package_name}
    ${is_installed}=    Is App Installed    ${driver}    ${package_name}
    ${is_visible}=      Search Application    ${driver}    ${app_name}

    Run Keyword And Continue On Failure     Should Be True    ${is_installed}    Application is not installed via ADB
    Run Keyword And Continue On Failure     Should Be True    ${is_visible}      Application is not visible in UI

Verify App Uninstallation
    [Documentation]    Verifies if the application is completely uninstalled
    [Arguments]    ${driver}    ${app_name}    ${package_name}
    ${is_installed}=    Is App Installed    ${driver}    ${package_name}
    ${is_visible}=      Search Application    ${driver}    ${app_name}

    Run Keyword And Continue On Failure     Should Not Be True    ${is_installed}    Application is still installed via ADB
    Run Keyword And Continue On Failure      Should Not Be True    ${is_visible}      Application is still visible in UI

Uninstall App If Exists
    [Documentation]    Uninstalls the application if it exists
    [Arguments]    ${driver}    ${app_name}    ${package_name}
    ${is_visible}=      Search Application    ${driver}    ${app_name}
    Run Keyword If     ${is_visible}    Uninstall Application    ${driver}    ${app_name}
    Sleep    ${QUICK_WAIT}

Uninstall Application
    [Documentation]    Performs the uninstallation process
    [Arguments]    ${driver}    ${app_name}
    # Navigate to Settings
    ${result}=    Open Application With Click    ${driver}    ${LANG_DICT.Setting}
    Sleep    ${QUICK_WAIT}

    # Verify Settings screen
    ${exists}=    Wait For Element    ${driver}    ${Setting_xpath_id}
    Should Be True    ${exists}    Settings screen is not displayed

    # Navigate to Apps section
    Clique Sur Setting    ${driver}    ${LANG_DICT.apps}    ${Setting_menu}
    Sleep    ${QUICK_WAIT}

    # Wait for and click on View All
    ${view_all_exists}=    Wait For Element    ${driver}    ${Setting_system}
    Should Be True    ${view_all_exists}    Apps section is not displayed
    Clique Sur Setting Include    ${driver}    ${LANG_DICT.view_all}    ${Setting_system}
    Sleep    ${QUICK_WAIT}

    # Uninstall application
    Clique Sur Setting    ${driver}    ${app_name}    ${Setting_system}
    Sleep    ${QUICK_WAIT}
    click Element By Text Att    ${driver}    ${LANG_DICT.uninstall}
    Sleep    ${QUICK_WAIT}
    click Element By Text    ${driver}    ${LANG_DICT.confirm}
    Sleep    ${QUICK_WAIT}

Execute Install Apk Test
    [Documentation]    Executes the APK installation test
    # Uninstall app if it exists
    Uninstall App If Exists    ${driver}    ${TEST_APP_NAME}    ${TEST_APP_PACKAGE}

    # Install APK
    Install Apk    ${driver}    ${TEST_APK_FILE}
    Sleep    ${QUICK_WAIT}

    # Verify installation
    Verify App Installation    ${driver}    ${TEST_APP_NAME}    ${TEST_APP_PACKAGE}

Execute Uninstall Application Test
    [Documentation]    Executes the application uninstallation test
    # Uninstall application
    Uninstall Application    ${driver}    ${TEST_APP_NAME}

    # Verify uninstallation
    Verify App Uninstallation    ${driver}    ${TEST_APP_NAME}    ${TEST_APP_PACKAGE}

*** Test Cases ***
Test Install Apk
    [Documentation]    Tests APK installation process
    ...                - Checks pre-installation state
    ...                - Installs the APK
    ...                - Verifies installation in system and UI
    [Tags]    installation    smoke
    Execute Test With Retry    Execute Install Apk Test    Test Install Apk

Test Uninstall Application
    [Documentation]    Tests application uninstallation
    ...                - Navigates through settings
    ...                - Performs uninstallation
    ...                - Verifies complete removal
    [Tags]    uninstallation    smoke
    Execute Test With Retry    Execute Uninstall Application Test    Test Uninstall Application




