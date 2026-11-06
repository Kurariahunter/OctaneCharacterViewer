// DI3 PC Gold static-mesh workflow. Format research: see README.md.
// Editor-only; no runtime components or external executables.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

using System.Numerics;


namespace AssetWiiUdio
{
    public class MaterialSlot { public string name = ""; public int reference; }
    public static class DI3MeshReader
    {
        public class Node
        {
            public string name;
            public object value;
            public List<Node> children = new List<Node>();
            public Node Get(string n) { return children.FirstOrDefault(x => x.name == n); }
            public string Text(string n) { return Get(n)?.value as string; }
            public int Number(string n, int fallback = 0) { var v = Get(n)?.value; return v == null ? fallback : Convert.ToInt32(v); }
            public int[] Numbers(string n) { return Get(n)?.value as int[]; }
            public IEnumerable<Node> All(string n)
            {
                foreach (var c in children) { if (c.name == n) yield return c; foreach (var d in c.All(n)) yield return d; }
            }
        }
        public class Model
        {
            public string path;
            public Vector3[] positions;
            public Vector2[] uvs;
            public List<int[]> triangles = new List<int[]>();
            public List<MaterialSlot> slots = new List<MaterialSlot>();
        }
        static string CString(BinaryReader r)
        {
            var b = new List<byte>(); byte c;
            while ((c = r.ReadByte()) != 0) { b.Add(c); if (b.Count > 1024 * 1024) throw new InvalidDataException("Invalid OCT string table."); }
            return Encoding.UTF8.GetString(b.ToArray());
        }
        static int U24(BinaryReader r) { return (r.ReadByte() << 16) | (r.ReadByte() << 8) | r.ReadByte(); }
        static ushort U16(BinaryReader r) => System.Buffers.Binary.BinaryPrimitives.ReadUInt16BigEndian(r.ReadBytes(2));
        static uint U32(BinaryReader r) => System.Buffers.Binary.BinaryPrimitives.ReadUInt32BigEndian(r.ReadBytes(4));
        static float F32(BinaryReader r) => BitConverter.Int32BitsToSingle(unchecked((int)U32(r)));
        sealed class OrderedReader : BinaryReader
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
        public static string[] FindModels(string folder)
        {
            if (!Directory.Exists(folder)) throw new DirectoryNotFoundException(folder);
            return Directory.GetFiles(folder, "*.oct", SearchOption.AllDirectories)
                .Where(p => Directory.GetFiles(Path.GetDirectoryName(p), Path.GetFileNameWithoutExtension(p) + "_*.ibuf").Length > 0)
                .OrderBy(p => p).ToArray();
        }
        static string BufferPath(string folder, string name)
        {
            if (string.IsNullOrEmpty(name) || Path.GetFileName(name) != name || name.Contains("..")) throw new InvalidDataException("Unsupported buffer filename.");
            return Path.Combine(folder, name);
        }
        static float Half(ushort bits)
        {
            int exp = (bits >> 10) & 31, mant = bits & 1023;
            double n = exp == 0 ? mant * Math.Pow(2, -24) : exp == 31 ? double.NaN : (1024 + mant) * Math.Pow(2, exp - 25);
            return (float)(((bits & 32768) != 0 ? -1 : 1) * n);
        }
        static bool Finite(float f) { return !float.IsNaN(f) && !float.IsInfinity(f); }
        public static Node[] Geometries(Node tree, string[] geometryIds = null)
        {
            var nodes = tree.All("Node").Where(n => n.Get("Primitives") != null).ToArray();
            if (geometryIds != null) nodes = nodes.Where(n => geometryIds.Contains((string)n.value)).ToArray();
            if (nodes.Length == 0) throw new InvalidDataException("Select at least one geometry part.");
            return nodes;
        }
        static Matrix4x4 ScenePlacement(Node tree,Node geometry)
        {
            var data=geometry.Get("LocalToParentMatrix")?.value as float[];
            if(data==null)return Matrix4x4.Identity;
            // Verified flat rigid-piece scenes: do not pretend a nested asset graph is flat.
            if(tree.All("Asset").Any(a=>a.Number("AggregateCount")!=0))
                throw new InvalidDataException("Nested scene placement requires parent transform resolution.");
            if(data.Length!=16||data.Any(f=>!Finite(f)))throw new InvalidDataException("Invalid scene matrix.");
            var m=new Matrix4x4(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10],data[11],data[12],data[13],data[14],data[15]);
            if(Math.Abs(m.M14)>1e-6||Math.Abs(m.M24)>1e-6||Math.Abs(m.M34)>1e-6||Math.Abs(m.M44-1)>1e-6||m.GetDeterminant()<=0)
                throw new InvalidDataException("Unsupported projective, singular or mirrored scene matrix.");
            return m;
        }
        public static Model Read(string path, string[] geometryIds = null)
        {
            var tree = Parse(path);
            bool big=BigEndian(path);
            foreach(var primitive in tree.All("Primitive"))ResolveStreams(tree,primitive);
            var vpool = tree.All("VertexBufferPool").FirstOrDefault();
            var ipool = tree.All("IndexBufferPool").FirstOrDefault();
            if (vpool == null || ipool == null) throw new InvalidDataException("OCT has no model buffers.");
            var geometryNodes=Geometries(tree,geometryIds);
            var owners=new Dictionary<Node,Node>();
            foreach(var geometry in geometryNodes)
                foreach(var primitive in geometry.Get("Primitives").children.Where(n=>n.name=="Primitive"&&n.Get("Vdata")!=null))owners.Add(primitive,geometry);
            var primitives=owners.Keys.ToArray();
            if (primitives.Length == 0) throw new InvalidDataException("No supported geometry primitives.");
            var result = new Model { path = path }; var verts = new List<Vector3>(); var uv = new List<Vector2>();
            string folder = Path.GetDirectoryName(path);
            foreach (var p in primitives)
            {
                var v = p.Numbers("Vdata"); var id = p.Numbers("Idata");
                var placement=ScenePlacement(tree,owners[p]);
                if (v == null || v.Length < 5 || v[4] != 16 || id == null || id.Length != 4 || id[3] % 3 != 0)
                    throw new InvalidDataException("Unsupported vertex/index layout (expected xyz float32 + UV float16, triangle list).");
                if (v[1] <= 0 || v[1] > 2000000 || id[3] <= 0 || id[3] > 12000000) throw new InvalidDataException("Mesh counts exceed supported limits.");
                Node vb = vpool.children.FirstOrDefault(n => n.value as string == v[2].ToString());
                Node ib = ipool.children.FirstOrDefault(n => n.value as string == id[0].ToString());
                if (vb == null || ib == null) throw new InvalidDataException("Missing buffer reference.");
                int width = ib.Number("Width"); if (width != 2 && width != 4) throw new InvalidDataException("Only 16/32-bit index buffers are supported.");
                int start = verts.Count;
                using (var r = new OrderedReader(File.OpenRead(BufferPath(folder, vb.Text("FileName"))),big))
                {
                    if (v[3] < 0 || (long)v[3] + v[1] * 16L > r.BaseStream.Length) throw new InvalidDataException("Vertex stream exceeds buffer size.");
                    r.BaseStream.Position = v[3];
                    for (int j = 0; j < v[1]; j++)
                    {
                        float x = r.ReadSingle(), y = r.ReadSingle(), z = r.ReadSingle(), u = Half(r.ReadUInt16()), w = Half(r.ReadUInt16());
                        if (!Finite(x) || !Finite(y) || !Finite(z) || !Finite(u) || !Finite(w)) throw new InvalidDataException("Non-finite vertex data.");
                        var placed=Vector3.Transform(new Vector3(x,y,z),placement);
                        if(!Finite(placed.X)||!Finite(placed.Y)||!Finite(placed.Z))throw new InvalidDataException("Non-finite scene placement.");
                        verts.Add(new Vector3(-placed.X,placed.Y,placed.Z)); uv.Add(new Vector2(u, 1 - w));
                    }
                }
                var tris = new int[id[3]];
                using (var r = new OrderedReader(File.OpenRead(BufferPath(folder, ib.Text("FileName"))),big))
                {
                    if (id[1] < 0 || (long)id[1] + id[3] * (long)width > r.BaseStream.Length) throw new InvalidDataException("Index stream exceeds buffer size.");
                    r.BaseStream.Position = id[1];
                    // Idata stores the index base; later geometry streams may restart at zero.
                    int baseVertex = id[2];
                    for (int j = 0; j < tris.Length; j++)
                    {
                        long raw = width == 2 ? r.ReadUInt16() : r.ReadUInt32(); long local = raw - baseVertex;
                        if (local < 0 || local >= v[1]) throw new InvalidDataException("Index is outside this primitive's vertex range. This layout needs a different decoder.");
                        tris[j] = start + (int)local;
                    }
                }
                // Reflect X and reverse winding together for Unity's handedness.
                for (int j = 0; j < tris.Length; j += 3) { int t = tris[j + 1]; tris[j + 1] = tris[j + 2]; tris[j + 2] = t; }
                result.triangles.Add(tris);
                result.slots.Add(new MaterialSlot { name = p.Text("MaterialName") ?? "Material", reference = p.Number("MaterialReference") });
            }
            result.positions = verts.ToArray(); result.uvs = uv.ToArray(); return result;
        }
        public static List<string> TextureIds(string modelPath)
        {
            string mtb = Path.ChangeExtension(modelPath, ".mtb"); var result = new List<string>();
            if (!File.Exists(mtb)) return result;
            byte[] b=File.ReadAllBytes(mtb);
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
            return result;
        }
    }
}

