from pathlib import Path
root=Path(r'C:\Users\Kurar\Documents\AssetWiiUdio');out=Path(__file__).parent
s=(root/'Di3MeshPreviewWindow.cs').read_text(encoding='utf-8-sig')
s=s.replace('using System.Linq;','using System.Linq;\nusing System.Collections.Generic;\nusing System.Windows.Media.Imaging;')
s=s.replace('    bool wireframe;', '''    bool wireframe;
    bool showRig,rigOnly;
    readonly Dictionary<int,Material> selectedMaterials=new();
    readonly List<PreviewRig.Joint> joints;
    readonly List<(string Name,BitmapSource Image)> textures=new();''')
s=s.replace('        this.model=model;', '''        this.model=model;
        joints=PreviewRig.Read(model.path);
        foreach(var file in Directory.GetFiles(Path.GetDirectoryName(model.path)!,"*.tbody"))
        {
            try {var r=Gx2ExternalPreview.Convert(File.ReadAllBytes(file));var image=BitmapSource.Create(r.Width,r.Height,96,96,PixelFormats.Bgra32,null,r.Bgra,r.Width*4);image.Freeze();textures.Add((Path.GetFileNameWithoutExtension(file),image));}
            catch(Exception ex){textures.Add((Path.GetFileName(file)+" ("+ex.Message+")",null!));}
        }''')
s=s.replace('        DockPanel.SetDock(bar,Dock.Top);root.Children.Add(bar);', '''        DockPanel.SetDock(bar,Dock.Top);root.Children.Add(bar);
        var side=new StackPanel{Width=265,Margin=new Thickness(8)};
        var overlay=new CheckBox{Content="Show rig / scene nodes",Foreground=Brushes.White};overlay.Checked+=(_,_)=>{showRig=true;BuildGeometry();};overlay.Unchecked+=(_,_)=>{showRig=false;BuildGeometry();};side.Children.Add(overlay);
        var only=new CheckBox{Content="Rig only",Foreground=Brushes.White};only.Checked+=(_,_)=>{rigOnly=true;showRig=true;overlay.IsChecked=true;BuildGeometry();};only.Unchecked+=(_,_)=>{rigOnly=false;BuildGeometry();};side.Children.Add(only);
        side.Children.Add(new TextBlock{Text=$"{joints.Count} scene nodes. Links show recorded parents only. A rigid-piece package is not a full skeleton.",TextWrapping=TextWrapping.Wrap,Foreground=Brushes.LightGray,Margin=new Thickness(0,8,0,8)});
        var list=new ListBox{Height=155};foreach(var j in joints)list.Items.Add(j.Name);side.Children.Add(list);
        side.Children.Add(new TextBlock{Text="Color texture per material (manual assignment)",TextWrapping=TextWrapping.Wrap,Foreground=Brushes.White,Margin=new Thickness(0,10,0,5)});
        foreach(int reference in model.slots.Select(s=>s.reference).Distinct())
        {
            int slot=reference;string name=model.slots.First(s=>s.reference==slot).name;
            side.Children.Add(new TextBlock{Text=name,TextWrapping=TextWrapping.Wrap,Foreground=Brushes.LightGray});
            var combo=new ComboBox{Margin=new Thickness(0,4,0,10)};combo.Items.Add("Plain preview color");foreach(var t in textures)combo.Items.Add(t.Name);combo.SelectedIndex=0;
            combo.SelectionChanged+=(_,_)=>{int i=combo.SelectedIndex-1;if(i>=0&&textures[i].Image!=null){var brush=new ImageBrush(textures[i].Image){TileMode=TileMode.Tile,ViewportUnits=BrushMappingMode.Absolute,Viewport=new Rect(0,0,1,1)};selectedMaterials[slot]=new DiffuseMaterial(brush);}else selectedMaterials.Remove(slot);BuildGeometry();};side.Children.Add(combo);
        }
        var scroll=new ScrollViewer{Content=side,VerticalScrollBarVisibility=ScrollBarVisibility.Auto};DockPanel.SetDock(scroll,Dock.Left);root.Children.Add(scroll);''')
s=s.replace('for(int group=0;group<model.triangles.Count;group++)','for(int group=0;!rigOnly&&group<model.triangles.Count;group++)')
s=s.replace('scene.Children.Add(new GeometryModel3D(mesh,mat){BackMaterial=mat});','var actual=selectedMaterials.TryGetValue(model.slots[group].reference,out var chosen)?chosen:mat;\n                scene.Children.Add(new GeometryModel3D(mesh,actual){BackMaterial=actual});',1)
s=s.replace('        info.Text=$', '''        if(showRig)
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
        info.Text=$''')
idx=s.rfind('\n}')
s=s[:idx]+'''
    void Rod(Point3D a,Point3D b,double width)
    {
        var d=b-a;if(d.LengthSquared<1e-15)return;
        var x=Vector3D.CrossProduct(d,new Vector3D(0,1,0));if(x.LengthSquared<1e-15)x=Vector3D.CrossProduct(d,new Vector3D(1,0,0));x.Normalize();x*=width;
        var y=Vector3D.CrossProduct(d,x);y.Normalize();y*=width;
        var pts=new Point3DCollection{a-x-y,a+x-y,a+x+y,a-x+y,b-x-y,b+x-y,b+x+y,b-x+y};
        var mesh=new MeshGeometry3D{Positions=pts,TriangleIndices=new Int32Collection{0,1,2,0,2,3,4,6,5,4,7,6,0,4,5,0,5,1,1,5,6,1,6,2,2,6,7,2,7,3,3,7,4,3,4,0}};
        var mat=new EmissiveMaterial(Brushes.Lime);scene.Children.Add(new GeometryModel3D(mesh,mat){BackMaterial=mat});
    }
'''+s[idx:]
(out/'Di3MeshPreviewWindow.cs').write_text(s,encoding='utf-8')
s=(root/'ArchiveBrowserWindow.cs').read_text(encoding='utf-8-sig')
s=s.replace('bool needed=string.Equals(name,Path.GetFileName(oct.Name),StringComparison.OrdinalIgnoreCase)', 'bool needed=name.EndsWith(".tbody",StringComparison.OrdinalIgnoreCase) || name.Equals(stem+".mtb",StringComparison.OrdinalIgnoreCase) || string.Equals(name,Path.GetFileName(oct.Name),StringComparison.OrdinalIgnoreCase)')
(out/'ArchiveBrowserWindow.cs').write_text(s,encoding='utf-8')
