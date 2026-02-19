from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import re
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

app = FastAPI(title="ShaderExplain", version="1.0.0", description="Tool-Augmented LLM System for Explaining Computer Graphics Shader Programs")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ ERROR: No Groq API key found!")
    print("Create a .env file with: GROQ_API_KEY=your-key-here")
    
client = Groq(api_key=api_key)

class ShaderRequest(BaseModel):
    code: str
    shader_type: str = "auto"  # auto, vertex, fragment

class ShaderAnalysis(BaseModel):
    shader_type: str
    uniforms: list
    attributes: list
    varyings: list
    inputs: list
    outputs: list
    uses_texture: bool
    uses_lighting: bool
    uses_transformations: bool
    has_vertex_transform: bool
    has_fragment_output: bool
    vector_operations: list
    matrix_operations: list
    mathematical_functions: list
    control_flow: list
    complexity_score: float

def advanced_shader_parser(code: str) -> dict:
    """
    Advanced shader parser that extracts:
    - Uniforms, attributes, varyings
    - Vector/matrix operations
    - Transformations
    - Lighting calculations
    - Texture sampling
    - Control flow
    """
    
    analysis = {
        "shader_type": "unknown",
        "uniforms": [],
        "attributes": [],
        "varyings": [],
        "inputs": [],
        "outputs": [],
        "uses_texture": False,
        "uses_lighting": False,
        "uses_transformations": False,
        "has_vertex_transform": False,
        "has_fragment_output": False,
        "vector_operations": [],
        "matrix_operations": [],
        "mathematical_functions": [],
        "control_flow": [],
        "complexity_score": 0.0
    }
    
    # Detect shader type
    if "gl_FragColor" in code or "fragColor" in code or "out vec4" in code:
        analysis["shader_type"] = "fragment"
        analysis["has_fragment_output"] = True
    elif "gl_Position" in code:
        analysis["shader_type"] = "vertex"
        analysis["has_vertex_transform"] = True
    
    # Extract uniforms
    uniforms = re.findall(r'uniform\s+(\w+)\s+(\w+)', code)
    analysis["uniforms"] = [{"type": u[0], "name": u[1]} for u in uniforms]
    
    # Extract attributes (vertex shader inputs)
    attributes = re.findall(r'attribute\s+(\w+)\s+(\w+)', code)
    analysis["attributes"] = [{"type": a[0], "name": a[1]} for a in attributes]
    
    # Extract varyings
    varyings = re.findall(r'varying\s+(\w+)\s+(\w+)', code)
    analysis["varyings"] = [{"type": v[0], "name": v[1]} for v in varyings]
    
    # Extract inputs (modern GLSL)
    inputs = re.findall(r'in\s+(\w+)\s+(\w+)', code)
    analysis["inputs"] = [{"type": i[0], "name": i[1]} for i in inputs]
    
    # Extract outputs (modern GLSL)
    outputs = re.findall(r'out\s+(\w+)\s+(\w+)', code)
    analysis["outputs"] = [{"type": o[0], "name": o[1]} for o in outputs]
    
    # Detect texture usage
    texture_keywords = ["texture", "texture2D", "textureCube", "sampler2D", "samplerCube"]
    analysis["uses_texture"] = any(keyword in code for keyword in texture_keywords)
    
    # Detect lighting calculations
    lighting_keywords = ["dot", "reflect", "normalize", "length", "distance", "diffuse", "specular", "ambient"]
    analysis["uses_lighting"] = any(keyword in code for keyword in lighting_keywords)
    
    # Detect transformations
    transform_keywords = ["mat4", "mat3", "modelMatrix", "viewMatrix", "projectionMatrix", "mvp"]
    analysis["uses_transformations"] = any(keyword in code for keyword in transform_keywords)
    
    # Vector operations
    vector_ops = []
    if "vec2" in code: vector_ops.append("2D vectors")
    if "vec3" in code: vector_ops.append("3D vectors")
    if "vec4" in code: vector_ops.append("4D vectors")
    if "normalize(" in code: vector_ops.append("normalization")
    if "dot(" in code: vector_ops.append("dot product")
    if "cross(" in code: vector_ops.append("cross product")
    if "length(" in code: vector_ops.append("vector length")
    analysis["vector_operations"] = vector_ops
    
    # Matrix operations
    matrix_ops = []
    if "mat2" in code: matrix_ops.append("2x2 matrices")
    if "mat3" in code: matrix_ops.append("3x3 matrices")
    if "mat4" in code: matrix_ops.append("4x4 matrices")
    if "*" in code and ("mat" in code or "Matrix" in code): matrix_ops.append("matrix multiplication")
    if "transpose(" in code: matrix_ops.append("matrix transpose")
    if "inverse(" in code: matrix_ops.append("matrix inverse")
    analysis["matrix_operations"] = matrix_ops
    
    # Mathematical functions
    math_funcs = []
    math_keywords = {
        "sin(": "sine",
        "cos(": "cosine",
        "tan(": "tangent",
        "pow(": "power",
        "exp(": "exponential",
        "log(": "logarithm",
        "sqrt(": "square root",
        "abs(": "absolute value",
        "floor(": "floor",
        "ceil(": "ceiling",
        "fract(": "fractional part",
        "mod(": "modulo",
        "min(": "minimum",
        "max(": "maximum",
        "clamp(": "clamp",
        "mix(": "linear interpolation",
        "step(": "step function",
        "smoothstep(": "smooth step"
    }
    for keyword, name in math_keywords.items():
        if keyword in code:
            math_funcs.append(name)
    analysis["mathematical_functions"] = math_funcs
    
    # Control flow
    control_flow = []
    if "if" in code: control_flow.append("conditionals")
    if "for" in code: control_flow.append("for loops")
    if "while" in code: control_flow.append("while loops")
    if "switch" in code: control_flow.append("switch statements")
    analysis["control_flow"] = control_flow
    
    # Calculate complexity score (simple heuristic)
    complexity = 0.0
    complexity += len(analysis["uniforms"]) * 0.5
    complexity += len(analysis["vector_operations"]) * 1.0
    complexity += len(analysis["matrix_operations"]) * 2.0
    complexity += len(analysis["mathematical_functions"]) * 0.5
    complexity += len(analysis["control_flow"]) * 3.0
    if analysis["uses_texture"]: complexity += 2.0
    if analysis["uses_lighting"]: complexity += 3.0
    if analysis["uses_transformations"]: complexity += 2.0
    
    analysis["complexity_score"] = round(complexity, 2)
    
    return analysis

@app.get("/")
def home():
    return {
        "message": "ShaderExplain API v1.0 - Tool-Augmented LLM System",
        "description": "Explaining Computer Graphics Shader Programs",
        "authors": "Munashe Fundira, Kumar Nalinaksh",
        "docs": "/docs",
        "endpoints": {
            "POST /explain": "Explain a shader program",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "api": "operational"}

@app.post("/explain")
def explain_shader(req: ShaderRequest):
    try:
        # Advanced shader analysis
        analysis = advanced_shader_parser(req.code)
        
        print(f"📊 Advanced Analysis: {analysis}")
        
        # Create enhanced prompt for LLM
        prompt = f"""You are an expert computer graphics teacher explaining GLSL shader code to students learning graphics programming.

**Shader Code:**
```glsl
{req.code}
```

**Automated Analysis Results:**
- Shader Type: {analysis['shader_type']}
- Complexity Score: {analysis['complexity_score']}/10
- Uniforms: {len(analysis['uniforms'])} found - {analysis['uniforms']}
- Attributes: {len(analysis['attributes'])} found - {analysis['attributes']}
- Varyings: {len(analysis['varyings'])} found - {analysis['varyings']}
- Uses Textures: {analysis['uses_texture']}
- Uses Lighting: {analysis['uses_lighting']}
- Uses Transformations: {analysis['uses_transformations']}
- Vector Operations: {', '.join(analysis['vector_operations'])}
- Matrix Operations: {', '.join(analysis['matrix_operations'])}
- Mathematical Functions: {', '.join(analysis['mathematical_functions'])}
- Control Flow: {', '.join(analysis['control_flow'])}

**Please provide a comprehensive educational explanation with:**

1. **Overview** (2-3 sentences)
   - What does this shader do?
   - What is its purpose in the graphics pipeline?

2. **Pipeline Stage**
   - Explain which stage of the graphics pipeline this shader belongs to
   - What data does it receive and what does it output?

3. **Line-by-Line Breakdown**
   - Explain each significant line of code
   - Focus on the graphics concepts being applied

4. **Graphics Concepts Used**
   - Explain the mathematical and graphical concepts
   - For vectors: explain coordinate spaces, transformations
   - For matrices: explain transformation matrices, spaces (model/view/projection)
   - For lighting: explain illumination models (Phong, Blinn-Phong, etc.)
   - For textures: explain UV coordinates, sampling, filtering

5. **Common Use Cases**
   - Where would this shader be used in real applications?
   - What visual effects does it create?

6. **Learning Tips for Beginners**
   - What should students understand before working with this shader?
   - Suggestions for experimentation and learning

Keep explanations clear, educational, and suitable for computer graphics students."""

        # Generate explanation using Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        explanation = response.choices[0].message.content
        
        return {
            "success": True,
            "analysis": analysis,
            "explanation": explanation,
            "metadata": {
                "model": "llama-3.3-70b-versatile",
                "provider": "Groq",
                "version": "1.0.0"
            }
        }
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating explanation: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ShaderExplain v1.0...")
    print("📖 Research-based Tool-Augmented LLM System")
    print("👥 Authors: Munashe Fundira, Kumar Nalinaksh")
    print("📚 Open http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)