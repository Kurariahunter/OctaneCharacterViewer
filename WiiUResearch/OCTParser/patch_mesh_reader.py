from pathlib import Path
src=Path(r'C:\Users\Kurar\Documents\AssetWiiUdio\DI3MeshReader.cs')
s=src.read_text(encoding='utf-8-sig')
a=s.index('        public static Node Parse(string path)');z=s.index('        public static string[] FindModels',a)
s=s[:a]+'''        sealed class OrderedReader : BinaryReader
        {
            public bool Big;
            public OrderedReader(Stream stream, bool big) : base(stream) { Big=big; }
            public uint Packed(int count) { uint v=0; for(int i=0;i<count;i++) { byte b=ReadByte(); if(Big)v=(v<<8)|b;else v|=(uint)b<<(8*i); } return v; }
            public override ushort ReadUInt16() => (ushort)Packed(2);
            public override uint ReadUInt32() => Packed(4);
            public override float ReadSingle() => BitConverter.Int32BitsToSingle(unchecked((int)Packed(4)));
        }
        static bool BigEndian(string path)
        {
            using var r=new BinaryReader(File.OpenRead(path));
            uint magic=r.ReadUInt32();
            if(magic==0x29760145)return true;
            if(magic==0x45017629)return false;
            throw new InvalidDataException("Unrecognized BinaryTup magic.");
        }
        public static Node Parse(string path)
        {
            using var r=new OrderedReader(File.OpenRead(path),BigEndian(path));
            if(r.BaseStream.Length<60||r.BaseStream.Length>128*1024*1024)throw new InvalidDataException("Unexpected OCT size.");
            r.BaseStream.Position=12;
            uint stringBytes=r.ReadUInt32(),atomBytes=r.ReadUInt32(),atomCount=r.ReadUInt32();
            long atomStart=60L+stringBytes;
            if(atomStart+atomBytes!=r.BaseStream.Length||atomCount>atomBytes/4)throw new InvalidDataException("Invalid OCT header lengths/count.");
            r.BaseStream.Position=60;
            var strings=new List<string>();
            while(r.BaseStream.Position<atomStart) { strings.Add(CString(r));if(r.BaseStream.Position>atomStart)throw new InvalidDataException("Unterminated OCT string table."); }
            int indexBytes=strings.Count<=65536?2:4;
            string StringIndex() { uint i=r.Packed(indexBytes);if(i>=strings.Count)throw new InvalidDataException("Invalid OCT string index.");return strings[(int)i]; }
            var root=new Node {name="Root"};var stack=new List<Node>();uint parsed=0;
            while(r.BaseStream.Position<r.BaseStream.Length)
            {
                long offset=r.BaseStream.Position;int flag=r.ReadUInt16(),depth=flag>>10,kind=flag&3,type=(flag>>3)&7;
                var node=new Node {name=StringIndex()};if((flag&4)!=0)node.value=StringIndex();
                int countWidth=((flag>>6)&3)+1,intWidth=((flag>>8)&3)+1;
                uint count=(kind==2||(kind==3&&type==4))?r.Packed(countWidth):1;
                if(count>r.BaseStream.Length-r.BaseStream.Position)throw new InvalidDataException("OCT count exceeds remaining data.");
                if(kind==1) { }
                else if(kind==2||kind==3)
                {
                    if(type==1) {var v=new string[(int)count];for(int i=0;i<v.Length;i++)v[i]=StringIndex();node.value=kind==3?(object)v[0]:v;}
                    else if(type==2) {var v=new float[(int)count];for(int i=0;i<v.Length;i++)v[i]=r.ReadSingle();node.value=kind==3?(object)v[0]:v;}
                    else if(type==3) {var v=new int[(int)count];for(int i=0;i<v.Length;i++){uint raw=r.Packed(intWidth);int shift=32-intWidth*8;v[i]=unchecked((int)(raw<<shift))>>shift;}node.value=kind==3?(object)v[0]:v;}
                    else if(type==4&&kind==3) {var v=r.ReadBytes((int)count);if(v.Length!=count)throw new EndOfStreamException();node.value=v;}
                    else throw new InvalidDataException("Unsupported OCT type at "+offset);
                }
                else throw new InvalidDataException("Invalid OCT atom at "+offset);
                while(stack.Count>depth)stack.RemoveAt(stack.Count-1);
                if(depth!=stack.Count||(parsed==0&&depth!=0)||(parsed>0&&depth==0))throw new InvalidDataException("Invalid OCT hierarchy at "+offset);
                if(depth==0)root.children.Add(node);else stack[depth-1].children.Add(node);
                stack.Add(node);parsed++;
            }
            if(parsed!=atomCount)throw new InvalidDataException("OCT atom count mismatch.");
            return root;
        }
        // Normalize explicit stream references into the existing static-mesh descriptors.
        static void ResolveStreams(Node tree, Node primitive)
        {
            if(primitive.Get("Vdata")!=null)return;
            var refs=primitive.Numbers("VertexStreamReferences");
            var vp=tree.All("VertexStreamPool").FirstOrDefault();var ip=tree.All("IndexStreamPool").FirstOrDefault();
            if(refs==null||vp==null||ip==null)return;
            var streams=vp.children.Where(n=>refs.Contains(int.TryParse(n.value as string,out int i)?i:-1)).ToArray();
            var v=streams.FirstOrDefault(n=>n.Get("Elements")?.children.Any(e=>e.Text("Name")=="position")==true);
            var index=ip.children.FirstOrDefault(n=>n.value as string==primitive.Number("IndexStreamReference",-1).ToString());
            if(v==null||index==null)throw new InvalidDataException("Missing geometry stream.");
            var elements=v.Get("Elements").children;var pos=elements.FirstOrDefault(e=>e.Text("Name")=="position");var uv=elements.FirstOrDefault(e=>e.Text("Name")=="texcoord0");
            if(v.Number("Width")!=16||v.Number("ExtraStride")!=0||pos?.Number("Type")!=2||pos.Number("Offset")!=0||uv?.Number("Type")!=45||uv.Number("Offset")!=12||index.Text("IndexStreamPrimitive")!="TRIANGLES")
                throw new InvalidDataException("Unsupported explicit vertex stream layout.");
            primitive.children.Add(new Node {name="Vdata",value=new[]{0,v.Number("Length"),v.Number("VertexBufferReference"),v.Number("VertexBufferOffset"),16}});
            primitive.children.Add(new Node {name="Idata",value=new[]{index.Number("IndexBufferReference"),index.Number("IndexBufferOffset"),index.Number("BaseVertexIndex"),index.Number("Length")}});
        }
''' +s[z:]
s=s.replace('var tree = Parse(path);','var tree = Parse(path);\n            bool big=BigEndian(path);\n            foreach(var primitive in tree.All("Primitive"))ResolveStreams(tree,primitive);')
s=s.replace('new BinaryReader(File.OpenRead(BufferPath(folder, vb.Text("FileName"))))','new OrderedReader(File.OpenRead(BufferPath(folder, vb.Text("FileName"))),big)')
s=s.replace('new BinaryReader(File.OpenRead(BufferPath(folder, ib.Text("FileName"))))','new OrderedReader(File.OpenRead(BufferPath(folder, ib.Text("FileName"))),big)')
out=Path(__file__).parent/'DI3MeshReader.cs';out.write_text(s,encoding='utf-8');print(out)
