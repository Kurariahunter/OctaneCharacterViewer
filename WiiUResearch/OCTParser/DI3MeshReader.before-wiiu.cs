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
        public static Node Parse(string path)
        {
            using (var r = new BinaryReader(File.OpenRead(path)))
            {
                if (r.BaseStream.Length < 64 || r.BaseStream.Length > 128 * 1024 * 1024) throw new InvalidDataException("Unexpected OCT size.");
                r.BaseStream.Position = 61;
                var strings = new List<string> { "" };
                for (;;) { string s = CString(r); strings.Add(s); if (s == "\x01") break; if (strings.Count > 65536) throw new InvalidDataException("Invalid OCT string table."); }
                U16(r);
                var root = new Node { name = "Root" }; var stack = new List<Node> { root };
                while (r.BaseStream.Position < r.BaseStream.Length)
                {
                    long offset = r.BaseStream.Position;
                    int flag = U16(r), si = U16(r), depth = flag / 0x400, type = flag % 0x400;
                    if (si >= strings.Count || depth < 1 || depth > stack.Count) throw new InvalidDataException("Invalid OCT hierarchy at " + offset);
                    var node = new Node { name = strings[si] }; int count = 0;
                    Func<int> element = null;
                    switch (type)
                    {
                        case 0x01: break;
                        case 0x05: case 0x0b: node.value = strings[U16(r)]; break;
                        case 0x13: node.value = F32(r); break;
                        case 0x1b: node.value = (int)r.ReadSByte(); break;
                        case 0x11b: node.value = (int)U16(r); break;
                        case 0x21b: node.value = U24(r); break;
                        case 0x31b: node.value = U32(r); break;
                        case 0x0a: case 0x4a:
                            count = type == 0x0a ? r.ReadByte() : U16(r);
                            var sa = new string[count]; for (int i = 0; i < count; i++) sa[i] = strings[U16(r)]; node.value = sa; break;
                        case 0x12:
                            count = r.ReadByte(); var fa = new float[count]; for (int i = 0; i < count; i++) fa[i] = F32(r); node.value = fa; break;
                        case 0x1a: count = r.ReadByte(); element = () => r.ReadSByte(); break;
                        case 0x23: count = r.ReadByte(); element = () => r.ReadByte(); break;
                        case 0x5a: count = U16(r); element = () => r.ReadByte(); break;
                        case 0x63:
                            // decode_tup.py identifies 0x63 as binary data: uint16 byte count + raw uint8 bytes.
                            // Preserve it as byte[] instead of widening to int[] so ClipDataBlock and other blobs
                            // remain byte-exact for downstream diagnostics/decoders.
                            count = U16(r);
                            node.value = r.ReadBytes(count);
                            if (((byte[])node.value).Length != count) throw new EndOfStreamException("Truncated OCT binary-data record at " + offset);
                            break;
                        case 0x11a: count = r.ReadByte(); element = () => U16(r); break;
                        case 0x15a: count = U16(r); element = () => U16(r); break;
                        case 0x21a: count = r.ReadByte(); element = () => U24(r); break;
                        default: throw new InvalidDataException("Unsupported OCT record 0x" + type.ToString("X") + " at " + offset + ". No mesh was created.");
                    }
                    if (element != null) { var a = new int[count]; for (int i = 0; i < count; i++) a[i] = element(); node.value = a; }
                    while (stack.Count > depth) stack.RemoveAt(stack.Count - 1);
                    stack[depth - 1].children.Add(node); stack.Add(node);
                }
                return root;
            }
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
        public static Model Read(string path, string[] geometryIds = null)
        {
            var tree = Parse(path);
            var vpool = tree.All("VertexBufferPool").FirstOrDefault();
            var ipool = tree.All("IndexBufferPool").FirstOrDefault();
            if (vpool == null || ipool == null) throw new InvalidDataException("OCT has no model buffers.");
            var primitives = Geometries(tree, geometryIds).SelectMany(n => n.Get("Primitives").children).Where(n => n.name == "Primitive" && n.Get("Vdata") != null).ToArray();
            if (primitives.Length == 0) throw new InvalidDataException("No supported geometry primitives.");
            var result = new Model { path = path }; var verts = new List<Vector3>(); var uv = new List<Vector2>();
            string folder = Path.GetDirectoryName(path);
            foreach (var p in primitives)
            {
                var v = p.Numbers("Vdata"); var id = p.Numbers("Idata");
                if (v == null || v.Length < 5 || v[4] != 16 || id == null || id.Length != 4 || id[3] % 3 != 0)
                    throw new InvalidDataException("Unsupported vertex/index layout (expected xyz float32 + UV float16, triangle list).");
                if (v[1] <= 0 || v[1] > 2000000 || id[3] <= 0 || id[3] > 12000000) throw new InvalidDataException("Mesh counts exceed supported limits.");
                Node vb = vpool.children.FirstOrDefault(n => n.value as string == v[2].ToString());
                Node ib = ipool.children.FirstOrDefault(n => n.value as string == id[0].ToString());
                if (vb == null || ib == null) throw new InvalidDataException("Missing buffer reference.");
                int width = ib.Number("Width"); if (width != 2 && width != 4) throw new InvalidDataException("Only 16/32-bit index buffers are supported.");
                int start = verts.Count;
                using (var r = new BinaryReader(File.OpenRead(BufferPath(folder, vb.Text("FileName")))))
                {
                    if (v[3] < 0 || (long)v[3] + v[1] * 16L > r.BaseStream.Length) throw new InvalidDataException("Vertex stream exceeds buffer size.");
                    r.BaseStream.Position = v[3];
                    for (int j = 0; j < v[1]; j++)
                    {
                        float x = r.ReadSingle(), y = r.ReadSingle(), z = r.ReadSingle(), u = Half(r.ReadUInt16()), w = Half(r.ReadUInt16());
                        if (!Finite(x) || !Finite(y) || !Finite(z) || !Finite(u) || !Finite(w)) throw new InvalidDataException("Non-finite vertex data.");
                        verts.Add(new Vector3(-x, y, z)); uv.Add(new Vector2(u, 1 - w));
                    }
                }
                var tris = new int[id[3]];
                using (var r = new BinaryReader(File.OpenRead(BufferPath(folder, ib.Text("FileName")))))
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
            byte[] b = File.ReadAllBytes(mtb);
            for (int p = 0; p + 20 <= b.Length; p++)
            {
                if (b[p] != 'T' || b[p + 1] != 'E' || b[p + 2] != 'X' || b[p + 3] != 'B') continue;
                uint count = BitConverter.ToUInt32(b, p + 12);
                if (count > 4096 || p + 20L + count * 12L > b.Length) throw new InvalidDataException("Invalid MTB texture table.");
                for (int i = 0; i < count; i++) result.Add(BitConverter.ToString(b, p + 20 + i * 12, 8).Replace("-", "").ToLowerInvariant());
                return result;
            }
            return result;
        }
    }
}

