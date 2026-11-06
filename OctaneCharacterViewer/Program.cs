using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Media.Media3D;
using System.Windows.Threading;

namespace OctaneCharacterViewer;
public class ModelData {
 public string source=""; public float[][] vertices=[]; public float[][] uv=[];public string[] bones=[];public float[][] bindposes=[];public Weight[] weights=[];public Part[] parts=[];
}
public class Weight {public int[] indices=[];public float[] weights=[];}
public class Part {public int[] triangles=[];public string? texture;}
public class Pose {public string bone=""; public float[] matrix=[];}
public class Sample {public float time;public Pose[] transforms=[];}
public class Motion {public string name="";public float duration;public Sample[] samples=[];}
public class TimingConfiguration {public string mode="fixture";}
public class MotionData {public bool reference_rig_adapter;public int reference_source_outputs;public string model_sha256="";public string scope="";public string[] fixture_assumptions=[];public Dictionary<string,int>? source_skin_nodes;public Motion[] clips=[];public TimingConfiguration? timing_configuration;}
public static class Program {
 [STAThread] public static int Main(string[] args) {
  try {var app=new Application();var window=new Viewer(args.Contains("--smoke-test"));app.Run(window);return window.Failed?1:0;}
  catch(Exception ex){File.WriteAllText(Path.Combine(AppContext.BaseDirectory,"startup-error.txt"),ex.ToString());if(!args.Contains("--smoke-test"))MessageBox.Show(ex.Message,"Viewer failed");return 1;}
 }
}
public class Viewer:Window {
 const string Root=@"F:\DisneyInfinityPortalTest";
 const string NativePython=@"C:\Users\Kurar\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe";
 const string WiiUModelSha="fdf7c0e753e8ae34a5f68cd9322c5b711e8b8fd3a161da3d08dbb682857dea92";
 readonly bool ahsokaTrial=Environment.GetCommandLineArgs().Contains("--ahsoka-trial");
 const string AhsokaModelSha="e2e09336a511db10d2f3b7eb8adb911fbecd1ca52bc3ceb12419b005df1ae248";
 readonly bool hulkTrial=Environment.GetCommandLineArgs().Contains("--hulk-trial");
 const string HulkModelSha="4aebf05205f13a29d6f6171862d471faee1f4285484b7093f8871357f733187e";
 readonly bool aladdinTrial=Environment.GetCommandLineArgs().Contains("--aladdin-trial");
 const string AladdinModelSha="aeb73f14001f75abb09e14ec8c9cc0531910cb3be655ac935baf94308624a9c6";
 readonly bool princessTrial=Environment.GetCommandLineArgs().Contains("--princess-trial");
 const string PrincessModelSha="3dd4d40e49b120094d472018133bb4a2da7fe6b94d253483516a53e62376854e";
 readonly bool wiiuMesh=Environment.GetCommandLineArgs().Contains("--wiiu-model")||Environment.GetCommandLineArgs().Contains("--princess-trial")||Environment.GetCommandLineArgs().Contains("--ahsoka-trial")||Environment.GetCommandLineArgs().Contains("--aladdin-trial")||Environment.GetCommandLineArgs().Contains("--hulk-trial");
 readonly string dataFolder=Path.Combine(Root,"OctaneCharacterViewer","Data");
 readonly string posePath=File.Exists(Path.Combine(Root,"OctaneCharacterViewer","NativePreviews","current-native-run.json"))
  ?Path.Combine(Root,"OctaneCharacterViewer","NativePreviews","current-native-run.json")
  :Path.Combine(Root,"ElsaSceneResearch","pc-run-braid-animation.json");
 static readonly JsonSerializerOptions JsonOptions=new(){IncludeFields=true,PropertyNameCaseInsensitive=true};
 ModelData model=null!; Motion motion=null!;
 Motion[] availableMotions=[];
 readonly ComboBox clipPicker=new(){MinWidth=230,Margin=new Thickness(5)};
 readonly Button previewNative=new(){Content="Preview native clip (.oct)",Margin=new Thickness(5)};
 readonly CheckBox nativeTiming=new(){Content="Native clock (single activation)",Foreground=Brushes.LightGray,Margin=new Thickness(5),VerticalAlignment=VerticalAlignment.Center,ToolTip="Apply the verified default clock and endpoint stop behavior to the next native preview. Uses an explicit preview tick schedule; full game scheduling remains incomplete."};
 readonly CheckBox fullPalette=new(){Content="Full palette (tested Elsa profiles)",Foreground=Brushes.LightGray,Margin=new Thickness(5),VerticalAlignment=VerticalAlignment.Center,ToolTip="Evaluate face, lids, eyes and forearm overlays for catalogued PC Elsa idles, turns and locomotion. Only catalogued PC Elsa profiles are supported. This does not imply full game parity or fix running fingers."};
 readonly ProgressBar evaluationProgress=new(){Minimum=0,Maximum=1,Height=6,Margin=new Thickness(0,2,0,3),Visibility=Visibility.Collapsed};
 string paletteCoverage="evaluated cache";
 readonly Button inspectClip=new(){Content="Inspect native clip (.oct)",Margin=new Thickness(5)};
 readonly Viewport3D viewport=new();readonly PerspectiveCamera camera=new();
 readonly List<MeshGeometry3D> geometries=[];
 readonly Slider timeline=new(){Minimum=0,Width=440,IsSnapToTickEnabled=true,TickFrequency=1.0/30};
 readonly TextBlock status=new(){Foreground=Brushes.LightGray,TextWrapping=TextWrapping.Wrap};
 readonly TextBlock scope=new(){Foreground=Brushes.Goldenrod,TextWrapping=TextWrapping.Wrap};
 readonly Button evaluate=new(){Content="Re-evaluate source (native backend)",Margin=new Thickness(5)};
 readonly DispatcherTimer timer=new(){Interval=TimeSpan.FromSeconds(1.0/30)};
 readonly Stopwatch clock=new();
 Process? backendProcess;
 bool playing,dragging,loading,lastBackendSucceeded;Point last;double yaw=150,pitch=8,distance=5.5,startTime;
 public bool Failed {get;private set;}
 public Viewer(bool smoke) {
  nativeTiming.IsChecked=Environment.GetCommandLineArgs().Contains("--native-default-timing");
  fullPalette.IsChecked=Environment.GetCommandLineArgs().Contains("--full-palette");
  Title="Octane Character Viewer â€” PC Elsa research prototype";Width=1180;Height=800;Background=new SolidColorBrush(Color.FromRgb(24,28,34));
  var dock=new DockPanel{Margin=new Thickness(12),Background=Background};Content=dock;
  var top=new StackPanel();DockPanel.SetDock(top,Dock.Top);dock.Children.Add(top);
  top.Children.Add(new TextBlock{Text="Standalone mesh + native-evaluated animation",FontSize=23,Foreground=Brushes.White,Margin=new Thickness(0,0,0,8)});
  scope.Text="Verified PC Elsa only â€¢ native-evaluated pose cache â€¢ partial engine reconstruction â€¢ no manual finger offsets";top.Children.Add(scope);
  var buttons=new WrapPanel{Margin=new Thickness(0,8,0,8)};top.Children.Add(buttons);
  Button Add(string title,Action action){var b=new Button{Content=title,Padding=new Thickness(12,5,12,5),Margin=new Thickness(0,0,7,0)};b.Click+=(_,_)=>action();buttons.Children.Add(b);return b;}
  Add("Play / pause",Toggle);Add("Restart",()=>{Pause();timeline.Value=0;Toggle();});
  Add("Previous frame",()=>{Pause();timeline.Value=Math.Max(0,timeline.Value-1.0/30);});
  Add("Next frame",()=>{Pause();timeline.Value=Math.Min(motion.duration,timeline.Value+1.0/30);});
  Add("Reset camera",()=>{yaw=150;pitch=8;distance=hulkTrial?8:ahsokaTrial?7:5.5;UpdateCamera();});
  if(ahsokaTrial||aladdinTrial||hulkTrial)Add("Source bind pose",ShowSourceBindPose);
  Add("Open evaluated animationâ€¦",OpenAnimation);
  Add(wiiuMesh?"Wii U source animation":"Wii U controls / PC reference",OpenWiiUReference);
  Add("Backward runs",OpenBackwardRuns);
  Add("Backward walks",OpenBackwardWalks);
  Add("Turns",OpenTurns);
  buttons.Children.Add(clipPicker);clipPicker.SelectionChanged+=(_,_)=>{if(!loading&&clipPicker.SelectedIndex>=0){Pause();SelectMotion(clipPicker.SelectedIndex);}};
  buttons.Children.Add(inspectClip);inspectClip.Click+=async(_,_)=>await InspectNativeClip();
  buttons.Children.Add(previewNative);previewNative.Click+=async(_,_)=>await PreviewNativeClip();
  buttons.Children.Add(nativeTiming);
  buttons.Children.Add(fullPalette);
  top.Children.Add(evaluationProgress);
  buttons.Children.Add(evaluate);evaluate.Click+=async(_,_)=>await Evaluate();
  Add("Research inventory",()=>Process.Start(new ProcessStartInfo(Path.Combine(Root,"OctaneCharacterViewer","DEPENDENCY_INVENTORY.md")){UseShellExecute=true}));
  var bottom=new StackPanel();DockPanel.SetDock(bottom,Dock.Bottom);dock.Children.Add(bottom);
  bottom.Children.Add(new TextBlock{Text="Drag: orbit â€¢ Mouse wheel: zoom â€¢ Scrubbing selects cached native poses; it does not rerun dynamics backwards.",Foreground=Brushes.LightGray,Margin=new Thickness(0,8,0,5)});
  bottom.Children.Add(timeline);bottom.Children.Add(status);
  viewport.Camera=camera;var surface=new Border{Background=Brushes.Transparent,Child=viewport};dock.Children.Add(surface);
  if(ahsokaTrial)distance=7;
  if(hulkTrial)distance=8;
  camera.FieldOfView=45;camera.NearPlaneDistance=.01;camera.FarPlaneDistance=100;
  var lighting=new Model3DGroup();lighting.Children.Add(new AmbientLight(Color.FromRgb(135,135,135)));lighting.Children.Add(new DirectionalLight(Colors.White,new Vector3D(-1,-2,-3)));lighting.Children.Add(new DirectionalLight(Color.FromRgb(100,100,100),new Vector3D(1,-1,2)));viewport.Children.Add(new ModelVisual3D{Content=lighting});
  surface.MouseLeftButtonDown+=(_,e)=>{dragging=true;last=e.GetPosition(viewport);surface.CaptureMouse();};
  surface.MouseLeftButtonUp+=(_,_)=>{dragging=false;surface.ReleaseMouseCapture();};
  surface.MouseMove+=(_,e)=>{if(!dragging)return;var point=e.GetPosition(viewport);yaw+=(point.X-last.X)*.4;pitch=Math.Clamp(pitch+(point.Y-last.Y)*.3,-70,70);last=point;UpdateCamera();};
  surface.MouseWheel+=(_,e)=>{distance=Math.Clamp(distance*Math.Exp(-e.Delta*.001),.3,12);UpdateCamera();};
  model=JsonSerializer.Deserialize<ModelData>(File.ReadAllText(hulkTrial?Path.Combine(Root,"WiiUResearch","AnimationViewerResearch","HulkTrial","hulk-model.json"):aladdinTrial?Path.Combine(Root,"WiiUResearch","AnimationViewerResearch","AladdinTrial","aladdin-model.json"):ahsokaTrial?Path.Combine(Root,"WiiUResearch","AnimationViewerResearch","AhsokaTrial","ahsoka-model.json"):princessTrial?Path.Combine(Root,"WiiUResearch","AnimationViewerResearch","PrincessTrial","princess-model.json"):Path.Combine(dataFolder,wiiuMesh?"elsa-wiiu-mesh.json":"elsa-pc-mesh.json")),JsonOptions)!;
  ValidateModel();LoadPoses(wiiuMesh?WiiUReferencePath:null);if(!wiiuMesh&&Environment.GetCommandLineArgs().Contains("--wiiu-adapter"))LoadPoses(WiiUReferencePath);CreateMeshes();UpdateCamera();
  if(wiiuMesh){Title=hulkTrial?"Octane Character Viewer - Wii U Hulk trial":aladdinTrial?"Octane Character Viewer - Wii U Aladdin trial":ahsokaTrial?"Octane Character Viewer - Wii U Ahsoka body trial":princessTrial?"Octane Character Viewer - Wii U psx_princess trial":"Octane Character Viewer - Wii U Elsa source mesh";evaluate.IsEnabled=previewNative.IsEnabled=fullPalette.IsEnabled=nativeTiming.IsEnabled=false;}
  timeline.ValueChanged+=(_,_)=>{if(!loading)RenderPose(timeline.Value);};RenderPose(0);
  timer.Tick+=(_,_)=>{if(!playing)return;double time=startTime+clock.Elapsed.TotalSeconds;if(time>=motion.duration){time=motion.duration;Pause();}timeline.Value=time;};timer.Start();
  Closed+=(_,_)=>{timer.Stop();try{if(backendProcess is {HasExited:false})backendProcess.Kill(true);}catch(InvalidOperationException){} };
  if(smoke){ShowInTaskbar=false;WindowStartupLocation=WindowStartupLocation.Manual;Left=-2000;Top=0;Loaded+=(_,_)=>{var wait=new DispatcherTimer{Interval=TimeSpan.FromMilliseconds(750)};wait.Tick+=async(_,_)=>{wait.Stop();try{if(Environment.GetCommandLineArgs().Contains("--selected-native-smoke-test")){await PreviewNativeClip(Path.Combine(Root,"ElsaSceneResearch","InstalledGameAssetCheck","RunMotions","fro_elsa","characters","class_girl","motions",Environment.GetCommandLineArgs().Contains("--backward-run-smoke-test")?"grl_bm_runb.oct":Environment.GetCommandLineArgs().Contains("--diagonal-run-smoke-test")?"grl_bm_runrf.oct":"grl_bm_runf.oct"));if(!lastBackendSucceeded)throw new Exception("Selected native clip failed");File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","selected-native-preview-smoke.json"),JsonSerializer.Serialize(new{pass=true,clip=motion.name,samples=motion.samples.Length,paletteCoverage}));}
if(Environment.GetCommandLineArgs().Contains("--backend-smoke-test")){await Evaluate();if(!lastBackendSucceeded)throw new Exception("Native backend refresh failed");}SelfTest();if(Environment.GetCommandLineArgs().Contains("--backward-pack-smoke-test")){OpenBackwardRuns();if(availableMotions.Length!=3||paletteCoverage!="62 source-driven / 0 fallback")throw new Exception("Backward pack coverage/count mismatch");foreach(var c in availableMotions){motion=c;RenderPose(.1);}File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","backward-pack-viewer-smoke.json"),JsonSerializer.Serialize(new{pass=true,clips=availableMotions.Select(c=>c.name).ToArray(),paletteCoverage}));}}catch(Exception ex){Failed=true;File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","smoke-test-error.txt"),ex.ToString());}Close();};wait.Start();};}
 }
 void ValidateModel(){
  int expectedBones=hulkTrial?68:aladdinTrial?63:ahsokaTrial?70:princessTrial?54:wiiuMesh?64:62;
  if(model.vertices.Length!=(hulkTrial?6386:aladdinTrial?4344:ahsokaTrial?5020:princessTrial?5163:5419)||model.bones.Length!=expectedBones||model.weights.Length!=model.vertices.Length||model.bindposes.Length!=expectedBones||model.bones.Distinct().Count()!=expectedBones)throw new InvalidDataException("Unexpected source mesh layout");
  for(int i=0;i<model.vertices.Length;i++){if(model.vertices[i].Length!=3||model.vertices[i].Any(x=>!float.IsFinite(x)))throw new InvalidDataException("Bad vertex");var w=model.weights[i];if(w.indices.Length!=4||w.weights.Length!=4||w.indices.Any(x=>x<0||x>=expectedBones)||w.weights.Any(x=>!float.IsFinite(x)||x<0)||Math.Abs(w.weights.Sum()-1)>0.002)throw new InvalidDataException("Bad skin weights");}
  if(model.parts.Any(p=>p.triangles.Length%3!=0||p.triangles.Any(i=>i<0||i>=model.vertices.Length)))throw new InvalidDataException("Bad triangles");
 }
 void LoadPoses(string? path=null){
  path??=posePath;
  var file=new FileInfo(path);if(!file.Exists||file.Length>128*1024*1024)throw new InvalidDataException("Animation file missing or larger than 128 MiB");
  var data=JsonSerializer.Deserialize<MotionData>(File.ReadAllText(path),JsonOptions)??throw new InvalidDataException("Missing animation data");
  if(data.model_sha256!=(hulkTrial?HulkModelSha:aladdinTrial?AladdinModelSha:ahsokaTrial?AhsokaModelSha:princessTrial?PrincessModelSha:wiiuMesh?WiiUModelSha:"38ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d")||data.clips==null||data.clips.Length==0||data.clips.Length>100)throw new InvalidDataException("Animation must match the selected verified character model");
  foreach(var candidate in data.clips){
   if(candidate==null||candidate.samples==null||candidate.samples.Length<2||candidate.samples.Length>20000||!float.IsFinite(candidate.duration)||candidate.duration<=0)throw new InvalidDataException("Invalid motion extent");
   float previous=-1;
   foreach(var sample in candidate.samples){
    if(sample==null||!float.IsFinite(sample.time)||sample.time<0||sample.time<=previous||sample.time>candidate.duration+.001f||sample.transforms==null)throw new InvalidDataException("Invalid sample timing");previous=sample.time;
    var names=sample.transforms.Select(p=>p?.bone).ToArray();
    if(names.Length!=model.bones.Length||names.Distinct().Count()!=model.bones.Length||model.bones.Any(b=>!names.Contains(b))||sample.transforms.Any(p=>p==null||p.matrix==null||p.matrix.Length!=16||p.matrix.Any(v=>!float.IsFinite(v))))throw new InvalidDataException("Invalid palette");
   }
  }
  // Commit only after every clip passes. Failed loads leave the previous preview intact.
  paletteCoverage=data.source_skin_nodes!=null?$"{data.source_skin_nodes.Count} source-driven / {model.bones.Length-data.source_skin_nodes.Count} fallback":"coverage in source report";
  scope.Text="Verified PC Elsa only â€¢ partial native graph â€¢ no manual pose corrections"+(data.fixture_assumptions.Length>0?" â€¢ evaluation fixtures recorded in output":"")+(data.timing_configuration?.mode=="native-default"?" â€¢ native clock / single activation":" â€¢ fixture timing");
  if(data.reference_rig_adapter)scope.Text=$"Wii U source controls on {(wiiuMesh?"Wii U source mesh":"PC reference mesh")} | {data.source_skin_nodes?.Count??0} evaluated outputs / {model.bones.Length-(data.source_skin_nodes?.Count??0)} bind-relative fallbacks | {data.clips[0].samples.Length} source-sampled poses; not full game parity";
  availableMotions=data.clips;loading=true;clipPicker.ItemsSource=availableMotions.Select(c=>c.name).ToArray();clipPicker.SelectedIndex=0;loading=false;SelectMotion(0);
 }
 void SelectMotion(int index){motion=availableMotions[index];if(wiiuMesh)scope.Text=$"{(ahsokaTrial?"EXPERIMENTAL: secondary motion incomplete | ":"")}Wii U source mesh | {paletteCoverage} | {motion.samples.Length} source-sampled poses | fixture dynamics; not full game parity";loading=true;timeline.Maximum=motion.duration;timeline.Value=0;loading=false;if(geometries.Count>0)RenderPose(0);}
 string WiiUReferencePath {
  get {
   var folder=Path.Combine(Root,"WiiUResearch","AnimationViewerResearch");
   if(hulkTrial)return Path.Combine(folder,"HulkTrial","hulk-animation.json");
   if(aladdinTrial)return Path.Combine(folder,"AladdinTrial","aladdin-animation.json");
   if(ahsokaTrial)return Path.Combine(folder,"AhsokaTrial","ahsoka-animation.json");
   if(princessTrial)return Path.Combine(folder,"PrincessTrial","princess-animation.json");
   if(wiiuMesh){var motions=Path.Combine(folder,"wiiu-elsa-motion-pack-full.json");if(File.Exists(motions))return motions;var pack=Path.Combine(folder,"wiiu-elsa-idles-full.json");if(File.Exists(pack))return pack;var full=Path.Combine(folder,"wiiu-source-mesh-animation-full.json");if(File.Exists(full))return full;var dress=Path.Combine(folder,"wiiu-source-mesh-animation-dress.json");return File.Exists(dress)?dress:Path.Combine(folder,"wiiu-source-mesh-animation.json");}
   var legs=Path.Combine(folder,"wiiu-controls-pc-reference-viewer-legs.json");
   if(File.Exists(legs))return legs;
   var continuous=Path.Combine(folder,"wiiu-controls-pc-reference-viewer-continuous.json");
   return File.Exists(continuous)?continuous:Path.Combine(folder,"wiiu-controls-pc-reference-viewer.json");
  }
 }
 void OpenWiiUReference(){
  if(backendProcess!=null)return;Pause();
  try{LoadPoses(WiiUReferencePath);RenderPose(0);}catch(Exception ex){MessageBox.Show(this,ex.Message+"\nExisting preview retained.","Wii U reference adapter not loaded");}
 }
 void OpenAnimation(){
  if(backendProcess!=null)return;
  var dialog=new Microsoft.Win32.OpenFileDialog{Title="Open evaluated native animation palette (verified PC Elsa)",Filter="Evaluated animation JSON|*.json",InitialDirectory=Path.Combine(Root,"ElsaSceneResearch")};
  if(dialog.ShowDialog()!=true)return;Pause();
  try{LoadPoses(dialog.FileName);RenderPose(0);}catch(Exception ex){MessageBox.Show(this,ex.Message+"\nExisting preview retained.","Animation not loaded");}
 }
 void OpenBackwardRuns(){
  if(backendProcess!=null)return;Pause();
  try{LoadPoses(Path.Combine(Root,"OctaneCharacterViewer","NativePreviews","backward-run-pack.json"));RenderPose(0);}
  catch(Exception ex){MessageBox.Show(this,ex.Message+"\nExisting preview retained.","Backward runs not loaded");}
 }
 void OpenBackwardWalks(){
  if(backendProcess!=null)return;Pause();
  try{LoadPoses(Path.Combine(Root,"OctaneCharacterViewer","NativePreviews","backward-walk-pack.json"));RenderPose(0);}
  catch(Exception ex){MessageBox.Show(this,ex.Message+"\nExisting preview retained.","Backward walks not loaded");}
 }
 void OpenTurns(){
  if(backendProcess!=null)return;Pause();
  try{LoadPoses(Path.Combine(Root,"OctaneCharacterViewer","NativePreviews","turn-pack.json"));RenderPose(0);}
  catch(Exception ex){MessageBox.Show(this,ex.Message+"\nExisting preview retained.","Turns not loaded");}
 }
 async Task PreviewNativeClip(string? source=null){
  if(backendProcess!=null)return;
  if(source==null){
   var dialog=new Microsoft.Win32.OpenFileDialog{Title="Preview native clip â€” PC Elsa idle, forward walk/run",Filter="Native clip OCT|*.oct",InitialDirectory=Path.Combine(Root,"ElsaSceneResearch","InstalledGameAssetCheck")};
   if(dialog.ShowDialog()!=true)return;source=dialog.FileName;
  }
  Pause();evaluate.IsEnabled=inspectClip.IsEnabled=previewNative.IsEnabled=nativeTiming.IsEnabled=fullPalette.IsEnabled=false;
  evaluationProgress.Visibility=Visibility.Visible;evaluationProgress.IsIndeterminate=true;
  status.Text="Preparing source rig and warming up native dynamicsâ€¦";
  try{
   string output=Path.Combine(Root,"OctaneCharacterViewer","NativePreviews",Path.GetFileNameWithoutExtension(source)+"-"+DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff")+".json");
   var info=new ProcessStartInfo(NativePython){UseShellExecute=false,CreateNoWindow=true,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=Root};
   info.ArgumentList.Add(Path.Combine(Root,"OctaneCharacterViewer","evaluate_native_clip.py"));info.ArgumentList.Add(source);info.ArgumentList.Add("--output");info.ArgumentList.Add(output);
   if(nativeTiming.IsChecked==true){info.ArgumentList.Add("--timing");info.ArgumentList.Add("native-default");}
   if(fullPalette.IsChecked==true){foreach(string flag in new[]{"--native-facial-paths","--native-eyelid-paths","--native-eye-paths","--native-forearm-paths"})info.ArgumentList.Add(flag);}
   using var process=Process.Start(info)??throw new Exception("Native evaluator did not start");backendProcess=process;
   var errorTask=process.StandardError.ReadToEndAsync();var log=new System.Text.StringBuilder();
   string? line;while((line=await process.StandardOutput.ReadLineAsync())!=null){
    log.AppendLine(line);
    if(line.StartsWith("PROGRESS ")){
     using var progress=JsonDocument.Parse(line[9..]);var r=progress.RootElement;
     evaluationProgress.IsIndeterminate=false;evaluationProgress.Value=(double)r.GetProperty("frame").GetInt32()/Math.Max(1,r.GetProperty("total").GetInt32());
     status.Text=$"Evaluating {Path.GetFileName(source)}: {r.GetProperty("frame").GetInt32()} / {r.GetProperty("total").GetInt32()} simulation ticks. Window remains responsive.";
    }else if(line.StartsWith("PROFILE "))status.Text="Preparing "+line[8..]+" and native dynamicsâ€¦";
   }
   await process.WaitForExitAsync();string error=await errorTask;
   File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","native-preview-last.log"),log+Environment.NewLine+error);
   if(process.ExitCode!=0)throw new InvalidDataException(fullPalette.IsChecked==true?"Full palette evaluation failed. This option supports catalogued PC Elsa profiles only. See native-preview-last.log. Previous preview retained.":"This clip could not be evaluated. Supported profiles: PC Elsa active/passive idle and class_girl forward/backward walk/run and tested directional runs. See native-preview-last.log. Previous preview retained.");
   if(fullPalette.IsChecked==true){using var result=JsonDocument.Parse(File.ReadAllText(output));if(result.RootElement.GetProperty("source_skin_nodes").EnumerateObject().Count()!=62||result.RootElement.GetProperty("fallback_parents").EnumerateObject().Any())throw new InvalidDataException("Full palette evaluation returned unexpected source coverage; previous preview retained.");}
   LoadPoses(output);RenderPose(0);
   scope.Text+=" â€¢ reset dynamics / fixture gravity / incomplete layer scheduling";
   lastBackendSucceeded=true;
  }catch(Exception ex){lastBackendSucceeded=false;status.Text=ex.Message;if(!Environment.GetCommandLineArgs().Contains("--selected-native-smoke-test"))MessageBox.Show(this,ex.Message,"Native preview not loaded");}
  finally{backendProcess=null;evaluate.IsEnabled=inspectClip.IsEnabled=previewNative.IsEnabled=nativeTiming.IsEnabled=fullPalette.IsEnabled=true;evaluationProgress.Visibility=Visibility.Collapsed;}
 }
 async Task InspectNativeClip(){
  if(backendProcess!=null)return;
  var dialog=new Microsoft.Win32.OpenFileDialog{Title="Inspect extracted native PC animation clip",Filter="Native animation OCT|*.oct",InitialDirectory=Path.Combine(Root,"ElsaSceneResearch","InstalledGameAssetCheck")};
  if(dialog.ShowDialog()!=true)return;
  Pause();evaluate.IsEnabled=inspectClip.IsEnabled=previewNative.IsEnabled=false;
  status.Text="Decoding native clip channelsâ€¦ existing mesh preview is unchanged.";
  try{
   string output=Path.Combine(Root,"OctaneCharacterViewer","Inspections",DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff")+".json");
   var info=new ProcessStartInfo(NativePython){UseShellExecute=false,CreateNoWindow=true,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=Root};
   info.ArgumentList.Add(Path.Combine(Root,"OctaneCharacterViewer","inspect_native_clip.py"));info.ArgumentList.Add(dialog.FileName);info.ArgumentList.Add("--output");info.ArgumentList.Add(output);
   using var process=Process.Start(info)??throw new Exception("Inspector did not start");backendProcess=process;
   var stdout=process.StandardOutput.ReadToEndAsync();var stderr=process.StandardError.ReadToEndAsync();await process.WaitForExitAsync();string text=await stdout,error=await stderr;
   File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","clip-inspection-last.log"),text+Environment.NewLine+error);
   if(process.ExitCode!=0)throw new InvalidDataException("This clip could not be decoded. See clip-inspection-last.log. Existing preview unchanged.");
   using var report=JsonDocument.Parse(File.ReadAllText(output));var r=report.RootElement;
   string summary=$"{Path.GetFileName(dialog.FileName)}\nDuration: {r.GetProperty("duration").GetDouble():F3} s\nCurves: {r.GetProperty("curve_count").GetInt32()}\nPorts mapped to PC Elsa: {r.GetProperty("mapped_ports").GetInt32()} / {r.GetProperty("referenced_ports").GetInt32()}\nUnmapped ports: {r.GetProperty("unmapped_ports").GetArrayLength()}\n\nDecoded channel report: {output}\n\nClip inspection does not replace the displayed animation or evaluate the full character graph.";
   status.Text=summary;MessageBox.Show(this,summary,"Native clip decoded");
  }catch(Exception ex){status.Text=ex.Message;MessageBox.Show(this,ex.Message,"Native clip inspection");}
  finally{backendProcess=null;evaluate.IsEnabled=inspectClip.IsEnabled=previewNative.IsEnabled=true;}
 }
 void CreateMeshes(){
  foreach(var part in model.parts){var mesh=new MeshGeometry3D();geometries.Add(mesh);foreach(var uv in model.uv)mesh.TextureCoordinates.Add(new Point(uv[0],1-uv[1]));
   for(int i=0;i<part.triangles.Length;i+=3){mesh.TriangleIndices.Add(part.triangles[i]);mesh.TriangleIndices.Add(part.triangles[i+2]);mesh.TriangleIndices.Add(part.triangles[i+1]);}
   Brush brush=Brushes.LightGray;
   if(part.texture!=null){string path=Path.GetFullPath(Path.Combine(dataFolder,part.texture));if(!path.StartsWith(dataFolder+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Texture path leaves data directory");var bitmap=new BitmapImage();bitmap.BeginInit();bitmap.UriSource=new Uri(path);bitmap.CacheOption=BitmapCacheOption.OnLoad;bitmap.EndInit();bitmap.Freeze();brush=new ImageBrush(bitmap){ViewportUnits=BrushMappingMode.Absolute,TileMode=TileMode.Tile};}
   var material=new DiffuseMaterial(brush);viewport.Children.Add(new ModelVisual3D{Content=new GeometryModel3D(mesh,material){BackMaterial=material}});
  }
 }
 static double[] Multiply(float[] a,float[] b){var result=new double[16];for(int r=0;r<4;r++)for(int c=0;c<4;c++)for(int k=0;k<4;k++)result[r*4+c]+=(double)a[r*4+k]*b[k*4+c];return result;}
 Point3D[] Skin(Sample sample){
  var poses=sample.transforms.ToDictionary(p=>p.bone,p=>p.matrix);var matrices=model.bones.Select((b,i)=>Multiply(poses[b],model.bindposes[i])).ToArray();var result=new Point3D[model.vertices.Length];
  for(int i=0;i<result.Length;i++){var v=model.vertices[i];var weight=model.weights[i];double x=0,y=0,z=0;for(int j=0;j<4;j++){var m=matrices[weight.indices[j]];double w=weight.weights[j];x+=(m[0]*v[0]+m[1]*v[1]+m[2]*v[2]+m[3])*w;y+=(m[4]*v[0]+m[5]*v[1]+m[6]*v[2]+m[7])*w;z+=(m[8]*v[0]+m[9]*v[1]+m[10]*v[2]+m[11])*w;}if(!double.IsFinite(x+y+z))throw new InvalidDataException("Nonfinite skinning");result[i]=new Point3D(x,y,-z);}
  return result;
 }
 void ShowSourceBindPose(){Pause();var points=model.vertices.Select(v=>new Point3D(v[0],v[1],-v[2])).ToArray();foreach(var mesh in geometries)mesh.Positions=new Point3DCollection(points);status.Text="SOURCE BIND GEOMETRY - animation and skin deformation bypassed; Play or scrub restores animation";}
 void RenderPose(double time){var sample=motion.samples.MinBy(s=>Math.Abs(s.time-time))!;var vertices=Skin(sample);foreach(var mesh in geometries)mesh.Positions=new Point3DCollection(vertices);status.Text=$"{motion.name}  |  {sample.time:F3} / {motion.duration:F3} s  |  {model.vertices.Length:N0} vertices â€¢ {model.bones.Length} palette bones â€¢ {paletteCoverage}";}
 void UpdateCamera(){double a=yaw*Math.PI/180,b=pitch*Math.PI/180;var center=new Point3D(0,hulkTrial?1.15:ahsokaTrial?1.25:.85,0);camera.Position=new Point3D(Math.Sin(a)*Math.Cos(b)*distance,center.Y+Math.Sin(b)*distance,Math.Cos(a)*Math.Cos(b)*distance);camera.LookDirection=center-camera.Position;camera.UpDirection=new Vector3D(0,1,0);}
 void Toggle(){if(playing){Pause();return;}if(timeline.Value>=motion.duration)timeline.Value=0;startTime=timeline.Value;clock.Restart();playing=true;}
 void Pause(){playing=false;clock.Stop();}
 async Task Evaluate(){
  Pause();lastBackendSucceeded=false;evaluate.IsEnabled=inspectClip.IsEnabled=previewNative.IsEnabled=false;status.Text="Evaluating original source tracks and native routinesâ€¦ window stays responsive.";
  try {var info=new ProcessStartInfo(NativePython){UseShellExecute=false,CreateNoWindow=true,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=Path.Combine(Root,"ElsaSceneResearch")};info.ArgumentList.Add(Path.Combine(Root,"ElsaSceneResearch","bake_pc_run_braid.py"));using var process=Process.Start(info)??throw new Exception("Backend did not start");backendProcess=process;var stdout=process.StandardOutput.ReadToEndAsync();var stderr=process.StandardError.ReadToEndAsync();await process.WaitForExitAsync();string output=await stdout,error=await stderr;File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","backend-last-run.log"),output+Environment.NewLine+error);if(process.ExitCode!=0)throw new Exception("Backend failed; see backend-last-run.log. Existing preview retained.");LoadPoses();RenderPose(0);lastBackendSucceeded=true;}
  catch(Exception ex){status.Text=ex.Message;}finally{backendProcess=null;evaluate.IsEnabled=inspectClip.IsEnabled=previewNative.IsEnabled=true;}
 }
 void TestAnimationImports(){
  LoadPoses(Path.Combine(Root,"ElsaSceneResearch","pc-gravity-dress-animation.json"));
  if(availableMotions.Length!=2)throw new Exception("Expected both cached native idles");
  foreach(int index in new[]{0,1}){SelectMotion(index);Skin(motion.samples[0]);Skin(motion.samples[^1]);}
  var previous=motion;
  string fixture=Path.Combine(Root,"OctaneCharacterViewer","invalid-animation-test.json");
  int rejected=0;
  try{
   File.WriteAllText(fixture,"{\"model_sha256\":\"wrong-model\",\"clips\":[]}");
   try{LoadPoses(fixture);throw new Exception("Wrong-model animation accepted");}catch(InvalidDataException){rejected++;}
   if(!ReferenceEquals(previous,motion))throw new Exception("Failed load replaced the previous preview");
   var malformed=new MotionData{model_sha256="38ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d",clips=[new Motion{name="bad time",duration=1,samples=[new Sample{time=0,transforms=previous.samples[0].transforms},new Sample{time=0,transforms=previous.samples[0].transforms}]}]};
   File.WriteAllText(fixture,JsonSerializer.Serialize(malformed,JsonOptions));
   try{LoadPoses(fixture);throw new Exception("Duplicate sample time accepted");}catch(InvalidDataException){rejected++;}
   if(!ReferenceEquals(previous,motion))throw new Exception("Invalid timing replaced the previous preview");
  }finally{File.Delete(fixture);LoadPoses();}
  File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","animation-import-validation.json"),JsonSerializer.Serialize(new{pass=true,clipsLoaded=2,rejectedInvalidFiles=rejected,previousPreviewRetained=true}));
 }
 void SelfTest(){
  if(!wiiuMesh)TestAnimationImports();
  if(Environment.GetCommandLineArgs().Contains("--wiiu-adapter-smoke-test")){
   LoadPoses(WiiUReferencePath);
   var legPreview=WiiUReferencePath.EndsWith("-legs.json");
   var dressPreview=WiiUReferencePath.EndsWith("-dress.json");
   var fullPreview=WiiUReferencePath.EndsWith("-full.json");
   if(paletteCoverage!=(wiiuMesh?(fullPreview?"64 source-driven / 0 fallback":dressPreview?"61 source-driven / 3 fallback":"57 source-driven / 7 fallback"):legPreview?"55 source-driven / 7 fallback":"49 source-driven / 13 fallback")||motion.samples.Length!=(wiiuMesh||legPreview||WiiUReferencePath.EndsWith("-continuous.json")?153:3))throw new InvalidDataException("Wii U adapter coverage/sample mismatch");
   foreach(var sample in motion.samples)RenderPose(sample.time);
   File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","wiiu-adapter-viewer-smoke.json"),JsonSerializer.Serialize(new{pass=true,clip=motion.name,samples=motion.samples.Length,paletteCoverage,scope=scope.Text}));
  }
  if(Environment.GetCommandLineArgs().Contains("--turn-pack-smoke-test")){
   OpenTurns();if(availableMotions.Length!=6||paletteCoverage!="62 source-driven / 0 fallback")throw new Exception("Turn pack mismatch");
   foreach(var c in availableMotions){motion=c;RenderPose(.1);}SelectMotion(0);
   File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","turn-pack-viewer-smoke.json"),JsonSerializer.Serialize(new{pass=true,clips=availableMotions.Select(c=>c.name).ToArray(),paletteCoverage}));
  }
  if(Environment.GetCommandLineArgs().Contains("--backward-walk-pack-smoke-test")){
   OpenBackwardWalks();if(availableMotions.Length!=3||paletteCoverage!="62 source-driven / 0 fallback")throw new Exception("Backward walk pack mismatch");
   foreach(var c in availableMotions){motion=c;RenderPose(.1);}SelectMotion(0);
   File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","backward-walk-pack-viewer-smoke.json"),JsonSerializer.Serialize(new{pass=true,clips=availableMotions.Select(c=>c.name).ToArray(),paletteCoverage}));
  }
  if(Environment.GetCommandLineArgs().Contains("--diagonal-run-smoke-test"))LoadPoses(Path.Combine(Root,"OctaneCharacterViewer","NativePreviews","native-runrf.json"));
  var smokeClip=Environment.GetCommandLineArgs().FirstOrDefault(a=>a.StartsWith("--smoke-clip="));
  if(smokeClip!=null){int index=Array.FindIndex(availableMotions,m=>m.name==smokeClip[13..]);if(index<0)throw new InvalidDataException("Requested smoke clip missing");SelectMotion(index);}
  var first=Skin(motion.samples[0]);double displacement=0;foreach(var sample in motion.samples){var points=Skin(sample);for(int i=0;i<points.Length;i++)displacement=Math.Max(displacement,(points[i]-first[i]).Length);}
  if(displacement<.001)throw new Exception("Skinned mesh did not move");
  var reference=new[]{0,3,36}.Select(i=>new{sampleIndex=i,sample=motion.samples[Math.Min(i,motion.samples.Length-1)],points=Skin(motion.samples[Math.Min(i,motion.samples.Length-1)]).Select(p=>new[]{p.X,p.Y,p.Z}).ToArray()}).ToArray();
  File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","skinning-reference-points.json"),JsonSerializer.Serialize(reference,JsonOptions));
  var smokeTimeArg=Environment.GetCommandLineArgs().FirstOrDefault(a=>a.StartsWith("--smoke-time="));
  double smokeTime=smokeTimeArg==null?(wiiuMesh?motion.duration:.1):double.Parse(smokeTimeArg[13..],System.Globalization.CultureInfo.InvariantCulture);
  if(!double.IsFinite(smokeTime)||smokeTime<0||smokeTime>motion.duration)throw new InvalidDataException("Smoke time outside clip");
  RenderPose(smokeTime);if(Environment.GetCommandLineArgs().Contains("--smoke-bind-pose"))ShowSourceBindPose();UpdateLayout();
  var image=new RenderTargetBitmap((int)ActualWidth,(int)ActualHeight,96,96,PixelFormats.Pbgra32);image.Render((Visual)Content);var encoder=new PngBitmapEncoder();encoder.Frames.Add(BitmapFrame.Create(image));using(var file=File.Create(Path.Combine(Root,"OctaneCharacterViewer","viewer-smoke.png")))encoder.Save(file);
  File.WriteAllText(Path.Combine(Root,"OctaneCharacterViewer","smoke-test.json"),JsonSerializer.Serialize(new{pass=true,clip=motion.name,availableClips=availableMotions.Select(m=>m.name).ToArray(),vertices=model.vertices.Length,bones=model.bones.Length,parts=model.parts.Length,samples=motion.samples.Length,maxSkinnedDisplacement=displacement,scope="Standalone cached native pose playback; not full engine parity"},new JsonSerializerOptions{WriteIndented=true}));
 }
}
