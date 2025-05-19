using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class Clock : MonoBehaviour
{
    public TMP_Text text = null;
    public double timeRemaining = 10;
    public bool timerIsRunning = false;

    private void Start()
    {
        // Starts the timer automatically
        //timerIsRunning = true;
        text.text = "00:00";
    }

    public void run(double time)
    {
        timeRemaining = time;
        timerIsRunning = true;
    }

    public void interrupt()
    {
        timerIsRunning = false;
        text.text = "00:00";
    }

    void FixedUpdate()
    {
        if (timerIsRunning)
        {
            if (timeRemaining > 0)
            {
                timeRemaining -= Time.deltaTime;
                DisplayTime(timeRemaining);
            }
            else
            {
                Debug.Log("Time has run out!");
                timeRemaining = 0;
                timerIsRunning = false;
                text.text = "00:00";
            }
        }
    }

    void DisplayTime(double timeToDisplay)
    {
        double minutes = Mathf.FloorToInt((float)(timeToDisplay / 60));
        double seconds = Mathf.FloorToInt((float)(timeToDisplay % 60));
        text.text = string.Format("{0:00}:{1:00}", minutes, seconds);
    }
}
