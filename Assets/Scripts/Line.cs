using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using UnityEngine;

public class Line : MonoBehaviour {
    public GameObject Shoulder; // The fixed point, represented as a sphere in the scene
    public GameObject DynamicPoint1; // The first dynamic point, represented as an empty game object in the scene
    public GameObject DynamicPoint2; // The second dynamic point, represented as an empty game object in the scene
    public int thickness = 5; // The thickness of the line
    public Material lineMaterial; // The material to use for the line
    private LineRenderer lineRenderer;
    private float Ex = 0f;
    private float Ey = 0f;
    private float Wx = 0f;
    private float Wy = 0f;

    private void Start() {
        lineRenderer = gameObject.AddComponent<LineRenderer>();
        lineRenderer.startWidth = thickness;
        lineRenderer.endWidth = thickness;
        lineRenderer.material = lineMaterial;
        lineRenderer.positionCount = 3;

        // Set initial positions of DynamicPoint1 and DynamicPoint2
        DynamicPoint1.transform.position = Shoulder.transform.position;
        DynamicPoint2.transform.position = Shoulder.transform.position;

        string activateScript = @"C:\Users\RaPIDadmin\anaconda3\Scripts\activate.bat";

        // specify the name of the Anaconda environment
        string environmentName = "py38";

        // specify the path to the Python script that you want to run
        string scriptPath = @"C:\Users\RaPIDadmin\CharacterJoints\RGBD.py";

        // specify the command to activate the Anaconda environment and run the Python script
        string command = $@"call {activateScript} {environmentName} && python -u {scriptPath}";

        // start a new process to run the command
        Process process = new Process();
        process.StartInfo.FileName = "cmd.exe";
        process.StartInfo.Arguments = $@"/c ""{command}""";
        process.StartInfo.UseShellExecute = false;
        process.StartInfo.RedirectStandardOutput = true;
        process.StartInfo.RedirectStandardError = true;

        process.OutputDataReceived += new DataReceivedEventHandler((sender, e) =>
        {
            if (e.Data.Contains("Entry"))
            {
                string[] data = e.Data.Split(',');
                Ex = 0.01f*float.Parse(data[1]);
                Ey = 0.01f*float.Parse(data[2]);
                Wx = 0.01f*float.Parse(data[4]);
                Wy = 0.01f*float.Parse(data[5]);
                UnityEngine.Debug.Log(Ex+","+Ey+","+Wx+","+Wy);
                // Update the positions of DynamicPoint1 and DynamicPoint2
                float distance1 = 1.0f; // set the desired distance between Shoulder and DynamicPoint1
                float distance2 = 1.0f; // set the desired distance between DynamicPoint1 and DynamicPoint2
                Vector3 fixedPoint = Shoulder.transform.position;
                Vector3 dynamicPoint1 = fixedPoint + distance1 * new Vector3(Ex, Ey, 0).normalized;
                Vector3 dynamicPoint2 = dynamicPoint1 + distance2 * new Vector3(Wx, Wy, 0).normalized;
                DynamicPoint1.transform.position = dynamicPoint1;
                DynamicPoint2.transform.position = dynamicPoint2;

                
            }
            else{
                Ex = 1.0f;
                Ey = 1.0f;
                Wx = 1.0f;
                Wy = 1.0f;
                // Update the positions of DynamicPoint1 and DynamicPoint2
                float distance1 = 1.0f; // set the desired distance between Shoulder and DynamicPoint1
                float distance2 = 1.0f; // set the desired distance between DynamicPoint1 and DynamicPoint2
                Vector3 fixedPoint = Shoulder.transform.position;
                Vector3 dynamicPoint1 = fixedPoint + distance1 * new Vector3(Ex, Ey, 0).normalized;
                Vector3 dynamicPoint2 = dynamicPoint1 + distance2 * new Vector3(Wx, Wy, 0).normalized;
                DynamicPoint1.transform.position = dynamicPoint1;
                DynamicPoint2.transform.position = dynamicPoint2;
                
            }
        });


        process.ErrorDataReceived += new DataReceivedEventHandler((sender, e) =>
        {
            if (!string.IsNullOrEmpty(e.Data))
            {
                UnityEngine.Debug.LogError("Python error: " + e.Data);
            }
        });

        process.Start();
        process.BeginErrorReadLine();
        process.BeginOutputReadLine();
    }

       private void FixedUpdate() {

                // Update the Line Renderer component
                lineRenderer.SetPosition(0, Shoulder.transform.position);
                lineRenderer.SetPosition(1, DynamicPoint1.transform.position);
                lineRenderer.SetPosition(2, DynamicPoint2.transform.position);
        }

}
