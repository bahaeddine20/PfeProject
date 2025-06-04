*** Settings ***
Documentation    Tests for audio recording and playback functionality
...              - Verifies audio recording capabilities
...              - Verifies audio playback capabilities
...              - Supports both French and English interfaces
Library    Process
Library    BuiltIn
Library    OperatingSystem
Library    Integration.py
Library    TestAudio.py

Library    Collections
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
# Configuration des retries
${MAX_RETRIES}    3
${RETRY_DELAY}    2s
${QUICK_WAIT}     2s

# Audio Configuration
${DEFAULT_RECORD_DURATION}    34
${DEFAULT_OUTPUT_FILE}        ${CURDIR}${/}test.wav
${DEFAULT_SAMPLE_RATE}        44100

# Language Configuration
&{LANG_FR}    System=Système    Setting=Paramètres    Audio=Enregistrement    Record=START    Stop=STOP    Play=Lire
&{LANG_EN}    System=System    Setting=Settings    Audio=Recording    Record=START    Stop=STOP    Play=Play



*** Keywords ***
Démarrer Driver
    Log    Tentative d'initialisation du driver Appium...
    Log    URL Appium: ${CURDIR}${/}..${/}config.py
    ${result}=    Run Keyword And Ignore Error    setup driver    ${Device}
    ${status}    ${driver}=    Set Variable    ${result}
    IF    '${status}' == 'FAIL'
        Log    Échec de l'initialisation du driver: ${driver}
        Fail    Impossible d'initialiser le driver Appium: ${driver}
    END
    Set Suite Variable    ${driver}
    Log    Driver Appium initialisé avec succès

Fermer Driver
    ${driver_exists}=    Run Keyword And Return Status    Variable Should Exist    ${driver}
    IF    ${driver_exists}
        ${close_success}=    Run Keyword And Return Status    Close Driver    ${driver}
        IF    not ${close_success}
            Log    Warning: Impossible de fermer proprement le driver Appium
        END
    END

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

Initialize Language Settings
    ${lang}=    Get System Language    ${Device}
    ${lang_dict}=    Set Variable If    '${lang}' == 'fr'    ${LANG_FR}    ${LANG_EN}
    Set Suite Variable    ${LANG_DICT}    ${lang_dict}

Get Localized Text
    [Arguments]    ${key}
    RETURN    ${LANG_DICT.${key}}

Navigate To Audio App
    Start Activity Code    ${driver}     com.example.audioapplicationtest/.MainActivity
    Sleep    22s
    ${current_activity}=    Print Activity    ${driver}

Wait For Record Button
    [Arguments]    ${timeout}=10s
    Wait Until Keyword Succeeds    ${timeout}    ${QUICK_WAIT}
    ...    Check Element Exists    ${driver}    //android.widget.Button[@text="START"]

Click Element By Id
    [Arguments]    ${driver}    ${element_id}
    ${success}=    Run Keyword And Return Status    click_element_by_id    ${driver}    ${element_id}
    Should Be True    ${success}    Impossible de cliquer sur l'élément avec l'ID: ${element_id}

Click Record Button
    Wait For Record Button
    ${button_exists}=    check_element_exists    ${driver}    //android.widget.Button[@text="START"]
    Should Be True    ${button_exists}    Le bouton START n'est pas visible
    ${success}=    Run Keyword And Return Status    click_element_by_xpath_bounds    ${driver}    //android.widget.Button[@text="START"]
    Should Be True    ${success}    Impossible de cliquer sur le bouton START

Click Stop Button
    ${button_exists}=    check_element_exists    ${driver}    //android.widget.Button[@text="STOP"]
    Should Be True    ${button_exists}    Le bouton STOP n'est pas visible
    ${success}=    Run Keyword And Return Status    click_element_by_xpath_bounds    ${driver}    //android.widget.Button[@text="STOP"]
    Should Be True    ${success}    Impossible de cliquer sur le bouton STOP

Get Element Bounds
    [Arguments]    ${driver}    ${element}
    ${bounds_str}=    Run Keyword And Return Status    ${element}.get_attribute    bounds
    Should Be True    ${bounds_str}    Impossible de récupérer les bounds de l'élément
    RETURN    ${bounds_str}

Get Audio File Duration
    [Arguments]    ${audio_file}=${DEFAULT_OUTPUT_FILE}
    ${duration}=    get_audio_duration    ${driver}    ${audio_file}
    Should Not Be Equal As Numbers    ${duration}    0    Impossible d'obtenir la durée du fichier audio
    RETURN    ${duration}

Start Audio Recording And Playback
    [Arguments]    ${audio_file}=${DEFAULT_OUTPUT_FILE}
    Log    Démarrage de l'enregistrement audio...
    # Obtenir la durée du fichier audio à lire
    ${duration}=    Get Audio File Duration    ${audio_file}
    Log    Durée du fichier audio à lire: ${duration} secondes

    Click Record Button    # Démarrer l'enregistrement avec START
    Sleep    2s

    ${success}=    Run Keyword And Return Status    play_audio    ${driver}    ${audio_file}
    Should Be True    ${success}    La lecture audio a échoué

    # Attendre que la lecture soit terminée
    Sleep    ${duration}s
    
    # Arrêter l'enregistrement avec STOP
    Click Stop Button

Verify Audio Recording
    Initialize Language Settings
    Navigate To Audio App
    Start Audio Recording And Playback
    ${result}=    Compare Audio Files    ${DEFAULT_OUTPUT_FILE}
    Log    Résultat de la comparaison: ${result}

Compare Audio Files
    [Arguments]    ${original_audio}
    ${test_passed}    ${metrics}=    Compare With Latest Recorded    ${original_audio}
    
    # Log all metrics for debugging
    Log    SNR: ${metrics['snr']} dB (seuil: 20 dB)
    Log    Corrélation: ${metrics['correlation']} (seuil: 0.9)
    Log    MOS: ${metrics['mos']}/5 (seuil: 3.0)
    Log    Clarté: ${metrics['clarity']} (seuil: 0.8)
    
    # Test is considered passed only if ALL critical metrics meet their thresholds
    ${snr_ok}=    Evaluate    ${metrics['snr']} >= 20
    ${correlation_ok}=    Evaluate    ${metrics['correlation']} >= 0.9
    ${mos_ok}=    Evaluate    ${metrics['mos']} >= 3.0
    ${clarity_ok}=    Evaluate    ${metrics['clarity']} >= 0.8
    
    ${test_passed}=    Evaluate    ${snr_ok} and ${correlation_ok} and ${mos_ok} and ${clarity_ok}
    
    IF    not ${test_passed}
        Log    ❌ Test échoué - Métriques critiques non satisfaites
        Fail    Test audio échoué - Vérifiez les métriques dans les logs
    ELSE
        Log    ✅ Test réussi - Toutes les métriques sont satisfaites
    END
    
    RETURN    ${test_passed}    ${metrics}

Click Play Button
    Wait For Record Button
    ${button_exists}=    check_element_exists    ${driver}    //android.widget.Button[@text="PLAY TEST WAV"]
    Should Be True    ${button_exists}    Le bouton PLAY TEST WAV n'est pas visible
    ${success}=    Run Keyword And Return Status    click_element_by_xpath_bounds    ${driver}    //android.widget.Button[@text="PLAY TEST WAV"]
    Should Be True    ${success}    Impossible de cliquer sur le bouton START


Navigate To Audio Player App
    Start Activity Code    ${driver}     com.example.audioapplicationtest/.AudioPlayerActivity
    Sleep    22s
    ${current_activity}=    Print Activity    ${driver}


Compare Audio Files Play
    [Arguments]    ${original_audio}
    ${test_passed}    ${metrics}=    Compare With Latest Recorded Play   ${original_audio}

    # Log all metrics for debugging
    Log    SNR: ${metrics['snr']} dB (seuil: 20 dB)
    Log    Corrélation: ${metrics['correlation']} (seuil: 0.9)
    Log    MOS: ${metrics['mos']}/5 (seuil: 3.0)
    Log    Clarté: ${metrics['clarity']} (seuil: 0.8)

    # Inclure l'image dans le rapport
    ${plot_file}=    Set Variable    ${metrics['plot_file']}
    Log    <img src="${plot_file}" width="800px"/>

    # Test is considered passed only if ALL critical metrics meet their thresholds
    ${snr_ok}=    Evaluate    ${metrics['snr']} >= 20
    ${correlation_ok}=    Evaluate    ${metrics['correlation']} >= 0.9
    ${mos_ok}=    Evaluate    ${metrics['mos']} >= 3.0
    ${clarity_ok}=    Evaluate    ${metrics['clarity']} >= 0.8

    ${test_passed}=    Evaluate    ${snr_ok} and ${correlation_ok} and ${mos_ok} and ${clarity_ok}

    IF    not ${test_passed}
        Log    ❌ Test échoué - Métriques critiques non satisfaites
        Fail    Test audio échoué - Vérifiez les métriques dans les logs
    ELSE
        Log    ✅ Test réussi - Toutes les métriques sont satisfaites
    END

    RETURN    ${test_passed}    ${metrics}

*** Test Cases ***
Test install
        Install Apk    ${driver}        AudioTestApplication.apk

        Close Activity Robot      ${driver}     com.example.audioapplicationtest

Test Audio Recording And Playback
    [Documentation]    Verifies audio recording and playback functionality
    ...                - Navigates to audio recording app
    ...                - Records audio for a specified duration
    ...                - Plays back the recorded audio
    ...                - Supports both French and English interfaces
    [Tags]    audio    recording    playback
    Close Activity       ${driver}     com.example.audioapplicationtest/.AudioPlayerActivity
    Sleep    10s
    Execute Test With Retry    Verify Audio Recording    Test Audio Recording And Playback


Test Audio Player And Playback
    [Documentation]    Verifies audio recording and playback functionality
    ...                - Navigates to audio recording app
    ...                - Records audio for a specified duration
    ...                - Plays audio
    ...                - Supports both French and English interfaces
    [Tags]    audio    recording    playback
    Navigate To Audio Player App

    ${recording_success}=    Record Audio    ${driver}     23    # Démarre l'enregistrement
    Should Be True    ${recording_success}    L'enregistrement audio a échoué
    Sleep    1s    # Petit délai pour s'assurer que l'enregistrement a bien démarré
    Click Play Button    # Démarre la lecture immédiatement après
    Sleep    22s
    Compare Audio Files Play       ${CURDIR}${/}test.wav




