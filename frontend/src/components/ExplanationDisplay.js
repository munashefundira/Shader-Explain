import React from 'react';
import ReactMarkdown from 'react-markdown';

function ExplanationDisplay({ analysis, explanation }) {
  return (
    <div className="explanation-container">
      <h2>📚 Shader Analysis & Explanation</h2>
      
      <div className="analysis-section">
        <h3>🔍 Automated Analysis</h3>
        
        <div className="analysis-grid">
          <div className="analysis-item">
            <strong>Shader Type</strong>
            <span>{analysis.shader_type}</span>
          </div>
          
          <div className="analysis-item">
            <strong>Complexity Score</strong>
            <span>{analysis.complexity_score} / 10</span>
          </div>
          
          <div className="analysis-item">
            <strong>Uniforms</strong>
            <span>{analysis.uniforms.length} found</span>
          </div>
          
          <div className="analysis-item">
            <strong>Uses Textures</strong>
            <span>{analysis.uses_texture ? 'Yes' : 'No'}</span>
          </div>
          
          <div className="analysis-item">
            <strong>Uses Lighting</strong>
            <span>{analysis.uses_lighting ? 'Yes' : 'No'}</span>
          </div>
          
          <div className="analysis-item">
            <strong>Transformations</strong>
            <span>{analysis.uses_transformations ? 'Yes' : 'No'}</span>
          </div>
        </div>

        {analysis.vector_operations.length > 0 && (
          <div style={{ marginTop: '15px' }}>
            <strong>Vector Operations:</strong>
            <p>{analysis.vector_operations.join(', ')}</p>
          </div>
        )}

        {analysis.matrix_operations.length > 0 && (
          <div style={{ marginTop: '10px' }}>
            <strong>Matrix Operations:</strong>
            <p>{analysis.matrix_operations.join(', ')}</p>
          </div>
        )}
      </div>

      <div className="explanation-text">
        <ReactMarkdown>{explanation}</ReactMarkdown>
      </div>
    </div>
  );
}

export default ExplanationDisplay;