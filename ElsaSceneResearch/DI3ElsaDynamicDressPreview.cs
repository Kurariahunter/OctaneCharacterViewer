using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

// Standalone historical-Elsa diagnostic. Does not extend production import support.
public static class DI3ElsaDynamicDressPreview {
 [Serializable] public class Bone { public string name; public int parent; public float[] world; }
 [Serializable] public class Weight { public int[] indices; public float[] values; }
 [Serializable] public class Part { public string name; public int reference; public int[] triangles; }
 [Serializable] public class Model { public string scope; public float[] positions,uvs,normals; public Bone[] bones; public Weight[] weights; public Part[] submeshes; public string[] texture_ids,parent_notes; }
 [Serializable] public class Pose { public string bone; public float[] matrix; }
 [Serializable] public class Sample { public float time; public Pose[] transforms; }
 [Serializable] public class Motion { public string name; public float duration; public Sample[] samples; }
 [Serializable] public class Data { public string scope; public Motion[] clips; public string[] animated_bones; }
 const string Input="Assets/DI3ElsaHeadResearch/Editor/Data";
 const string Warning="BOUNDED NATIVE DRESS SIMULATION: source idle anchors, native DynamicChain and native Aim. Zero external force, reset start, previous-frame local-aim feedback. Complete loader/update order not demonstrated; loop seam not guaranteed. Arms, face and hair remain partial. Independent palette preserves weights/binds. Not Humanoid retargetable.";
 static bool Finite(float x)=>!float.IsNaN(x)&&!float.IsInfinity(x);
 static Matrix4x4 Matrix(float[] a) { if(a==null||a.Length!=16||a.Any(v=>!Finite(v)))throw new InvalidDataException("Invalid matrix");var m=new Matrix4x4();for(int r=0;r<4;r++)for(int c=0;c<4;c++)m[r,c]=a[r*4+c];return m; }
 static void Folder(string path) {if(AssetDatabase.IsValidFolder(path))return;Folder(Path.GetDirectoryName(path).Replace('\\','/'));AssetDatabase.CreateFolder(Path.GetDirectoryName(path).Replace('\\','/'),Path.GetFileName(path));}
 static void SetLocal(Transform t,Matrix4x4 m) {t.localPosition=m.GetColumn(3);t.localRotation=m.rotation;t.localScale=new Vector3(((Vector3)m.GetColumn(0)).magnitude,((Vector3)m.GetColumn(1)).magnitude,((Vector3)m.GetColumn(2)).magnitude);}
 [MenuItem("Tools/DI3 Static Converter/Research/Create Elsa Dynamic Dress Preview")]
 public static void Create() {try {var folder=Build();var scene=AssetDatabase.LoadAssetAtPath<GameObject>(folder+"/Elsa_DynamicDressComparison.prefab");Selection.activeObject=scene;EditorGUIUtility.PingObject(scene);Debug.Log("Elsa corrected torso diagnostic created: "+folder+". Drag its comparison prefab into a test scene and press Play. "+Warning);}catch(Exception e){Debug.LogException(e);} }
 public static string Build() {
  var model=JsonUtility.FromJson<Model>(File.ReadAllText("Assets/DI3ElsaDynamicDressResearch/Editor/elsa-native-dynamic-dress-model.json"));var data=JsonUtility.FromJson<Data>(File.ReadAllText("Assets/DI3ElsaDynamicDressResearch/Editor/elsa-native-dynamic-dress-animation.json"));
  if(model.positions.Length%3!=0||model.weights.Length!=model.positions.Length/3||model.uvs.Length!=model.weights.Length*2)throw new InvalidDataException("Mesh dimensions");
  if(model.positions.Any(v=>!Finite(v))||model.uvs.Any(v=>!Finite(v)))throw new InvalidDataException("Nonfinite mesh");
  Folder("Assets/ElsaDynamicDressResearch");string folder=AssetDatabase.GenerateUniqueAssetPath("Assets/ElsaDynamicDressResearch/DynamicDressDiagnostic");Folder(folder);
  var workingScene=EditorSceneManager.NewPreviewScene();var root=new GameObject("Elsa_DynamicDressNative_DIAGNOSTIC");SceneManager.MoveGameObjectToScene(root,workingScene);Scene testScene=default;Mesh baked=null;RenderTexture rt=null;Texture2D capture=null;
  try {
   var skeleton=new GameObject("Skeleton").transform;skeleton.SetParent(root.transform,false);
   var bones=model.bones.Select(b=>new GameObject(b.name).transform).ToArray();var worlds=model.bones.Select(b=>Matrix(b.world)).ToArray();
   if(model.bones.Select(b=>b.name).Distinct().Count()!=bones.Length)throw new InvalidDataException("Duplicate bones");
   for(int i=0;i<bones.Length;i++) {int parent=model.bones[i].parent;if(parent>=bones.Length||parent==i)throw new InvalidDataException("Bad parent");var seen=new HashSet<int>();int p=i;while(p>=0){if(!seen.Add(p))throw new InvalidDataException("Parent cycle");p=model.bones[p].parent;}bones[i].SetParent(parent<0?skeleton:bones[parent],false);}
   for(int i=0;i<bones.Length;i++){int p=model.bones[i].parent;SetLocal(bones[i],p<0?worlds[i]:worlds[p].inverse*worlds[i]);}
   var mesh=new Mesh{name="Historical Elsa diagnostic mesh"};var vertices=Enumerable.Range(0,model.weights.Length).Select(i=>new Vector3(model.positions[3*i],model.positions[3*i+1],model.positions[3*i+2])).ToArray();mesh.vertices=vertices;
   mesh.uv=Enumerable.Range(0,vertices.Length).Select(i=>new Vector2(model.uvs[2*i],model.uvs[2*i+1])).ToArray();mesh.subMeshCount=model.submeshes.Length;
   for(int i=0;i<model.submeshes.Length;i++){var tri=model.submeshes[i].triangles;if(tri.Length%3!=0||tri.Any(x=>x<0||x>=vertices.Length))throw new InvalidDataException("Bad triangles");mesh.SetTriangles(tri,i);}
   mesh.boneWeights=model.weights.Select(w=>{if(w.indices.Length!=4||w.values.Length!=4||w.indices.Any(i=>i<0||i>=bones.Length)||w.values.Any(v=>!Finite(v)||v<0)||Mathf.Abs(w.values.Sum()-1)>0.00001f)throw new InvalidDataException("Bad weight");return new BoneWeight{boneIndex0=w.indices[0],boneIndex1=w.indices[1],boneIndex2=w.indices[2],boneIndex3=w.indices[3],weight0=w.values[0],weight1=w.values[1],weight2=w.values[2],weight3=w.values[3]};}).ToArray();
   mesh.bindposes=worlds.Select(m=>m.inverse).ToArray();if(model.normals==null||model.normals.Length!=vertices.Length*3)throw new InvalidDataException("Missing source normals");mesh.normals=Enumerable.Range(0,vertices.Length).Select(i=>new Vector3(model.normals[i*3],model.normals[i*3+1],model.normals[i*3+2]).normalized).ToArray();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,folder+"/ElsaMesh.asset");
   var go=new GameObject("Skin");go.transform.SetParent(root.transform,false);var skin=go.AddComponent<SkinnedMeshRenderer>();skin.sharedMesh=mesh;skin.bones=bones;skin.rootBone=skeleton;skin.updateWhenOffscreen=true;
   Shader shader=UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline!=null?Shader.Find("Universal Render Pipeline/Lit"):Shader.Find("Standard");if(shader==null)throw new InvalidOperationException("Preview shader unavailable");var mats=new List<Material>();
   for(int i=0;i<model.submeshes.Length;i++) {var mat=new Material(shader){name="Elsa slot "+i};int ti=model.submeshes[i].reference*2;Texture2D texture=null;if(ti>=0&&ti<model.texture_ids.Length)texture=AssetDatabase.LoadAssetAtPath<Texture2D>(Input+"/Textures/"+model.texture_ids[ti]+".dds");if(texture!=null){mat.mainTexture=texture;if(mat.HasProperty("_BaseMap"))mat.SetTexture("_BaseMap",texture);}mat.SetFloat("_Glossiness",0.15f);AssetDatabase.CreateAsset(mat,folder+"/Material"+i+".mat");mats.Add(mat);}skin.sharedMaterials=mats.ToArray();
   var bind=bones.Select(b=>(p:b.localPosition,q:b.localRotation,s:b.localScale)).ToArray();baked=new Mesh();skin.BakeMesh(baked);float bindError=baked.vertices.Select((v,i)=>Vector3.Distance(v,vertices[i])).Max();if(bindError>0.0001f)throw new InvalidOperationException("Bind deformation error "+bindError);
   var prefabs=new List<GameObject>();var reports=new List<string>();
   foreach(var motion in data.clips) {
    foreach(var pair in bones.Select((b,i)=>(b,i))){pair.b.localPosition=bind[pair.i].p;pair.b.localRotation=bind[pair.i].q;pair.b.localScale=bind[pair.i].s;}
    if(motion.samples.Length<2||motion.duration<=0)throw new InvalidDataException("Invalid samples");var clip=new AnimationClip{name=motion.name+"_DIAGNOSTIC",frameRate=60};
    foreach(string name in data.animated_bones) {
     var bone=bones.Single(b=>b.name==name);string path=AnimationUtility.CalculateTransformPath(bone,root.transform);string[] properties={"localPosition.x","localPosition.y","localPosition.z","localRotation.x","localRotation.y","localRotation.z","localRotation.w","localScale.x","localScale.y","localScale.z"};var curves=properties.Select(_=>new AnimationCurve()).ToArray();Quaternion last=Quaternion.identity;
     for(int i=0;i<motion.samples.Length;i++) {var sample=motion.samples[i];if(!Finite(sample.time)||sample.time<0||(i>0&&sample.time<=motion.samples[i-1].time))throw new InvalidDataException("Sample time order");var m=Matrix(sample.transforms.Single(t=>t.bone==name).matrix);var q=m.rotation;if(i>0&&Quaternion.Dot(last,q)<0)q=new Quaternion(-q.x,-q.y,-q.z,-q.w);last=q;float[] values={m.m03,m.m13,m.m23,q.x,q.y,q.z,q.w,((Vector3)m.GetColumn(0)).magnitude,((Vector3)m.GetColumn(1)).magnitude,((Vector3)m.GetColumn(2)).magnitude};for(int k=0;k<10;k++)curves[k].AddKey(sample.time,values[k]);}
     for(int k=0;k<10;k++){for(int j=0;j<curves[k].length;j++){AnimationUtility.SetKeyLeftTangentMode(curves[k],j,AnimationUtility.TangentMode.Linear);AnimationUtility.SetKeyRightTangentMode(curves[k],j,AnimationUtility.TangentMode.Linear);}clip.SetCurve(path,typeof(Transform),properties[k],curves[k]);}
    }
    clip.EnsureQuaternionContinuity();var settings=AnimationUtility.GetAnimationClipSettings(clip);settings.loopTime=true;AnimationUtility.SetAnimationClipSettings(clip,settings);
    float error=0,motionDistance=0;Vector3[] first=null;
    foreach(var sample in motion.samples) {clip.SampleAnimation(root,sample.time);foreach(var pose in sample.transforms){var bone=bones.Single(b=>b.name==pose.bone);var actual=Matrix4x4.TRS(bone.localPosition,bone.localRotation,bone.localScale);var expected=Matrix(pose.matrix);for(int j=0;j<16;j++)error=Mathf.Max(error,Mathf.Abs(actual[j]-expected[j]));}
     for(int j=0;j<bones.Length;j++)if(!data.animated_bones.Contains(bones[j].name)&&(bones[j].localPosition!=bind[j].p||bones[j].localRotation!=bind[j].q||bones[j].localScale!=bind[j].s))throw new InvalidOperationException("Unrelated bone changed");
     skin.BakeMesh(baked);var vs=baked.vertices;if(vs.Any(v=>!Finite(v.x)||!Finite(v.y)||!Finite(v.z)))throw new InvalidOperationException("Nonfinite deformation");if(first==null)first=vs;else for(int j=0;j<vs.Length;j++)motionDistance=Mathf.Max(motionDistance,Vector3.Distance(vs[j],first[j]));}
    if(error>0.0002f||motionDistance<0.00001f)throw new InvalidOperationException("Preview validation failed");
    AssetDatabase.CreateAsset(clip,folder+"/"+motion.name+".anim");var controller=AnimatorController.CreateAnimatorControllerAtPath(folder+"/"+motion.name+".controller");controller.AddMotion(clip);
    for(int j=0;j<bones.Length;j++){bones[j].localPosition=bind[j].p;bones[j].localRotation=bind[j].q;bones[j].localScale=bind[j].s;}
    var animator=root.GetComponent<Animator>();if(animator==null)animator=root.AddComponent<Animator>();animator.runtimeAnimatorController=controller;animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
    var prefab=PrefabUtility.SaveAsPrefabAsset(root,folder+"/"+motion.name+"_DIAGNOSTIC.prefab");prefabs.Add(prefab);reports.Add(motion.name+": sample matrix error="+error+", skinned motion="+motionDistance);
    var fresh=UnityEngine.Object.Instantiate(prefab);try{var a=fresh.GetComponent<Animator>();a.Rebind();a.Update(0);var h=fresh.GetComponentsInChildren<Transform>().Single(t=>t.name=="Head");var q=h.localRotation;a.Update(motion.duration*0.4f);if(Quaternion.Angle(q,h.localRotation)<0.001f)throw new InvalidOperationException("Saved Animator did not move");}finally{UnityEngine.Object.DestroyImmediate(fresh);}
   }
   testScene=EditorSceneManager.NewPreviewScene();var comparison=new GameObject("Elsa_DynamicDressComparison_DIAGNOSTIC");SceneManager.MoveGameObjectToScene(comparison,testScene);var sceneObjects=new List<GameObject>();
   for(int i=0;i<prefabs.Count;i++){var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefabs[i],testScene);instance.transform.SetParent(comparison.transform,false);int slot=i;instance.transform.position=new Vector3((slot-(prefabs.Count-1)*.5f)*1.5f,0,0);var label=new GameObject("Label");SceneManager.MoveGameObjectToScene(label,testScene);label.transform.SetParent(comparison.transform,false);label.transform.position=instance.transform.position+new Vector3(0,2.05f,0);label.transform.rotation=Quaternion.Euler(0,180,0);var text=label.AddComponent<TextMesh>();text.text=(data.clips[i].name.Contains("idle_active")?"ACTIVE":"PASSIVE")+"\n"+"DYNAMIC DRESS + LEGS";text.characterSize=.035f;text.anchor=TextAnchor.MiddleCenter;text.fontSize=32;text.color=Color.white;sceneObjects.Add(instance);}
   var gridMaterial=new Material(Shader.Find("Universal Render Pipeline/Unlit")??Shader.Find("Unlit/Color"));gridMaterial.color=new Color(.22f,.28f,.32f);AssetDatabase.CreateAsset(gridMaterial,folder+"/FloorGrid.mat");
   for(int axis=0;axis<2;axis++)for(int k=-8;k<=8;k++){var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name="Floor grid";SceneManager.MoveGameObjectToScene(g,testScene);g.transform.SetParent(comparison.transform,false);g.transform.localPosition=axis==0?new Vector3(k*.25f,-.015f,0):new Vector3(0,-.015f,k*.25f);g.transform.localScale=axis==0?new Vector3(.006f,.006f,4):new Vector3(4,.006f,.006f);g.GetComponent<Renderer>().sharedMaterial=gridMaterial;UnityEngine.Object.DestroyImmediate(g.GetComponent<Collider>());}
   var cameraObject=new GameObject("Camera");SceneManager.MoveGameObjectToScene(cameraObject,testScene);cameraObject.transform.SetParent(comparison.transform,false);var camera=cameraObject.AddComponent<Camera>();camera.transform.position=new Vector3(0,1.5f,6.3f);camera.transform.LookAt(new Vector3(0,.95f,0));camera.orthographic=true;camera.orthographicSize=1.6f;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.055f,.07f,.09f);cameraObject.tag="MainCamera";
   var lightObject=new GameObject("Key Light");SceneManager.MoveGameObjectToScene(lightObject,testScene);lightObject.transform.SetParent(comparison.transform,false);var light=lightObject.AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.1f;light.transform.rotation=Quaternion.Euler(35,-30,0);
   var fillObject=new GameObject("Fill Light");SceneManager.MoveGameObjectToScene(fillObject,testScene);fillObject.transform.SetParent(comparison.transform,false);var fill=fillObject.AddComponent<Light>();fill.type=LightType.Directional;fill.intensity=.45f;fill.transform.rotation=Quaternion.Euler(25,140,0);
   if(PrefabUtility.SaveAsPrefabAsset(comparison,folder+"/Elsa_DynamicDressComparison.prefab")==null)throw new InvalidOperationException("Could not save comparison prefab");
   File.WriteAllText(folder+"/README.txt",Warning+"\nDrag Elsa_DynamicDressComparison.prefab into an empty test scene and press Play. Each prefab loops active or passive torso/head motion. Native controls sampled at 30 Hz, linear Unity interpolation.\nTexture-pair/UV assignment requires visual review.\nBind error="+bindError+"\n"+string.Join("\n",reports)+"\nPreview helper parents:\n"+string.Join("\n",model.parent_notes));AssetDatabase.SaveAssets();AssetDatabase.Refresh();return folder;
  } finally {if(testScene.IsValid())EditorSceneManager.ClosePreviewScene(testScene);if(root!=null)UnityEngine.Object.DestroyImmediate(root);if(workingScene.IsValid())EditorSceneManager.ClosePreviewScene(workingScene);if(baked!=null)UnityEngine.Object.DestroyImmediate(baked);if(rt!=null)UnityEngine.Object.DestroyImmediate(rt);if(capture!=null)UnityEngine.Object.DestroyImmediate(capture);}
 }
 public static void Render(string folder){
 var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(folder+"/Elsa_DynamicDressComparison.prefab"),scene);
 foreach(var animator in UnityEngine.Object.FindObjectsByType<Animator>(FindObjectsSortMode.None)){animator.Rebind();animator.Update(0);animator.Update(2);}
 var camera=UnityEngine.Object.FindFirstObjectByType<Camera>();var rt=new RenderTexture(1600,900,24);var image=new Texture2D(1600,900,TextureFormat.RGB24,false);var old=RenderTexture.active;
 try{camera.targetTexture=rt;camera.Render();RenderTexture.active=rt;image.ReadPixels(new Rect(0,0,1600,900),0,0);image.Apply();File.WriteAllBytes(@"F:/DisneyInfinityPortalTest/ElsaSceneResearch/elsa-dynamic-dress-preview.png",image.EncodeToPNG());}
 finally{camera.targetTexture=null;RenderTexture.active=old;UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(image);}
 }
 public static void BatchValidate(){try{string folder=Build();File.WriteAllText(Path.Combine(Path.GetDirectoryName(Application.dataPath),"elsa-dynamic-dress-validation.txt"),folder+"\n"+File.ReadAllText(folder+"/README.txt"));Debug.Log("ELSA_DYNAMIC_DRESS_DIAGNOSTIC_PASS");if(SystemInfo.graphicsDeviceType!=UnityEngine.Rendering.GraphicsDeviceType.Null)Render(folder);EditorApplication.Exit(0);}catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
}
