using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

public class InteractionTest : XRSimpleInteractable
{
    public GameObject LSLManager = null;
    public GameObject counterText = null;

    private static int counter = 0;
    private bool allowInteract = true;
    // Start is called before the first frame update
    void Start()
    {
        if (LSLManager == null)
        {
            Debug.LogError("LSLManager must be set");
        }
        if (counterText == null)
        {
            Debug.LogError("counterText must be set");
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnDisable()
    {
        counter = 0;
    }

    // Override the OnSelectEntered method to define behavior when the object is selected
    protected override void OnSelectEntered(SelectEnterEventArgs args)
    {
        base.OnSelectEntered(args);
        Debug.Log("Interacted");
        return;
        if (!allowInteract) return;
        allowInteract = false;
        
        //Button is pressed, push next count to LSL and update counter
        LSLManager.GetComponent<LSLOutletTriggerEvent>().pushSample(counter.ToString());
        counterText.GetComponent<CurrentCounter>().setCounter((counter + 1).ToString()); //Normal people counting for readability
        counter++;
    }

    protected override void OnSelectExited(SelectExitEventArgs args)
    {
        base.OnSelectExited(args);
        Debug.Log("Interacted exit");
        return;
        if (allowInteract) return;
        allowInteract = true;
    }

    protected override void OnHoverEntered(HoverEnterEventArgs args)
    {
        base.OnHoverEntered(args);
        GetComponent<Renderer>().material.color = Color.red;
    }
}
