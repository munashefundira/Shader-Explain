import React, { useState } from 'react';
import './App.css';
import ShaderEditor from './components/ShaderEditor';
import ShaderVisualization from './components/ShaderVisualization';
import ExplanationDisplay from './components/ExplanationDisplay';
import axios from 'axios';

function App() {
  const [shaderCode, setShaderCode] = useState(`void main() {\n  gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);\n}`);
  const [analysis, setAnalysis] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleExplain = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://127.0.0.1:8000/explain', {
        code: shaderCode
      });
      
      setAnalysis(response.data.analysis);
      setExplanation(response.data.explanation);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to explain shader');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎨 ShaderExplain</h1>
        <p>Tool-Augmented LLM System for Explaining Computer Graphics Shader Programs</p>
        <p className="authors">by Munashe Fundira</p>
      </header>

      <div className="container">
        <div className="left-panel">
          <ShaderEditor 
            code={shaderCode} 
            onChange={setShaderCode}
            onExplain={handleExplain}
            loading={loading}
          />
          
          {analysis && (
            <ShaderVisualization 
              shaderCode={shaderCode}
              shaderType={analysis.shader_type}
            />
          )}
        </div>

        <div className="right-panel">
          {error && (
            <div className="error-box">
              <h3>❌ Error</h3>
              <p>{error}</p>
            </div>
          )}
          
          {analysis && explanation && (
            <ExplanationDisplay 
              analysis={analysis}
              explanation={explanation}
            />
          )}
          
          {!analysis && !error && !loading && (
            <div className="welcome-box">
              <h2>👋 Welcome to ShaderExplain</h2>
              <p>Enter your GLSL shader code on the left and click "Explain Shader" to get a detailed, educational explanation.</p>
              <h3>Features:</h3>
              <ul>
                <li>🔍 Advanced shader analysis</li>
                <li>🤖 AI-powered explanations</li>
                <li>📊 Complexity scoring</li>
                <li>🎓 Educational breakdowns</li>
                <li>🎨 Real-time visualization</li>
              </ul>
            </div>
          )}
        </div>
      </div>

      <footer className="App-footer">
        <p>Research Project - Menedżerska Akademia Nauk Stosowanych w Warszawie</p>
      </footer>
    </div>
  );
}

export default App;