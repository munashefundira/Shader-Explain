import React from 'react';
import Editor from '@monaco-editor/react';

function ShaderEditor({ code, onChange, onExplain, loading }) {
  return (
    <div className="editor-container">
      <h2>📝 Shader Code Editor</h2>
      
      <div className="monaco-wrapper">
        <Editor
          height="400px"
          defaultLanguage="glsl"
          value={code}
          onChange={onChange}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
          }}
        />
      </div>

      <button 
        className="explain-button"
        onClick={onExplain}
        disabled={loading}
      >
        {loading ? '⏳ Analyzing...' : '🚀 Explain Shader'}
      </button>
    </div>
  );
}

export default ShaderEditor;