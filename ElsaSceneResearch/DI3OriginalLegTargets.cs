using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
public static class DI3OriginalLegTargets {
 static string DataSource="passive";
 [Serializable] public class Frame {public int processor;public float time;public float[] start,mid,end,target;}
 [Serializable] public class Data {public string scope;public Frame[] frames;}
 static Vector3 V(float[] a,float offset){return new Vector3(a[1]+offset,.92f-a[2],a[0]);}
 static void Folder(string s){if(AssetDatabase.IsValidFolder(s))return;Folder(Path.GetDirectoryName(s).Replace('\\','/'));AssetDatabase.CreateFolder(Path.GetDirectoryName(s).Replace('\\','/'),Path.GetFileName(s));}
 [MenuItem("Tools/DI3 Static Converter/Research/Create Original Idle Leg Target Diagnostics")]
 public static void Create(){try{var p=Build();Selection.activeObject=AssetDatabase.LoadAssetAtPath<GameObject>(p+"/OriginalLegTargets.prefab");}catch(Exception e){Debug.LogException(e);}}
 static void Curves(AnimationClip c,string path,string prefix,float[] times,Vector4[] values,int count){string[] axes={"x","y","z","w"};for(int k=0;k<count;k++){int j=k;var keys=times.Select((t,i)=>new Keyframe(t,values[i][j])).ToArray();var curve=new AnimationCurve(keys);for(int i=0;i<keys.Length;i++){AnimationUtility.SetKeyLeftTangentMode(curve,i,AnimationUtility.TangentMode.Linear);AnimationUtility.SetKeyRightTangentMode(curve,i,AnimationUtility.TangentMode.Linear);}AnimationUtility.SetEditorCurve(c,EditorCurveBinding.FloatCurve(path,typeof(Transform),prefix+"."+axes[k]),curve);}}
 public static string Build(){
  var data=JsonUtility.FromJson<Data>(File.ReadAllText("Assets/DI3OriginalLegResearch/Editor/original-leg-targets-"+DataSource+".json"));
  Folder("Assets/ElsaOriginalLegResearch");var folder=AssetDatabase.GenerateUniqueAssetPath("Assets/ElsaOriginalLegResearch/OriginalTargetsDiagnostic_"+DataSource);Folder(folder);
  var scene=EditorSceneManager.NewPreviewScene();var root=new GameObject("NativeIK_CONTROLLED_TARGETS_NOT_ORIGINAL_ANIMATION");SceneManager.MoveGameObjectToScene(root,scene);
  try{
   var shader=Shader.Find("Universal Render Pipeline/Unlit")??Shader.Find("Unlit/Color");var colors=new[]{Color.white,Color.cyan,new Color(1,.5f,0)};var mats=new Material[3];for(int i=0;i<3;i++){mats[i]=new Material(shader);mats[i].color=colors[i];if(mats[i].HasProperty("_BaseColor"))mats[i].SetColor("_BaseColor",colors[i]);AssetDatabase.CreateAsset(mats[i],folder+"/Color"+i+".mat");}
   var clip=new AnimationClip{name="OriginalIdleTargets_PartialScaleFixture",frameRate=30};float maxError=0;
   foreach(int id in new[]{408,412}){
    var fs=data.frames.Where(f=>f.processor==id).OrderBy(f=>f.time).ToArray();if(fs.Length!=(DataSource=="active"?127:186))throw new Exception("Sample count");var times=fs.Select(f=>f.time).ToArray();float offset=id==408?-.45f:.45f;
    var points=new[]{fs.Select(f=>V(f.start,offset)).ToArray(),fs.Select(f=>V(f.mid,offset)).ToArray(),fs.Select(f=>V(f.end,offset)).ToArray(),fs.Select(f=>V(f.target,offset)).ToArray()};
    for(int k=0;k<4;k++){var g=GameObject.CreatePrimitive(k==3?PrimitiveType.Cube:PrimitiveType.Sphere);g.name="Leg"+id+"_Point"+k;SceneManager.MoveGameObjectToScene(g,scene);g.transform.SetParent(root.transform,false);g.transform.localScale=Vector3.one*(k==3?.027f:.035f);g.GetComponent<Renderer>().sharedMaterial=mats[k==2?1:k==3?2:0];UnityEngine.Object.DestroyImmediate(g.GetComponent<Collider>());Curves(clip,g.name,"m_LocalPosition",times,points[k].Select(v=>(Vector4)v).ToArray(),3);}
    for(int k=0;k<2;k++){var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name="Leg"+id+"_Segment"+k;SceneManager.MoveGameObjectToScene(g,scene);g.transform.SetParent(root.transform,false);g.GetComponent<Renderer>().sharedMaterial=mats[0];UnityEngine.Object.DestroyImmediate(g.GetComponent<Collider>());var ps=new List<Vector4>();var qs=new List<Vector4>();var ss=new List<Vector4>();for(int j=0;j<fs.Length;j++){var a=points[k][j];var b=points[k+1][j];var q=Quaternion.FromToRotation(Vector3.up,b-a);ps.Add((a+b)*.5f);qs.Add(new Vector4(q.x,q.y,q.z,q.w));ss.Add(new Vector3(.012f,Vector3.Distance(a,b),.012f));}Curves(clip,g.name,"m_LocalPosition",times,ps.ToArray(),3);Curves(clip,g.name,"m_LocalRotation",times,qs.ToArray(),4);Curves(clip,g.name,"m_LocalScale",times,ss.ToArray(),3);}
    for(int j=0;j<fs.Length;j++)maxError=Mathf.Max(maxError,Vector3.Distance(points[2][j],points[3][j]));
   }
   if(float.IsNaN(maxError)||maxError>5e-5f)throw new Exception("Endpoint error "+maxError);clip.EnsureQuaternionContinuity();var settings=AnimationUtility.GetAnimationClipSettings(clip);settings.loopTime=true;AnimationUtility.SetAnimationClipSettings(clip,settings);AssetDatabase.CreateAsset(clip,folder+"/ControlledTargets.anim");var controller=AnimatorController.CreateAnimatorControllerAtPath(folder+"/ControlledTargets.controller");controller.AddMotion(clip);var animator=root.AddComponent<Animator>();animator.runtimeAnimatorController=controller;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
   var label=new GameObject("Explanation");SceneManager.MoveGameObjectToScene(label,scene);label.transform.SetParent(root.transform,false);label.transform.position=new Vector3(0,1.15f,0);var text=label.AddComponent<TextMesh>();text.text="SOURCE "+DataSource.ToUpper()+" IDLE TARGETS\nPARTIAL LEG GRAPH - SCALE FIXTURE\nOrange: target    Cyan: solved ankle";text.anchor=TextAnchor.MiddleCenter;text.characterSize=.025f;text.fontSize=32;
   var camObject=new GameObject("Camera");SceneManager.MoveGameObjectToScene(camObject,scene);camObject.transform.SetParent(root.transform,false);var camera=camObject.AddComponent<Camera>();camObject.tag="MainCamera";camObject.transform.position=new Vector3(0,.55f,-3);camObject.transform.rotation=Quaternion.identity;camera.orthographic=true;camera.orthographicSize=.85f;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.035f,.045f,.06f);
   clip.SampleAnimation(root,0);PrefabUtility.SaveAsPrefabAsset(root,folder+"/OriginalLegTargets.prefab");
   File.WriteAllText(folder+"/README.txt",data.scope+"\nDrag OriginalLegTargets.prefab into an empty scene and press Play. Includes camera.\nSampled ankle-target error="+maxError+"\nOriginal idle targets with explicit scale-compensation fixture; original skin metadata assignment unresolved.\n");AssetDatabase.SaveAssets();return folder;
  }finally{EditorSceneManager.ClosePreviewScene(scene);}
 }
 public static void BatchValidate(){try{DataSource="active";Build();DataSource="passive";var p=Build();File.WriteAllText("original-leg-targets-validation.txt",p+"\n"+File.ReadAllText(p+"/README.txt"));var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);var instance=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(p+"/OriginalLegTargets.prefab"),scene);var a=instance.GetComponent<Animator>();a.Rebind();a.Update(0);var point=instance.transform.Find("Leg408_Point2");var start=point.localPosition;a.Update(2);if(Vector3.Distance(start,point.localPosition)<.00001f)throw new Exception("Saved Animator did not bend");if(SystemInfo.graphicsDeviceType!=UnityEngine.Rendering.GraphicsDeviceType.Null){var camera=instance.GetComponentInChildren<Camera>();var rt=new RenderTexture(1200,800,24);var image=new Texture2D(1200,800,TextureFormat.RGB24,false);camera.targetTexture=rt;camera.Render();RenderTexture.active=rt;image.ReadPixels(new Rect(0,0,1200,800),0,0);image.Apply();File.WriteAllBytes(@"F:/DisneyInfinityPortalTest/ElsaSceneResearch/original-leg-targets.png",image.EncodeToPNG());camera.targetTexture=null;RenderTexture.active=null;rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(image);}Debug.Log("ORIGINAL_LEG_TARGETS_PASS");EditorApplication.Exit(0);}catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
}
