from pathlib import Path
p=Path(__file__).parent/'DI3MeshReader.cs'
s=p.read_text(encoding='utf-8-sig')
s=s.replace('var primitives = Geometries(tree, geometryIds).SelectMany(n => n.Get("Primitives").children).Where(n => n.name == "Primitive" && n.Get("Vdata") != null).ToArray();', '''var geometryNodes=Geometries(tree,geometryIds);
            var owners=new Dictionary<Node,Node>();
            foreach(var geometry in geometryNodes)
                foreach(var primitive in geometry.Get("Primitives").children.Where(n=>n.name=="Primitive"&&n.Get("Vdata")!=null))owners.Add(primitive,geometry);
            var primitives=owners.Keys.ToArray();''')
s=s.replace('var v = p.Numbers("Vdata"); var id = p.Numbers("Idata");', '''var v = p.Numbers("Vdata"); var id = p.Numbers("Idata");
                var placement=ScenePlacement(tree,owners[p]);''')
s=s.replace('verts.Add(new Vector3(-x, y, z)); uv.Add(new Vector2(u, 1 - w));', '''var placed=Vector3.Transform(new Vector3(x,y,z),placement);
                        if(!Finite(placed.X)||!Finite(placed.Y)||!Finite(placed.Z))throw new InvalidDataException("Non-finite scene placement.");
                        verts.Add(new Vector3(-placed.X,placed.Y,placed.Z)); uv.Add(new Vector2(u, 1 - w));''')
marker='        public static Model Read(string path, string[] geometryIds = null)'
helper='''        static Matrix4x4 ScenePlacement(Node tree,Node geometry)
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
'''
assert marker in s
s=s.replace(marker,helper+marker)
out=Path(__file__).parent/'DI3MeshReader.cs';out.write_text(s,encoding='utf-8');print(out)

