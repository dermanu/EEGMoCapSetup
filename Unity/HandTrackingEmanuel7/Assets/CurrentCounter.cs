using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class CurrentCounter : MonoBehaviour
{

    public TMP_Text counterText;

    // Start is called before the first frame update
    void Start()
    {
        counterText.text = "0";
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void setCounter(string newCounter)
    {
        counterText.text = newCounter;
    }

    public void resetCounter()
    {
        counterText.text = "0";
    }
}
