using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Windows.Media.Imaging;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Media3D;

namespace AssetWiiUdio;

public sealed class Di3MeshPreviewWindow : Window
{
    readonly PerspectiveCamera camera = new();
    readonly Model3DGroup scene = new();
    readonly Viewport3D viewport = new();
    readonly TextBlock info = new();
    double radius = 5, azimuth = 0.6, elevation = 0.25;
    System.Windows.Point? last;
    Point3D center;
    bool wireframe;
    bool showRig,rigOnly;
    bool initializing=true;
    readonly Dictionary<int,Material> selectedMaterials=new();
    readonly List<PreviewRig.Joint> joints;
    readonly List<(string Name,BitmapSource Image)> textures=new();
    readonly DI3MeshReader.Model model;

    public Di3MeshPreviewWindow(DI3MeshReader.Model model, string label)
    {
        this.model=model;
        joints=PreviewRig.Read(model.path);
        foreach(var file in Directory.GetFiles(Path.GetDirectoryName(model.path)!,"*.tbody",SearchOption.AllDirectories))
        {
            try {var r=Gx2ExternalPreview.Convert(File.ReadAllBytes(file));var image=BitmapSource.Create(r.Width,r.Height,96,96,PixelFormats.Bgra32,null,r.Bgra,r.Width*4);image.Freeze();textures.Add((Path.GetFileNameWithoutExtension(file),image));}
            catch(Exception ex){textures.Add((Path.GetFileName(file)+" ("+ex.Message+")",null!));}
        }
        Title="DI3 Mesh Preview — "+label; Width=1100; Height=780; MinWidth=600; MinHeight=450;
        Background=Brushes.Black;
        var root=new DockPanel(); Content=root;
        var bar=new StackPanel { Orientation=Orientation.Horizontal, Margin=new Thickness(8) };
        var toggle=new Button { Content="Toggle wireframe", Padding=new Thickness(12,5,12,5) };
        toggle.Click+=(_,_)=>{wireframe=!wireframe; BuildGeometry();};bar.Children.Add(toggle);
        info.Foreground=Brushes.White;info.Margin=new Thickness(12,6,0,0);bar.Children.Add(info);
        DockPanel.SetDock(bar,Dock.Top);root.Children.Add(bar);
        var side=new StackPanel{Width=265,Margin=new Thickness(8)};
        var overlay=new System.Windows.Controls.CheckBox{Content="Show rig / scene nodes",Foreground=Brushes.White};overlay.Checked+=(_,_)=>{showRig=true;BuildGeometry();};overlay.Unchecked+=(_,_)=>{showRig=false;BuildGeometry();};side.Children.Add(overlay);
        var only=new System.Windows.Controls.CheckBox{Content="Rig only",Foreground=Brushes.White};only.Checked+=(_,_)=>{rigOnly=true;showRig=true;overlay.IsChecked=true;BuildGeometry();};only.Unchecked+=(_,_)=>{rigOnly=false;BuildGeometry();};side.Children.Add(only);
        side.Children.Add(new TextBlock{Text=$"{joints.Count} rig entries. Skin bind bones when present; otherwise scene nodes. Unverified helper links are omitted.",TextWrapping=TextWrapping.Wrap,Foreground=Brushes.LightGray,Margin=new Thickness(0,8,0,8)});
        var list=new System.Windows.Controls.ListBox{Height=155};foreach(var j in joints)list.Items.Add(j.Name);side.Children.Add(list);
        side.Children.Add(new TextBlock{Text="Color texture per material (MTB sampler references)",TextWrapping=TextWrapping.Wrap,Foreground=Brushes.White,Margin=new Thickness(0,10,0,5)});
        var mtbPath=Path.ChangeExtension(model.path,".mtb");
        var bundle=File.Exists(mtbPath)?MaterialBundleReader.Read(File.ReadAllBytes(mtbPath)):null;
        foreach(int reference in model.slots.Select(s=>s.reference).Distinct())
        {
            int slot=reference;string name=model.slots.First(s=>s.reference==slot).name;
            side.Children.Add(new TextBlock{Text=name,TextWrapping=TextWrapping.Wrap,Foreground=Brushes.LightGray});
            var combo=new System.Windows.Controls.ComboBox{Margin=new Thickness(0,4,0,10)};combo.Items.Add("Plain preview color");foreach(var t in textures)combo.Items.Add(t.Name);combo.SelectedIndex=0;
            combo.SelectionChanged+=(_,_)=>{int i=combo.SelectedIndex-1;if(i>=0&&textures[i].Image!=null){var brush=new ImageBrush(textures[i].Image){TileMode=TileMode.Tile,ViewportUnits=BrushMappingMode.Absolute,Viewport=new Rect(0,0,1,1)};selectedMaterials[slot]=new DiffuseMaterial(brush);}else selectedMaterials.Remove(slot);if(!initializing)BuildGeometry();};
            string? colorId=bundle?.ColorTexture(slot);
            if(colorId!=null)
            {
                int match=textures.FindIndex(t=>string.Equals(t.Name,colorId,StringComparison.OrdinalIgnoreCase)&&t.Image!=null);
                if(match>=0)combo.SelectedIndex=match+1;
            }
            side.Children.Add(combo);
        }
        var scroll=new ScrollViewer{Content=side,VerticalScrollBarVisibility=ScrollBarVisibility.Auto};DockPanel.SetDock(scroll,Dock.Left);root.Children.Add(scroll);
        viewport.Camera=camera;root.Children.Add(viewport);
        var visual=new ModelVisual3D{Content=scene};viewport.Children.Add(visual);
        scene.Children.Add(new AmbientLight(Color.FromRgb(115,115,115)));
        scene.Children.Add(new DirectionalLight(Colors.White,new Vector3D(-0.6,-0.8,-1)));
        scene.Children.Add(new DirectionalLight(Color.FromRgb(100,110,135),new Vector3D(0.7,0.3,0.6)));
        camera.FieldOfView=50;camera.UpDirection=new Vector3D(0,1,0);
        SetBounds();initializing=false;BuildGeometry();UpdateCamera();
        viewport.MouseDown+=(_,e)=>{last=e.GetPosition(viewport);viewport.CaptureMouse();};
        viewport.MouseUp+=(_,_)=>{last=null;viewport.ReleaseMouseCapture();};
        viewport.MouseMove+=(_,e)=>{if(last is not System.Windows.Point old || e.LeftButton!=MouseButtonState.Pressed)return;var next=e.GetPosition(viewport);azimuth+=(next.X-old.X)*0.01;elevation=Math.Clamp(elevation+(next.Y-old.Y)*0.01,-1.5,1.5);last=next;UpdateCamera();};
        viewport.MouseWheel+=(_,e)=>{radius*=Math.Pow(0.85,e.Delta/120.0);radius=Math.Clamp(radius,0.01,1e8);UpdateCamera();};
    }
    void SetBounds()
    {
        if(model.positions.Length==0)throw new InvalidDataException("No vertices.");
        var lo = new System.Numerics.Vector3(float.MaxValue);
        var hi = new System.Numerics.Vector3(float.MinValue);
        foreach(var p in model.positions){lo=System.Numerics.Vector3.Min(lo,p);hi=System.Numerics.Vector3.Max(hi,p);}
        center=new Point3D((lo.X+hi.X)/2,(lo.Y+hi.Y)/2,(lo.Z+hi.Z)/2);
        radius=Math.Max(0.01,(hi-lo).Length()*1.7);
    }
    void UpdateCamera()
    {
        var ce=Math.Cos(elevation);
        camera.Position=new Point3D(center.X+radius*ce*Math.Sin(azimuth),center.Y+radius*Math.Sin(elevation),center.Z+radius*ce*Math.Cos(azimuth));
        camera.LookDirection=center-camera.Position;
        camera.NearPlaneDistance=Math.Max(0.001,radius/10000);
        camera.FarPlaneDistance=Math.Max(100,radius*100);
    }
    void BuildGeometry()
    {
        while(scene.Children.Count>3)scene.Children.RemoveAt(3);
        var pts=new Point3DCollection(model.positions.Select(p=>new Point3D(p.X,p.Y,p.Z)));
        int triCount=0;
        for(int group=0;!rigOnly&&group<model.triangles.Count;group++)
        {
            var indices=model.triangles[group];triCount+=indices.Length/3;
            if(!wireframe)
            {
                var mesh=new MeshGeometry3D { Positions=pts, TriangleIndices=new Int32Collection(indices), TextureCoordinates=new PointCollection(model.uvs.Select(v=>new System.Windows.Point(v.X,1-v.Y))) };
                var mat=new DiffuseMaterial(new SolidColorBrush(Color.FromRgb((byte)(140+group*31%90),(byte)(150+group*17%85),(byte)(165+group*13%70))));
                var actual=selectedMaterials.TryGetValue(model.slots[group].reference,out var chosen)?chosen:mat;
                scene.Children.Add(new GeometryModel3D(mesh,actual){BackMaterial=actual});
            }
            else
            {
                // Thin triangle-edge strips provide a wireframe-like view in native WPF 3D.
                // Duplicate edges are retained; line width is relative to model size.
                double thickness=Math.Max(radius/2500,0.00001);
                var linePts=new Point3DCollection();var lineIndices=new Int32Collection();
                void Edge(int a,int b)
                {
                    if(a<0||b<0||a>=pts.Count||b>=pts.Count)return;
                    var x=pts[a];var y=pts[b];var d=y-x;
                    if(d.LengthSquared<1e-15)return;
                    var cross=Vector3D.CrossProduct(d,new Vector3D(0,1,0));
                    if(cross.LengthSquared<1e-15)cross=Vector3D.CrossProduct(d,new Vector3D(1,0,0));
                    cross.Normalize();cross*=thickness;
                    int i=linePts.Count;
                    linePts.Add(x+cross);linePts.Add(x-cross);linePts.Add(y+cross);linePts.Add(y-cross);
                    lineIndices.Add(i);lineIndices.Add(i+1);lineIndices.Add(i+2);
                    lineIndices.Add(i+1);lineIndices.Add(i+3);lineIndices.Add(i+2);
                }
                for(int i=0;i+2<indices.Length;i+=3){Edge(indices[i],indices[i+1]);Edge(indices[i+1],indices[i+2]);Edge(indices[i+2],indices[i]);}
                var mesh=new MeshGeometry3D{Positions=linePts,TriangleIndices=lineIndices};
                var mat=new DiffuseMaterial(Brushes.Cyan);
                scene.Children.Add(new GeometryModel3D(mesh,mat){BackMaterial=mat});
            }
        }
        if(showRig)
        {
            double size=Math.Max(radius/180,0.002);
            foreach(var j in joints)
            {
                var p=new Point3D(j.Position.X,j.Position.Y,j.Position.Z);
                Rod(p-new Vector3D(size,0,0),p+new Vector3D(size,0,0),size/3);
                Rod(p-new Vector3D(0,size,0),p+new Vector3D(0,size,0),size/3);
                if(j.Parent>=0){var q=joints[j.Parent].Position;Rod(p,new Point3D(q.X,q.Y,q.Z),size/4);}
            }
        }
        info.Text=$"{model.positions.Length:N0} vertices · {triCount:N0} triangles · {model.triangles.Count} primitives | Drag: orbit · Wheel: zoom";
    }
    void Rod(Point3D a,Point3D b,double width)
    {
        var d=b-a;if(d.LengthSquared<1e-15)return;
        var x=Vector3D.CrossProduct(d,new Vector3D(0,1,0));if(x.LengthSquared<1e-15)x=Vector3D.CrossProduct(d,new Vector3D(1,0,0));x.Normalize();x*=width;
        var y=Vector3D.CrossProduct(d,x);y.Normalize();y*=width;
        var pts=new Point3DCollection{a-x-y,a+x-y,a+x+y,a-x+y,b-x-y,b+x-y,b+x+y,b-x+y};
        var mesh=new MeshGeometry3D{Positions=pts,TriangleIndices=new Int32Collection{0,1,2,0,2,3,4,6,5,4,7,6,0,4,5,0,5,1,1,5,6,1,6,2,2,6,7,2,7,3,3,7,4,3,4,0}};
        var mat=new EmissiveMaterial(Brushes.Lime);scene.Children.Add(new GeometryModel3D(mesh,mat){BackMaterial=mat});
    }

}




