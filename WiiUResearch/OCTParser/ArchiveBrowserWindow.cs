using System;
using System.IO;
using System.Diagnostics;
using System.Windows.Media.Imaging;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using Microsoft.Win32;

namespace AssetWiiUdio;

public sealed class ArchiveBrowserWindow : Window
{
    private readonly DisneyInfinityArchive.Archive archive;
    private readonly ListView list;
    private readonly TextBox details;
    private readonly System.Windows.Controls.Image textureImage = new System.Windows.Controls.Image { Stretch=Stretch.Uniform };
    private readonly TextBlock textureStatus = new TextBlock { Text="Select a .tbody or .tstream texture to preview", TextWrapping=TextWrapping.Wrap, Margin=new Thickness(5) };
    private byte[]? previewPng;
    private byte[]? previewDds;

    private ArchiveBrowserWindow(string path, DisneyInfinityArchive.Archive a)
    {
        archive=a;
        Title="Archive Browser · "+Path.GetFileName(path);
        Width=1080; Height=730; MinWidth=720; MinHeight=450;
        Background=new SolidColorBrush(Color.FromRgb(22,27,36)); Foreground=Brushes.White;
        var root=new DockPanel{Margin=new Thickness(12)};
        var header=new TextBlock{Text=$"{a.Format}  |  {a.Members.Count:N0} members  |  {a.Encryption}",FontSize=17,FontWeight=FontWeights.Bold,Margin=new Thickness(4,4,4,10)};
        DockPanel.SetDock(header,Dock.Top);root.Children.Add(header);
        var bar=new StackPanel{Orientation=Orientation.Horizontal,Margin=new Thickness(0,0,0,8)};
        var export=new Button{Content="Export selected",Padding=new Thickness(12,7,12,7),Margin=new Thickness(4)};
        export.Click+=(_,_)=>ExportSelected();bar.Children.Add(export);
        var exportAll=new Button{Content="Export all supported",Padding=new Thickness(12,7,12,7),Margin=new Thickness(4)};
        exportAll.Click+=(_,_)=>ExportAll();bar.Children.Add(exportAll);
        var meshPreview=new Button{Content="Preview DI3 mesh",Padding=new Thickness(12,7,12,7),Margin=new Thickness(4)};
        meshPreview.Click+=(_,_)=>PreviewDi3Mesh();bar.Children.Add(meshPreview);
        var exportPng=new Button{Content="Export PNG",Padding=new Thickness(12,7,12,7),Margin=new Thickness(4)};
        exportPng.Click+=(_,_)=>SavePreview(previewPng,"PNG image|*.png","png");bar.Children.Add(exportPng);
        var exportDds=new Button{Content="Export DDS",Padding=new Thickness(12,7,12,7),Margin=new Thickness(4)};
        exportDds.Click+=(_,_)=>SavePreview(previewDds,"DDS texture|*.dds","dds");bar.Children.Add(exportDds);
        DockPanel.SetDock(bar,Dock.Top);root.Children.Add(bar);
        details=new TextBox{Height=135,IsReadOnly=true,TextWrapping=TextWrapping.Wrap,VerticalScrollBarVisibility=ScrollBarVisibility.Auto,Background=new SolidColorBrush(Color.FromRgb(17,25,35)),Foreground=Brushes.LightCyan,Margin=new Thickness(0,8,0,0)};
        DockPanel.SetDock(details,Dock.Bottom);root.Children.Add(details);
        list=new ListView{SelectionMode=SelectionMode.Extended,Background=new SolidColorBrush(Color.FromRgb(29,38,51)),Foreground=Brushes.White};
        var grid=new GridView();
        grid.Columns.Add(new GridViewColumn{Header="Member",Width=490,DisplayMemberBinding=new System.Windows.Data.Binding("Name")});
        grid.Columns.Add(new GridViewColumn{Header="Packed",Width=100,DisplayMemberBinding=new System.Windows.Data.Binding("PackedSize")});
        grid.Columns.Add(new GridViewColumn{Header="Unpacked",Width=100,DisplayMemberBinding=new System.Windows.Data.Binding("Size")});
        grid.Columns.Add(new GridViewColumn{Header="Method",Width=70,DisplayMemberBinding=new System.Windows.Data.Binding("Method")});
        grid.Columns.Add(new GridViewColumn{Header="Offset",Width=100,DisplayMemberBinding=new System.Windows.Data.Binding("Offset")});
        list.View=grid;
        foreach(var member in a.Members)list.Items.Add(member);
        list.SelectionChanged+=(_,_)=>
        {
            if(list.SelectedItem is DisneyInfinityArchive.Member m)
            {
                details.Text=$"Name: {m.Name}\nOffset: 0x{m.Offset:X} | Method: {m.Method} | Encrypted payload: {m.Encrypted}\n{m.Note}\n{a.Note}";
                if((m.Name.EndsWith(".tbody",StringComparison.OrdinalIgnoreCase)||m.Name.EndsWith(".tstream",StringComparison.OrdinalIgnoreCase))) _=PreviewTextureAsync(m);
                else {textureImage.Source=null;previewPng=null;previewDds=null;textureStatus.Text="Select a .tbody or .tstream texture to preview";}
            }
        };
        var columns=new Grid();
        columns.ColumnDefinitions.Add(new ColumnDefinition{Width=new GridLength(3,GridUnitType.Star)});
        columns.ColumnDefinitions.Add(new ColumnDefinition{Width=new GridLength(2,GridUnitType.Star)});
        Grid.SetColumn(list,0);columns.Children.Add(list);
        var previewPanel=new DockPanel{Margin=new Thickness(8,0,0,0)};
        DockPanel.SetDock(textureStatus,Dock.Bottom);previewPanel.Children.Add(textureStatus);
        var checker=new Border{Background=new SolidColorBrush(Color.FromRgb(60,60,60)),Child=textureImage};
        previewPanel.Children.Add(checker);
        Grid.SetColumn(previewPanel,1);columns.Children.Add(previewPanel);
        root.Children.Add(columns);Content=root;
        details.Text=a.Note;
    }
    public static void Show(Window owner,string filename,byte[] bytes)
    {
        var a=DisneyInfinityArchive.Open(filename,bytes);
        new ArchiveBrowserWindow(filename,a){Owner=owner}.ShowDialog();
    }
    private async System.Threading.Tasks.Task PreviewTextureAsync(DisneyInfinityArchive.Member member)
    {
        previewPng=null;previewDds=null;textureImage.Source=null;
        textureStatus.Text="Extracting and converting GX2 texture...";
        try
        {
            byte[] input=DisneyInfinityArchive.Extract(archive,member);
            var result=await System.Threading.Tasks.Task.Run(()=>Gx2ExternalPreview.Convert(input));
            if(!ReferenceEquals(list.SelectedItem, member))return;
            previewDds=result.Dds;
            var bitmap=BitmapSource.Create(result.Width,result.Height,96,96,PixelFormats.Bgra32,null,result.Bgra,result.Width*4);
            bitmap.Freeze();textureImage.Source=bitmap;
            var png=new PngBitmapEncoder();png.Frames.Add(BitmapFrame.Create(bitmap));
            using var mem=new MemoryStream();png.Save(mem);previewPng=mem.ToArray();
            textureStatus.Text=$"{result.Width} × {result.Height}  |  BC1/DXT1  |  GX2 native linear BC1";
        }
        catch(Exception ex){if(ReferenceEquals(list.SelectedItem, member))textureStatus.Text="Preview unavailable: "+ex.Message;}
    }
    private void SavePreview(byte[]? bytes,string filter,string extension)
    {
        if(bytes==null){MessageBox.Show(this,"Select and successfully preview a supported TBODY first.");return;}
        var dlg=new SaveFileDialog{Filter=filter,DefaultExt=extension,FileName=Path.GetFileNameWithoutExtension((list.SelectedItem as DisneyInfinityArchive.Member)?.Name??"texture")+"."+extension};
        if(dlg.ShowDialog(this)==true)File.WriteAllBytes(dlg.FileName,bytes);
    }
    private void PreviewDi3Mesh()
    {
        var octs=archive.Members.Where(m=>m.Name.EndsWith(".oct",StringComparison.OrdinalIgnoreCase)).ToArray();
        if(octs.Length==0){MessageBox.Show(this,"This archive has no OCT model descriptor.");return;}
        var chosen=list.SelectedItem as DisneyInfinityArchive.Member;
        var oct=chosen!=null && chosen.Name.EndsWith(".oct",StringComparison.OrdinalIgnoreCase)?chosen:octs[0];
        string dir=Path.Combine(Path.GetTempPath(),"AssetWiiUdio-Mesh-"+Guid.NewGuid().ToString("N"));
        try
        {
            Directory.CreateDirectory(dir);
            string stem=Path.GetFileNameWithoutExtension(oct.Name);
            foreach(var m in archive.Members)
            {
                string name=Path.GetFileName(m.Name);
                bool needed=name.EndsWith(".tbody",StringComparison.OrdinalIgnoreCase) || name.Equals(stem+".mtb",StringComparison.OrdinalIgnoreCase) || string.Equals(name,Path.GetFileName(oct.Name),StringComparison.OrdinalIgnoreCase)
                    || (name.StartsWith(stem+"_",StringComparison.OrdinalIgnoreCase) &&
                        (name.EndsWith(".vbuf",StringComparison.OrdinalIgnoreCase)||name.EndsWith(".ibuf",StringComparison.OrdinalIgnoreCase)));
                if(!needed)continue;
                File.WriteAllBytes(Path.Combine(dir,name),DisneyInfinityArchive.Extract(archive,m));
            }
            var model=DI3MeshReader.Read(Path.Combine(dir,Path.GetFileName(oct.Name)));
            new Di3MeshPreviewWindow(model,oct.Name){Owner=this}.ShowDialog();
        }
        catch(Exception ex){MessageBox.Show(this,ex.Message,"DI3 mesh preview unavailable",MessageBoxButton.OK,MessageBoxImage.Warning);}
        finally{try{Directory.Delete(dir,true);}catch{}}
    }
    private void ExportSelected()
    {
        if(list.SelectedItem is not DisneyInfinityArchive.Member member){MessageBox.Show("Select a member.");return;}
        try
        {
            string safe=DisneyInfinityArchive.SafeRelativePath(member.Name);
            var dialog=new SaveFileDialog{FileName=Path.GetFileName(safe)};
            if(dialog.ShowDialog(this)!=true)return;
            var data=DisneyInfinityArchive.Extract(archive,member);
            string temp=dialog.FileName+".assetwiiudio-partial";
            try{File.WriteAllBytes(temp,data);File.Move(temp,dialog.FileName,true);}
            finally{if(File.Exists(temp))File.Delete(temp);}
            MessageBox.Show(this,$"Exported {data.Length:N0} bytes.");
        }
        catch(Exception ex){MessageBox.Show(this,ex.Message,"Archive export failed");}
    }
    private void ExportAll()
    {
        using var folder=new System.Windows.Forms.FolderBrowserDialog{Description="Select archive extraction folder"};
        if(folder.ShowDialog()!=System.Windows.Forms.DialogResult.OK)return;
        int success=0,failed=0;
        var failures=new System.Text.StringBuilder();
        foreach(var member in archive.Members)
        {
            try
            {
                string rel=DisneyInfinityArchive.SafeRelativePath(member.Name);
                string target=Path.GetFullPath(Path.Combine(folder.SelectedPath,rel));
                string basePath=Path.GetFullPath(folder.SelectedPath).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar;
                if(!target.StartsWith(basePath,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Member path escaped export directory.");
                byte[] data=DisneyInfinityArchive.Extract(archive,member);
                Directory.CreateDirectory(Path.GetDirectoryName(target)!);
                string temp=target+".assetwiiudio-partial";
                try{File.WriteAllBytes(temp,data);File.Move(temp,target,true);}
                finally{if(File.Exists(temp))File.Delete(temp);}
                success++;
            }
            catch(Exception ex){failed++;if(failures.Length<2000)failures.AppendLine(member.Name+": "+ex.Message);}
        }
        MessageBox.Show(this,$"Exported: {success}; failed/unsupported: {failed}\n"+failures,"Archive export results");
    }
}
