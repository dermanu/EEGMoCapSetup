using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ClickLogic : MonoBehaviour
{
    public Button fingertappingR, reachingR, fingertappingVR, reachingVR;
    public Button calibrate = null;
    public Button openEyes = null;
    public Button closeEyes = null;
    public GameObject calibrateGO = null;
    public GameObject fingertappingGO = null;
    public GameObject reachingGO = null;
    public GameObject counterText = null;
    public GameObject metronome = null;
    public GameObject lslManager = null;
    public GameObject clockResearcherGO = null;
    public GameObject clockParticipantGO = null;

    [Tooltip("Fingertapping real duration in minutes")]
    public double fingertappingRDuration = 5.0;
    [Tooltip("Reaching real duration in minutes")]
    public double reachingRDuration = 8.0;
    [Tooltip("Fingertapping VR duration in minutes")]
    public double fingertappingVRDuration = 5.0;
    [Tooltip("Reaching VR duration in minutes")]
    public double reachingVRDuration = 8.0;
    [Tooltip("Open eye duration in minutes")]
    public double openEyesDuration = 2;
    [Tooltip("Close eye duration in minutes")]
    public double closeEyesDuration = 2;

    private Button[] allButtons = null;

    private bool buttonIsActive = false;
    private bool calibrated = false;

    private IEnumerator countDownRoutine;

    // Start is called before the first frame update
    void Start()
    {
        if (fingertappingR == null || reachingR == null || fingertappingVR == null || reachingVR == null
            || calibrate == null
            || calibrateGO == null
            || metronome == null 
            || lslManager == null
            || fingertappingGO == null
            || reachingGO == null
            || counterText == null
            || openEyes == null
            || closeEyes == null
            || clockResearcherGO == null
            || clockParticipantGO == null
            )
        {
            Debug.LogError("One of the components in ClickLogic is null");
            return;
        }
        fingertappingR.onClick.AddListener(fingertappingRHandler);
        reachingR.onClick.AddListener(reachingRHandler);
        openEyes.onClick.AddListener(openEyesHandler);
        closeEyes.onClick.AddListener(closeEyesHandler);
        fingertappingVR.onClick.AddListener(fingertappingVRHandler);
        reachingVR.onClick.AddListener(reachingVRHandler);

        calibrate.onClick.AddListener(calibrateHandler);

        allButtons = new[] { fingertappingR, reachingR, fingertappingVR, reachingVR, openEyes, closeEyes };
    }
    
    // Update is called once per frame
    void Update()
    {
        
    }

    private void makeInteractable(Button clickedB, bool interrupted, string mode)
    {
        //Button is pressed and already active, make everything interactable again
        buttonIsActive = false;

        //can interact with buttons again
        foreach (Button b in allButtons)
        {
            if (b.GetComponentInChildren<TMP_Text>().text != clickedB.GetComponentInChildren<TMP_Text>().text)
            {
                b.interactable = true;
            }
        }
        if (interrupted)
        {
            lslManager.GetComponent<LSLOutletTriggerEvent>().pushSample(mode + "eb"); //Notify via lsl that interrupted
            interruptMetronome();
        }
        else
        {
            lslManager.GetComponent<LSLOutletTriggerEvent>().pushSample(mode + "ea"); //Notify via lsl that timed out
            timeoutMetronome();
        }
        return;
    }

    IEnumerator countDown(Button clickedB, double minutes, bool interrupted, string mode)
    {
        yield return new WaitForSeconds((float)(minutes * 60.0));
        Debug.Log("Time ran out for " + mode);
        clockResearcherGO.GetComponent<Clock>().interrupt();
        clockParticipantGO.GetComponent<Clock>().interrupt();
        makeInteractable(clickedB, interrupted, mode);
    }

    private void generalHandler(Button clickedB, double minutes, string mode)
    {
        if (!buttonIsActive)
        {
            //Button is pressed, currently have one active
            Debug.Log("Activated " + mode);
            buttonIsActive = true;

            //cant interact with other buttons anymore
            foreach (Button b in allButtons)
            {
                if (b.GetComponentInChildren<TMP_Text>().text != clickedB.GetComponentInChildren<TMP_Text>().text)
                {
                    b.interactable = false;
                }
            }
            lslManager.GetComponent<LSLOutletTriggerEvent>().pushSample(mode + "s"); //Notify via lsl that started
            startMetronome(minutes * 60.0, mode); //Need timeLimit in seconds
            clockResearcherGO.GetComponent<Clock>().run(minutes * 60);
            clockParticipantGO.GetComponent<Clock>().run(minutes * 60);
            countDownRoutine = countDown(clickedB, minutes, false, mode);
            StartCoroutine(countDownRoutine); //Make stuff interactable again if timeout
            return;
        }

        if (buttonIsActive)
        {
            Debug.Log("Manually deactivated " + mode);
            StopCoroutine(countDownRoutine); //Assume countDownRoutine is always set because of code above
            clockResearcherGO.GetComponent<Clock>().interrupt();
            clockParticipantGO.GetComponent<Clock>().interrupt();
            makeInteractable(clickedB, true, mode); //Make stuff interactable again in explicitly stopped
        }
    }

    private void vrHandler(Button clickedB, double minutes, string mode)
    {
        if (!buttonIsActive)
        {
            if (mode.Equals("fv"))
            {
                fingertappingGO.SetActive(true);
            }
            if (mode.Equals("rv"))
            {
                reachingGO.SetActive(true);
            }
        }
        if (buttonIsActive)
        {
            if (mode.Equals("fv"))
            {
                fingertappingGO.SetActive(false);
            }
            if (mode.Equals("rv"))
            {
                reachingGO.SetActive(false);
            }
        }
        generalHandler(clickedB, minutes, mode);
        counterText.GetComponent<CurrentCounter>().setCounter(0.ToString());
    }

    void fingertappingRHandler()
    {
        Debug.Log("Pressed fingertapping (real)");
        generalHandler(fingertappingR, fingertappingRDuration, "fr");
    }

    void reachingRHandler()
    {
        Debug.Log("Pressed reaching (real)");
        generalHandler(reachingR, reachingRDuration, "rr");
    }

    void fingertappingVRHandler()
    {
        Debug.Log("Pressed fingertapping (VR)");
        //vrHandler(fingertappingVR, fingertappingVRDuration, "fv");
        generalHandler(fingertappingVR, fingertappingVRDuration, "fv");
    }

    void reachingVRHandler()
    {
        Debug.Log("Pressed reaching (VR)");
        //vrHandler(reachingVR, reachingVRDuration, "rv");
        generalHandler(reachingVR, reachingVRDuration, "rv");
    }

    void openEyesHandler()
    {
        Debug.Log("Pressed openEyes");
        generalHandler(openEyes, openEyesDuration, "oe");
    }

    void closeEyesHandler()
    {
        Debug.Log("Pressed closeEyes");
        generalHandler(closeEyes, closeEyesDuration, "ce");
    }

    void startMetronome(double timeLimit, string mode)
    {
        metronome.GetComponent<Metronome>().setCurrentMode(mode);
        metronome.GetComponent<Metronome>().run(timeLimit);
    }

    void interruptMetronome()
    {
        metronome.GetComponent<Metronome>().interrupt();
    }

    void timeoutMetronome()
    {
        metronome.GetComponent<Metronome>().timeOut();
    }

    void calibrateHandler()
    {
        if (!calibrated)
        {
            calibrateGO.GetComponent<Calibrate>().calibrate();
            calibrate.GetComponentInChildren<TMP_Text>().text = "Recalibrate";
            calibrated = true;
            return;
        }
        if (calibrated)
        {
            calibrateGO.GetComponent<Calibrate>().recalibrate();
            calibrate.GetComponentInChildren<TMP_Text>().text = "Calibrate";
            calibrated = false;
            return;
        }
    }
}
