using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;


public class ButtonInteractionCounter : MonoBehaviour
{
    public GameObject LSLManager = null;
    public GameObject counterText = null;
    public Button counterButton = null;

    private static int counter = 0;

    // Start is called before the first frame update
    void Start()
    {
        if (LSLManager == null)
        {
            Debug.LogError("LSLManager must be set");
            return;
        }
        if (counterText == null)
        {
            Debug.LogError("counterText must be set");
            return;
        }
        if (counterButton == null)
        {
            Debug.LogError("counterButton must be set");
            return;
        }

        counterButton.onClick.AddListener(buttonHandler);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnDisable()
    {
        counter = 0;
    }

    private void buttonHandler()
    {
        //Button is pressed, push next count to LSL and update counter
        //LSLManager.GetComponent<LSLOutletTriggerEvent>().pushSample(counter.ToString());
        counterText.GetComponent<CurrentCounter>().setCounter((counter + 1).ToString()); //Normal people counting for readability
        counter++;
    }
}
