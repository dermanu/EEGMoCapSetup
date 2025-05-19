using UnityEngine;
using System.Collections;

// Taken from https://docs.unity3d.com/ScriptReference/AudioSettings-dspTime.html 
// The code example shows how to implement a metronome that procedurally generates the click sounds via the OnAudioFilterRead callback.
// While the game is paused or suspended, this time will not be updated and sounds playing will be paused. Therefore developers of music scheduling routines do not have to do any rescheduling after the app is unpaused

[RequireComponent(typeof(AudioSource))]
public class Metronome : MonoBehaviour
{
    public double bpm = 140.0F;
    public float gain = 0.5F;
    public int signatureHi = 4;
    public int signatureLo = 4;
    private double nextTick = 0.0F;
    private float amp = 0.0F;
    private float phase = 0.0F;
    private double sampleRate = 0.0F;
    private int accent;
    private bool running = false;
    private double runFor = -1.0;
    private double started = -1.0;
    //private double timer; // Timer to keep track of time since the last beat

    private string currentMode= "";

    //private int currentTick = 0;
    void Start()
    {
        accent = signatureHi;
        double startTick = AudioSettings.dspTime;
        sampleRate = AudioSettings.outputSampleRate;
        nextTick = startTick * sampleRate;

    }

    private void FixedUpdate()
    {
        if (!running)
            return;

        if (started <= 0) //Has not yet started, need to set start
        {
            Debug.Log("Metronome started, will tick for " + runFor + "s");
            started = Time.time;
        }
        
        if ((started + runFor) < Time.time) //If run longer than given timelimt (runFor), stop metronome
        {
            timeOut();
            return;
        }
    }

    void OnAudioFilterRead(float[] data, int channels)
    {
        if (!running)
            return;

        double samplesPerTick = sampleRate * 60.0F / bpm * 4.0F / signatureLo;
        double sample = AudioSettings.dspTime * sampleRate;
        int dataLen = data.Length / channels;
        int n = 0;
        while (n < dataLen)
        {
            float x = gain * amp * Mathf.Sin(phase);
            int i = 0;
            while (i < channels)
            {
                data[n * channels + i] += x;
                i++;
            }
            while (sample + n >= nextTick)
            {
                nextTick += samplesPerTick;
                amp = 1.0F;
                if (++accent > signatureHi)
                {
                    accent = 1;
                    amp *= 2.0F;
                }
            }
            phase += amp * 0.3F;
            amp *= 0.993F;
            n++;
        }
    }

    public void run(double timeLimit)
    {
        running = true;
        runFor = timeLimit;
    }

    public void interrupt()
    {
        Debug.Log("Metronome interrupted...");

        running = false;
        started = -1.0;
        runFor = -1.0;
        //currentTick = 0;
    }

    public void timeOut()
    {
        Debug.Log("Metronome timed out...");

        running = false;
        started = -1.0;
        runFor = -1.0;
        //currentTick = 0;
    }

    public void setCurrentMode(string newMode)
    {
        currentMode = newMode;
    }
}