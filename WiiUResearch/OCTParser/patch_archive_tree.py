from pathlib import Path
root=Path(r'C:\Users\Kurar\Documents\AssetWiiUdio');out=Path(__file__).parent
s=(root/'ArchiveBrowserWindow.cs').read_text(encoding='utf-8-sig')
s=s.replace('private readonly ListView list;', '''private readonly TreeView list;
    private DisneyInfinityArchive.Member? SelectedMember => (list.SelectedItem as TreeViewItem)?.Tag as DisneyInfinityArchive.Member;''')
a=s.index('        list=new ListView');z=s.index('        var columns=new Grid();',a)
s=s[:a]+'''        list=new TreeView{Background=new SolidColorBrush(Color.FromRgb(29,38,51)),Foreground=Brushes.White};
        var directories=new System.Collections.Generic.Dictionary<string,TreeViewItem>(StringComparer.Ordinal);
        foreach(var member in a.Members.OrderBy(m=>m.Name,StringComparer.OrdinalIgnoreCase).ThenBy(m=>m.Name,StringComparer.Ordinal))
        {
            var parts=member.Name.Replace('\\\\','/').Split('/',StringSplitOptions.RemoveEmptyEntries);
            ItemsControl parent=list;string prefix="";
            for(int i=0;i<parts.Length-1;i++)
            {
                prefix+=parts[i]+"/";
                if(!directories.TryGetValue(prefix,out var folder))
                {
                    folder=new TreeViewItem{Header=parts[i]+"/",Tag=prefix,Foreground=Brushes.LightSkyBlue,IsExpanded=i==0};
                    directories.Add(prefix,folder);parent.Items.Add(folder);
                }
                parent=folder;
            }
            parent.Items.Add(new TreeViewItem{Header=parts.Length==0?member.Name:parts[^1],Tag=member,Foreground=Brushes.White,ToolTip=$"{member.Name}\\nPacked: {member.PackedSize:N0} bytes | Unpacked: {member.Size:N0} bytes"});
        }
        void SortTree(ItemsControl parent)
        {
            var sorted=parent.Items.Cast<TreeViewItem>().OrderBy(n=>n.Tag is DisneyInfinityArchive.Member?1:0).ThenBy(n=>n.Header.ToString(),StringComparer.OrdinalIgnoreCase).ToArray();
            parent.Items.Clear();foreach(var child in sorted){parent.Items.Add(child);if(child.Tag is not DisneyInfinityArchive.Member)SortTree(child);}
        }
        SortTree(list);
        void ClearPreview(){textureImage.Source=null;previewPng=null;previewDds=null;textureStatus.Text="Select a .tbody or .tstream texture to preview";}
        list.SelectedItemChanged+=(_,_)=>
        {
            if(SelectedMember is DisneyInfinityArchive.Member m)
            {
                details.Text=$"Name: {m.Name}\\nPacked: {m.PackedSize:N0} | Unpacked: {m.Size:N0} bytes\\nOffset: 0x{m.Offset:X} | Method: {m.Method} | Encrypted payload: {m.Encrypted}\\n{m.Note}\\n{a.Note}";
                if(m.Name.EndsWith(".tbody",StringComparison.OrdinalIgnoreCase)||m.Name.EndsWith(".tstream",StringComparison.OrdinalIgnoreCase))_=PreviewTextureAsync(m);
                else ClearPreview();
            }
            else
            {
                ClearPreview();var prefix=(list.SelectedItem as TreeViewItem)?.Tag as string??"";
                details.Text=$"Folder: {prefix}\\n{a.Members.Count(m=>m.Name.Replace('\\\\','/').StartsWith(prefix,StringComparison.Ordinal)):N0} contained files. Select a file to export or preview.";
            }
        };
        void Expand(ItemsControl parent,bool expanded){foreach(TreeViewItem item in parent.Items)if(item.Tag is not DisneyInfinityArchive.Member){item.IsExpanded=expanded;Expand(item,expanded);}}
        var expand=new Button{Content="Expand all",Padding=new Thickness(8,7,8,7),Margin=new Thickness(4)};expand.Click+=(_,_)=>Expand(list,true);bar.Children.Add(expand);
        var collapse=new Button{Content="Collapse all",Padding=new Thickness(8,7,8,7),Margin=new Thickness(4)};collapse.Click+=(_,_)=>Expand(list,false);bar.Children.Add(collapse);
''' +s[z:]
s=s.replace('ReferenceEquals(list.SelectedItem, member)','ReferenceEquals(SelectedMember, member)')
s=s.replace('(list.SelectedItem as DisneyInfinityArchive.Member)?.Name','SelectedMember?.Name')
s=s.replace('var chosen=list.SelectedItem as DisneyInfinityArchive.Member;','var chosen=SelectedMember;')
s=s.replace('if(list.SelectedItem is not DisneyInfinityArchive.Member member)','if(SelectedMember is not DisneyInfinityArchive.Member member)')
s=s.replace('BC1/DXT1  |  GX2 native linear BC1','GX2 texture')
# Keep toolbar within the window now that navigation buttons have been added.
s=s.replace('var bar=new StackPanel{Orientation=Orientation.Horizontal,','var bar=new WrapPanel{Orientation=Orientation.Horizontal,')
(out/'ArchiveBrowserWindow.tree.cs').write_text(s,encoding='utf-8')
print(out/'ArchiveBrowserWindow.tree.cs')
