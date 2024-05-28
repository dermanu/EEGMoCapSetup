using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Calibrate : MonoBehaviour
{
    public GameObject rHandRef = null;
    public GameObject vrActivities = null;
    public GameObject buttons = null;
    public GameObject vrCamera = null;

    void Start()
    {
        if (rHandRef == null || vrActivities == null || buttons == null || vrCamera == null)
        {
            Debug.LogError("Some GameObject used in Calibrate is wrongfully null");
        }
    }

    public void calibrate()
    {
        // Set position of vrActivities based on the difference between handRef and calibration square
        vrActivities.transform.rotation = Quaternion.Euler(0, vrCamera.transform.eulerAngles.y, 0);
        vrActivities.transform.position += (rHandRef.transform.position - transform.position);
        Debug.Log("Calibrated!");


        // Disable this object and enable buttons
        gameObject.SetActive(false);
        buttons.SetActive(true);
    }

    public void recalibrate()
    {
        //Enable gameobjects to signal recalibration
        gameObject.SetActive(true);
        buttons.SetActive(false);
    }
}

