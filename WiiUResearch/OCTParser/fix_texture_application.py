from pathlib import Path
root=Path(r'C:\Users\Kurar\Documents\AssetWiiUdio');out=Path(__file__).parent
s=(root/'DI3MeshReader.cs').read_text(encoding='utf-8-sig')
a=s.index('            byte[] b = File.ReadAllBytes(mtb);',s.index('public static List<string> TextureIds'));z=s.index('            return result;',a)
# Replace the entire old scan through its final return (first return is inside loop).
end=s.index('\n        }',a)
s=s[:a]+'''            byte[] b=File.ReadAllBytes(mtb);
            bool big=b.Length>=16&&Encoding.ASCII.GetString(b,0,4)=="LDNB";
            using var r=new OrderedReader(new MemoryStream(b),big);
            if(b.Length<16)return result;
            int at=16;
            while(at+16<=b.Length)
            {
                string tag=Encoding.ASCII.GetString(b,at,4);r.BaseStream.Position=at+8;
                uint size=r.ReadUInt32(),count=r.ReadUInt32();
                if(size<16||at+(long)size>b.Length)throw new InvalidDataException("Invalid MTB section.");
                if(tag==(big?"BXET":"TEXB"))
                {
                    // Observed Wii U v3 has an extra table field and 16-byte entries;
                    // PC v3 has a name-table byte count followed by 12-byte entries.
                    r.BaseStream.Position=at+16;uint names=r.ReadUInt32();
                    long first=at+(big?24L:20L)+names;int stride=big?16:12;
                    if(count>4096||first+(long)count*stride>at+size)throw new InvalidDataException("Invalid MTB texture table.");
                    for(int i=0;i<count;i++)result.Add(BitConverter.ToString(b,(int)(first+i*stride),8).Replace("-","").ToLowerInvariant());
                    return result;
                }
                at=checked(at+(int)size);
            }
            return result;''' +s[end:]
(out/'DI3MeshReader.texturefix.cs').write_text(s,encoding='utf-8')
s=(root/'Di3MeshPreviewWindow.cs').read_text(encoding='utf-8-sig')
s=s.replace('model.uvs.Select(v=>new System.Windows.Point(v.X,v.Y))','model.uvs.Select(v=>new System.Windows.Point(v.X,1-v.Y))')
s=s.replace('Color texture per material (manual assignment)','Color texture per material (MTB pair suggestions)')
needle='        foreach(int reference in model.slots.Select(s=>s.reference).Distinct())'
s=s.replace(needle,'        var textureOrder=DI3MeshReader.TextureIds(model.path);\n'+needle)
needle='selectedMaterials.Remove(slot);BuildGeometry();};side.Children.Add(combo);'
replacement='''selectedMaterials.Remove(slot);BuildGeometry();};
            int proposed=slot*2;
            if(proposed>=0&&proposed<textureOrder.Count)
            {
                int match=textures.FindIndex(t=>string.Equals(t.Name,textureOrder[proposed],StringComparison.OrdinalIgnoreCase)&&t.Image!=null);
                if(match>=0)combo.SelectedIndex=match+1;
            }
            side.Children.Add(combo);'''
assert needle in s;s=s.replace(needle,replacement)
(out/'Di3MeshPreviewWindow.texturefix.cs').write_text(s,encoding='utf-8')
